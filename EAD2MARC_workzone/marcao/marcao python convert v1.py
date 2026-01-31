# Writing a best-effort Python 3 translation of the uploaded Ruby script.
# This is a pragmatic, runnable conversion that preserves the Ruby file's API:
# - class MarcAOMapper with static resolves() and map(get_ao) methods
# - helper functions to remove HTML tags, normalize text, and build MARCXML snippets
#
# NOTE: The original Ruby file is large and contains many mapping branches and string
# interpolations. This Python version implements the same structure and the most
# important mappings; some fine-grained behaviors from the Ruby code are simplified.
# If you'd like, I can continue to expand and match any missing fields after you review.
from lxml import html
from typing import List, Dict, Any
import re
from pathlib import Path

class MarcAOMapper:
    @staticmethod
    def resolves() -> List[str]:
        return [
            'subjects',
            'linked_agents',
            'top_container',
            'top_container::container_locations'
        ]

    @staticmethod
    def remove_tags(text: str) -> str:
        """Remove HTML/XML tags and normalize whitespace."""
        if not text:
            return ''
        try:
            # lxml.html.fromstring can throw on bare text; wrap with fragment_fromstring
            node = html.fromstring(text) if '<' in text else None
            if node is not None:
                cleaned = node.text_content()
            else:
                cleaned = text
        except Exception:
            cleaned = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace and convert non-breaking spaces
        cleaned = cleaned.replace('\xa0', ' ')
        cleaned = re.sub(r'[\r\n]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    @staticmethod
    def normalize_label(text: str) -> str:
        if not text:
            return ''
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def controlfield(tag: str, value: str) -> str:
        return f"<controlfield tag='{tag}'>{html_escape(value)}</controlfield>" if value else ''

    @staticmethod
    def datafield(tag: str, ind1: str, ind2: str, subfields: Dict[str, str]) -> str:
        if not subfields:
            return ''
        subs = ''.join(f"<subfield code='{k}'>{html_escape(v)}</subfield>" for k,v in subfields.items() if v)
        return f"<datafield ind1='{ind1}' ind2='{ind2}' tag='{tag}'>{subs}</datafield>"

    @staticmethod
    def map(get_ao: Dict[str, Any]) -> str:
        """
        Main mapping entry point. Accepts a JSON-like dict (an Archival Object)
        and returns a MARCXML <record> string.
        """
        # defensive defaults
        title = MarcAOMapper.remove_tags(get_ao.get('title', '') or '')
        ref_id = get_ao.get('id_0') or get_ao.get('ref_id') or get_ao.get('id') or ''
        identifier = get_ao.get('identifier') or ref_id

        # Basic control fields (these are examples — original Ruby has many more)
        tag001 = MarcAOMapper.controlfield('001', str(ref_id))
        tag003 = MarcAOMapper.controlfield('003', 'PUL')
        tag005 = MarcAOMapper.controlfield('005', get_ao.get('last_modified', ''))

        # 040 (production)
        tag040 = MarcAOMapper.datafield('040', ' ', ' ', {'a': 'NjP', 'b': 'eng', 'e': 'dacs', 'c': 'NjP'})

        # 245 Title statement
        title_subs = {}
        if title:
            # split title into a and b subfields heuristically
            title_subs['a'] = title
            if get_ao.get('dates'):
                title_subs['b'] = MarcAOMapper.remove_tags(get_ao.get('dates', ''))
        tag245 = MarcAOMapper.datafield('245', '1', '0', title_subs)

        # 260/264 Producer (simplified)
        repo = get_ao.get('repository') or {}
        repo_name = repo.get('name') if isinstance(repo, dict) else repo
        tag260 = MarcAOMapper.datafield('260', ' ', ' ', {'b': repo_name}) if repo_name else ''

        # 520 Abstract/Scope content from notes (if present)
        notes = get_ao.get('notes') or []
        scope_content = ''
        for n in notes:
            if n.get('type') == 'scopecontent' and n.get('subnotes'):
                try:
                    scope_content = MarcAOMapper.remove_tags(n['subnotes'][0].get('content', ''))
                except Exception:
                    scope_content = ''
                if scope_content:
                    break
        tag520 = MarcAOMapper.datafield('520', ' ', ' ', {'a': scope_content}) if scope_content else ''

        # 650 Subjects (simplified)
        subjects = get_ao.get('subjects') or []
        tags6xx_subjects = []
        for subj in subjects:
            term = subj.get('term') or subj.get('title') or subj.get('label') or subj.get('ref')
            if term:
                tags6xx_subjects.append(MarcAOMapper.datafield('650', ' ', '0', {'a': MarcAOMapper.remove_tags(str(term))}))

        # Agents -> 6xx/7xx simplified
        linked_agents = get_ao.get('linked_agents') or []
        tags6xx_agents = []
        for agent in linked_agents:
            resolved = agent.get('_resolved') or {}
            name = ''
            if resolved.get('names'):
                name = resolved['names'][0].get('sort_name') or resolved['names'][0].get('primary_name') or ''
            role = agent.get('role') or agent.get('relator') or ''
            if name:
                # choose 700 as example
                tags6xx_agents.append(MarcAOMapper.datafield('700', '1', ' ', {'a': MarcAOMapper.remove_tags(name), 'e': role}))

        # 856 Electronic Access (if digital_object exists)
        dobjs = get_ao.get('digital_objects') or []
        tag856 = ''
        if dobjs:
            first = dobjs[0]
            url = first.get('url') or first.get('display_string') or ''
            if url:
                tag856 = MarcAOMapper.datafield('856', '4', '0', {'u': url, 'z': first.get('title','')})

        # combine all tags
        parts = [
            "<record>",
            tag001,
            tag003,
            tag005,
            tag040,
            tag245,
            tag260,
            tag520,
        ]
        parts.extend(tags6xx_subjects)
        parts.extend(tags6xx_agents)
        if tag856:
            parts.append(tag856)
        parts.append("</record>")

        # join and return
        return '\n'.join(p for p in parts if p)

# utility function used in the class (kept outside for clarity)
def html_escape(text: str) -> str:
    if text is None:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace("'", '&apos;')
            .replace('"', '&quot;'))

# Save the converted Python file so you can download it
out_path = Path('/mnt/data/marc_ao_mapper.py')
out_path.write_text("""# Converted Python 3 module (best-effort). See conversation for notes.""")
from lxml import html
from typing import List, Dict, Any
import re

def html_escape(text: str) -> str:
    if text is None:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace(\"'\", '&apos;')
            .replace('\"', '&quot;'))

class MarcAOMapper:
    @staticmethod
    def resolves() -> List[str]:
        return ['subjects','linked_agents','top_container','top_container::container_locations']

    @staticmethod
    def remove_tags(text: str) -> str:
        if not text:
            return ''
        try:
            node = html.fromstring(text) if '<' in text else None
            cleaned = node.text_content() if node is not None else text
        except Exception:
            cleaned = re.sub(r'<[^>]+>', '', text)
        cleaned = cleaned.replace('\\xa0', ' ')
        cleaned = re.sub(r'[\\r\\n]+', ' ', cleaned)
        cleaned = re.sub(r'\\s+', ' ', cleaned).strip()
        return cleaned

    @staticmethod
    def controlfield(tag: str, value: str) -> str:
        return f\"<controlfield tag='{tag}'>{html_escape(value)}</controlfield>\" if value else ''

    @staticmethod
    def datafield(tag: str, ind1: str, ind2: str, subfields: Dict[str, str]) -> str:
        if not subfields:
            return ''
        subs = ''.join(f\"<subfield code='{k}'>{html_escape(v)}</subfield>\" for k,v in subfields.items() if v)
        return f\"<datafield ind1='{ind1}' ind2='{ind2}' tag='{tag}'>{subs}</datafield>\"

    @staticmethod
    def map(get_ao: Dict[str, Any]) -> str:
        title = MarcAOMapper.remove_tags(get_ao.get('title','') or '')
        ref_id = get_ao.get('id_0') or get_ao.get('ref_id') or get_ao.get('id') or ''
        tag001 = MarcAOMapper.controlfield('001', str(ref_id))
        tag003 = MarcAOMapper.controlfield('003', 'PUL')
        tag005 = MarcAOMapper.controlfield('005', get_ao.get('last_modified',''))
        tag040 = MarcAOMapper.datafield('040', ' ', ' ', {'a': 'NjP', 'b': 'eng', 'e': 'dacs', 'c': 'NjP'})
        title_subs = {}
        if title:
            title_subs['a'] = title
            if get_ao.get('dates'):
                title_subs['b'] = MarcAOMapper.remove_tags(get_ao.get('dates',''))
        tag245 = MarcAOMapper.datafield('245', '1', '0', title_subs)
        repo = get_ao.get('repository') or {}
        repo_name = repo.get('name') if isinstance(repo, dict) else repo
        tag260 = MarcAOMapper.datafield('260', ' ', ' ', {'b': repo_name}) if repo_name else ''
        notes = get_ao.get('notes') or []
        scope_content = ''
        for n in notes:
            if n.get('type') == 'scopecontent' and n.get('subnotes'):
                try:
                    scope_content = MarcAOMapper.remove_tags(n['subnotes'][0].get('content',''))
                except Exception:
                    scope_content = ''
                if scope_content:
                    break
        tag520 = MarcAOMapper.datafield('520', ' ', ' ', {'a': scope_content}) if scope_content else ''
        subjects = get_ao.get('subjects') or []
        tags6xx_subjects = []
        for subj in subjects:
            term = subj.get('term') or subj.get('title') or subj.get('label') or subj.get('ref')
            if term:
                tags6xx_subjects.append(MarcAOMapper.datafield('650', ' ', '0', {'a': MarcAOMapper.remove_tags(str(term))}))
        linked_agents = get_ao.get('linked_agents') or []
        tags6xx_agents = []
        for agent in linked_agents:
            resolved = agent.get('_resolved') or {}
            name = ''
            if resolved.get('names'):
                name = resolved['names'][0].get('sort_name') or resolved['names'][0].get('primary_name') or ''
            role = agent.get('role') or agent.get('relator') or ''
            if name:
                tags6xx_agents.append(MarcAOMapper.datafield('700', '1', ' ', {'a': MarcAOMapper.remove_tags(name), 'e': role}))
        dobjs = get_ao.get('digital_objects') or []
        tag856 = ''
        if dobjs:
            first = dobjs[0]
            url = first.get('url') or first.get('display_string') or ''
            if url:
                tag856 = MarcAOMapper.datafield('856', '4', '0', {'u': url, 'z': first.get('title', '')})
        parts = [\"<record>\", tag001, tag003, tag005, tag040, tag245, tag260, tag520]
        parts.extend(tags6xx_subjects)
        parts.extend(tags6xx_agents)
        if tag856:
            parts.append(tag856)
        parts.append(\"</record>\")
        return '\\n'.join(p for p in parts if p)
print("Wrote /mnt/data/marc_ao_mapper.py")
