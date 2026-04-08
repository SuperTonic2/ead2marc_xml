import re
import time
import requests
import html
import pycallnumber as pycn
import unicodedata
from copy import deepcopy
from lxml import etree
from datetime import datetime
# import collections

# Rate-limited wrapper for requests to loc.gov (max 10 requests/minute)
# (This portion of code was generated utilizing Claude Opus 4.6)
_last_loc_request_time = 0

def loc_get(url, **kwargs):
    """Rate-limited requests.get for loc.gov endpoints."""
    global _last_loc_request_time
    elapsed = time.time() - _last_loc_request_time
    if elapsed < 7:
        time.sleep(7 - elapsed)
    _last_loc_request_time = time.time()
    return requests.get(url, **kwargs)

marc_rda_relators = {
# Creates dictionary of relator codes common to MARC and RDA
    "ape": "appellee",
    "apl": "appellant",
    "arc": "architect",
    "art": "artist",
    "aup": "audio producer",
    "aus": "screenwriter",
    "aut": "author",
    "bka": "book artist",
    "cad": "casting director",
    "chr": "choreographer",
    "cll": "calligrapher",
    "cmp": "composer",
    "com": "compiler",
    "cou": "court governed",
    "csl": "consultant",
    "ctg": "cartographer",
    "dfd": "defendant",
    "dgc": "degree committee member",
    "dgg": "degree granting institution",
    "dgs": "degree supervisor",
    "drt": "director",
    "dsr": "designer",
    "dte": "dedicatee",
    "dto": "dedicator",
    "edd": "editorial director",
    "enj": "enacting jurisdiction",
    "fmd": "film director",
    "fmk": "filmmaker",
    "fmp": "film producer",
    "his": "host institution",
    "inv": "inventor",
    "isb": "issuing body",
    "ive": "interviewee",
    "ivr": "interviewer",
    "jud": "judge",
    "jug": "jurisdiction governed",
    "lbt": "librettist",
    "lsa": "landscape architect",
    "lyr": "lyricist",
    "med": "medium",
    "orm": "organizer",
    "pht": "photographer",
    "pra": "praeses",
    "prf": "performer",
    "prg": "programmer",
    "prn": "production company",
    "pro": "producer",
    "ptf": "plaintiff",
    "rap": "rapporteur",
    "rcp": "addressee",
    "rdd": "radio director",
    "res": "researcher",
    "rpc": "radio producer",
    "rsp": "respondent",
    "rxa": "remix artist",
    "scl": "sculptor",
    "tld": "television director",
    "tlp": "television producer",
    }


def oclc_check(raw):
    '''Checks unitid elements for OCLC identifiers and returns XML comment if found'''

    unitid_list = raw.xpath(".//*[local-name()='unitid']")
    for unitid in unitid_list:
        unitid_type = unitid.get("type", "").lower()
        unitid_str = unitid.xpath("string()").strip()
        if unitid_type == "oclc":
            oclc_comment_str = (
                f"NOTE: OCLC no. {unitid_str} is listed as an identifier in this record.\n"
                f"Check and consider updating the existing OCLC record.\n"
            )
            oclc_comment = etree.Comment(oclc_comment_str)
            return oclc_comment


def ead2marc_020(unitid_raw):
    '''Creates 020 (ISBN) from unitid element'''

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    a_020 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 020 FIELD
    field_020_open = """<datafield tag="020" ind1=" " ind2=" ">"""
    field_020_str_nb = field_020_open + a_020 + "</datafield>"
    field_020_xml = etree.fromstring(field_020_str_nb)
    # field_020_str = etree.tostring(field_020_xml, pretty_print=True, encoding="unicode")

    # print(field_020_str)
    return field_020_xml


def ead2marc_022(unitid_raw):
    '''Creates 022 (ISSN) from unitid element'''

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    a_022 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 022 FIELD
    field_022_open = """<datafield tag="022" ind1=" " ind2=" ">"""
    field_022_str_nb = field_022_open + a_022 + "</datafield>"
    field_022_xml = etree.fromstring(field_022_str_nb)
    # field_022_str = etree.tostring(field_022_xml, pretty_print=True, encoding="unicode")

    # print(field_022_str)
    return field_022_xml


def ead2marc_023(unitid_raw):
    '''Creates 023 (standard film number) from unitid element'''

    # INDICATORS
    # Indicator 1
    unitid_type = unitid_raw.get("type", "").lower()
    if unitid_type == "issn-h":
        ind1_023 = "1"
    else:
        ind1_023 = "0"

    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    a_023 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 023 FIELD
    field_023_open = f"""<datafield tag="023" ind1="{ind1_023}" ind2=" ">"""
    field_023_str_nb = field_023_open + a_023 + "</datafield>"
    field_023_xml = etree.fromstring(field_023_str_nb)
    # field_023_str = etree.tostring(field_023_xml, pretty_print=True, encoding="unicode")

    # print(field_023_str)
    return field_023_xml


def ead2marc_024(unitid_raw):
    '''Creates 024 (other standard identifier) from unitid element'''

    # INDICATORS
    # Indicator 1
    unitid_type = unitid_raw.get("type", "").lower()
    field_2_024 = ""
    if (unitid_type == "isrc") or ("international standard recording code" in unitid_type):
        ind1_024 = "0"
    elif (unitid_type == "upc") or ("universal product code" in unitid_type):
        ind1_024 = "1"
    elif (unitid_type == "ismn") or ("international standard music" in unitid_type):
        ind1_024 = "2"
    elif (unitid_type == "ean") or ("international article number" in unitid_type):
        ind1_024 = "3"
    elif (unitid_type == "sici") or ("serial item and contribution" in unitid_type):
        ind1_024 = "4"
    elif unitid_type:
        ind1_024 = "7"
        field_2_024 = f"""<subfield code="2">{unitid_type}</subfield>"""
    else:
        ind1_024 = "8"

    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    a_024 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 024 FIELD
    field_024_open = f"""<datafield tag="024" ind1="{ind1_024}" ind2=" ">"""
    field_024_str_nb = field_024_open + a_024 + field_2_024 + "</datafield>"
    field_024_xml = etree.fromstring(field_024_str_nb)
    # field_024_str = etree.tostring(field_024_xml, pretty_print=True, encoding="unicode")

    # print(field_024_str)
    return field_024_xml


def ead2marc_026(unitid_raw):
    '''Creates 026 (fingerprint identifier) from unitid element'''

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield E
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    e_026 = f"""<subfield code="e">{unitid_str}</subfield>"""
    #NOTE: Only unparsed fingerprint identifiers (subfield E) are currently supported

    # PRINT 026 FIELD
    field_026_open = """<datafield tag="026" ind1=" " ind2=" ">"""
    field_026_str_nb = field_026_open + e_026 + "</datafield>"
    field_026_xml = etree.fromstring(field_026_str_nb)
    # field_026_str = etree.tostring(field_026_xml, pretty_print=True, encoding="unicode")

    # print(field_026_str)
    return field_026_xml


def ead2marc_027(unitid_raw):
    '''Creates 027 (standard technical report number) from unitid element'''

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    a_027 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 027 FIELD
    field_027_open = """<datafield tag="027" ind1=" " ind2=" ">"""
    field_027_str_nb = field_027_open + a_027 + "</datafield>"
    field_027_xml = etree.fromstring(field_027_str_nb)
    # field_027_str = etree.tostring(field_027_xml, pretty_print=True, encoding="unicode")

    # print(field_027_str)
    return field_027_xml


def ead2marc_028(unitid_raw):
    '''Creates 028 (publisher or distributor number) from unitid element'''

    # INDICATORS
    # Indicator 1
    unitid_type = unitid_raw.get("type", "").lower()
    field_2_028 = ""
    if "issue" in unitid_type:
        ind1_028 = "0"
    elif "matrix" in unitid_type:
        ind1_028 = "1"
    elif "plate" in unitid_type:
        ind1_028 = "2"
    elif "music" in unitid_type:
        ind1_028 = "3"
    elif "video" in unitid_type:
        ind1_028 = "4"
    elif "distributor" in unitid_type:
        ind1_028 = "6"
    else:
        ind1_028 = "5"

    # Indicator 2 is constant (0)
    # NOTE: Only ind2 0 is currently supported

    # SUBFIELDS
    # Subfield A
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    unitid_str = html.escape(unitid_str)
    a_028 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 028 FIELD
    field_028_open = f"""<datafield tag="028" ind1="{ind1_028}" ind2=" ">"""
    field_028_str_nb = field_028_open + a_028 + field_2_028 + "</datafield>"
    field_028_xml = etree.fromstring(field_028_str_nb)
    # field_028_str = etree.tostring(field_028_xml, pretty_print=True, encoding="unicode")

    # print(field_028_str)
    return field_028_xml


def ead2marc_050(unitid_raw):
    '''Parses LC call number and creates 050 with classification and cutter'''

    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (4)

    # SUBFIELDS
    #Checks for number of cutters and constrcuts $a content and $b content accordingly
    cn = pycn.callnumber(unitid_str)
    class_str = str(cn.classification)
    class_ns = class_str.replace(" ", "")
    if cn.edition:
        all_eds = str(cn.edition)
    else:
        all_eds = ""
    if cn.item:
        all_items = str(cn.item)
    else:
        all_items = ""
    first_cutter = "." + str(cn.cutters[0])
    if len(cn.cutters) <= 1:
        #Subfield content construction for call numbers with 1 cutter
        a_content = class_ns
        b_content = first_cutter + all_eds + all_items
    else:
        #Subfield content construction for call numbers with 2+ cutters
        second_on_cutters_raw = cn.cutters[1:]
        second_on_cutters_list = []
        for cutter in second_on_cutters_raw:
            cutter_str = str(cutter)
            second_on_cutters_list.append(cutter_str)
        second_on_cutters = " ".join(second_on_cutters_list)
        a_content = class_ns + first_cutter
        b_content = second_on_cutters + all_eds + all_items

    # Subfield A
    a_050 = f"""<subfield code="a">{a_content}</subfield>"""

    # Subfield B
    b_050 = f"""<subfield code="b">{b_content}</subfield>"""

    # PRINT 050 FIELD
    field_050_open = """<datafield tag="050" ind1=" " ind2="4">"""
    field_050_str_nb = field_050_open + a_050 + b_050 + "</datafield>"
    field_050_xml = etree.fromstring(field_050_str_nb)
    # field_050_str = etree.tostring(field_050_xml, pretty_print=True, encoding="unicode")

    # print(field_050_str)
    return field_050_xml

def ead2marc_035(unitid_raw):
    '''Parses local collection numbers and creates 035'''
    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    if unitid_str.startswith("MC"):
        a_content = f"""(Inu-MuID){unitid_str}"""
    else:
        a_content = f"""{unitid_str}"""
    a_035 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 035 FIELD
    field_035_open = """<datafield tag="035" ind1=" " ind2=" ">"""
    field_035_str_nb = field_035_open + a_035 + "</datafield>"
    field_035_xml = etree.fromstring(field_035_str_nb)
    # field_035_str = etree.tostring(field_035_xml, pretty_print=True, encoding="unicode")

    # print(field_035_str)
    return field_035_xml

def ead2marc_035_va(root, raw):
    level = raw.attrib['level']
    num_fetch = root.xpath(".//*[local-name()='num']")
    recordid_fetch = root.xpath(".//*[local-name()='recordid']")
    num_fetch.extend(recordid_fetch) # (Troubleshot with Claude Opus 4.6)
    field_035_va_xml_list = []
    if level == "collection" and num_fetch:
        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indiactor 2 is constant (9)

        # SUBFIELDS
        # Subfield A
        for num_raw in num_fetch:
            num_clean = num_raw.xpath("string()").strip()
            num_clean = html.escape(num_clean)
            a_035_va = f"""<subfield code="a">(EADID){num_clean}</subfield>"""

            # PRINT 099 FIELD
            field_035_va_open = """<datafield tag="099" ind1=" " ind2="9">"""
            field_035_va_str_nb = field_035_va_open + a_035_va + "</datafield>"
            field_035_va_xml = etree.fromstring(field_035_va_str_nb)
            field_035_va_xml_list.append(field_035_va_xml)
            # field_035_va_str = etree.tostring(field_035_va_xml, pretty_print=True, encoding="unicode")
            # print(field_035_va_str)
        
        return field_035_va_xml_list



def ead2marc_082(unitid_raw):
    '''Parses Dewey call number and creates 082 with classification and cutter'''

    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())
    cn = pycn.callnumber(unitid_str)

    # INDICATORS
    # Indicator 1 is constant (0)
    # Indicator 2 is constant (4)

    # SUBFIELDS
    # Subfield A
    class_str = str(cn.classification)
    class_ns = class_str.replace(" ", "")
    a_082 = f"""<subfield code="a">{class_ns}</subfield>"""

    # Subfield B
    if cn.cutters:
        all_cutters = str(cn.cutters)
    else:
        all_cutters = ""
    if cn.item:
        all_items = str(cn.item)
    else:
        all_items = ""
    b_content = all_cutters + all_items
    b_082 = f"""<subfield code="b">{b_content}</subfield>"""

    # PRINT 082 FIELD
    field_082_open = """<datafield tag="082" ind1="0" ind2="4">"""
    field_082_str_nb = field_082_open + a_082 + b_082 + "</datafield>"
    field_082_xml = etree.fromstring(field_082_str_nb)
    # field_082_str = etree.tostring(field_082_xml, pretty_print=True, encoding="unicode")

    # print(field_082_str)
    return field_082_xml


def ead2marc_086(unitid_raw):
    '''Creates 086 (Government Documents Classification Number) from unitid'''

    unitid_str = unitid_raw.xpath("string()").strip()
    unitid_str = " ".join(unitid_str.split())

    # INDICATORS
    # Indicator 1 is constant (0)
    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield A
    a_086 = f"""<subfield code="a">{unitid_str}</subfield>"""

    # PRINT 086 FIELD
    field_086_open = """<datafield tag="086" ind1=" " ind2="4">"""
    field_086_str_nb = field_086_open + a_086 + "</datafield>"
    field_086_xml = etree.fromstring(field_086_str_nb)
    # field_086_str = etree.tostring(field_086_xml, pretty_print=True, encoding="unicode")

    # print(field_086_str)
    return field_086_xml


def ead2marc_02x_03x_05x_08x(raw):
    '''Routes unitid elements to a 02x, 035, 050, or 08x field based on number type'''
    
    level = raw.attrib['level']
    field_02x_03x_05x_08x_xml_list = []
    unitid_list = raw.xpath(".//*[local-name()='unitid']")
    for unitid in unitid_list:
        unitid_type = unitid.get("type", "").lower()
        unitid_str = unitid.xpath("string()").strip()
        if unitid.get("localtype") == "aspace_uri":
            continue
        else:
            # (Troubleshot with Claude Opus 4.6)
            callnotest = pycn.callnumber(unitid_str)
            callno_type = type(callnotest).__name__
            if callno_type == "LC":
                field_050_xml = ead2marc_050(unitid)
                field_02x_03x_05x_08x_xml_list.append(field_050_xml)
            elif callno_type == "Dewey":
                field_082_xml = ead2marc_082(unitid)
                field_02x_03x_05x_08x_xml_list.append(field_082_xml)
            elif callno_type == "SuDoc":
                field_086_xml = ead2marc_086(unitid)
                field_02x_03x_05x_08x_xml_list.append(field_086_xml)
            else:
                if (unitid_type == "isbn") or ("international standard book" in unitid_type):
                    field_020_xml = ead2marc_020(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_020_xml)
                elif unitid_type == "issn" or ("international standard serial" in unitid_type and "cluster" not in unitid_type):
                    field_022_xml = ead2marc_022(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_022_xml)
                elif (unitid_type == "issn-l" or unitid_type == "issn-h") or ("international standard serial" in unitid_type and "cluster" in unitid_type):
                    field_023_xml = ead2marc_023(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_023_xml)
                elif (unitid_type == "isrc") or ("international standard recording code" in unitid_type):
                    field_024_xml = ead2marc_024(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_024_xml)
                elif (unitid_type == "upc") or ("universal product code" in unitid_type):
                    field_024_xml = ead2marc_024(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_024_xml)
                elif (unitid_type == "ismn") or ("international standard music" in unitid_type):
                    field_024_xml = ead2marc_024(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_024_xml)
                elif (unitid_type == "ean") or ("international article number" in unitid_type):
                    field_024_xml = ead2marc_024(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_024_xml)
                elif (unitid_type == "sici") or ("serial item and contribution" in unitid_type):
                    field_024_xml = ead2marc_024(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_024_xml)
                elif unitid_type == "fingerprint" or unitid_type == "fingerprint identifier":
                    field_026_xml = ead2marc_026(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_026_xml)
                elif (unitid_type == "strn" or unitid_type == "isrn") or ("standard technical report" in unitid_type):
                    field_027_xml = ead2marc_027(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_027_xml)
                elif ("publisher" in unitid_type) or ("issue" in unitid_type) or ("matrix" in unitid_type) or ("plate" in unitid_type) or ("distributor" in unitid_type):
                    field_028_xml = ead2marc_028(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_028_xml)
                elif level == "collection":
                    if unitid_str.startswith("VA"):
                        field_035_xml = ead2marc_035_va(unitid)
                    else:
                        field_035_xml = ead2marc_035(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_035_xml)
                else:
                    field_024_xml = ead2marc_024(unitid)
                    field_02x_03x_05x_08x_xml_list.append(field_024_xml)
    
    if field_02x_03x_05x_08x_xml_list:
        return field_02x_03x_05x_08x_xml_list


def ead2marc_040():
    '''Creates 040 for IU Libraries (constant)'''

    field_040_xml_list = []
    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)
    # SUBFIELDS
    # PRINT 040 FIELD
    field_040_open = """<datafield tag="040" ind1=" " ind2=" ">"""

    # Subfield A
    a_040 = """<subfield code="a">IUL</subfield>"""

    # Subfield B
    b_040 = """<subfield code="b">eng</subfield>"""

    # Subfield E
    e_040 = """<subfield code="e">rda</subfield>"""

    # Subfield C
    c_040 = """<subfield code="c">IUL</subfield>"""
    field_040_close = """</datafield>"""

    field_040_str_nb = field_040_open + a_040 + b_040 + e_040 + c_040 + field_040_close
    field_040_xml = etree.fromstring(field_040_str_nb)
    field_040_xml_list.append(field_040_xml)
    # field_040_str = etree.tostring(field_040_xml, pretty_print=True, encoding="unicode")

    # print(field_040_str)
    return field_040_xml_list


def ead2marc_041(raw):
    '''Creates 041 (language code) from languageset elements'''
    # ISO 639-2/T to MARC (ISO 639-2/B) mapping
    # Only needed if source uses terminology codes instead of bibliographic codes
    marc_language_codes = {
        "aar": "Afar",
        "abk": "Abkhaz",
        "ace": "Achinese",
        "ach": "Acoli",
        "ada": "Adangme",
        "ady": "Adygei",
        "afa": "Afroasiatic (Other)",
        "afh": "Afrihili (Artificial language)",
        "afr": "Afrikaans",
        "ain": "Ainu",
        "ajm": "Aljamía",
        "aka": "Akan",
        "akk": "Akkadian",
        "alb": "Albanian",
        "ale": "Aleut",
        "alg": "Algonquian (Other)",
        "alt": "Altai",
        "amh": "Amharic",
        "ang": "English, Old (ca. 450-1100)",
        "anp": "Angika",
        "apa": "Apache languages",
        "ara": "Arabic",
        "arc": "Aramaic",
        "arg": "Aragonese",
        "arm": "Armenian",
        "arn": "Mapuche",
        "arp": "Arapaho",
        "art": "Artificial (Other)",
        "arw": "Arawak",
        "asm": "Assamese",
        "ast": "Bable",
        "ath": "Athapascan (Other)",
        "aus": "Australian languages",
        "ava": "Avaric",
        "ave": "Avestan",
        "awa": "Awadhi",
        "aym": "Aymara",
        "aze": "Azerbaijani",
        "bad": "Banda languages",
        "bai": "Bamileke languages",
        "bak": "Bashkir",
        "bal": "Baluchi",
        "bam": "Bambara",
        "ban": "Balinese",
        "baq": "Basque",
        "bas": "Basa",
        "bat": "Baltic (Other)",
        "bej": "Beja",
        "bel": "Belarusian",
        "bem": "Bemba",
        "ben": "Bengali",
        "ber": "Berber (Other)",
        "bho": "Bhojpuri",
        "bih": "Bihari (Other)",
        "bik": "Bikol",
        "bin": "Edo",
        "bis": "Bislama",
        "bla": "Siksika",
        "bnt": "Bantu (Other)",
        "bos": "Bosnian",
        "bra": "Braj",
        "bre": "Breton",
        "btk": "Batak",
        "bua": "Buriat",
        "bug": "Bugis",
        "bul": "Bulgarian",
        "bur": "Burmese",
        "byn": "Bilin",
        "cad": "Caddo",
        "cai": "Central American Indian (Other)",
        "cam": "Khmer",
        "car": "Carib",
        "cat": "Catalan",
        "cau": "Caucasian (Other)",
        "ceb": "Cebuano",
        "cel": "Celtic (Other)",
        "cha": "Chamorro",
        "chb": "Chibcha",
        "che": "Chechen",
        "chg": "Chagatai",
        "chi": "Chinese",
        "chk": "Chuukese",
        "chm": "Mari",
        "chn": "Chinook jargon",
        "cho": "Choctaw",
        "chp": "Chipewyan",
        "chr": "Cherokee",
        "chu": "Church Slavic",
        "chv": "Chuvash",
        "chy": "Cheyenne",
        "cmc": "Chamic languages",
        "cnr": "Montenegrin",
        "cop": "Coptic",
        "cor": "Cornish",
        "cos": "Corsican",
        "cpe": "Creoles and Pidgins, English-based (Other)",
        "cpf": "Creoles and Pidgins, French-based (Other)",
        "cpp": "Creoles and Pidgins, Portuguese-based (Other)",
        "cre": "Cree",
        "crh": "Crimean Tatar",
        "crp": "Creoles and Pidgins (Other)",
        "csb": "Kashubian",
        "cus": "Cushitic (Other)",
        "cze": "Czech",
        "dak": "Dakota",
        "dan": "Danish",
        "dar": "Dargwa",
        "day": "Dayak",
        "del": "Delaware",
        "den": "Slavey",
        "dgr": "Tlicho",
        "din": "Dinka",
        "div": "Divehi",
        "doi": "Dogri",
        "dra": "Dravidian (Other)",
        "dsb": "Lower Sorbian",
        "dua": "Duala",
        "dum": "Dutch, Middle (ca. 1050-1350)",
        "dut": "Dutch",
        "dyu": "Dyula",
        "dzo": "Dzongkha",
        "efi": "Efik",
        "egy": "Egyptian",
        "eka": "Ekajuk",
        "elx": "Elamite",
        "eng": "English",
        "enm": "English, Middle (1100-1500)",
        "epo": "Esperanto",
        "esk": "Eskimo languages",
        "esp": "Esperanto",
        "est": "Estonian",
        "eth": "Ethiopic",
        "ewe": "Ewe",
        "ewo": "Ewondo",
        "fan": "Fang",
        "fao": "Faroese",
        "far": "Faroese",
        "fat": "Fanti",
        "fij": "Fijian",
        "fil": "Filipino",
        "fin": "Finnish",
        "fiu": "Finno-Ugrian (Other)",
        "fon": "Fon",
        "fre": "French",
        "fri": "Frisian",
        "frm": "French, Middle (ca. 1300-1600)",
        "fro": "French, Old (ca. 842-1300)",
        "frr": "North Frisian",
        "frs": "East Frisian",
        "fry": "Frisian",
        "ful": "Fula",
        "fur": "Friulian",
        "gaa": "Gã",
        "gae": "Scottish Gaelic",
        "gag": "Galician",
        "gal": "Oromo",
        "gay": "Gayo",
        "gba": "Gbaya",
        "gem": "Germanic (Other)",
        "geo": "Georgian",
        "ger": "German",
        "gez": "Ethiopic",
        "gil": "Gilbertese",
        "gla": "Scottish Gaelic",
        "gle": "Irish",
        "glg": "Galician",
        "glv": "Manx",
        "gmh": "German, Middle High (ca. 1050-1500)",
        "goh": "German, Old High (ca. 750-1050)",
        "gon": "Gondi",
        "gor": "Gorontalo",
        "got": "Gothic",
        "grb": "Grebo",
        "grc": "Greek, Ancient (to 1453)",
        "gre": "Greek, Modern (1453-)",
        "grn": "Guarani",
        "gsw": "Swiss German",
        "gua": "Guarani",
        "guj": "Gujarati",
        "gwi": "Gwich'in",
        "hai": "Haida",
        "hat": "Haitian French Creole",
        "hau": "Hausa",
        "haw": "Hawaiian",
        "heb": "Hebrew",
        "her": "Herero",
        "hil": "Hiligaynon",
        "him": "Western Pahari languages",
        "hin": "Hindi",
        "hit": "Hittite",
        "hmn": "Hmong",
        "hmo": "Hiri Motu",
        "hrv": "Croatian",
        "hsb": "Upper Sorbian",
        "hun": "Hungarian",
        "hup": "Hupa",
        "iba": "Iban",
        "ibo": "Igbo",
        "ice": "Icelandic",
        "ido": "Ido",
        "iii": "Sichuan Yi",
        "ijo": "Ijo",
        "iku": "Inuktitut",
        "ile": "Interlingue",
        "ilo": "Iloko",
        "ina": "Interlingua (International Auxiliary Language Association)",
        "inc": "Indic (Other)",
        "ind": "Indonesian",
        "ine": "Indo-European (Other)",
        "inh": "Ingush",
        "int": "Interlingua (International Auxiliary Language Association)",
        "ipk": "Inupiaq",
        "ira": "Iranian (Other)",
        "iri": "Irish",
        "iro": "Iroquoian (Other)",
        "ita": "Italian",
        "jav": "Javanese",
        "jbo": "Lojban (Artificial language)",
        "jpn": "Japanese",
        "jpr": "Judeo-Persian",
        "jrb": "Judeo-Arabic",
        "kaa": "Kara-Kalpak",
        "kab": "Kabyle",
        "kac": "Kachin",
        "kal": "Kalâtdlisut",
        "kam": "Kamba",
        "kan": "Kannada",
        "kar": "Karen languages",
        "kas": "Kashmiri",
        "kau": "Kanuri",
        "kaw": "Kawi",
        "kaz": "Kazakh",
        "kbd": "Kabardian",
        "kha": "Khasi",
        "khi": "Khoisan (Other)",
        "khm": "Khmer",
        "kho": "Khotanese",
        "kik": "Kikuyu",
        "kin": "Kinyarwanda",
        "kir": "Kyrgyz",
        "kmb": "Kimbundu",
        "kok": "Konkani",
        "kom": "Komi",
        "kon": "Kongo",
        "kor": "Korean",
        "kos": "Kosraean",
        "kpe": "Kpelle",
        "krc": "Karachay-Balkar",
        "krl": "Karelian",
        "kro": "Kru (Other)",
        "kru": "Kurukh",
        "kua": "Kuanyama",
        "kum": "Kumyk",
        "kur": "Kurdish",
        "kus": "Kusaie",
        "kut": "Kootenai",
        "lad": "Ladino",
        "lah": "Lahndā",
        "lam": "Lamba (Zambia and Congo)",
        "lan": "Occitan (post 1500)",
        "lao": "Lao",
        "lap": "Sami",
        "lat": "Latin",
        "lav": "Latvian",
        "lez": "Lezgian",
        "lim": "Limburgish",
        "lin": "Lingala",
        "lit": "Lithuanian",
        "lol": "Mongo-Nkundu",
        "loz": "Lozi",
        "ltz": "Luxembourgish",
        "lua": "Luba-Lulua",
        "lub": "Luba-Katanga",
        "lug": "Ganda",
        "lui": "Luiseño",
        "lun": "Lunda",
        "luo": "Luo (Kenya and Tanzania)",
        "lus": "Lushai",
        "mac": "Macedonian",
        "mad": "Madurese",
        "mag": "Magahi",
        "mah": "Marshallese",
        "mai": "Maithili",
        "mak": "Makasar",
        "mal": "Malayalam",
        "man": "Mandingo",
        "mao": "Maori",
        "map": "Austronesian (Other)",
        "mar": "Marathi",
        "mas": "Maasai",
        "max": "Manx",
        "may": "Malay",
        "mdf": "Moksha",
        "mdr": "Mandar",
        "men": "Mende",
        "mga": "Irish, Middle (ca. 1100-1550)",
        "mic": "Micmac",
        "min": "Minangkabau",
        "mis": "Miscellaneous languages",
        "mkh": "Mon-Khmer (Other)",
        "mla": "Malagasy",
        "mlg": "Malagasy",
        "mlt": "Maltese",
        "mnc": "Manchu",
        "mni": "Manipuri",
        "mno": "Manobo languages",
        "moh": "Mohawk",
        "mol": "Moldavian",
        "mon": "Mongolian",
        "mos": "Mooré",
        "mul": "Multiple languages",
        "mun": "Munda (Other)",
        "mus": "Creek",
        "mwl": "Mirandese",
        "mwr": "Marwari",
        "myn": "Mayan languages",
        "myv": "Erzya",
        "nah": "Nahuatl",
        "nai": "North American Indian (Other)",
        "nap": "Neapolitan Italian",
        "nau": "Nauru",
        "nav": "Navajo",
        "nbl": "Ndebele (South Africa)",
        "nde": "Ndebele (Zimbabwe)",
        "ndo": "Ndonga",
        "nds": "Low German",
        "nep": "Nepali",
        "new": "Newari",
        "nia": "Nias",
        "nic": "Niger-Kordofanian (Other)",
        "niu": "Niuean",
        "nno": "Norwegian (Nynorsk)",
        "nob": "Norwegian (Bokmål)",
        "nog": "Nogai",
        "non": "Old Norse",
        "nor": "Norwegian",
        "nqo": "N'Ko",
        "nso": "Northern Sotho",
        "nub": "Nubian languages",
        "nwc": "Newari, Old",
        "nya": "Nyanja",
        "nym": "Nyamwezi",
        "nyn": "Nyankole",
        "nyo": "Nyoro",
        "nzi": "Nzima",
        "oci": "Occitan (post-1500)",
        "oji": "Ojibwa",
        "ori": "Oriya",
        "orm": "Oromo",
        "osa": "Osage",
        "oss": "Ossetic",
        "ota": "Turkish, Ottoman",
        "oto": "Otomian languages",
        "paa": "Papuan (Other)",
        "pag": "Pangasinan",
        "pal": "Pahlavi",
        "pam": "Pampanga",
        "pan": "Panjabi",
        "pap": "Papiamento",
        "pau": "Palauan",
        "peo": "Old Persian (ca. 600-400 B.C.)",
        "per": "Persian",
        "phi": "Philippine (Other)",
        "phn": "Phoenician",
        "pli": "Pali",
        "pol": "Polish",
        "pon": "Pohnpeian",
        "por": "Portuguese",
        "pra": "Prakrit languages",
        "pro": "Provençal (to 1500)",
        "pus": "Pushto",
        "que": "Quechua",
        "raj": "Rajasthani",
        "rap": "Rapanui",
        "rar": "Rarotongan",
        "roa": "Romance (Other)",
        "roh": "Raeto-Romance",
        "rom": "Romani",
        "rum": "Romanian",
        "run": "Rundi",
        "rup": "Aromanian",
        "rus": "Russian",
        "sad": "Sandawe",
        "sag": "Sango (Ubangi Creole)",
        "sah": "Yakut",
        "sai": "South American Indian (Other)",
        "sal": "Salishan languages",
        "sam": "Samaritan Aramaic",
        "san": "Sanskrit",
        "sao": "Samoan",
        "sas": "Sasak",
        "sat": "Santali",
        "scc": "Serbian",
        "scn": "Sicilian Italian",
        "sco": "Scots",
        "scr": "Croatian",
        "sel": "Selkup",
        "sem": "Semitic (Other)",
        "sga": "Irish, Old (to 1100)",
        "sgn": "Sign languages",
        "shn": "Shan",
        "sho": "Shona",
        "sid": "Sidamo",
        "sin": "Sinhalese",
        "sio": "Siouan (Other)",
        "sit": "Sino-Tibetan (Other)",
        "sla": "Slavic (Other)",
        "slo": "Slovak",
        "slv": "Slovenian",
        "sma": "Southern Sami",
        "sme": "Northern Sami",
        "smi": "Sami",
        "smj": "Lule Sami",
        "smn": "Inari Sami",
        "smo": "Samoan",
        "sms": "Skolt Sami",
        "sna": "Shona",
        "snd": "Sindhi",
        "snh": "Sinhalese",
        "snk": "Soninke",
        "sog": "Sogdian",
        "som": "Somali",
        "son": "Songhai",
        "sot": "Sotho",
        "spa": "Spanish",
        "srd": "Sardinian",
        "srn": "Sranan",
        "srp": "Serbian",
        "srr": "Serer",
        "ssa": "Nilo-Saharan (Other)",
        "sso": "Sotho",
        "ssw": "Swazi",
        "suk": "Sukuma",
        "sun": "Sundanese",
        "sus": "Susu",
        "sux": "Sumerian",
        "swa": "Swahili",
        "swe": "Swedish",
        "swz": "Swazi",
        "syc": "Syriac",
        "syr": "Syriac, Modern",
        "tag": "Tagalog",
        "tah": "Tahitian",
        "tai": "Tai (Other)",
        "taj": "Tajik",
        "tam": "Tamil",
        "tar": "Tatar",
        "tat": "Tatar",
        "tel": "Telugu",
        "tem": "Temne",
        "ter": "Terena",
        "tet": "Tetum",
        "tgk": "Tajik",
        "tgl": "Tagalog",
        "tha": "Thai",
        "tib": "Tibetan",
        "tig": "Tigré",
        "tir": "Tigrinya",
        "tiv": "Tiv",
        "tkl": "Tokelauan",
        "tlh": "Klingon (Artificial language)",
        "tli": "Tlingit",
        "tmh": "Tamashek",
        "tog": "Tonga (Nyasa)",
        "ton": "Tongan",
        "tpi": "Tok Pisin",
        "tru": "Truk",
        "tsi": "Tsimshian",
        "tsn": "Tswana",
        "tso": "Tsonga",
        "tsw": "Tswana",
        "tuk": "Turkmen",
        "tum": "Tumbuka",
        "tup": "Tupi languages",
        "tur": "Turkish",
        "tut": "Altaic (Other)",
        "tvl": "Tuvaluan",
        "twi": "Twi",
        "tyv": "Tuvinian",
        "udm": "Udmurt",
        "uga": "Ugaritic",
        "uig": "Uighur",
        "ukr": "Ukrainian",
        "umb": "Umbundu",
        "und": "Undetermined",
        "urd": "Urdu",
        "uzb": "Uzbek",
        "vai": "Vai",
        "ven": "Venda",
        "vie": "Vietnamese",
        "vol": "Volapük",
        "vot": "Votic",
        "wak": "Wakashan languages",
        "wal": "Wolayta",
        "war": "Waray",
        "was": "Washoe",
        "wel": "Welsh",
        "wen": "Sorbian (Other)",
        "wln": "Walloon",
        "wol": "Wolof",
        "xal": "Oirat",
        "xho": "Xhosa",
        "yao": "Yao (Africa)",
        "yap": "Yapese",
        "yid": "Yiddish",
        "yor": "Yoruba",
        "ypk": "Yupik languages",
        "zap": "Zapotec",
        "zbl": "Blissymbolics",
        "zen": "Zenaga",
        "zha": "Zhuang",
        "znd": "Zande languages",
        "zul": "Zulu",
        "zun": "Zuni",
        "zxx": "No linguistic content",
        "zza": "Zaza",
    }
    iso639t_to_marc = {
        "sqi": "alb",  # Albanian
        "hye": "arm",  # Armenian
        "eus": "baq",  # Basque
        "mya": "bur",  # Burmese
        "zho": "chi",  # Chinese
        "ces": "cze",  # Czech
        "nld": "dut",  # Dutch
        "fra": "fre",  # French
        "kat": "geo",  # Georgian
        "deu": "ger",  # German
        "ell": "gre",  # Greek, Modern
        "isl": "ice",  # Icelandic
        "mkd": "mac",  # Macedonian
        "mri": "mao",  # Maori
        "msa": "may",  # Malay
        "fas": "per",  # Persian
        "ron": "rum",  # Romanian
        "slk": "slo",  # Slovak
        "bod": "tib",  # Tibetan
        "cym": "wel",  # Welsh
    }

    languageset_list = raw.xpath(".//*[local-name()='languageset']")
    a_041_lists = []
    a_041_marc_list = []
    a_041_iso_list = []
    field_041_xml_list = []
    all_langcodes = []

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (7)

    # SUBFIELDS
    # Subfield A
    if languageset_list:
        for languageset in languageset_list:
            language_list = languageset.xpath(".//*[local-name()='language']")
            language = language_list[0]
            langcode = language.attrib["langcode"].lower()
            if langcode in marc_language_codes.keys():
                langcode_marc = langcode
                all_langcodes.append(langcode_marc)
            elif langcode in iso639t_to_marc.keys():
                langcode_marc = iso639t_to_marc[langcode]
                all_langcodes.append(langcode_marc)
            else:
                langcode_marc = None
            if langcode_marc:
                a_041_marc = f"""<subfield code="a">{langcode_marc}</subfield>"""
                a_041_marc_list.append(a_041_marc)
            else:
                a_041_iso = f"""<subfield code="a">{langcode}</subfield>"""
                a_041_iso_list.append(a_041_iso)
        a_041_lists.append(a_041_marc_list)
        a_041_lists.append(a_041_iso_list)
            
        for a_041_list in a_041_lists:
            if not a_041_list:
                continue
            # PRINT 041 FIELD
            if a_041_list == a_041_marc_list:
                ind2_041 = " "
                sf_2_041 = ""
            elif a_041_list == a_041_iso_list:
                ind2_041 = "7"
                sf_2_041 = """<subfield code="2">iso639-2b</subfield>"""
            field_041_open = f"""<datafield tag="041" ind1=" " ind2="{ind2_041}">"""
            field_041_str_nb = field_041_open + "".join(a_041_list) + sf_2_041 + "</datafield>"
            field_041_xml = etree.fromstring(field_041_str_nb)
            field_041_xml_list.append(field_041_xml)
            # field_041_str = etree.tostring(field_041_xml, pretty_print=True, encoding="unicode")

            # print(field_041_str)

        return field_041_xml_list, all_langcodes
    return [], []

        # NOTE:
            # Subfields beyond $a and $2 are not currently supported.


def ead2marc_049():
    '''Creates 049 for IU Libraries holdings (constant)'''

    field_049_xml_list = []
    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (blank)
    # SUBFIELDS
    # PRINT 049 FIELD
    field_049_open = """<datafield tag="049" ind1=" " ind2=" ">"""

    # Subfield A
    a_049 = """<subfield code="a">IULA</subfield>"""
    field_049_close = """</datafield>"""

    field_049_str_nb = field_049_open + a_049 + field_049_close
    field_049_xml = etree.fromstring(field_049_str_nb)
    field_049_xml_list.append(field_049_xml)
    # field_049_str = etree.tostring(field_049_xml, pretty_print=True, encoding="unicode")

    # print(field_049_str)
    return field_049_xml_list

### TODO: chcek if ead2marc_035va is working correctly and ask L if 035 or 099 is better for VAE.
# def ead2marc_099(root, raw):
#     level = raw.attrib['level']
#     num_fetch = root.xpath(".//*[local-name()='num']")
#     recordid_fetch = root.xpath(".//*[local-name()='recordid']")
#     num_fetch.extend(recordid_fetch) # (Troubleshot with Claude Opus 4.6)
#     field_099_xml_list = []
#     if level == "collection" and num_fetch:
#         # INDICATORS
#         # Indicator 1 is constant (blank)
#         # Indiactor 2 is constant (9)

#         # SUBFIELDS
#         # Subfield A
#         for num_raw in num_fetch:
#             num_clean = num_raw.xpath("string()").strip()
#             num_clean = html.escape(num_clean)
#             a_099 = f"""<subfield code="a">{num_clean}</subfield>"""

#             # PRINT 099 FIELD
#             field_099_open = """<datafield tag="099" ind1=" " ind2="9">"""
#             field_099_str_nb = field_099_open + a_099 + "</datafield>"
#             field_099_xml = etree.fromstring(field_099_str_nb)
#             field_099_xml_list.append(field_099_xml)
#             # field_099_str = etree.tostring(field_099_xml, pretty_print=True, encoding="unicode")
#             # print(field_099_str)
        
#         return field_099_xml_list


def ead2marc_100(name):
    a_alpha = []
    d_num = []
    authority_100_str = None
    '''Creates 100 (main entry personal name) with authority validation'''

    # Check if main name is associated with an authority file
    # (This portion of code partially revised utilizing ChatGPT 5.2)
    # Pull identifier
    # (This portion of code was generated utilizing Claude Opus 4.6)
    timeout_error = False
    timeout_authfile_no = None
    if name.get("source") in {"lcnaf", "naf", "viaf"} and name.get("identifier") and not name.get("identifier", "").startswith("aspace_"):
        authfile_no = name.get("identifier")
    elif name.get("source") in {"lcnaf", "naf"}:
        name_str = name.xpath("string()").strip()
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={name_str}"""
        # (This portion of code was generated utilizing Claude Opus 4.5)
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        authfile_no = None
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == name_str:
                authfile_no = hit["token"]
                break
    elif name.get("source") == "viaf":
         # (This portion of code was generated utilizing Claude Opus 4.5)
        name_str = name.xpath("string()").strip()
        viaf_search_url = f"""https://viaf.org/viaf/search?query=local.personalNames+all+%22{name_str}%22&sortKeys=holdingscount&maximumRecords=5"""
        viaf_headers = {'Accept': 'application/xml'}
        viaf_search_response = requests.get(viaf_search_url, headers=viaf_headers)
        viaf_search_root = etree.fromstring(viaf_search_response.content)
        authfile_no = None
        records = viaf_search_root.xpath('//*[local-name()="record"]')
        for rec in records:
            headings = rec.xpath('.//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_id = rec.xpath('.//*[local-name()="viafID"]')
            if headings and viaf_id and headings[0].text == name_str:
                authfile_no = viaf_id[0].text
                break
    else:
        authfile_no = None

    # Pull authority file using identifier
    if name.get("source") in {"lcnaf", "naf"} and authfile_no:
        # Get Library of Congress Name Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority = "lcnaf"
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_100_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='100']")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            # Fallback to tag 110 if tag 100 not found (handles mismatched EAD name types)
            if not authority_100_list:
                authority_100_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
            authority_100_raw = authority_100_list[0]
            # Clean authority_100_raw
            authority_100_str = etree.tostring(authority_100_raw, pretty_print=True, encoding="unicode")
            authority_100_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_100_str)
            authority_100_str_list = authority_100_str.split("\n")
            authority_100_str_list_stripped = [str.strip() for str in authority_100_str_list]
            authority_100_str = "".join(authority_100_str_list_stripped)
            authority_100_str = re.sub(r'</datafield>', '', authority_100_str).strip()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authority = None
            timeout_error = True
            timeout_authfile_no = authfile_no
    elif name.get("source") == "viaf" and authfile_no:
        # Get VIAF cluster XML and extract 100 field data
        # (This portion of code was generated utilizing Claude Opus 4.5)
        authority = "viaf"
        viaf_headers = {'Accept': 'application/xml'}
        viaf_url = f"https://viaf.org/viaf/{authfile_no}"
        viaf_response = requests.get(viaf_url, headers=viaf_headers)
        viaf_root = etree.fromstring(viaf_response.content)
        # Check if VIAF cluster has linked LCNAF -- if so, use LCNAF
        # (This portion of code was generated utilizing Claude Opus 4.5)
        lc_sources = viaf_root.xpath('//*[local-name()="source" and starts-with(text(), "LC|")]')
        if lc_sources:
            # VIAF has LC link -- fetch from LCNAF
            # (This portion of code was generated utilizing Claude Opus 4.6)
            try:
                lc_id = lc_sources[0].text.split('|')[1]
                authority_url = f"https://lccn.loc.gov/{lc_id}/marcxml"
                authority_xml = loc_get(authority_url, timeout=10).content
                authority_root = etree.fromstring(authority_xml)
                authority_100_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='100']")
                # (This portion of code was generated utilizing Claude Opus 4.6)
                # Fallback to tag 110 if tag 100 not found (handles mismatched EAD name types)
                if not authority_100_list:
                    authority_100_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
                authority_100_raw = authority_100_list[0]
                authority_100_str = etree.tostring(authority_100_raw, pretty_print=True, encoding="unicode")
                authority_100_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_100_str)
                authority_100_str_list = authority_100_str.split("\n")
                authority_100_str_list_stripped = [str.strip() for str in authority_100_str_list]
                authority_100_str = "".join(authority_100_str_list_stripped)
                authority_100_str = re.sub(r'</datafield>', '', authority_100_str).strip()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
                print(f"WARNING: Connection to lccn.loc.gov timed out for {lc_id}. Constructing field manually.")
                authority = None
                timeout_error = True
                timeout_authfile_no = lc_id
        else:
            # No LC source -- parse VIAF cluster directly
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_headings = viaf_root.xpath('//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_main_heading = viaf_headings[0].text if viaf_headings else None
            # Get normalized dates from VIAF
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_birth = viaf_root.xpath('//*[local-name()="birthDate"]')
            viaf_death = viaf_root.xpath('//*[local-name()="deathDate"]')
            viaf_birth_year = viaf_birth[0].text[:4] if viaf_birth and viaf_birth[0].text and not viaf_birth[0].text.startswith('0') else None
            viaf_death_year = viaf_death[0].text[:4] if viaf_death and viaf_death[0].text and not viaf_death[0].text.startswith('0') else None
            # Parse heading to separate name from dates
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_parts = viaf_main_heading.split(', ') if viaf_main_heading else []
            viaf_name_parts = []
            for part in viaf_parts:
                if not (any(c.isdigit() for c in part) and ('-' in part or part.endswith('-'))):
                    viaf_name_parts.append(part)
            viaf_ind1 = '1' if len(viaf_name_parts) > 1 else '0'
            viaf_a_content = ', '.join(viaf_name_parts)
            # Determine date subfield
            # (This portion of code was generated utilizing Claude Opus 4.5)
            if viaf_birth_year and viaf_death_year:
                viaf_d_content = f'{viaf_birth_year}-{viaf_death_year}'
            elif viaf_birth_year:
                viaf_d_content = f'{viaf_birth_year}-'
            else:
                viaf_d_content = None
            # Build authority_100_str for VIAF-direct
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_subfields = f'<subfield code="a">{viaf_a_content}</subfield>'
            if viaf_d_content:
                viaf_subfields += f'<subfield code="d">{viaf_d_content}</subfield>'
            authority_100_str = f'<datafield tag="100" ind1="{viaf_ind1}" ind2=" ">{viaf_subfields}'
    else:
        authority = None

    # If authority fetch failed, reset authority so manual construction runs
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_100_str is None:
        authority = None

    # INDICATORS
    # Indicator 1
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority not in ["lcnaf", "viaf"]:
        a_content = name.xpath("string()").strip()
        a_split = a_content.split(", ")
        # (This portion of code was troubleshot utilizing Claude Opus 4.6)
        if name.tag.endswith('famname') or name in creator_famnames_list:

            ind1_100 = "3"
        else:
            for item in a_split:
                if re.search(r'\b\d{4}\b', item):
                    d_num.append(item)
                else:
                    a_alpha.append(item)
            if len(a_alpha) > 1:
                ind1_100 = "1"
            else:
                ind1_100 = "0"
    else:
        ind1_100 = ""

    # Indicator 2 is constant (blank)

    # Subfield E
    if 'relator' in name.attrib:
        aspace_relator = name.attrib["relator"].lower()
        if aspace_relator in marc_rda_relators.keys():
            e_content = marc_rda_relators[aspace_relator]
            e_100 = f"""<subfield code="e">{e_content}</subfield>"""
        else:
            e_100 = ""
    else:
        e_100 = ""

    # Subfield D
    if d_num:
        if authority not in ["lcnaf", "viaf"] and not (name.tag.endswith('famname') or name in creator_famnames_list):
            d_content = d_num[0]
            d_content = d_content.rstrip(".")
            if e_100:
                d_content += ","
            d_100 = f"""<subfield code="d">{d_content}</subfield>"""
    else:
        d_100 = ""

    # Subfield A
    if authority not in ["lcnaf", "viaf"]:
        if name.tag.endswith('famname') or name in creator_famnames_list:
            a_content = a_content
        else:
            a_content = ", ".join(a_alpha)
        if d_100:
            a_content += ","
        a_100 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 100 FIELD
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_100_str is not None:
        field_100_str_nb = authority_100_str + e_100 + "</datafield>"
        field_100_xml = etree.fromstring(field_100_str_nb)
        field_100_str = etree.tostring(field_100_xml, pretty_print=True, encoding="unicode")
    else:
        field_100_open = f"""<datafield tag="100" ind1="{ind1_100}" ind2=" ">"""
        field_100_str_nb = field_100_open + a_100 + d_100 + e_100 + "</datafield>"
        field_100_xml = etree.fromstring(field_100_str_nb)
        field_100_str = etree.tostring(field_100_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.5)
    field_100_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_100_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_100 = []
    if timeout_error:
        result_100.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_100.append(field_100_xml)

    # print(field_100_str)
    if field_100_xml is not None:
        return result_100

    # NOTE:
        # Subfield C is not currently supported for non-lcaf/viaf name authorities.
        # Manually constructed amily names are not currently parsed and separated into subfields. All information placed in subfield A.


def ead2marc_110(name):
    authority_110_str = None
    '''Creates 110 (main entry corporate name) with authority validation'''

    # Check if main name is associated with an authority file
    # (This portion of code partially revised utilizing ChatGPT 5.2)
    # Pull identifier
    # (This portion of code was generated utilizing Claude Opus 4.6)
    timeout_error = False
    timeout_authfile_no = None
    if name.get("source") in {"lcnaf", "naf", "viaf"} and name.get("identifier") and not name.get("identifier", "").startswith("aspace_"):
        authfile_no = name.get("identifier")
    elif name.get("source") in {"lcnaf", "naf"}:
        name_str = name.xpath("string()").strip()
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={name_str}"""
        # (This portion of code was generated utilizing Claude Opus 4.5)
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        authfile_no = None
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == name_str:
                authfile_no = hit["token"]
                break
    elif name.get("source") == "viaf":
        # (This portion of code was generated utilizing Claude Opus 4.5)
        name_str = name.xpath("string()").strip()
        viaf_search_url = f"""https://viaf.org/viaf/search?query=local.corporateNames+all+%22{name_str}%22&sortKeys=holdingscount&maximumRecords=5"""
        viaf_headers = {'Accept': 'application/xml'}
        viaf_search_response = requests.get(viaf_search_url, headers=viaf_headers)
        viaf_search_root = etree.fromstring(viaf_search_response.content)
        authfile_no = None
        records = viaf_search_root.xpath('//*[local-name()="record"]')
        for rec in records:
            headings = rec.xpath('.//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_id = rec.xpath('.//*[local-name()="viafID"]')
            if headings and viaf_id and headings[0].text == name_str:
                authfile_no = viaf_id[0].text
                break
    else:
        authfile_no = None

    # Pull authority file using identifier
    if name.get("source") in {"lcnaf", "naf"} and authfile_no:
        # Get Library of Congress Name Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority = "lcnaf"
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_110_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
            authority_110_raw = authority_110_list[0]
            # Clean authority_110_raw
            authority_110_str = etree.tostring(authority_110_raw, pretty_print=True, encoding="unicode")
            authority_110_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_110_str)
            authority_110_str_list = authority_110_str.split("\n")
            authority_110_str_list_stripped = [str.strip() for str in authority_110_str_list]
            authority_110_str = "".join(authority_110_str_list_stripped)
            authority_110_str = re.sub(r'</datafield>', '', authority_110_str).strip()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authority = None
            timeout_error = True
            timeout_authfile_no = authfile_no
    elif name.get("source") == "viaf" and authfile_no:
        # Get VIAF cluster XML and extract 110 field data
        # (This portion of code was generated utilizing Claude Opus 4.5)
        authority = "viaf"
        viaf_headers = {'Accept': 'application/xml'}
        viaf_url = f"https://viaf.org/viaf/{authfile_no}"
        viaf_response = requests.get(viaf_url, headers=viaf_headers)
        viaf_root = etree.fromstring(viaf_response.content)
        # Check if VIAF cluster has linked LCNAF -- if so, use LCNAF
        # (This portion of code was generated utilizing Claude Opus 4.5)
        lc_sources = viaf_root.xpath('//*[local-name()="source" and starts-with(text(), "LC|")]')
        if lc_sources:
            # VIAF has LC link -- fetch from LCNAF
            # (This portion of code was generated utilizing Claude Opus 4.6)
            try:
                lc_id = lc_sources[0].text.split('|')[1]
                authority_url = f"https://lccn.loc.gov/{lc_id}/marcxml"
                authority_xml = loc_get(authority_url, timeout=10).content
                authority_root = etree.fromstring(authority_xml)
                authority_110_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
                authority_110_raw = authority_110_list[0]
                authority_110_str = etree.tostring(authority_110_raw, pretty_print=True, encoding="unicode")
                authority_110_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_110_str)
                authority_110_str_list = authority_110_str.split("\n")
                authority_110_str_list_stripped = [str.strip() for str in authority_110_str_list]
                authority_110_str = "".join(authority_110_str_list_stripped)
                authority_110_str = re.sub(r'</datafield>', '', authority_110_str).strip()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
                print(f"WARNING: Connection to lccn.loc.gov timed out for {lc_id}. Constructing field manually.")
                authority = None
                timeout_error = True
                timeout_authfile_no = lc_id
        else:
            # No LC source -- parse VIAF cluster directly
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_headings = viaf_root.xpath('//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_main_heading = viaf_headings[0].text if viaf_headings else None
            # Build authority_110_str for VIAF-direct
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_subfields = f'<subfield code="a">{viaf_main_heading}</subfield>'
            authority_110_str = f'<datafield tag="110" ind1="2" ind2=" ">{viaf_subfields}'
    else:
        authority = None

    # If authority fetch failed, reset authority so manual construction runs
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_110_str is None:
        authority = None

    # INDICATORS
    # Indicator 1
    if authority not in ["lcnaf", "viaf"]:
        ind1_110 = "2"

    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield E
    if 'relator' in name.attrib:
        aspace_relator = name.attrib["relator"].lower()
        if aspace_relator in marc_rda_relators.keys():
            e_content = marc_rda_relators[aspace_relator]
            e_110 = f"""<subfield code="e">{e_content}</subfield>"""
        else:
            e_110 = ""
    else:
        e_110 = ""

    # Subfield A
    # (This portion of code was generated utilizing Claude Opus 4.5)
    if authority not in ["lcnaf", "viaf"]:
        a_content = name.xpath("string()").strip()
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if e_110:
            a_content += ","
        a_110 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 110 FIELD
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_110_str is not None:
        field_110_str_nb = authority_110_str + e_110 + "</datafield>"
        field_110_xml = etree.fromstring(field_110_str_nb)
        field_110_str = etree.tostring(field_110_xml, pretty_print=True, encoding="unicode")
    else:
        field_110_open = f"""<datafield tag="110" ind1="{ind1_110}" ind2=" ">"""
        field_110_str_nb = field_110_open + a_110 + e_110 + "</datafield>"
        field_110_xml = etree.fromstring(field_110_str_nb)
        field_110_str = etree.tostring(field_110_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.5)
    field_110_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_110_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_110 = []
    if timeout_error:
        result_110.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_110.append(field_110_xml)

    # print(field_110_str)
    if field_110_xml is not None:
        return result_110

    # NOTE:
        # Currently no subfields beyond subfields A and E are supported for non-authority 110s. All content except relators will be placed in subfield A.
        # ind1 0 (inverted name) and 1 (jurisdiction name) are not supported for non-authority 110s


def ead2marc_100_110(names_list):
    '''Routes main entry name to ead2marc_100 or ead2marc_110 based on name type'''

    # Set function-wide variables
    if names_list:
        main_name_ead = names_list[0]
        field_100_110_xml_list = []

        # Determine whether first name is persname or corpname to determine if field is 100 or 110
        # Extract the actual name element (persname/famname/corpname) from the origination
        # (This portion of code was generated utilizing Claude Opus 4.5)
        if main_name_ead in creator_persnames_list:
            name_element = main_name_ead.xpath(".//*[local-name()='persname']")[0]
            field_100_xml = ead2marc_100(name_element)
            field_100_110_xml_list.extend(field_100_xml)
        elif main_name_ead in creator_famnames_list:
            name_element = main_name_ead.xpath(".//*[local-name()='famname']")[0]
            field_100_xml = ead2marc_100(name_element)
            field_100_110_xml_list.extend(field_100_xml)
        elif main_name_ead in creator_corpnames_list:
            name_element = main_name_ead.xpath(".//*[local-name()='corpname']")[0]
            field_110_xml = ead2marc_110(name_element)
            field_100_110_xml_list.extend(field_110_xml)
        else:
            name_element = main_name_ead
            field_100_xml = ead2marc_100(name_element)
            field_100_110_xml_list.extend(field_100_xml)
        return field_100_110_xml_list


def ead2marc_245(raw):
    '''Creates 245 (title statement) from unittitle element'''

    level = raw.attrib['level']
    field_245_xml_list = []
    # INDICATORS
    # Indicator 1 is constant (1)
    # Indicator 2 is constant (0)

    # Subfield A
    # (This portion of code was partially revised utilizing ChatGPT 5.2)
    title_fetch = raw.xpath(".//*[local-name()='unittitle']")
    title_raw = title_fetch[0]
    title_clean = title_raw.xpath("string()").strip()
    title_clean = html.escape(title_clean)
    title_clean = " ".join(title_clean.split())
    # Adds [brackets] around title if collection level
    if level == "collection":
        title_clean = "[" + title_clean + "]"
    a_245 = f"""<subfield code="a">{title_clean}</subfield>"""

    # PRINT 245 FIELD
    field_245_str_nb = """<datafield tag="245" ind1="1" ind2="0">""" + a_245 + "</datafield>"
    field_245_xml = etree.fromstring(field_245_str_nb)
    field_245_xml_list.append(field_245_xml)
    # field_245_str = etree.tostring(field_245_xml, pretty_print=True, encoding="unicode")

    # print(field_245_str)
    return field_245_xml_list, title_clean


def ead2marc_246(raw):
    '''Creates 246 fields following Lilly Library and IU Archives conventions (collection-level only)'''
    
    field_245_xml_list, title_clean = ead2marc_245(raw)
    iuarch_title_clean = ""
    lilly_title_clean = ""
    title_lower = title_clean.lower()
    level = raw.attrib['level']
    field_246_xml_list = []
    if level == "collection" and title_lower.endswith("collection]"):
        iuarch_title_clean = re.sub(r"collection]", "papers]", title_clean, flags=re.I)
        lilly_title_clean = re.sub(r"collection]", "mss.]", title_clean, flags=re.I)

        # 246 Field #1 (IU Archives Convention)
        if iuarch_title_clean:
            # INDICATORS
            # Indicator 1 is constant (3)
            # Indicator 2 is constant (3)

            # Subfield A
            a_246_iuarch = f"""<subfield code="a">{iuarch_title_clean}</subfield>"""

            # Compile field
            field_246_str_nb_iuarch = """<datafield tag="246" ind1="3" ind2="3">""" + a_246_iuarch + "</datafield>"
            field_246_xml_iuarch = etree.fromstring(field_246_str_nb_iuarch)
            field_246_xml_list.append(field_246_xml_iuarch)

        # 246 Field #2 (Lilly Library Convention)
        if lilly_title_clean:
            # INDICATORS
            # Indicator 1 is constant (3)
            # Indicator 2 is constant (3)

            # Subfield A
            a_246_lilly = f"""<subfield code="a">{lilly_title_clean}</subfield>"""

            # Compile field
            field_246_str_nb_lilly = """<datafield tag="246" ind1="3" ind2="3">""" + a_246_lilly + "</datafield>"
            field_246_xml_lilly = etree.fromstring(field_246_str_nb_lilly)
            field_246_xml_list.append(field_246_xml_lilly)

        return field_246_xml_list


def ead2marc_264(raw):
    '''Creates 264 (production/publication/distribution date) from unitdate elements'''

    # Create a list of all unitdates
    unitdates_list = raw.xpath(".//*[starts-with(local-name(), 'unitdate')]")
    field_264_xml_list = []

    if len(unitdates_list) > 0:
        # Complete INDICATORS through PRINT 264 Field for each unitdate
        for unitdate in unitdates_list:

            # INDICATORS
            # Indicator 1 is constant (blank)

            # Indicator 2
            # (This portion of code was partially revised utilizing ChatGPT 5.2)
            # Get date label (datechar)
            datechar_clean = (unitdate.get("datechar")).strip()
            if unitdate.get("certainty"):
                certainty_clean = (unitdate.get("certainty")).strip()

            # Set indicator 2 based on datechar
            if datechar_clean in ['broadcast', 'publication']:
                ind2_264 = 1 # Publication
            elif datechar_clean in ['issued']:
                ind2_264 = 3 # Manufacture
            elif datechar_clean in ['copyright']:
                ind2_264 = 4 # Copyright notice date
            else:
                # AKA elif datechar_clean in ['creation', 'deaccession', 'digitized', 'event', 'existence', 'modified', 'other', 'record keeping', 'usage']
                ind2_264 = 0 # Production

            # Subfield C
            # Set date to read [not after dddd] if datechar is "deaccession"
            # (Laikin's idea)
            if datechar_clean in ['deaccession']:
                qualifier_open = "[not after "
                qualifier_close = "]"
            else:
                # If unitdate has certainty specified, add qualifiers
                if unitdate.get("certainty"):
                    if certainty_clean == "approximate":
                        qualifier_close = "approximately"
                        qualifier_open = ""
                    elif certainty_clean == "inferred":
                        qualifier_close = "["
                        qualifier_open = "]"
                    elif certainty_clean == "questionable":
                        qualifier_close = "["
                        qualifier_open = "?]"
                else:
                    qualifier_close = ""
                    qualifier_open = ""

            # Get date or daterange
            is_daterange = unitdate.xpath(".//*[local-name()='daterange']")
            if is_daterange:
                fromdate_raw = unitdate.xpath(".//*[local-name()='fromdate']")[0]
                todate_raw = unitdate.xpath(".//*[local-name()='todate']")[0]
                fromdate_clean = fromdate_raw.xpath("string()").strip()
                todate_clean = todate_raw.xpath("string()").strip()
                date_clean = f"{fromdate_clean}-{todate_clean}"
            else:
                date_clean = unitdate.xpath("string()").strip()
                date_clean = html.escape(date_clean)

            c_264 = f"""<subfield code="c">{qualifier_open}{date_clean}{qualifier_close}</subfield>"""

            # PRINT 264 FIELD
            field_264_open = f"""<datafield tag="264" ind1=" " ind2="{ind2_264}">"""
            field_264_str_nb = field_264_open + c_264 + "</datafield>"
            field_264_xml = etree.fromstring(field_264_str_nb)
            field_264_xml_list.append(field_264_xml)
            # field_264_str = etree.tostring(field_264_xml, pretty_print=True, encoding="unicode")
            # print(field_264_str)

    return field_264_xml_list


def ead2marc_300(raw):
    '''Creates 300 (physical description) from physdescstructured and physdesc elements'''

    # (This portion of code was generated utilizing Claude Opus 4.6)
    # Get physdescstructured and physdesc elements separately
    physdesc_structured_list = raw.xpath(".//*[local-name()='physdescstructured']")
    physdesc_list = raw.xpath(".//*[local-name()='physdesc']")
    field_300_xml_list = []
    consumed_physdescs = []
    unittypes_f_list = ["box", "feet", "file", "folder", "foot", "page", "volume"]

    if physdesc_list or physdesc_structured_list:
        # If physdesc or phydescstructured elements exist, proceeds with processing
        # Process each physdescstructured paired with its following physdesc sibling
        for pds in physdesc_structured_list:
            a_300_cs = ""
            a_300_qu = ""
            f_300 = ""
            c_300 = ""

            # INDICATORS

            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS

            # Process structured fields
            if pds.get("physdescstructuredtype") == "spaceoccupied":
                if pds.xpath(".//*[local-name()='quantity']"):
                    quantity_raw = pds.xpath(".//*[local-name()='quantity']")[0]
                    quantity_clean = html.escape(quantity_raw.xpath("string()").strip())
                else:
                    quantity_clean = ""
                if pds.xpath(".//*[local-name()='unittype']"):
                    unittype_raw = pds.xpath(".//*[local-name()='unittype']")[0]
                    unittype_clean = html.escape(unittype_raw.xpath("string()").strip())
                else:
                    unittype_clean = ""
                if quantity_clean and unittype_clean:
                    # Subfield A (1/2)
                    a_300_qu = f"""<subfield code="a">{quantity_clean}</subfield>"""

                    # Subfield F
                    f_field = False
                    for utype in unittypes_f_list:
                        if utype in unittype_clean:
                            f_field = True
                    if f_field:
                        a_300_qu = f"""<subfield code="a">{quantity_clean}</subfield>"""
                        f_300 = f"""<subfield code="f">{unittype_clean}</subfield>"""
                    else:
                        a_300_qu = f"""<subfield code="a">{quantity_clean} {unittype_clean}</subfield>"""
                        f_300 = ""
                if pds.xpath(".//*[local-name()='dimensions']"):
                    dimensions_raw = pds.xpath(".//*[local-name()='dimensions']")[0]
                    dimensions_clean = html.escape(dimensions_raw.xpath("string()").strip())

                    # Subfield C
                    # TODO: Check if ending in "ft" or "in" and add period if so (no period after cm)
                    c_300 = f"""<subfield code="c">{dimensions_clean}</subfield>"""

            # Get paired following physdesc sibling (e.g. container_summary)
            following_physdesc = pds.xpath("following-sibling::*[local-name()='physdesc'][1]")
            if following_physdesc and following_physdesc[0].get("localtype") == "container_summary":
                fp = following_physdesc[0]
                fp_clean = html.escape(fp.xpath("string()").strip())

                # Subfield A (2/2)
                a_300_cs = f"""<subfield code="a">{fp_clean}</subfield>"""
                consumed_physdescs.append(fp)

            # Build 300 field
            # PRINT 300 FIELD
            field_300_open = """<datafield tag="300" ind1=" " ind2=" ">"""
            field_300_str_nb = field_300_open + a_300_cs + c_300 + a_300_qu + f_300 + "</datafield>"
            field_300_xml = etree.fromstring(field_300_str_nb)
            field_300_xml_list.append(field_300_xml)
            # field_300_str = etree.tostring(field_300_xml, pretty_print=True, encoding="unicode")
            # print(field_300_str)
    else:
        # If no physdesc or phydescstructured elements exist, fallback is $a 1 [hierarchy level]
        # PRINT 300 FIELD
        field_300_open = """<datafield tag="300" ind1=" " ind2=" ">"""
        a_300 = c0_raw.attrib['level']
        field_300_str_nb = field_300_open + "1 " + a_300 + "</datafield>"
        field_300_xml = etree.fromstring(field_300_str_nb)
        field_300_xml_list.append(field_300_xml)
        # field_300_str = etree.tostring(field_300_xml, pretty_print=True, encoding="unicode")
        # print(field_300_str)

    return field_300_xml_list, consumed_physdescs
        # Consumed_physdescs included in return for use in ead2marc_500


def ead2marc_336(raw):
    '''Maps unit types and physdesc keywords to RDA content types and creates 336 fields'''

    unittype_336_map = {
        "cassette": "performed music",
        "cubic foot": "text",
        "cubic feet": "text",
        "gigabytes": "computer program",
        "bytes": "computer program",
        "leaves": "text",
        "linear feet": "text",
        "linear foot": "text",
        "megabytes": "computer program",
        "photographic print": "still image",
        "photographic slide": "still image",
        "slide": "still image",
        "reel": "performed music",
        "sheet": "text",
        "terabyte": "computer program",
        "volume": "text",
        "folder": "text",
        "cd": "performed music",
        "dvd": "performed music",
        "box": "text",
        "score": "notated music",
        "sheet music": "notated music",
    }
    ctype_code_dict = {
        "cartographic dataset": "crd",
        "cartographic image": "cri",
        "cartographic moving image": "crm",
        "cartographic tactile image": "crt",
        "cartographic tactile three-dimensional form": "crn",
        "cartographic three-dimensional form": "crf",
        "computer dataset": "cod",
        "computer program": "cop",
        "notated movement": "ntv",
        "notated music": "ntm",
        "performed music": "prm",
        "sounds": "snd",
        "spoken word": "spw",
        "still image": "sti",
        "tactile image": "tci",
        "tactile notated music": "tcm",
        "tactile notated movement": "tcn",
        "tactile text": "tct",
        "tactile three-dimensional form": "tcf",
        "text": "txt",
        "three-dimensional form": "tdf",
        "three-dimensional moving image": "tdm",
        "two-dimensional moving image": "tdi",
        "other": "xxx",
        "unspecified": "zzz",
    }

    crtype_keycheck_list = []
    ctype_list = []
    ctype_code_list = []
    field_336_xml_list = []
    all_physdesc_list = raw.xpath(".//*[starts-with(local-name(), 'physdesc')]")

    for physdesc in all_physdesc_list:
        # Extract unittype text from physdescstructured elements
        # (This portion of code was troubleshot utilizing Claude Opus 4.6)
        unittype_children = physdesc.xpath(".//*[local-name()='unittype']")
        if unittype_children:
            unittype_clean = html.escape(unittype_children[0].xpath("string()").strip())
            crtype_keycheck_list.append(unittype_clean)
        # Extract text from plain physdesc elements (not physdescstructured)
        # (This portion of code was troubleshot utilizing Claude Opus 4.6)
        if physdesc.tag.endswith('physdesc') and not physdesc.tag.endswith('physdescstructured'):
            physdesc_clean = html.escape(physdesc.xpath("string()").strip())
            crtype_keycheck_list.append(physdesc_clean)
        crtype_keycheck_list.append(subj_gft_list)
    for search_target in crtype_keycheck_list:
        for key in unittype_336_map:
            if key.casefold() in search_target:
                if key not in ctype_list:
                    ctype_list.append(unittype_336_map[key])
    for ctype in ctype_list:
        ctype_code = ctype_code_dict[ctype]
        ctype_code_list.append(ctype_code)

        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2 is constant (blank)

        # SUBFIELDS
        # Subfield A
        a_336 = f"""<subfield code="a">{ctype}</subfield>"""

        # Subfield B
        b_336 = f"""<subfield code="b">{ctype_code}</subfield>"""

        # Subfield 2
        sf2_336 = """<subfield code="2">rdacontent</subfield>"""

        # PRINT 336 FIELD
        field_336_op = """<datafield tag="336" ind1=" " ind2=" ">"""
        field_336_str_nb = field_336_op + a_336 + b_336 + sf2_336 + "</datafield>"
        field_336_xml = etree.fromstring(field_336_str_nb)
        field_336_xml_list.append(field_336_xml)
        # field_336_str = etree.tostring(field_336_xml, pretty_print=True, encoding="unicode")

        # print(field_336_str)

    if field_336_xml_list:
        return field_336_xml_list, ctype_code_list
    return [], []


def ead2marc_337(raw):
    '''Maps unit types to RDA media types and creates 337 fields'''

    unittype_337_map = {
        "cassette": "audio",
        "cubic foot": "unmediated",
        "cubic feet": "unmediated",
        "gigabytes": "computer",
        "bytes": "computer",
        "leaves": "unmediated",
        "linear feet": "unmediated",
        "linear foot": "unmediated",
        "megabytes": "computer",
        "photographic print": "unmediated",
        "photographic slide": "projected",
        "slide": "projected",
        "reel": "audio",
        "sheet": "unmediated",
        "terabyte": "computer",
        "volume": "unmediated",
        "folder": "unmediated",
        "cd": "audio",
        "dvd": "video",
        "box": "unmediated",
        "score": "unmediated",
        "sheet music": "unmediated",
    }
    mtype_code_list = {
        "audio": "s",
        "computer": "c",
        "microform": "h",
        "microscopic": "p",
        "projected": "g",
        "stereographic": "e",
        "unmediated": "n",
        "video": "v",
        "other": "x",
        "unspecified": "z",
    }

    unittype_list = []
    mtype_list = []
    field_337_xml_list = []
    all_physdesc_list = raw.xpath(".//*[starts-with(local-name(), 'physdesc')]")

    for physdesc in all_physdesc_list:
        if physdesc.xpath(".//*[local-name()='unittype']"):
            unittype_raw = raw.xpath(".//*[local-name()='unittype']")[0]
            unittype_clean = html.escape(unittype_raw.xpath("string()").strip())
            unittype_list.append(unittype_clean)
    for unittype in unittype_list:
        for key in unittype_337_map:
            if key in unittype:
                mtype_list.append(unittype_337_map[key])
    for mtype in mtype_list:
        mtype_code = mtype_code_list[mtype]

        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2 is constant (blank)

        # SUBFIELDS
        # Subfield A
        a_337 = f"""<subfield code="a">{mtype}</subfield>"""

        # Subfield B
        b_337 = f"""<subfield code="b">{mtype_code}</subfield>"""

        # Subfield 2
        sf2_337 = """<subfield code="2">rdacontent</subfield>"""

        # PRINT 337 FIELD
        field_337_op = """<datafield tag="337" ind1=" " ind2=" ">"""
        field_337_str_nb = field_337_op + a_337 + b_337 + sf2_337 + "</datafield>"
        field_337_xml = etree.fromstring(field_337_str_nb)
        field_337_xml_list.append(field_337_xml)
        # field_337_str = etree.tostring(field_337_xml, pretty_print=True, encoding="unicode")

        # print(field_337_str)

    if field_337_xml_list:
        return field_337_xml_list


def ead2marc_338(raw):
    '''Maps unit types to RDA carrier types and creates 338 fields'''

    unittype_338_map = {
        "cassette": "audiocassette",
        "cubic foot": "object",
        "cubic feet": "object",
        "gigabytes": "computer disc",
        "bytes": "computer disc",
        "leaves": "sheet",
        "linear feet": "object",
        "linear foot": "object",
        "megabytes": "computer disc",
        "photographic print": "sheet",
        "photographic slide": "slide",
        "slide": "slide",
        "reel": "audiotape reel",
        "sheet": "sheet",
        "terabyte": "computer disc",
        "volume": "volume",
        "folder": "sheet",
        "cd": "audio disc",
        "dvd": "videodisc",
        "box": "object",
        "score": "sheet",
        "sheet music": "sheet",
    }
    crtype_code_list = {
        "audio cartridge": "sg",
        "audio belt": "sb",
        "audio cylinder": "se",
        "audio disc": "sd",
        "sound track reel": "si",
        "audio roll": "sq",
        "audio wire reel": "sw",
        "audiocassette": "ss",
        "audiotape reel": "st",
        "computer card": "ck",
        "computer chip cartridge": "cb",
        "computer disc": "cd",
        "computer disc cartridge": "ce",
        "computer tape cartridge": "ca",
        "computer tape cassette": "cf",
        "computer tape reel": "ch",
        "online resource": "cr",
        "aperture card": "ha",
        "microfiche": "he",
        "microfiche cassette": "hf",
        "microfilm cartridge": "hb",
        "microfilm cassette": "hc",
        "microfilm reel": "hd",
        "microfilm roll": "hj",
        "microfilm slip": "hh",
        "microopaque": "hg",
        "microscope slide": "pp",
        "film cartridge": "mc",
        "film cassette": "mf",
        "film reel": "mr",
        "film roll": "mo",
        "filmslip": "gd",
        "filmstrip": "gf",
        "filmstrip cartridge": "gc",
        "overhead transparency": "gt",
        "slide": "gs",
        "stereograph card": "eh",
        "stereograph disc": "es",
        "card": "no",
        "flipchart": "nn",
        "roll": "na",
        "sheet": "nb",
        "volume": "nc",
        "object": "nr",
        "video cartridge": "vc",
        "videocassette": "vf",
        "videodisc": "vd",
        "videotape reel": "vr",
        "unspecified": "zu",
    }

    unittype_list = []
    crtype_list = []
    field_338_xml_list = []
    all_physdesc_list = raw.xpath(".//*[starts-with(local-name(), 'physdesc')]")

    for physdesc in all_physdesc_list:
        if physdesc.xpath(".//*[local-name()='unittype']"):
            unittype_raw = raw.xpath(".//*[local-name()='unittype']")[0]
            unittype_clean = html.escape(unittype_raw.xpath("string()").strip())
            unittype_list.append(unittype_clean)
    for unittype in unittype_list:
        for key in unittype_338_map:
            if key in unittype:
                crtype_list.append(unittype_338_map[key])
    for crtype in crtype_list:
        crtype_code = crtype_code_list[crtype]

        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2 is constant (blank)

        # SUBFIELDS
        # Subfield A
        a_338 = f"""<subfield code="a">{crtype}</subfield>"""

        # Subfield B
        b_338 = f"""<subfield code="b">{crtype_code}</subfield>"""

        # Subfield 2
        sf2_338 = """<subfield code="2">rdacontent</subfield>"""

        # PRINT 338 FIELD
        field_338_op = """<datafield tag="338" ind1=" " ind2=" ">"""
        field_338_str_nb = field_338_op + a_338 + b_338 + sf2_338 + "</datafield>"
        field_338_xml = etree.fromstring(field_338_str_nb)
        field_338_xml_list.append(field_338_xml)
        # field_338_str = etree.tostring(field_338_xml, pretty_print=True, encoding="unicode")

        # print(field_338_str)

    if field_338_xml_list:
        return field_338_xml_list


def ead2marc_351(raw):
    '''Creates 351 (organization and arrangement of materials) from arrangement element'''
    field_351_xml_list = []
    level = raw.attrib['level']
    arrnote_list = raw.xpath(".//*[local-name()='arrangement']")
    if level == "collection" and arrnote_list:
        for arrnote in arrnote_list:
            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            # Strips heads from notes if there are any
            arrnote_cleanish = arrnote.xpath("string()").strip(".")
            arrnote_head_list = arrnote.xpath(".//*[local-name()='head']")
            if arrnote_head_list:
                arrnote_head = arrnote_head_list[0].xpath("string()").strip(".")
                arrnote_cleanish = arrnote_cleanish.replace(arrnote_head, "")
            # Changes all-caps series names in notes to title case
            # (This code was troubleshot utilizing Claude Opus 4.6)
            arrnote_cleanish = html.escape(arrnote_cleanish)
            arrnote_split = arrnote_cleanish.split()
            arrnote_clean_list = []
            for word in arrnote_split:
                indx = arrnote_split.index(word)
                if indx < len(arrnote_split) - 1:
                    nextword = arrnote_split[indx + 1]
                else:
                    nextword = "none"
                if word.isupper() and nextword.lower() == "series":
                    word = word.title()
                arrnote_clean_list.append(word)
            arrnote_clean = " ".join(arrnote_clean_list)
            arrnote_clean = html.escape(arrnote_clean)

        a_351 = f"""<subfield code="a">{arrnote_clean}</subfield>"""

        # PRINT 351 FIELD
        field_351_str_nb = """<datafield tag="351" ind1=" " ind2=" ">""" + a_351 + "</datafield>"
        field_351_xml = etree.fromstring(field_351_str_nb)
        field_351_xml_list.append(field_351_xml)
        # field_351_str = etree.tostring(field_351_xml, pretty_print=True, encoding="unicode")

        # print(field_351_str)

    if field_351_xml_list:
        return field_351_xml_list


def ead2marc_500(raw):
    '''Creates 500 (general notes) from odd, dimensions, physdesc, and materialspec elements'''

    field_300_result, consumed_physdescs = ead2marc_300(c0_raw)
    field_500_xml_list = []
    gnote_pref = {
        "odd": "",
        "dimensions": "Dimensions: ",
        "physdesc": "Physical Description note: ",
        "materialspec": "Material Specific Details: ",
        "physloc": "Location of resource: ",
        "phystech": "Physical Characteristics / Technical Requirements: ",
        "physfacet": "Physical Facet: ",
        "processinfo": "Processing Information: ",
        "separatedmaterial": "Materials Separated from the Resource: ",
    }
    gnote_list = raw.xpath(
        # (Troubleshot utilizing Claude Opus 4.6)
        ".//*[local-name()='odd' or local-name()='dimensions' or local-name()='physdesc' or local-name()='materialspec' or local-name()='physloc' or local-name()='phystech' or local-name()='physfacet' or local-name()='processinfo' or local-name()='separatedmaterial']"
    )
    if gnote_list:
        for gnote in gnote_list:
            if gnote in consumed_physdescs:
                # (This code generated utilizing Claude Opus 4.6)
                continue
            if etree.QName(gnote.getparent()).localname == 'physdescstructured':
                # (This code generated utilizing Claude Opus 4.6)
                continue

            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            gnote_type = etree.QName(gnote).localname
            if gnote_type in gnote_pref.keys():
                a_pref = gnote_pref[gnote_type]
            else:
                a_pref = ""
            gnote_clean = gnote.xpath("string()").strip(".")

            gnote_head_list = gnote.xpath(".//*[local-name()='head']")
            if gnote_head_list:
                gnote_head = gnote_head_list[0].xpath("string()").strip(".")
                gnote_clean = gnote_clean.replace(gnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            gnote_clean = " ".join(gnote_clean.split())
            gnote_clean = html.escape(gnote_clean)
            a_500 = f"""<subfield code="a">{a_pref}{gnote_clean}</subfield>"""

            # PRINT 500 FIELD
            field_500_str_nb = """<datafield tag="500" ind1=" " ind2=" ">""" + a_500 + "</datafield>"
            field_500_xml = etree.fromstring(field_500_str_nb)
            field_500_xml_list.append(field_500_xml)
            # field_500_str = etree.tostring(field_500_xml, pretty_print=True, encoding="unicode")

            # print(field_500_str)

        if field_500_xml_list:
            return field_500_xml_list


def ead2marc_506(raw):
    '''Creates 506 (restrictions on access) from accessrestrict elements'''

    field_506_xml_list = []
    ranote_list = raw.xpath(".//*[local-name()='accessrestrict']")
    if ranote_list:
        for ranote in ranote_list:
            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            ranote_clean = ranote.xpath("string()").strip(".")
            ranote_head_list = ranote.xpath(".//*[local-name()='head']")
            if ranote_head_list:
                ranote_head = ranote_head_list[0].xpath("string()").strip(".")
                ranote_clean = ranote_clean.replace(ranote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            ranote_clean = " ".join(ranote_clean.split())
            ranote_clean = html.escape(ranote_clean)
    else:
        ranote_clean = "This item is part of a collection that is open for research. Retrieval requires advance notice. Please contact the Cook Music Library to access this item."

    a_506 = f"""<subfield code="a">{ranote_clean}</subfield>"""

    # PRINT 506 FIELD
    field_506_str_nb = """<datafield tag="506" ind1=" " ind2=" ">""" + a_506 + "</datafield>"
    field_506_xml = etree.fromstring(field_506_str_nb)
    field_506_xml_list.append(field_506_xml)
    # field_506_str = etree.tostring(field_506_xml, pretty_print=True, encoding="unicode")

    # print(field_506_str)

    if field_506_xml_list:
        return field_506_xml_list


def ead2marc_520(raw):
    '''Creates 520 (summary/abstract) from scopecontent and abstract elements'''

    field_520_xml_list = []
    snote_ind1 = {
        "abstract": "3",
        "scopecontent": "2",
    }
    snote_list = raw.xpath(
        # (Troubleshot utilizing Claude Opus 4.6)
        ".//*[local-name()='abstract' or local-name()='scopecontent']"
    )
    if snote_list:
        for snote in snote_list:
            # INDICATORS
            # Indicator 1
            snote_type = etree.QName(snote).localname
            ind1_520 = snote_ind1[snote_type]
            field_520_open = f"""<datafield tag="520" ind1="{ind1_520}" ind2=" ">"""

            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            # Strips heads from notes if there are any
            snote_cleanish = snote.xpath("string()").strip(".")
            snote_head_list = snote.xpath(".//*[local-name()='head']")
            if snote_head_list:
                snote_head = snote_head_list[0].xpath("string()").strip(".")
                snote_cleanish = snote_cleanish.replace(snote_head, "")
            # Changes all-caps series names in notes to title case
            # (This portion of code was troubleshot utilizing Claude Opus 4.6)
            snote_cleanish = html.escape(snote_cleanish)
            snote_split = snote_cleanish.split()
            snote_clean_list = []
            for word in snote_split:
                indx = snote_split.index(word)
                if indx < len(snote_split) - 1:
                    nextword = snote_split[indx + 1]
                else:
                    nextword = "none"
                if word.isupper() and nextword.lower() == "series":
                    word = word.title()
                snote_clean_list.append(word)
            snote_clean = " ".join(snote_clean_list)
            snote_clean = html.escape(snote_clean)

            a_520 = f"""<subfield code="a">{snote_clean}</subfield>"""

            # PRINT 520 FIELD
            field_520_str_nb = field_520_open + a_520 + "</datafield>"
            field_520_xml = etree.fromstring(field_520_str_nb)
            field_520_xml_list.append(field_520_xml)
            # field_520_str = etree.tostring(field_520_xml, pretty_print=True, encoding="unicode")

            # print(field_520_str)

        if field_520_xml_list:
            return field_520_xml_list


def ead2marc_524(raw):
    '''Creates 524 (preferred citation) from prefercite elements'''

    prefercite_list = raw.xpath(".//*[local-name()='prefercite']")
    if len(prefercite_list) > 0:
        field_524_xml_list = []
        for prefercite_raw in prefercite_list:

            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            prefercite_clean = prefercite_raw.xpath("string()").strip(".")
            prefercite_head_list = prefercite_raw.xpath(".//*[local-name()='head']")
            if prefercite_head_list:
                prefercite_head = prefercite_head_list[0].xpath("string()").strip(".")
                prefercite_clean = prefercite_clean.replace(prefercite_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            prefercite_clean = " ".join(prefercite_clean.split())
            prefercite_clean = html.escape(prefercite_clean)
            a_524 = f"""<subfield code="a">{prefercite_clean}</subfield>"""

            # PRINT 524 FIELD
            field_524_str_nb = """<datafield tag="524" ind1=" " ind2=" ">""" + a_524 + "</datafield>"
            field_524_xml = etree.fromstring(field_524_str_nb)
            field_524_xml_list.append(field_524_xml)
            # field_524_str = etree.tostring(field_524_xml, pretty_print=True, encoding="unicode")

            # print(field_524_str)

        return field_524_xml_list


def ead2marc_535(raw):
    '''Creates 535 (location of originals/duplicates) from altformavail and originalsloc elements'''

    field_535_xml_list = []
    ldnote_ind1 = {
        "altformavail": "2",
        "originalsloc": "1",
    }
    ldnote_list = raw.xpath(
        ".//*[local-name()='altformavail' or local-name()='originalsloc']"
    )

    if ldnote_list:
        for ldnote in ldnote_list:
            # INDICATORS
            # Indicator 1
            ldnote_type = etree.QName(ldnote).localname
            ind1_535 = ldnote_ind1[ldnote_type]
            field_535_open = f"""<datafield tag="535" ind1="{ind1_535}" ind2=" ">"""

            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            ldnote_clean = ldnote.xpath("string()").strip(".")
            ldnote_head_list = ldnote.xpath(".//*[local-name()='head']")
            if ldnote_head_list:
                ldnote_head = ldnote_head_list[0].xpath("string()").strip(".")
                ldnote_clean = ldnote_clean.replace(ldnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            ldnote_clean = " ".join(ldnote_clean.split())
            ldnote_clean = html.escape(ldnote_clean)
            a_535 = f"""<subfield code="a">{ldnote_clean}</subfield>"""

            # PRINT 535 FIELD
            field_535_str_nb = field_535_open + a_535 + "</datafield>"
            field_535_xml = etree.fromstring(field_535_str_nb)
            field_535_xml_list.append(field_535_xml)
            # field_535_str = etree.tostring(field_535_xml, pretty_print=True, encoding="unicode")

            # print(field_535_str)

        if field_535_xml_list:
            return field_535_xml_list


def ead2marc_540(raw):
    '''Creates 540 (terms governing use) from userestrict and legalstatus elements'''

    field_540_xml_list = []
    tgurnote_list = raw.xpath(
        ".//*[local-name()='userestrict' or local-name()='legalstatus']"
    )
    if tgurnote_list:
        for tgurnote in tgurnote_list:
            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            tgurnote_clean = tgurnote.xpath("string()").strip(".")
            tgurnote_head_list = tgurnote.xpath(".//*[local-name()='head']")
            if tgurnote_head_list:
                tgurnote_head = tgurnote_head_list[0].xpath("string()").strip(".")
                tgurnote_clean = tgurnote_clean.replace(tgurnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            tgurnote_clean = " ".join(tgurnote_clean.split())
            tgurnote_clean = html.escape(tgurnote_clean)
            a_540 = f"""<subfield code="a">{tgurnote_clean}</subfield>"""

            # PRINT 540 FIELD
            field_540_str_nb = """<datafield tag="540" ind1=" " ind2=" ">""" + a_540 + "</datafield>"
            field_540_xml = etree.fromstring(field_540_str_nb)
            field_540_xml_list.append(field_540_xml)
            # field_540_str = etree.tostring(field_540_xml, pretty_print=True, encoding="unicode")

            # print(field_540_str)

        if field_540_xml_list:
            return field_540_xml_list


def ead2marc_541(raw):
    '''Creates 541 (immediate source of acquisition) from acqinfo elements'''

    field_541_xml_list = []
    acqnote_list = raw.xpath(
        ".//*[local-name()='acqinfo']"
    )

    if acqnote_list:
        for acqnote in acqnote_list:
            # INDICATORS
            # Indicator 1
            # (Troubleshoot using Claude Opus 4.6)
            if acqnote.get("audience", "").lower() == "internal":
                ind1_541 = "0"
            else:
                ind1_541 = "1"
            field_541_open = f"""<datafield tag="541" ind1="{ind1_541}" ind2=" ">"""

            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            acqnote_clean = acqnote.xpath("string()").strip(".")
            acqnote_head_list = acqnote.xpath(".//*[local-name()='head']")
            if acqnote_head_list:
                acqnote_head = acqnote_head_list[0].xpath("string()").strip(".")
                acqnote_clean = acqnote_clean.replace(acqnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            acqnote_clean = " ".join(acqnote_clean.split())
            acqnote_clean = html.escape(acqnote_clean)
            a_541 = f"""<subfield code="a">{acqnote_clean}</subfield>"""

            # PRINT 541 FIELD
            field_541_str_nb = field_541_open + a_541 + "</datafield>"
            field_541_xml = etree.fromstring(field_541_str_nb)
            field_541_xml_list.append(field_541_xml)
            # field_541_str = etree.tostring(field_541_xml, pretty_print=True, encoding="unicode")

            # print(field_541_str)

        if field_541_xml_list:
            return field_541_xml_list


def ead2marc_544(raw):
    '''Creates 544 (location of related materials) from relatedmaterial elements'''

    field_544_xml_list = []
    loamnote_list = raw.xpath(
        ".//*[local-name()='relatedmaterial']"
    )
    if loamnote_list:
        for loamnote in loamnote_list:
            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield N
            loamnote_clean = loamnote.xpath("string()").strip(".")
            loamnote_head_list = loamnote.xpath(".//*[local-name()='head']")
            if loamnote_head_list:
                loamnote_head = loamnote_head_list[0].xpath("string()").strip(".")
                loamnote_clean = loamnote_clean.replace(loamnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            loamnote_clean = " ".join(loamnote_clean.split())
            loamnote_clean = html.escape(loamnote_clean)
            n_544 = f"""<subfield code="n">{loamnote_clean}</subfield>"""

            # PRINT 544 FIELD
            field_544_str_nb = """<datafield tag="544" ind1=" " ind2=" ">""" + n_544 + "</datafield>"
            field_544_xml = etree.fromstring(field_544_str_nb)
            field_544_xml_list.append(field_544_xml)
            # field_544_str = etree.tostring(field_544_xml, pretty_print=True, encoding="unicode")

            # print(field_544_str)

        if field_544_xml_list:
            return field_544_xml_list


def ead2marc_545(raw):
    '''Creates 545 (biographical/historical note) from bioghist elements'''

    field_545_xml_list = []
    bhnote_list = raw.xpath(
        ".//*[local-name()='bioghist']"
    )
    if bhnote_list:
        for bhnote in bhnote_list:
            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            bhnote_clean = bhnote.xpath("string()").strip(".")
            bhnote_head_list = bhnote.xpath(".//*[local-name()='head']")
            if bhnote_head_list:
                bhnote_head = bhnote_head_list[0].xpath("string()").strip(".")
                bhnote_clean = bhnote_clean.replace(bhnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            bhnote_clean = " ".join(bhnote_clean.split())
            bhnote_clean = html.escape(bhnote_clean)
            a_545 = f"""<subfield code="a">{bhnote_clean}</subfield>"""

            # PRINT 545 FIELD
            field_545_str_nb = """<datafield tag="545" ind1=" " ind2=" ">""" + a_545 + "</datafield>"
            field_545_xml = etree.fromstring(field_545_str_nb)
            field_545_xml_list.append(field_545_xml)
            # field_545_str = etree.tostring(field_545_xml, pretty_print=True, encoding="unicode")

            # print(field_545_str)

        if field_545_xml_list:
            return field_545_xml_list


def ead2marc_546(raw):
    '''Creates 546 (language note) from langmaterial elements'''

    langmaterial_list = raw.xpath(".//*[local-name()='langmaterial']")
    languageset_list = raw.xpath(".//*[local-name()='languageset']")
    if len(langmaterial_list) > 0:
        field_546_xml_list = []
        for langmaterial_raw in langmaterial_list:

            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS

            langnote_fetch = langmaterial_raw.xpath(".//*[local-name()='descriptivenote']")
            if langnote_fetch:
                # Uses descriptive language note if one exists
                # Subfield A
                langnote_raw = langnote_fetch[0]
                langnote_clean = langnote_raw.xpath("string()").strip(".")
                langnote_head_list = langnote_raw.xpath(".//*[local-name()='head']")
                if langnote_head_list:
                    langnote_head = langnote_head_list[0].xpath("string()").strip(".")
                    langnote_clean = langnote_clean.replace(langnote_head, "")
                # (This portion of code was generated utilizing Claude Opus 4.6)
                langnote_clean = " ".join(langnote_clean.split())
                langnote_clean = html.escape(langnote_clean)
                a_546 = f"""<subfield code="a">{langnote_clean}</subfield>"""
            else:
                # If descriptive language note does not exist, $a is [Language 1], [Language 2], ...
                language_clean_list = []
                for languageset in languageset_list:
                    # Subfield A
                    language_fetch = languageset.xpath(".//*[local-name()='language']")
                    language_raw = language_fetch[0]
                    language_clean = language_raw.xpath("string()").strip(".")
                    language_clean = html.escape(language_clean)
                    language_clean_list.append(language_clean)
                    languages = (", ").join(language_clean_list)
                    a_546 = f"""<subfield code="a">{languages}</subfield>"""

            # PRINT 546 FIELD
            field_546_str_nb = """<datafield tag="546" ind1=" " ind2=" ">""" + a_546 + "</datafield>"
            field_546_xml = etree.fromstring(field_546_str_nb)
            field_546_xml_list.append(field_546_xml)
            # field_546_str = etree.tostring(field_546_xml, pretty_print=True, encoding="unicode")

            # print(field_546_str)

        return field_546_xml_list


def ead2marc_555(va_id):
    '''Creates 555 (finding aid note) with link to ArchivesSpace finding aid'''

    level = c0_raw.attrib['level']
    field_555_xml_list = []
    if va_id:

        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2 is constant (blank)

        # SUBFIELDS
        # Subfield A
        a_555 = """<subfield code="a">Finding aid (work): </subfield>"""

        # Subfield U
        faid_uri = f"""https://archives.iu.edu/catalog/{va_id}"""
        u_555 = f"""<subfield code="u">{faid_uri} </subfield>"""

        # PRINT 555 FIELD
        # (Troubleshoot using Claude Opus 4.6)
        field_555_op = """<datafield tag="555" ind1=" " ind2=" ">"""
        if level == "collection":
            field_555_static_ms = "Finding aid (available on Indiana University Archives Online) includes series and subseries listing of items in the collection including dates, descriptions, scope, and extent of the materials."
            field_555_static_str_nb = field_555_op + f"""<subfield code="a">{field_555_static_ms}</subfield>""" + "</datafield>"
            field_555_static_xml = etree.fromstring(field_555_static_str_nb)
            field_555_xml_list.append(field_555_static_xml)
        field_555_str_nb = field_555_op + a_555 + u_555 + "</datafield>"
        field_555_xml = etree.fromstring(field_555_str_nb)
        field_555_xml_list.append(field_555_xml)
        # field_555_str = etree.tostring(field_555_xml, pretty_print=True, encoding="unicode")

        # print(field_555_str)

    return field_555_xml_list


def ead2marc_561(raw):
    '''Creates 561 (ownership and custodial history) from custodhist elements'''

    field_561_xml_list = []
    chnote_list = raw.xpath(
        ".//*[local-name()='custodhist']"
    )

    if chnote_list:
        for chnote in chnote_list:
            # INDICATORS
            # Indicator 1
            # (Troubleshoot using Claude Opus 4.6)
            if chnote.get("audience", "").lower() == "internal":
                ind1_561 = "0"
            else:
                ind1_561 = "1"
            field_561_open = f"""<datafield tag="561" ind1="{ind1_561}" ind2=" ">"""

            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            chnote_clean = chnote.xpath("string()").strip(".")
            chnote_head_list = chnote.xpath(".//*[local-name()='head']")
            if chnote_head_list:
                chnote_head = chnote_head_list[0].xpath("string()").strip(".")
                chnote_clean = chnote_clean.replace(chnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            chnote_clean = " ".join(chnote_clean.split())
            chnote_clean = html.escape(chnote_clean)
            a_561 = f"""<subfield code="a">{chnote_clean}</subfield>"""

            # PRINT 561 FIELD
            field_561_str_nb = field_561_open + a_561 + "</datafield>"
            field_561_xml = etree.fromstring(field_561_str_nb)
            field_561_xml_list.append(field_561_xml)
            # field_561_str = etree.tostring(field_561_xml, pretty_print=True, encoding="unicode")

            # print(field_561_str)

        if field_561_xml_list:
            return field_561_xml_list


def ead2marc_583(raw):
    '''Creates 583 (action note) from appraisal elements'''

    field_583_xml_list = []
    aprnote_list = raw.xpath(
        ".//*[local-name()='appraisal']"
    )

    if aprnote_list:
        for aprnote in aprnote_list:
            # INDICATORS
            # Indicator 1
            # (Troubleshoot using Claude Opus 4.6)
            if aprnote.get("audience", "").lower() == "internal":
                ind1_583 = "0"
            else:
                ind1_583 = "1"
            field_583_open = f"""<datafield tag="583" ind1="{ind1_583}" ind2=" ">"""

            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            aprnote_clean = aprnote.xpath("string()").strip(".")
            aprnote_head_list = aprnote.xpath(".//*[local-name()='head']")
            if aprnote_head_list:
                aprnote_head = aprnote_head_list[0].xpath("string()").strip(".")
                aprnote_clean = aprnote_clean.replace(aprnote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            aprnote_clean = " ".join(aprnote_clean.split())
            aprnote_clean = html.escape(aprnote_clean)
            a_583 = f"""<subfield code="a">{aprnote_clean}</subfield>"""

            # PRINT 583 FIELD
            field_583_str_nb = field_583_open + a_583 + "</datafield>"
            field_583_xml = etree.fromstring(field_583_str_nb)
            field_583_xml_list.append(field_583_xml)
            # field_583_str = etree.tostring(field_583_xml, pretty_print=True, encoding="unicode")

            # print(field_583_str)

        if field_583_xml_list:
            return field_583_xml_list


def ead2marc_584(raw):
    '''Creates 584 (accumulation and frequency of use) from accruals elements'''

    field_584_xml_list = []
    afunote_list = raw.xpath(
        ".//*[local-name()='accruals']"
    )
    if afunote_list:
        for afunote in afunote_list:
            # INDICATORS
            # Indicator 1 is constant (blank)
            # Indicator 2 is constant (blank)

            # SUBFIELDS
            # Subfield A
            afunote_clean = afunote.xpath("string()").strip(".")
            afunote_head_list = afunote.xpath(".//*[local-name()='head']")
            if afunote_head_list:
                afunote_head = afunote_head_list[0].xpath("string()").strip(".")
                afunote_clean = afunote_clean.replace(afunote_head, "")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            afunote_clean = " ".join(afunote_clean.split())
            afunote_clean = html.escape(afunote_clean)
            a_584 = f"""<subfield code="a">{afunote_clean}</subfield>"""

            # PRINT 584 FIELD
            field_584_str_nb = """<datafield tag="584" ind1=" " ind2=" ">""" + a_584 + "</datafield>"
            field_584_xml = etree.fromstring(field_584_str_nb)
            field_584_xml_list.append(field_584_xml)
            # field_584_str = etree.tostring(field_584_xml, pretty_print=True, encoding="unicode")

            # print(field_584_str)

        if field_584_xml_list:
            return field_584_xml_list


def ead2marc_600(name):
    a_alpha = []
    d_num = []
    authority_600_str = None
    '''Creates 600 (personal name subject) with authority validation'''

    # Check if name is associated with an authority file
    authority_raw = (name.get("source") or "").lower()
    if authority_raw == "lcac":
        authority = "cyac"
    else:
        authority = authority_raw
    # Pull identifier and check if name is associated with lcnaf or viaf
    # (This portion of code was generated utilizing Claude Opus 4.6)
    timeout_error = False
    timeout_authfile_no = None
    if authority in {"lcnaf", "naf", "viaf"} and name.get("identifier") and not name.get("identifier", "").startswith("aspace_"):
        authfile_no = name.get("identifier")
    elif authority in {"lcnaf", "naf"}:
        name_str = name.xpath("string()").strip()
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={name_str}"""
        # (This portion of code was generated utilizing Claude Opus 4.5)
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        authfile_no = None
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == name_str:
                authfile_no = hit["token"]
                break
    elif authority == "viaf":
        # (This portion of code was generated utilizing Claude Opus 4.5)
        name_str = name.xpath("string()").strip()
        viaf_search_url = f"""https://viaf.org/viaf/search?query=local.personalNames+all+%22{name_str}%22&sortKeys=holdingscount&maximumRecords=5"""
        viaf_headers = {'Accept': 'application/xml'}
        viaf_search_response = requests.get(viaf_search_url, headers=viaf_headers)
        viaf_search_root = etree.fromstring(viaf_search_response.content)
        authfile_no = None
        records = viaf_search_root.xpath('//*[local-name()="record"]')
        for rec in records:
            headings = rec.xpath('.//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_id = rec.xpath('.//*[local-name()="viafID"]')
            if headings and viaf_id and headings[0].text == name_str:
                authfile_no = viaf_id[0].text
                break
    else:
        authfile_no = None

    # Pull authority file using identifier
    if authority in {"lcnaf", "naf"} and authfile_no:
        # Get Library of Congress Name Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority = "lcnaf"
            authfile_no = name.get("identifier")
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_600_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='100']")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            # Fallback to tag 110 if tag 100 not found (handles mismatched EAD name types)
            if not authority_600_list:
                authority_600_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
            authority_600_raw = authority_600_list[0]
            # Clean authority_600_raw
            authority_600_str = etree.tostring(authority_600_raw, pretty_print=True, encoding="unicode")
            authority_600_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_600_str)
            authority_600_str_list = authority_600_str.split("\n")
            authority_600_str_list_stripped = [str.strip() for str in authority_600_str_list]
            authority_600_str = "".join(authority_600_str_list_stripped)
            authority_600_str = re.sub(r'</datafield>', '', authority_600_str).strip()
            # Change tag from 100 to 600
            # (This portion of code was generated utilizing Claude Opus 4.5)
            authority_600_str = authority_600_str.replace('tag="100"', 'tag="600"')
            # (This portion of code was generated utilizing Claude Opus 4.6)
            authority_600_str = authority_600_str.replace('tag="110"', 'tag="710"')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authority = None
            timeout_error = True
            timeout_authfile_no = authfile_no
    elif authority == "viaf" and authfile_no:
        # Get VIAF cluster XML and extract 600 field data
        # (This portion of code was generated utilizing Claude Opus 4.5)
        authority = "viaf"
        viaf_headers = {'Accept': 'application/xml'}
        viaf_url = f"https://viaf.org/viaf/{authfile_no}"
        viaf_response = requests.get(viaf_url, headers=viaf_headers)
        viaf_root = etree.fromstring(viaf_response.content)
        # Check if VIAF cluster has linked LCNAF -- if so, use LCNAF
        # (This portion of code was generated utilizing Claude Opus 4.5)
        lc_sources = viaf_root.xpath('//*[local-name()="source" and starts-with(text(), "LC|")]')
        if lc_sources:
            # VIAF has LC link -- fetch from LCNAF
            # (This portion of code was generated utilizing Claude Opus 4.6)
            try:
                lc_id = lc_sources[0].text.split('|')[1]
                authority_url = f"https://lccn.loc.gov/{lc_id}/marcxml"
                authority_xml = loc_get(authority_url, timeout=10).content
                authority_root = etree.fromstring(authority_xml)
                authority_600_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='100']")
                # (This portion of code was generated utilizing Claude Opus 4.6)
                # Fallback to tag 110 if tag 100 not found (handles mismatched EAD name types)
                if not authority_600_list:
                    authority_600_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
                authority_600_raw = authority_600_list[0]
                authority_600_str = etree.tostring(authority_600_raw, pretty_print=True, encoding="unicode")
                authority_600_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_600_str)
                authority_600_str_list = authority_600_str.split("\n")
                authority_600_str_list_stripped = [str.strip() for str in authority_600_str_list]
                authority_600_str = "".join(authority_600_str_list_stripped)
                authority_600_str = re.sub(r'</datafield>', '', authority_600_str).strip()
                # Change tag from 100 to 600
                authority_600_str = authority_600_str.replace('tag="100"', 'tag="600"')
                # (This portion of code was generated utilizing Claude Opus 4.6)
                authority_600_str = authority_600_str.replace('tag="110"', 'tag="710"')
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
                print(f"WARNING: Connection to lccn.loc.gov timed out for {lc_id}. Constructing field manually.")
                authority = None
                timeout_error = True
                timeout_authfile_no = lc_id
        else:
            # No LC source -- parse VIAF cluster directly
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_headings = viaf_root.xpath('//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_main_heading = viaf_headings[0].text if viaf_headings else None
            # Get normalized dates from VIAF
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_birth = viaf_root.xpath('//*[local-name()="birthDate"]')
            viaf_death = viaf_root.xpath('//*[local-name()="deathDate"]')
            viaf_birth_year = viaf_birth[0].text[:4] if viaf_birth and viaf_birth[0].text and not viaf_birth[0].text.startswith('0') else None
            viaf_death_year = viaf_death[0].text[:4] if viaf_death and viaf_death[0].text and not viaf_death[0].text.startswith('0') else None
            # Parse heading to separate name from dates
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_parts = viaf_main_heading.split(', ') if viaf_main_heading else []
            viaf_name_parts = []
            for part in viaf_parts:
                if not (any(c.isdigit() for c in part) and ('-' in part or part.endswith('-'))):
                    viaf_name_parts.append(part)
            viaf_ind1 = '1' if len(viaf_name_parts) > 1 else '0'
            viaf_a_content = ', '.join(viaf_name_parts)
            # Determine date subfield
            # (This portion of code was generated utilizing Claude Opus 4.5)
            if viaf_birth_year and viaf_death_year:
                viaf_d_content = f'{viaf_birth_year}-{viaf_death_year}'
            elif viaf_birth_year:
                viaf_d_content = f'{viaf_birth_year}-'
            else:
                viaf_d_content = None
            # Build authority_600_str for VIAF-direct
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_subfields = f'<subfield code="a">{viaf_a_content}</subfield>'
            if viaf_d_content:
                viaf_subfields += f'<subfield code="d">{viaf_d_content}</subfield>'
            authority_600_str = f'<datafield tag="600" ind1="{viaf_ind1}" ind2=" ">{viaf_subfields}'

    # If authority fetch failed, reset authority so manual construction runs
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_600_str is None:
        authority = None

    # INDICATORS
    # Indicator 1
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority not in ["lcnaf", "viaf"]:
        a_content = name.xpath("string()").strip()
        a_split = a_content.split(", ")
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if name.tag.endswith('famname'):
            ind1_600 = "3"
        else:
            for item in a_split:
                if re.search(r'\b\d{4}\b', item):
                    d_num.append(item)
                else:
                    a_alpha.append(item)
            if len(a_alpha) > 1:
                ind1_600 = "1"
            else:
                ind1_600 = "0"
    else:
        ind1_600 = ""

    # Indicator 2
    if authority == "lcsh":
        ind2_600 = "0"
    elif authority == "cyac":
        ind2_600 = "1"
    elif authority == "mesh":
        ind2_600 = "2"
    elif authority == "nal":
        ind2_600 = "3"
    elif authority in ("", None, "source not specified"):
        ind2_600 = "4"
    elif authority == "cash":
        ind2_600 = "5"
    elif authority == "rvm":
        ind2_600 = "6"
    else:
        ind2_600 = "7"

    # Subfield E
    if 'relator' in name.attrib:
        aspace_relator = name.attrib["relator"].lower()
        if aspace_relator in marc_rda_relators.keys():
            e_content = marc_rda_relators[aspace_relator]
            e_600 = f"""<subfield code="e">{e_content}</subfield>"""
        else:
            e_600 = ""
    else:
        e_600 = ""

    # Subfield F
    if ind2_600 == "7" and authority is not None:
        f_600 = f"""<subfield code="2">{authority}</subfield>"""
    else:
        f_600 = ""

    # Subfield D
    if d_num:
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if authority not in ["lcnaf", "viaf"] and not name.tag.endswith('famname'):
            d_content = d_num[0]
            d_content = d_content.rstrip(".")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            if e_600:
                d_content += ","
            d_600 = f"""<subfield code="d">{d_content}</subfield>"""
    else:
        d_600 = ""

    # Subfield A
    if authority not in ["lcnaf", "viaf"]:
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if name.tag.endswith('famname'):
            a_content = a_content
        else:
            a_content = ", ".join(a_alpha)
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if d_600:
            a_content += ","
        a_600 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 600 FIELD
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_600_str is not None:
        field_600_str_nb = authority_600_str + e_600 + "</datafield>"
        field_600_xml = etree.fromstring(field_600_str_nb)
        field_600_str = etree.tostring(field_600_xml, pretty_print=True, encoding="unicode")
    else:
        field_600_open = f"""<datafield tag="600" ind1="{ind1_600}" ind2="{ind2_600}">"""
        field_600_str_nb = field_600_open + a_600 + d_600 + e_600 + f_600 + "</datafield>"
        field_600_xml = etree.fromstring(field_600_str_nb)
        field_600_str = etree.tostring(field_600_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.5)
    field_600_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_600_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_600 = []
    if timeout_error:
        result_600.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_600.append(field_600_xml)

    # print(field_600_str)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    return result_600


def ead2marc_610(name):
    authority_610_str = None
    '''Creates 610 (corporate name subject) with authority validation'''

    # Check if main name is associated with an authority file
    authority_raw = (name.get("source") or "").lower()
    if authority_raw == "lcac":
        authority = "cyac"
    else:
        authority = authority_raw
    # Pull identifier and check if name is associated with lcnaf or viaf
    # (This portion of code was generated utilizing Claude Opus 4.6)
    timeout_error = False
    timeout_authfile_no = None
    if authority in {"lcnaf", "naf", "viaf"} and name.get("identifier") and not name.get("identifier", "").startswith("aspace_"):
        authfile_no = name.get("identifier")
    elif authority in {"lcnaf", "naf"}:
        name_str = name.xpath("string()").strip()
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={name_str}"""
        # (This portion of code was generated utilizing Claude Opus 4.5)
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        authfile_no = None
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == name_str:
                authfile_no = hit["token"]
                break
    elif authority == "viaf":
        # (This portion of code was generated utilizing Claude Opus 4.5)
        name_str = name.xpath("string()").strip()
        viaf_search_url = f"""https://viaf.org/viaf/search?query=local.corporateNames+all+%22{name_str}%22&sortKeys=holdingscount&maximumRecords=5"""
        viaf_headers = {'Accept': 'application/xml'}
        viaf_search_response = requests.get(viaf_search_url, headers=viaf_headers)
        viaf_search_root = etree.fromstring(viaf_search_response.content)
        authfile_no = None
        records = viaf_search_root.xpath('//*[local-name()="record"]')
        for rec in records:
            headings = rec.xpath('.//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_id = rec.xpath('.//*[local-name()="viafID"]')
            if headings and viaf_id and headings[0].text == name_str:
                authfile_no = viaf_id[0].text
                break
    else:
        authfile_no = None

    # Pull authority file using identifier
    if authority in {"lcnaf", "naf"} and authfile_no:
        # Get Library of Congress Name Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority = "lcnaf"
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_610_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
            authority_610_raw = authority_610_list[0]
            # Clean authority_610_raw
            authority_610_str = etree.tostring(authority_610_raw, pretty_print=True, encoding="unicode")
            authority_610_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_610_str)
            authority_610_str_list = authority_610_str.split("\n")
            authority_610_str_list_stripped = [str.strip() for str in authority_610_str_list]
            authority_610_str = "".join(authority_610_str_list_stripped)
            authority_610_str = re.sub(r'</datafield>', '', authority_610_str).strip()
            # Change tag from 110 to 610
            # (This portion of code was generated utilizing Claude Opus 4.5)
            authority_610_str = authority_610_str.replace('tag="110"', 'tag="610"')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authority = None
            timeout_error = True
            timeout_authfile_no = authfile_no
    elif authority == "viaf" and authfile_no:
        # Get VIAF cluster XML and extract 610 field data
        # (This portion of code was generated utilizing Claude Opus 4.5)
        authority = "viaf"
        viaf_headers = {'Accept': 'application/xml'}
        viaf_url = f"https://viaf.org/viaf/{authfile_no}"
        viaf_response = requests.get(viaf_url, headers=viaf_headers)
        viaf_root = etree.fromstring(viaf_response.content)
        # Check if VIAF cluster has linked LCNAF -- if so, use LCNAF
        # (This portion of code was generated utilizing Claude Opus 4.5)
        lc_sources = viaf_root.xpath('//*[local-name()="source" and starts-with(text(), "LC|")]')
        if lc_sources:
            # VIAF has LC link -- fetch from LCNAF
            # (This portion of code was generated utilizing Claude Opus 4.6)
            try:
                lc_id = lc_sources[0].text.split('|')[1]
                authority_url = f"https://lccn.loc.gov/{lc_id}/marcxml"
                authority_xml = loc_get(authority_url, timeout=10).content
                authority_root = etree.fromstring(authority_xml)
                authority_610_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
                authority_610_raw = authority_610_list[0]
                authority_610_str = etree.tostring(authority_610_raw, pretty_print=True, encoding="unicode")
                authority_610_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_610_str)
                authority_610_str_list = authority_610_str.split("\n")
                authority_610_str_list_stripped = [str.strip() for str in authority_610_str_list]
                authority_610_str = "".join(authority_610_str_list_stripped)
                authority_610_str = re.sub(r'</datafield>', '', authority_610_str).strip()
                # Change tag from 110 to 610
                # (This portion of code was generated utilizing Claude Opus 4.5)
                authority_610_str = authority_610_str.replace('tag="110"', 'tag="610"')
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
                print(f"WARNING: Connection to lccn.loc.gov timed out for {lc_id}. Constructing field manually.")
                authority = None
                timeout_error = True
                timeout_authfile_no = lc_id
        else:
            # No LC source -- parse VIAF cluster directly
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_headings = viaf_root.xpath('//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_main_heading = viaf_headings[0].text if viaf_headings else None
            # Build authority_610_str for VIAF-direct
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_subfields = f'<subfield code="a">{viaf_main_heading}</subfield>'
            authority_610_str = f'<datafield tag="610" ind1="2" ind2=" ">{viaf_subfields}'
    else:
        authority = None

    # If authority fetch failed, reset authority so manual construction runs
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_610_str is None:
        authority = None

    # INDICATORS
    # Indicator 1
    if authority not in ["lcnaf", "viaf"]:
        ind1_610 = "2"
    else:
        ind1_610 = ""

    # Indicator 2
    if authority == "lcsh":
        ind2_610 = "0"
    elif authority == "cyac":
        ind2_610 = "1"
    elif authority == "mesh":
        ind2_610 = "2"
    elif authority == "nal":
        ind2_610 = "3"
    elif authority in ("", None, "source not specified"):
        ind2_610 = "4"
    elif authority == "cash":
        ind2_610 = "5"
    elif authority == "rvm":
        ind2_610 = "6"
    else:
        ind2_610 = "7"

    # SUBFIELDS
    # Subfield E
    if 'relator' in name.attrib:
        aspace_relator = name.attrib["relator"].lower()
        if aspace_relator in marc_rda_relators.keys():
            e_content = marc_rda_relators[aspace_relator]
            e_610 = f"""<subfield code="e">{e_content}</subfield>"""
        else:
            e_610 = ""
    else:
        e_610 = ""

    # Subfield F
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if ind2_610 == "7" and authority is not None:
        f_610 = f"""<subfield code="2">{authority}</subfield>"""
    else:
        f_610 = ""

    # Subfield A
    if authority not in ["lcnaf", "viaf"]:
        a_content = name.xpath("string()").strip()
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if e_610:
            a_content += ","
        a_610 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 610 FIELD
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_610_str is not None:
        field_610_str_nb = authority_610_str + e_610 + "</datafield>"
        field_610_xml = etree.fromstring(field_610_str_nb)
        field_610_str = etree.tostring(field_610_xml, pretty_print=True, encoding="unicode")
    else:
        field_610_open = f"""<datafield tag="610" ind1="{ind1_610}" ind2="{ind2_610}">"""
        field_610_str_nb = field_610_open + a_610 + e_610 + f_610 + "</datafield>"
        field_610_xml = etree.fromstring(field_610_str_nb)
        field_610_str = etree.tostring(field_610_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.5)
    field_610_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_610_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_610 = []
    if timeout_error:
        result_610.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_610.append(field_610_xml)

    # print(field_610_str)
    return result_610

    # NOTE:
        # Currently no subfields beyond subfields A and E are supported for non-authority 110s. All content except relators will be placed in subfield A.
        # ind1 0 (inverted name) and 1 (jurisdiction name) are not supported for non-authority 110s


def ead2marc_630(title):
    '''Creates 630 (uniform title subject) with authority validation and subdivision classification'''

    authority_raw = title.get("source").lower()
    if authority_raw == "lcac":
        authority = "cyac"
    else:
        authority = authority_raw
    title_clean = title.xpath("string()").strip()
    title_clean = html.escape(title_clean)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    title_clean = " ".join(title_clean.split())
    timeout_error = False
    timeout_authfile_no = None

    # Split heading into main heading and subdivisions
    # (This portion of code was generated utilizing Claude Opus 4.6)
    parts = title_clean.split(" -- ")
    main_heading = parts[0]
    subdivisions = parts[1:] if len(parts) > 1 else []

    # Pull identifier if source is lcsh
    authfile_no = None
    if title.get("source").lower() in {"lcsh"}:
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={main_heading}"""
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == main_heading:
                authfile_no = hit["token"]
                break

    # Pull authority file using identifier
    if title.get("source").lower() in {"lcsh"} and authfile_no:
        # Get LC Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_130_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='130']")
            authority_130_raw = authority_130_list[0]
            # Clean authority_130_raw
            authority_130_str = etree.tostring(authority_130_raw, pretty_print=True, encoding="unicode")
            authority_130_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_130_str)
            authority_130_str_list = authority_130_str.split("\n")
            authority_130_str_list_stripped = [str.strip() for str in authority_130_str_list]
            authority_130_str = "".join(authority_130_str_list_stripped)
            authority_130_str = re.sub(r'</datafield>', '', authority_130_str).strip()
            authority_630_str = authority_130_str.replace('tag="130"', 'tag="630"')

            # Classify and append subdivisions
            # (This portion of code was generated utilizing Claude Opus 4.6)
            subdiv_subfields = ""
            for subdiv in subdivisions:
                subdiv_code = "x"  # default to general
                subdiv_suggest_url = f"""https://id.loc.gov/authorities/subjects/suggest2?q={subdiv}"""
                subdiv_response = loc_get(subdiv_suggest_url)
                try:
                    subdiv_data = subdiv_response.json()
                except requests.exceptions.JSONDecodeError:
                    subdiv_data = {}
                for subdiv_hit in subdiv_data.get("hits", []):
                    if subdiv_hit["aLabel"] == subdiv:
                        subdiv_token = subdiv_hit["token"]
                        subdiv_auth_url = f"""https://lccn.loc.gov/{subdiv_token}/marcxml"""
                        subdiv_auth_xml = loc_get(subdiv_auth_url, timeout=10).content
                        subdiv_auth_root = etree.fromstring(subdiv_auth_xml)
                        if subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='185']"):
                            subdiv_code = "v"  # form subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='181']"):
                            subdiv_code = "z"  # geographic subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='182']"):
                            subdiv_code = "y"  # chronological subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='180']"):
                            subdiv_code = "x"  # general subdivision
                        break
                subdiv_subfields += f"""<subfield code="{subdiv_code}">{subdiv}</subfield>"""
            authority_630_str += subdiv_subfields
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authfile_no = None
            timeout_error = True
            timeout_authfile_no = authfile_no

    if not authfile_no:
        # Compile field manually if no lcsh match
        # INDICATORS
        # Indicator 1 is constant (0)
        # Indicator 2
        if authority == "lcsh":
            ind2_630 = "0"
        elif authority == "cyac":
            ind2_630 = "1"
        elif authority == "mesh":
            ind2_630 = "2"
        elif authority == "nal":
            ind2_630 = "3"
        elif authority == "":
            ind2_630 = "4"
        elif authority == "source not specified":
            ind2_630 = "4"
        elif authority == "cash":
            ind2_630 = "5"
        elif authority == "rvm":
            ind2_630 = "6"
        else:
            ind2_630 = "7"

        field_630_open = f"""<datafield tag="630" ind1="0" ind2="{ind2_630}">"""

        # Subfield A
        a_630 = f"""<subfield code="a">{title_clean}</subfield>"""

        # Subfield F
        if ind2_630 == "7":
            f_630 = f"""<subfield code="2">{authority}</subfield>""" if authority is not None else ""
        else:
            f_630 = ""

    # PRINT 630 FIELD
    if authfile_no:
        field_630_str_nb = authority_630_str + "</datafield>"
        field_630_xml = etree.fromstring(field_630_str_nb)
        field_630_str = etree.tostring(field_630_xml, pretty_print=True, encoding="unicode")
    else:
        # (This portion of code was troubleshot using Claud Opus 4.5)
        field_630_str_nb = field_630_open + a_630 + f_630 + "</datafield>"
        field_630_xml = etree.fromstring(field_630_str_nb)
        field_630_str = etree.tostring(field_630_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.6)
    field_630_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_630_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_630 = []
    if timeout_error:
        result_630.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_630.append(field_630_xml)

    # print(field_630_str)
    return result_630


def ead2marc_650(sh):
    '''Creates 650 (topical subject) with authority validation and subdivision classification'''

    sh_clean = sh.xpath("string()").strip()
    sh_clean = html.escape(sh_clean)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    sh_clean = " ".join(sh_clean.split())
    timeout_error = False
    timeout_authfile_no = None

    authority_raw = sh.get("source").lower()
    if authority_raw == "lcac":
        authority = "cyac"
    else:
        authority = authority_raw

    # Split heading into main heading and subdivisions
    # (This portion of code was generated utilizing Claude Opus 4.6)
    parts = sh_clean.split(" -- ")
    main_heading = parts[0]
    subdivisions = parts[1:] if len(parts) > 1 else []

    # Pull identifier if source is lcsh
    authfile_no = None
    if sh.get("source").lower() in {"lcsh"}:
        suggest_url = f"""https://id.loc.gov/authorities/subjects/suggest2?q={main_heading}"""
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == main_heading:
                authfile_no = hit["token"]
                break

    # Pull authority file using identifier
    if sh.get("source").lower() in {"lcsh"} and authfile_no:
        # Get LC Subject Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_150_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='150']")
            authority_150_raw = authority_150_list[0]
            # Clean authority_150_raw
            authority_150_str = etree.tostring(authority_150_raw, pretty_print=True, encoding="unicode")
            authority_150_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_150_str)
            authority_150_str_list = authority_150_str.split("\n")
            authority_150_str_list_stripped = [str.strip() for str in authority_150_str_list]
            authority_150_str = "".join(authority_150_str_list_stripped)
            authority_150_str = re.sub(r'</datafield>', '', authority_150_str).strip()
            authority_650_str = authority_150_str.replace('tag="150"', 'tag="650"')

            # Classify and append subdivisions
            # (This portion of code was generated utilizing Claude Opus 4.6)
            subdiv_subfields = ""
            for subdiv in subdivisions:
                subdiv_code = "x"  # default to general
                subdiv_suggest_url = f"""https://id.loc.gov/authorities/subjects/suggest2?q={subdiv}"""
                subdiv_response = loc_get(subdiv_suggest_url)
                try:
                    subdiv_data = subdiv_response.json()
                except requests.exceptions.JSONDecodeError:
                    subdiv_data = {}
                for subdiv_hit in subdiv_data.get("hits", []):
                    if subdiv_hit["aLabel"] == subdiv:
                        subdiv_token = subdiv_hit["token"]
                        subdiv_auth_url = f"""https://lccn.loc.gov/{subdiv_token}/marcxml"""
                        subdiv_auth_xml = loc_get(subdiv_auth_url, timeout=10).content
                        subdiv_auth_root = etree.fromstring(subdiv_auth_xml)
                        if subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='185']"):
                            subdiv_code = "v"  # form subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='181']"):
                            subdiv_code = "z"  # geographic subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='182']"):
                            subdiv_code = "y"  # chronological subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='180']"):
                            subdiv_code = "x"  # general subdivision
                        break
                subdiv_subfields += f"""<subfield code="{subdiv_code}">{subdiv}</subfield>"""
            authority_650_str += subdiv_subfields
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authfile_no = None
            timeout_error = True
            timeout_authfile_no = authfile_no

    if not authfile_no:
        # Compile field manually if no lcsh match
        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2
        if authority == "lcsh":
            ind2_650 = "0"
        elif authority == "cyac":
            ind2_650 = "1"
        elif authority == "mesh":
            ind2_650 = "2"
        elif authority == "nal":
            ind2_650 = "3"
        elif authority == "":
            ind2_650 = "4"
        elif authority == "source not specified":
            ind2_650 = "4"
        elif authority == "cash":
            ind2_650 = "5"
        elif authority == "rvm":
            ind2_650 = "6"
        else:
            ind2_650 = "7"

        field_650_open = f"""<datafield tag="650" ind1=" " ind2="{ind2_650}">"""

        # Subfield A
        a_650 = f"""<subfield code="a">{sh_clean}</subfield>"""

        # Subfield F
        if ind2_650 == "7":
            f_650 = f"""<subfield code="2">{authority}</subfield>""" if authority is not None else ""
        else:
            f_650 = ""

    # PRINT 650 FIELD
    if authfile_no:
        field_650_str_nb = authority_650_str + "</datafield>"
        field_650_xml = etree.fromstring(field_650_str_nb)
        field_650_str = etree.tostring(field_650_xml, pretty_print=True, encoding="unicode")
    else:
        # (This portion of code was troubleshot using Claud Opus 4.5)
        field_650_str_nb = field_650_open + a_650 + f_650 + "</datafield>"
        field_650_xml = etree.fromstring(field_650_str_nb)
        field_650_str = etree.tostring(field_650_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.6)
    field_650_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_650_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_650 = []
    if timeout_error:
        result_650.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_650.append(field_650_xml)

    # print(field_650_str)
    return result_650


def ead2marc_651(geo):
    '''Creates 651 (geographic subject) with authority validation and subdivision classification'''

    geo_clean = geo.xpath("string()").strip()
    geo_clean = html.escape(geo_clean)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    geo_clean = " ".join(geo_clean.split())
    timeout_error = False
    timeout_authfile_no = None

    authority_raw = geo.get("source").lower()
    if authority_raw == "lcac":
        authority = "cyac"
    else:
        authority = authority_raw

    # Split heading into main heading and subdivisions
    # (This portion of code was generated utilizing Claude Opus 4.6)
    parts = geo_clean.split(" -- ")
    main_heading = parts[0]
    subdivisions = parts[1:] if len(parts) > 1 else []

    # Pull identifier if source is lcsh
    authfile_no = None
    if geo.get("source").lower() in {"lcsh"}:
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={main_heading}"""
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == main_heading:
                authfile_no = hit["token"]
                break

    # Pull authority file using identifier
    if geo.get("source").lower() in {"lcsh"} and authfile_no:
        # Get LC Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_151_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='151']")
            authority_151_raw = authority_151_list[0]
            # Clean authority_151_raw
            authority_151_str = etree.tostring(authority_151_raw, pretty_print=True, encoding="unicode")
            authority_151_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_151_str)
            authority_151_str_list = authority_151_str.split("\n")
            authority_151_str_list_stripped = [str.strip() for str in authority_151_str_list]
            authority_151_str = "".join(authority_151_str_list_stripped)
            authority_151_str = re.sub(r'</datafield>', '', authority_151_str).strip()
            authority_651_str = authority_151_str.replace('tag="151"', 'tag="651"')

            # Classify and append subdivisions
            # (This portion of code was generated utilizing Claude Opus 4.6)
            subdiv_subfields = ""
            for subdiv in subdivisions:
                subdiv_code = "x"  # default to general
                subdiv_suggest_url = f"""https://id.loc.gov/authorities/subjects/suggest2?q={subdiv}"""
                subdiv_response = loc_get(subdiv_suggest_url)
                try:
                    subdiv_data = subdiv_response.json()
                except requests.exceptions.JSONDecodeError:
                    subdiv_data = {}
                for subdiv_hit in subdiv_data.get("hits", []):
                    if subdiv_hit["aLabel"] == subdiv:
                        subdiv_token = subdiv_hit["token"]
                        subdiv_auth_url = f"""https://lccn.loc.gov/{subdiv_token}/marcxml"""
                        subdiv_auth_xml = loc_get(subdiv_auth_url, timeout=10).content
                        subdiv_auth_root = etree.fromstring(subdiv_auth_xml)
                        if subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='185']"):
                            subdiv_code = "v"  # form subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='181']"):
                            subdiv_code = "z"  # geographic subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='182']"):
                            subdiv_code = "y"  # chronological subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='180']"):
                            subdiv_code = "x"  # general subdivision
                        break
                subdiv_subfields += f"""<subfield code="{subdiv_code}">{subdiv}</subfield>"""
            authority_651_str += subdiv_subfields
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authfile_no = None
            timeout_error = True
            timeout_authfile_no = authfile_no

    if not authfile_no:
        # Compile field manually if no lcsh match
        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2
        if authority == "lcsh":
            ind2_651 = "0"
        elif authority == "cyac":
            ind2_651 = "1"
        elif authority == "mesh":
            ind2_651 = "2"
        elif authority == "nal":
            ind2_651 = "3"
        elif authority == "":
            ind2_651 = "4"
        elif authority == "source not specified":
            ind2_651 = "4"
        elif authority == "cash":
            ind2_651 = "5"
        elif authority == "rvm":
            ind2_651 = "6"
        else:
            ind2_651 = "7"

        field_651_open = f"""<datafield tag="651" ind1=" " ind2="{ind2_651}">"""

        # Subfield A
        a_651 = f"""<subfield code="a">{geo_clean}</subfield>"""

        # Subfield F
        if ind2_651 == "7":
            f_651 = f"""<subfield code="2">{authority}</subfield>""" if authority is not None else ""
        else:
            f_651 = ""

    # PRINT 651 FIELD
    if authfile_no:
        field_651_str_nb = authority_651_str + "</datafield>"
        field_651_xml = etree.fromstring(field_651_str_nb)
        field_651_str = etree.tostring(field_651_xml, pretty_print=True, encoding="unicode")
    else:
        # (This portion of code was troubleshot using Claud Opus 4.5)
        field_651_str_nb = field_651_open + a_651 + f_651 + "</datafield>"
        field_651_xml = etree.fromstring(field_651_str_nb)
        field_651_str = etree.tostring(field_651_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.6)
    field_651_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_651_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_651 = []
    if timeout_error:
        result_651.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_651.append(field_651_xml)

    # print(field_651_str)
    return result_651


def ead2marc_655(gf):
    '''Creates 655 (genre/form) with authority validation and subdivision classification'''

    gf_clean = gf.xpath("string()").strip()
    gf_clean = html.escape(gf_clean)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    gf_clean = " ".join(gf_clean.split())
    timeout_error = False
    timeout_authfile_no = None

    authority_raw = gf.get("source").lower()
    if authority_raw == "lcac":
        authority = "cyac"
    else:
        authority = authority_raw

    # Split heading into main heading and subdivisions
    # (This portion of code was generated utilizing Claude Opus 4.6)
    parts = gf_clean.split(" -- ")
    main_heading = parts[0]
    subdivisions = parts[1:] if len(parts) > 1 else []

    # Pull identifier if source is lcgft or lcsh
    authfile_no = None
    if gf.get("source").lower() in {"lcgft"}:
        suggest_url = f"""https://id.loc.gov/authorities/genreForms/suggest2?q={main_heading}"""
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == main_heading:
                authfile_no = hit["token"]
                break
    elif gf.get("source").lower() in {"lcsh"}:
        suggest_url = f"""https://id.loc.gov/authorities/subjects/suggest2?q={main_heading}"""
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == main_heading:
                authfile_no = hit["token"]
                break

    # Pull authority file using identifier
    if gf.get("source").lower() in {"lcgft", "lcsh"} and authfile_no:
        # Get LC Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_155_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='155']")
            authority_155_raw = authority_155_list[0]
            # Clean authority_155_raw
            authority_155_str = etree.tostring(authority_155_raw, pretty_print=True, encoding="unicode")
            authority_155_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_155_str)
            authority_155_str_list = authority_155_str.split("\n")
            authority_155_str_list_stripped = [str.strip() for str in authority_155_str_list]
            authority_155_str = "".join(authority_155_str_list_stripped)
            authority_155_str = re.sub(r'</datafield>', '', authority_155_str).strip()
            authority_655_str = authority_155_str.replace('tag="155"', 'tag="655"')

            # Classify and append subdivisions
            # (This portion of code was generated utilizing Claude Opus 4.6)
            subdiv_subfields = ""
            for subdiv in subdivisions:
                subdiv_code = "x"  # default to general
                subdiv_suggest_url = f"""https://id.loc.gov/authorities/subjects/suggest2?q={subdiv}"""
                subdiv_response = loc_get(subdiv_suggest_url)
                try:
                    subdiv_data = subdiv_response.json()
                except requests.exceptions.JSONDecodeError:
                    subdiv_data = {}
                for subdiv_hit in subdiv_data.get("hits", []):
                    if subdiv_hit["aLabel"] == subdiv:
                        subdiv_token = subdiv_hit["token"]
                        subdiv_auth_url = f"""https://lccn.loc.gov/{subdiv_token}/marcxml"""
                        subdiv_auth_xml = loc_get(subdiv_auth_url, timeout=10).content
                        subdiv_auth_root = etree.fromstring(subdiv_auth_xml)
                        if subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='185']"):
                            subdiv_code = "v"  # form subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='181']"):
                            subdiv_code = "z"  # geographic subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='182']"):
                            subdiv_code = "y"  # chronological subdivision
                        elif subdiv_auth_root.xpath(".//*[local-name()='datafield' and @tag='180']"):
                            subdiv_code = "x"  # general subdivision
                        break
                subdiv_subfields += f"""<subfield code="{subdiv_code}">{subdiv}</subfield>"""
            authority_655_str += subdiv_subfields
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authfile_no = None
            timeout_error = True
            timeout_authfile_no = authfile_no

    if not authfile_no:
        # Compile field manually if no authority match
        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2
        if authority == "lcsh":
            ind2_655 = "0"
        elif authority == "cyac":
            ind2_655 = "1"
        elif authority == "mesh":
            ind2_655 = "2"
        elif authority == "nal":
            ind2_655 = "3"
        elif authority == "":
            ind2_655 = "4"
        elif authority == "source not specified":
            ind2_655 = "4"
        elif authority == "cash":
            ind2_655 = "5"
        elif authority == "rvm":
            ind2_655 = "6"
        else:
            ind2_655 = "7"

        field_655_open = f"""<datafield tag="655" ind1=" " ind2="{ind2_655}">"""

        # Subfield A
        a_655 = f"""<subfield code="a">{gf_clean}</subfield>"""

        # Subfield F
        if ind2_655 == "7":
            f_655 = f"""<subfield code="2">{authority}</subfield>""" if authority is not None else ""
        else:
            f_655 = ""

    # PRINT 655 FIELD
    if authfile_no:
        field_655_str_nb = authority_655_str + "</datafield>"
        field_655_xml = etree.fromstring(field_655_str_nb)
        field_655_str = etree.tostring(field_655_xml, pretty_print=True, encoding="unicode")
    else:
        # (This portion of code was troubleshot using Claud Opus 4.5)
        field_655_str_nb = field_655_open + a_655 + f_655 + "</datafield>"
        field_655_xml = etree.fromstring(field_655_str_nb)
        field_655_str = etree.tostring(field_655_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.6)
    field_655_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_655_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_655 = []
    if timeout_error:
        result_655.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_655.append(field_655_xml)

    # print(field_655_str)
    return result_655
    # NOTE: Indicators beyond $a and $f are not currently supported


def ead2marc_656(occ):
    '''Creates 656 (occupation) from occupation term element'''

    occ_clean = occ.xpath("string()").strip()
    occ_clean = html.escape(occ_clean)

    authority = occ.get("source")

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (7)

    field_656_open = """<datafield tag="656" ind1=" " ind2="7">"""

    # Subfield A
    a_656 = f"""<subfield code="a">{occ_clean}</subfield>"""

    # Subfield F
    f_656 = f"""<subfield code="2">{authority}</subfield>""" if authority is not None else ""

    # PRINT 656 FIELD
    # (This portion of code was troubleshot using Claud Opus 4.5)
    field_656_str_nb = field_656_open + a_656 + f_656 + "</datafield>"
    field_656_xml = etree.fromstring(field_656_str_nb)
    # field_656_str = etree.tostring(field_656_xml, pretty_print=True, encoding="unicode")

    # print(field_656_str)
    return field_656_xml

    # NOTE: Indicators beyond $a and $f are not currently supported


def ead2marc_657(funct):
    '''Creates 657 (function) from function term element'''

    funct_clean = funct.xpath("string()").strip()
    funct_clean = html.escape(funct_clean)

    authority = funct.get("source")

    # INDICATORS
    # Indicator 1 is constant (blank)
    # Indicator 2 is constant (7)

    field_657_open = """<datafield tag="657" ind1=" " ind2="7">"""

    # Subfield A
    a_657 = f"""<subfield code="a">{funct_clean}</subfield>"""

    # Subfield F
    f_657 = f"""<subfield code="2">{authority}</subfield>""" if authority is not None else ""

    # PRINT 657 FIELD
    # (This portion of code was troubleshot using Claud Opus 4.5)
    field_657_str_nb = field_657_open + a_657 + f_657 + "</datafield>"
    field_657_xml = etree.fromstring(field_657_str_nb)
    # field_657_str = etree.tostring(field_657_xml, pretty_print=True, encoding="unicode")

    # print(field_657_str)
    return field_657_xml

    # NOTE: Indicators beyond $a and $f are not currently supported


def ead2marc_600_610_630_65x(names_list):
    '''Routes subject entries to 600, 610, 630, or 65x functions based on element type'''

    # Set function-wide variables
    if len(names_list) > 0:
        field_600_610_630_65x_xml_list = []
        for target_subj_ead in names_list:
            # Extract actual name element and send to 600, 610, or 630 function
            if target_subj_ead in subj_persnames_list:
                field_600_xml = ead2marc_600(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_600_xml)
            elif target_subj_ead in subj_famnames_list:
                field_600_xml = ead2marc_600(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_600_xml)
            elif target_subj_ead in subj_corpnames_list:
                field_610_xml = ead2marc_610(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_610_xml)
            elif target_subj_ead in subj_titles_list:
                field_630_xml = ead2marc_630(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_630_xml)
            elif target_subj_ead in subj_topic_list:
                field_650_xml = ead2marc_650(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_650_xml)
            elif target_subj_ead in subj_geognames_list:
                field_651_xml = ead2marc_651(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_651_xml)
            elif target_subj_ead in subj_gft_list:
                field_655_xml = ead2marc_655(target_subj_ead)
                field_600_610_630_65x_xml_list.extend(field_655_xml)
            elif target_subj_ead in subj_occ_list:
                field_656_xml = ead2marc_656(target_subj_ead)
                field_600_610_630_65x_xml_list.append(field_656_xml)
            elif target_subj_ead in subj_function_list:
                field_657_xml = ead2marc_657(target_subj_ead)
                field_600_610_630_65x_xml_list.append(field_657_xml)
        return field_600_610_630_65x_xml_list


def ead2marc_690(raw_root):
    '''Creates 690 (local subject) from title with archival terms removed'''

    arch_terms_sp = ["collection ",
                     "Collection ",
                     "papers ",
                     "Papers",
                     "records ",
                     "Records ",
                     "manuscripts ",
                     "Manuscripts ",
                     "mss. ",
                     "Mss. "]
    lsh_fetch = raw_root.xpath(".//*[local-name()='titleproper']")
    if len(lsh_fetch) > 0:
        field_690_xml_list = []
        lsh = lsh_fetch[0]
        lsh_all = lsh.xpath("string()").strip()
        lsh_list = lsh_all.split(", ")
        lsh_cleanish = ", ".join(lsh_list[:-1])
        not_cleaned = True
        for arch_term in arch_terms_sp:
            if arch_term in lsh_cleanish:
                not_cleaned = False
                lsh_cleanish_list = re.split(arch_term, lsh_cleanish)
                lsh_clean_part = lsh_cleanish_list[0]
                lsh_clean = lsh_clean_part + arch_term.strip() + "."
        if not_cleaned:
            if not lsh_cleanish.endswith("."):
                lsh_clean = lsh_cleanish + "."
            else:
                lsh_clean = lsh_cleanish
        lsh_clean = html.escape(lsh_clean)

        # INDICATORS
        # Indicator 1 is constant (blank)
        # Indicator 2 is constant (7)

        field_690_open = """<datafield tag="690" ind1=" " ind2="7">"""

        # Subfield A
        a_690 = f"""<subfield code="a">{lsh_clean}</subfield>"""

        # Subfield 2
        sf2_690 = """<subfield code="2">local</subfield>"""

        # Subfield 5
        sf5_690 = """<subfield code="5">InU-Mu</subfield>"""

        # PRINT 690 FIELD
        # (This portion of code was troubleshot using Claud Opus 4.5)
        field_690_str_nb = field_690_open + a_690 + sf2_690 + sf5_690 + "</datafield>"
        field_690_xml = etree.fromstring(field_690_str_nb)
        # field_690_str = etree.tostring(field_690_xml, pretty_print=True, encoding="unicode")
        # print(field_690_str)
        field_690_xml_list.append(field_690_xml)

        return field_690_xml_list


def ead2marc_700(name):
    a_alpha = []
    d_num = []
    authority_700_str = None
    '''Creates 700 (added entry personal name) with authority validation'''

    # Check if name is associated with an authority file
    # (This portion of code partially revised utilizing ChatGPT 5.2)
    # Pull identifier
    # (This portion of code was generated utilizing Claude Opus 4.6)
    timeout_error = False
    timeout_authfile_no = None
    if name.get("source") in {"lcnaf", "naf", "viaf"} and name.get("identifier") and not name.get("identifier", "").startswith("aspace_"):
        authfile_no = name.get("identifier")
    elif name.get("source") in {"lcnaf", "naf"}:
        name_str = name.xpath("string()").strip()
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={name_str}"""
        # (This portion of code was generated utilizing Claude Opus 4.5)
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        authfile_no = None
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == name_str:
                authfile_no = hit["token"]
                break
    elif name.get("source") == "viaf":
        # (This portion of code was generated utilizing Claude Opus 4.5)
        name_str = name.xpath("string()").strip()
        viaf_search_url = f"""https://viaf.org/viaf/search?query=local.personalNames+all+%22{name_str}%22&sortKeys=holdingscount&maximumRecords=5"""
        viaf_headers = {'Accept': 'application/xml'}
        viaf_search_response = requests.get(viaf_search_url, headers=viaf_headers)
        viaf_search_root = etree.fromstring(viaf_search_response.content)
        authfile_no = None
        records = viaf_search_root.xpath('//*[local-name()="record"]')
        for rec in records:
            headings = rec.xpath('.//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_id = rec.xpath('.//*[local-name()="viafID"]')
            if headings and viaf_id and headings[0].text == name_str:
                authfile_no = viaf_id[0].text
                break
    else:
        authfile_no = None

    # Pull authority file using identifier
    if name.get("source") in {"lcnaf", "naf"} and authfile_no:
        # Get Library of Congress Name Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority = "lcnaf"
            authfile_no = name.get("identifier")
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_700_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='100']")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            # Fallback to tag 110 if tag 100 not found (handles mismatched EAD name types)
            if not authority_700_list:
                authority_700_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
            authority_700_raw = authority_700_list[0]
            # Clean authority_700_raw
            authority_700_str = etree.tostring(authority_700_raw, pretty_print=True, encoding="unicode")
            authority_700_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_700_str)
            authority_700_str_list = authority_700_str.split("\n")
            authority_700_str_list_stripped = [str.strip() for str in authority_700_str_list]
            authority_700_str = "".join(authority_700_str_list_stripped)
            authority_700_str = re.sub(r'</datafield>', '', authority_700_str).strip()
            # Change tag from 100 to 700
            # (This portion of code was generated utilizing Claude Opus 4.5)
            authority_700_str = authority_700_str.replace('tag="100"', 'tag="700"')
            # (This portion of code was generated utilizing Claude Opus 4.6)
            authority_700_str = authority_700_str.replace('tag="110"', 'tag="710"')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authority = None
            timeout_error = True
            timeout_authfile_no = authfile_no
    elif name.get("source") == "viaf" and authfile_no:
        # Get VIAF cluster XML and extract 700 field data
        # (This portion of code was generated utilizing Claude Opus 4.5)
        authority = "viaf"
        viaf_headers = {'Accept': 'application/xml'}
        viaf_url = f"https://viaf.org/viaf/{authfile_no}"
        viaf_response = requests.get(viaf_url, headers=viaf_headers)
        viaf_root = etree.fromstring(viaf_response.content)
        # Check if VIAF cluster has linked LCNAF -- if so, use LCNAF
        # (This portion of code was generated utilizing Claude Opus 4.5)
        lc_sources = viaf_root.xpath('//*[local-name()="source" and starts-with(text(), "LC|")]')
        if lc_sources:
            # VIAF has LC link -- fetch from LCNAF
            # (This portion of code was generated utilizing Claude Opus 4.6)
            try:
                lc_id = lc_sources[0].text.split('|')[1]
                authority_url = f"https://lccn.loc.gov/{lc_id}/marcxml"
                authority_xml = loc_get(authority_url, timeout=10).content
                authority_root = etree.fromstring(authority_xml)
                authority_700_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='100']")
                # (This portion of code was generated utilizing Claude Opus 4.6)
                # Fallback to tag 110 if tag 100 not found (handles mismatched EAD name types)
                if not authority_700_list:
                    authority_700_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
                authority_700_raw = authority_700_list[0]
                authority_700_str = etree.tostring(authority_700_raw, pretty_print=True, encoding="unicode")
                authority_700_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_700_str)
                authority_700_str_list = authority_700_str.split("\n")
                authority_700_str_list_stripped = [str.strip() for str in authority_700_str_list]
                authority_700_str = "".join(authority_700_str_list_stripped)
                authority_700_str = re.sub(r'</datafield>', '', authority_700_str).strip()
                # Change tag from 100 to 700
                authority_700_str = authority_700_str.replace('tag="100"', 'tag="700"')
                # (This portion of code was generated utilizing Claude Opus 4.6)
                authority_700_str = authority_700_str.replace('tag="110"', 'tag="710"')
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
                print(f"WARNING: Connection to lccn.loc.gov timed out for {lc_id}. Constructing field manually.")
                authority = None
                timeout_error = True
                timeout_authfile_no = lc_id
        else:
            # No LC source -- parse VIAF cluster directly
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_headings = viaf_root.xpath('//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_main_heading = viaf_headings[0].text if viaf_headings else None
            # Get normalized dates from VIAF
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_birth = viaf_root.xpath('//*[local-name()="birthDate"]')
            viaf_death = viaf_root.xpath('//*[local-name()="deathDate"]')
            viaf_birth_year = viaf_birth[0].text[:4] if viaf_birth and viaf_birth[0].text and not viaf_birth[0].text.startswith('0') else None
            viaf_death_year = viaf_death[0].text[:4] if viaf_death and viaf_death[0].text and not viaf_death[0].text.startswith('0') else None
            # Parse heading to separate name from dates
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_parts = viaf_main_heading.split(', ') if viaf_main_heading else []
            viaf_name_parts = []
            for part in viaf_parts:
                if not (any(c.isdigit() for c in part) and ('-' in part or part.endswith('-'))):
                    viaf_name_parts.append(part)
            viaf_ind1 = '1' if len(viaf_name_parts) > 1 else '0'
            viaf_a_content = ', '.join(viaf_name_parts)
            # Determine date subfield
            # (This portion of code was generated utilizing Claude Opus 4.5)
            if viaf_birth_year and viaf_death_year:
                viaf_d_content = f'{viaf_birth_year}-{viaf_death_year}'
            elif viaf_birth_year:
                viaf_d_content = f'{viaf_birth_year}-'
            else:
                viaf_d_content = None
            # Build authority_700_str for VIAF-direct
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_subfields = f'<subfield code="a">{viaf_a_content}</subfield>'
            if viaf_d_content:
                viaf_subfields += f'<subfield code="d">{viaf_d_content}</subfield>'
            authority_700_str = f'<datafield tag="700" ind1="{viaf_ind1}" ind2=" ">{viaf_subfields}'
    else:
        authority = None

    # If authority fetch failed, reset authority so manual construction runs
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_700_str is None:
        authority = None

    # INDICATORS
    # Indicator 1
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority not in ["lcnaf", "viaf"]:
        a_content = name.xpath("string()").strip()
        a_split = a_content.split(", ")
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if name.tag.endswith('famname'):
            ind1_700 = "3"
        else:
            for item in a_split:
                if re.search(r'\b\d{4}\b', item):
                    d_num.append(item)
                else:
                    a_alpha.append(item)
            if len(a_alpha) > 1:
                ind1_700 = "1"
            else:
                ind1_700 = "0"
    else:
        ind1_700 = ""

    # Indicator 2 is constant (blank)

    # Subfield E
    if 'relator' in name.attrib:
        aspace_relator = name.attrib["relator"].lower()
        if aspace_relator in marc_rda_relators.keys():
            e_content = marc_rda_relators[aspace_relator]
            e_700 = f"""<subfield code="e">{e_content}</subfield>"""
        else:
            e_700 = ""
    else:
        e_700 = ""

    # Subfield D
    if d_num:
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if authority not in ["lcnaf", "viaf"] and not name.tag.endswith('famname'):
            d_content = d_num[0]
            d_content = d_content.rstrip(".")
            # (This portion of code was generated utilizing Claude Opus 4.6)
            if e_700:
                d_content += ","
            d_700 = f"""<subfield code="d">{d_content}</subfield>"""
    else:
        d_700 = ""

    # Subfield A
    if authority not in ["lcnaf", "viaf"]:
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if name.tag.endswith('famname'):
            a_content = a_content
        else:
            a_content = ", ".join(a_alpha)
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if d_700:
            a_content += ","
        a_700 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 700 FIELD
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_700_str is not None:
        field_700_str_nb = authority_700_str + e_700 + "</datafield>"
        field_700_xml = etree.fromstring(field_700_str_nb)
        field_700_str = etree.tostring(field_700_xml, pretty_print=True, encoding="unicode")
    else:
        field_700_open = f"""<datafield tag="700" ind1="{ind1_700}" ind2=" ">"""
        field_700_str_nb = field_700_open + a_700 + d_700 + e_700 + "</datafield>"
        field_700_xml = etree.fromstring(field_700_str_nb)
        field_700_str = etree.tostring(field_700_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.5)
    field_700_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_700_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_700 = []
    if timeout_error:
        result_700.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_700.append(field_700_xml)

    # print(field_700_str)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    return result_700


def ead2marc_710(name):
    authority_710_str = None
    '''Creates 710 (added entry corporate name) with authority validation'''

    # Check if main name is associated with an authority file
    # (This portion of code partially revised utilizing ChatGPT 5.2)
    # Pull identifier
    # (This portion of code was generated utilizing Claude Opus 4.6)
    timeout_error = False
    timeout_authfile_no = None
    if name.get("source") in {"lcnaf", "naf", "viaf"} and name.get("identifier") and not name.get("identifier", "").startswith("aspace_"):
        authfile_no = name.get("identifier")
    elif name.get("source") in {"lcnaf", "naf"}:
        name_str = name.xpath("string()").strip()
        suggest_url = f"""https://id.loc.gov/authorities/names/suggest2?q={name_str}"""
        # (This portion of code was generated utilizing Claude Opus 4.5)
        suggest_response = loc_get(suggest_url)
        try:
            suggest_data = suggest_response.json()
        except requests.exceptions.JSONDecodeError:
            suggest_data = {}
        authfile_no = None
        for hit in suggest_data.get("hits", []):
            if hit["aLabel"] == name_str:
                authfile_no = hit["token"]
                break
    elif name.get("source") == "viaf":
        # (This portion of code was generated utilizing Claude Opus 4.5)
        name_str = name.xpath("string()").strip()
        viaf_search_url = f"""https://viaf.org/viaf/search?query=local.corporateNames+all+%22{name_str}%22&sortKeys=holdingscount&maximumRecords=5"""
        viaf_headers = {'Accept': 'application/xml'}
        viaf_search_response = requests.get(viaf_search_url, headers=viaf_headers)
        viaf_search_root = etree.fromstring(viaf_search_response.content)
        authfile_no = None
        records = viaf_search_root.xpath('//*[local-name()="record"]')
        for rec in records:
            headings = rec.xpath('.//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_id = rec.xpath('.//*[local-name()="viafID"]')
            if headings and viaf_id and headings[0].text == name_str:
                authfile_no = viaf_id[0].text
                break
    else:
        authfile_no = None

    # Pull authority file using identifier
    if name.get("source") in {"lcnaf", "naf"} and authfile_no:
        # Get Library of Congress Name Authority MARC/XML and clean
        # (This portion of code was generated utilizing Claude Opus 4.6)
        try:
            authority = "lcnaf"
            authority_url = f"""https://lccn.loc.gov/{authfile_no}/marcxml"""
            authority_xml = loc_get(authority_url, timeout=10).content
            authority_root = etree.fromstring(authority_xml)
            authority_710_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
            authority_710_raw = authority_710_list[0]
            # Clean authority_710_raw
            authority_710_str = etree.tostring(authority_710_raw, pretty_print=True, encoding="unicode")
            authority_710_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_710_str)
            authority_710_str_list = authority_710_str.split("\n")
            authority_710_str_list_stripped = [str.strip() for str in authority_710_str_list]
            authority_710_str = "".join(authority_710_str_list_stripped)
            authority_710_str = re.sub(r'</datafield>', '', authority_710_str).strip()
            # Change tag from 110 to 710
            # (This portion of code was generated utilizing Claude Opus 4.5)
            authority_710_str = authority_710_str.replace('tag="110"', 'tag="710"')
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
            print(f"WARNING: Connection to lccn.loc.gov timed out for {authfile_no}. Constructing field manually.")
            authority = None
            timeout_error = True
            timeout_authfile_no = authfile_no
    elif name.get("source") == "viaf" and authfile_no:
        # Get VIAF cluster XML and extract 710 field data
        # (This portion of code was generated utilizing Claude Opus 4.5)
        authority = "viaf"
        viaf_headers = {'Accept': 'application/xml'}
        viaf_url = f"https://viaf.org/viaf/{authfile_no}"
        viaf_response = requests.get(viaf_url, headers=viaf_headers)
        viaf_root = etree.fromstring(viaf_response.content)
        # Check if VIAF cluster has linked LCNAF -- if so, use LCNAF
        # (This portion of code was generated utilizing Claude Opus 4.5)
        lc_sources = viaf_root.xpath('//*[local-name()="source" and starts-with(text(), "LC|")]')
        if lc_sources:
            # VIAF has LC link -- fetch from LCNAF
            # (This portion of code was generated utilizing Claude Opus 4.6)
            try:
                lc_id = lc_sources[0].text.split('|')[1]
                authority_url = f"https://lccn.loc.gov/{lc_id}/marcxml"
                authority_xml = loc_get(authority_url, timeout=10).content
                authority_root = etree.fromstring(authority_xml)
                authority_710_list = authority_root.xpath(".//*[local-name()='datafield' and @tag='110']")
                authority_710_raw = authority_710_list[0]
                authority_710_str = etree.tostring(authority_710_raw, pretty_print=True, encoding="unicode")
                authority_710_str = re.sub(r'\s+xmlns(:zs)?="[^"]+"', '', authority_710_str)
                authority_710_str_list = authority_710_str.split("\n")
                authority_710_str_list_stripped = [str.strip() for str in authority_710_str_list]
                authority_710_str = "".join(authority_710_str_list_stripped)
                authority_710_str = re.sub(r'</datafield>', '', authority_710_str).strip()
                # Change tag from 110 to 710
                # (This portion of code was generated utilizing Claude Opus 4.5)
                authority_710_str = authority_710_str.replace('tag="110"', 'tag="710"')
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, etree.XMLSyntaxError, IndexError):
                print(f"WARNING: Connection to lccn.loc.gov timed out for {lc_id}. Constructing field manually.")
                authority = None
                timeout_error = True
                timeout_authfile_no = lc_id
        else:
            # No LC source -- parse VIAF cluster directly
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_headings = viaf_root.xpath('//*[local-name()="mainHeadings"]/*[local-name()="data"]/*[local-name()="text"]')
            viaf_main_heading = viaf_headings[0].text if viaf_headings else None
            # Build authority_710_str for VIAF-direct
            # (This portion of code was generated utilizing Claude Opus 4.5)
            viaf_subfields = f'<subfield code="a">{viaf_main_heading}</subfield>'
            authority_710_str = f'<datafield tag="710" ind1="2" ind2=" ">{viaf_subfields}'
    else:
        authority = None

    # If authority fetch failed, reset authority so manual construction runs
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_710_str is None:
        authority = None

    # INDICATORS
    # Indicator 1
    if authority not in ["lcnaf", "viaf"]:
        ind1_710 = "2"

    # Indicator 2 is constant (blank)

    # SUBFIELDS
    # Subfield E
    if 'relator' in name.attrib:
        aspace_relator = name.attrib["relator"].lower()
        if aspace_relator in marc_rda_relators.keys():
            e_content = marc_rda_relators[aspace_relator]
            e_710 = f"""<subfield code="e">{e_content}</subfield>"""
        else:
            e_710 = ""
    else:
        e_710 = ""

    # Subfield A
    if authority not in ["lcnaf", "viaf"]:
        a_content = name.xpath("string()").strip()
        # (This portion of code was generated utilizing Claude Opus 4.6)
        if e_710:
            a_content += ","
        a_710 = f"""<subfield code="a">{a_content}</subfield>"""

    # PRINT 710 FIELD
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if authority in ("lcnaf", "viaf") and authority_710_str is not None:
        field_710_str_nb = authority_710_str + e_710 + "</datafield>"
        field_710_xml = etree.fromstring(field_710_str_nb)
        field_710_str = etree.tostring(field_710_xml, pretty_print=True, encoding="unicode")
    else:
        field_710_open = f"""<datafield tag="710" ind1="{ind1_710}" ind2=" ">"""
        field_710_str_nb = field_710_open + a_710 + e_710 + "</datafield>"
        field_710_xml = etree.fromstring(field_710_str_nb)
        field_710_str = etree.tostring(field_710_xml, pretty_print=True, encoding="unicode")

    # Reorder attributes to put tag first
    # (This portion of code was generated utilizing Claude Opus 4.5)
    field_710_str = re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', r'<datafield tag="\3" ind1="\1" ind2="\2">', field_710_str)

    # Add timeout comment if applicable
    # (This portion of code was generated utilizing Claude Opus 4.6)
    result_710 = []
    if timeout_error:
        result_710.append(etree.Comment(f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "))
    result_710.append(field_710_xml)

    # print(field_710_str)
    return result_710

    # NOTE:
        # Currently no subfields beyond subfields A and E are supported for non-authority 110s. All content except relators will be placed in subfield A.
        # ind1 0 (inverted name) and 1 (jurisdiction name) are not supported for non-authority 110s


def ead2marc_700_710(names_list):
    '''Routes added entry names to ead2marc_700 or ead2marc_710 based on name type'''

    # Set function-wide variables
    other_names_ead = names_list[1:]

    if len(other_names_ead) > 0:
        field_700_710_xml_list = []
        for target_name_ead in other_names_ead:
            # Extract actual name element and send to 700 or 710 functions
            # (This portion of code was generated utilizing Claude Opus 4.5)
            if target_name_ead in creator_persnames_list:
                name_element = target_name_ead.xpath(".//*[local-name()='persname']")[0]
                field_700_xml = ead2marc_700(name_element)
                field_700_710_xml_list.extend(field_700_xml)
            elif target_name_ead in creator_famnames_list:
                name_element = target_name_ead.xpath(".//*[local-name()='famname']")[0]
                field_700_xml = ead2marc_700(name_element)
                field_700_710_xml_list.extend(field_700_xml)
            elif target_name_ead in creator_corpnames_list:
                name_element = target_name_ead.xpath(".//*[local-name()='corpname']")[0]
                field_710_xml = ead2marc_710(name_element)
                field_700_710_xml_list.extend(field_710_xml)

        return field_700_710_xml_list


def ead2marc_856(raw):
    '''Creates 856 (electronic location) with link to ArchivesSpace catalog record'''

    field_856_xml_list = []
    if vaid_clean:

        # INDICATORS
        # Indicator 1 is constant (4)
        # Indicator 2 is constant (2)

        # SUBFIELDS

        # Subfield U
        cid_fetch = raw.get("id", "")
        if cid_fetch:
            cid_clean = html.escape(cid_fetch)
        else:
            cid_clean = ""

        faid_uri = f"""https://archives.iu.edu/catalog/{vaid_clean}{cid_clean}"""
        u_856 = f"""<subfield code="u">{faid_uri} </subfield>"""

        # Subfield 3
        s3_856 = """<subfield code="3">Finding aid</subfield>"""

        # PRINT 856 FIELD
        field_856_str_nb = """<datafield tag="856" ind1="4" ind2="2">""" + s3_856 + u_856 + "</datafield>"
        field_856_xml = etree.fromstring(field_856_str_nb)
        field_856_xml_list.append(field_856_xml)
        # field_856_str = etree.tostring(field_856_xml, pretty_print=True, encoding="unicode")

        # print(field_856_str)

    return field_856_xml_list


def ead2marc_leader(raw):
    '''Builds leader with position 06 based on carrier type (336) and 07 based on hierarchy level'''
    leader_xml_list = []
    ctype_code_p6_dict = {
        "crd": "e",
        "cri": "e",
        "crm": "e",
        "crt": "e",
        "crn": "e",
        "crf": "e",
        "cod": "m",
        "cop": "m",
        "ntv": "a",
        "ntm": "c",
        "prm": "j",
        "snd": "i",
        "spw": "i",
        "sti": "k",
        "tci": "k",
        "tcm": "c",
        "tcn": "a",
        "tct": "a",
        "tcf": "r",
        "txt": "a",
        "tdf": "r",
        "tdm": "g",
        "tdi": "g",
        "xxx": "p",
        "zzz": "p"
    }
    # Priority ranking for p6 codes: higher number = more specific, overrides lower
    # (This portion of code was generated utilizing Claude Opus 4.6)
    p6_priority = {
        "a": 0,  # text (most generic/default)
        "p": 1,  # mixed materials
        "m": 2,  # computer file
        "e": 3,  # cartographic
        "k": 4,  # 2D graphic
        "r": 5,  # 3D artifact
        "g": 6,  # projected medium / moving image
        "i": 7,  # nonmusical sound recording
        "j": 8,  # musical sound recording
        "c": 9,  # notated music (score)
    }
    
    # Character position 7
    level = c0_raw.attrib['level']
    if level == "item":
        p7 = "m"
    else:
        p7 = "c"

    # Character position 6 (based on 7 and carrier type from field 336)
    if p7 == "m":
        field_336_xml_list, ctype_code_list = ead2marc_336(raw)
        p6_code_list = []
        for ctype_code in ctype_code_list:
            p6_code = ctype_code_p6_dict[ctype_code]
            p6_code_list.append(p6_code)
        if p6_code_list:
            # (This portion of code was generated utilizing Claude Opus 4.6)
            # Select p6 code with highest priority (most specific type wins)
            p6 = max(p6_code_list, key=lambda c: p6_priority.get(c, 0))
        else:
            p6 = "p"
    elif p7 == "c":
        p6 = "p"

    # Character positions 0-5, 8-23
    p0to4 = "00000"
    p5 = "n"
    
    p8 = " "
    p9 = "a"
    p10 = "2"
    p11 = "2"
    p12to16 = "00000"
    p17 = "7"
    p18 = "i"
    p19 = " "
    p20to23 = "4500"

    # Print leader
    leader_content = f"{p0to4}{p5}{p6}{p7}{p8}{p9}{p10}{p11}{p12to16}{p17}{p18}{p19}{p20to23}"
    leader_str_nb = f"""<leader>{leader_content}</leader>"""
    leader_xml = etree.fromstring(leader_str_nb)
    leader_xml_list.append(leader_xml)
    # leader_str = etree.tostring(leader_xml, pretty_print=True, encoding="unicode")

    # print(leader_str)
    return leader_xml_list, p6, p7


def ead2marc_008(raw):
    leader_xml_list, leader_p6, leader_p7 = ead2marc_leader(raw)
    leader_p6_to_format_dict = {
        "a": "bks",
        "t": "bks",
        "s": "cnr",
        "m": "com",
        "e": "map",
        "f": "map",
        "p": "mix",
        "i": "rec",
        "j": "rec",
        "c": "sco",
        "d": "sco",
        "g": "vis",
        "k": "vis",
        "o": "vis",
        "r": "vis",
    }
    level = c0_raw.attrib['level']
    field_008_xml_list = []
    unitdates_list = raw.xpath(".//*[starts-with(local-name(), 'unitdate')]")

    # Positions 0-5
    p0to5 = datetime.now().strftime("%y%m%d")

    # Positions 6, 7-10, and 11-14
    # TODO: Check for copyright dates, exclude copyright dates from date list if there are multiple
    if len(unitdates_list) == 0:
        p6 = "n"
        p7to10 = "uuuu"
        p11to14 = "uuuu"
    elif len(unitdates_list) == 1:
        unitdate = unitdates_list[0]
        is_daterange = unitdate.xpath(".//*[local-name()='daterange']")
        if not is_daterange and level == "item":
            datesingle_raw = unitdate.xpath(".//*[local-name()='datesingle']")[0]
            date_clean = datesingle_raw.attrib['standarddate']
            date_clean = html.escape(date_clean)
            p6 = "s"
            p7to10 = date_clean
            p11to14 = "    "
        else:
            fromdate_raw = unitdate.xpath(".//*[local-name()='fromdate']")[0]
            fromdate_clean = fromdate_raw.attrib['standarddate']
            fromdate_clean = html.escape(fromdate_clean)
            todate_raw = unitdate.xpath(".//*[local-name()='todate']")[0]
            p6 = "i"
            p7to10 = fromdate_clean
            if todate_raw:
                todate_clean = todate_raw.attrib['standarddate']
                todate_clean = html.escape(todate_clean)
                p11to14 = todate_clean
            else:
                p11to14 = "    "
    elif len(unitdates_list) > 1:
        date_list = []
        for unitdate in unitdates_list:
            is_daterange = unitdate.xpath(".//*[local-name()='daterange']")
            if is_daterange:
                fromdate_raw = unitdate.xpath(".//*[local-name()='fromdate']")[0]
                fromdate_clean = fromdate_raw.attrib['standarddate']
                fromdate_clean = html.escape(fromdate_clean)
                todate_raw = unitdate.xpath(".//*[local-name()='todate']")[0]
                todate_clean = todate_raw.attrib['standarddate']
                todate_clean = html.escape(todate_clean)
                date_list.append(fromdate_clean)
                date_list.append(todate_clean)
            else:
                datesingle_raw = unitdate.xpath(".//*[local-name()='datesingle']")[0]
                date_clean = datesingle_raw.attrib['standarddate']
                date_clean = html.escape(date_clean)
                date_list.append(date_clean)
        unq_dates = len(set(date_list))
        if unq_dates == 1:
            unitdate = unitdates_list[0]
            is_daterange = unitdate.xpath(".//*[local-name()='daterange']")
            if not is_daterange and level == "item":
                datesingle_raw = unitdate.xpath(".//*[local-name()='datesingle']")[0]
                date_clean = datesingle_raw.attrib['standarddate']
                date_clean = html.escape(date_clean)
                p6 = "s"
                p7to10 = date_clean
                p11to14 = "    "
            else:
                fromdate_raw = unitdate.xpath(".//*[local-name()='fromdate']")[0]
                fromdate_clean = fromdate_raw.attrib['standarddate']
                fromdate_clean = html.escape(fromdate_clean)
                todate_raw = unitdate.xpath(".//*[local-name()='todate']")[0]
                todate_clean = todate_raw.attrib['standarddate']
                todate_clean = html.escape(todate_clean)
                p6 = "i"
                p7to10 = fromdate_clean
                p11to14 = todate_clean
        else:
            p6 = "i"
            p7to10 = min(date_list)
            p11to14 = max(date_list)

    # Positions 15-17
    # NOTE: country of publication (p15to17) is not currently supported. Set to static "xx ".
    p15to17 = "xx "
    
    # Positions 18-34
    # NOTE: for positions where accurate population based on EAD alone is not possible, codes are set statically to the default code, "not specified", or "unknown"
    pformat = leader_p6_to_format_dict[leader_p6]
    if pformat == "bks":
        # Positions 18-21
        ills_raw = "    "
        field_300_xml_list, consumed_physdescs = ead2marc_300(raw)
        field_300_xml = field_300_xml_list[0]
        field_300_str = etree.tostring(field_300_xml, pretty_print=True, encoding="unicode")
        ills_keyword_dict = {
            "illumination": "p",
            "photograph": "o",
            "audiotape reel": "m",
            "audiocassette": "m",
            "audio roll": "m",
            "audio disc": "m",
            "audio cylinder": "m",
            "audio cartridge": "m",
            "phonowire": "m",
            "phonodisc": "m",
            "sample": "l",
            "form": "k",
            "genealogicial table": "j",
            "coats of arms": "i",
            "coat of arm": "i",
            "facsimile": "h",
            "music": "g",
            "plate": "f",
            "plan": "e",
            "chart": "d",
            "portrait": "c",
            "map": "b",
            "illustration": "a",
        }
        for ills_keyword in ills_keyword_dict.keys():
            if ills_keyword in field_300_str:
                ills_raw = ills_keyword_dict[ills_keyword] + ills_raw
                #TODO: Alphabetize by code before slicing
            p18to21 = ills_raw[:5]
        # Position 22
        p22 = " "
        # Position 23
        p23 = " "
        # Positions 24-27
        p24to27 = "    "
        # Position 28
        p28 = " "
        # Position 29
        p29 = "0"
        # Position 30
        p30 = "0"
        # Position 31
        p31 = "0"
        # Position 32
        p32 = " "
        # Position 33
        p33 = "0"
        # Position 34
        p34 = " "
        # Construct positions 18-34
        p18to34 = f"{p18to21}{p22}{p23}{p24to27}{p28}{p29}{p30}{p31}{p32}{p33}{p34}"
    elif pformat == "cnr":
        # Position 18
        p18 = "u"
        # Position 19
        p19 = "u"
        # Position 20
        p20 = " "
        # Position 21
        p21 = " "
        # Position 22
        p22 = " "
        # Position 23
        p23 = " "
        # Position 24
        p24 = " "
        # Positions 25-27
        p25to27 = "    "
        # Position 28
        p28 = " "
        # Position 29
        p29 = "0"
        # Positions 30-32
        p30to32 = "   "
        # Position 33
        # Detect script of 245 title string and set p33 
        # (This portion of code was generated utilizing Claude Opus 4.6)
        field_245_xml = ead2marc_245(raw)
        title_text = ""
        for sf in field_245_xml.xpath(".//*[local-name()='subfield' and @code='a']"):
            title_text += sf.text or ""
        scripts = set()
        for char in title_text:
            if not char.isalpha():
                continue
            uname = unicodedata.name(char, "")
            if "CJK" in uname or "IDEOGRAPH" in uname:
                scripts.add("cjk")
            elif "HIRAGANA" in uname or "KATAKANA" in uname:
                scripts.add("japanese")
            elif "HANGUL" in uname:
                scripts.add("korean")
            elif "CYRILLIC" in uname:
                scripts.add("cyrillic")
            elif "ARABIC" in uname:
                scripts.add("arabic")
            elif "GREEK" in uname:
                scripts.add("greek")
            elif "HEBREW" in uname:
                scripts.add("hebrew")
            elif "THAI" in uname:
                scripts.add("thai")
            elif "DEVANAGARI" in uname:
                scripts.add("devanagari")
            elif "TAMIL" in uname:
                scripts.add("tamil")
            elif "LATIN" in uname:
                scripts.add("latin")
        non_latin = scripts - {"latin"}
        if not scripts:
            p33 = " "
        elif not non_latin:
            if all(ord(c) < 128 for c in title_text if c.isalpha()):
                p33 = "a"
            else:
                p33 = "b"
        elif non_latin == {"cyrillic"}:
            p33 = "c"
        elif non_latin <= {"japanese", "cjk"}:
            p33 = "d"
        elif non_latin == {"cjk"}:
            p33 = "e"
        elif non_latin == {"arabic"}:
            p33 = "f"
        elif non_latin == {"greek"}:
            p33 = "g"
        elif non_latin == {"hebrew"}:
            p33 = "h"
        elif non_latin == {"thai"}:
            p33 = "i"
        elif non_latin == {"devanagari"}:
            p33 = "j"
        elif non_latin <= {"korean", "cjk"}:
            p33 = "k"
        elif non_latin == {"tamil"}:
            p33 = "l"
        elif len(non_latin) > 1:
            p33 = "z"
        else:
            p33 = "u"
        # Position 34
        p34 = "0"
        # Construct positions 18-34
        p18to34 = f"{p18}{p19}{p20}{p21}{p22}{p23}{p24}{p25to27}{p28}{p29}{p30to32}{p33}{p34}"
    elif pformat == "com":
        # Positions 18-21
        p18to21 = "    "
        # Position 22
        p22 = " "
        # Position 23
        p23 = " "
        # Position 24-25
        p24to25 = "  "
        # Position 26
        p26 = "u"
        # Position 27
        p27 = " "
        # Position 28
        p28 = " "
        # Positions 29-34
        p29to34 = "      "
        # Construct positions 18-34
        p18to34 = f"{p18to21}{p22}{p23}{p24to25}{p26}{p27}{p28}{p29to34}"
    elif pformat == "map":
        # Positions 18-21
        p18to21 = "    "
        # Positions 22-23
        p22to23 = "  "
        # Position 24
        p24 = " "
        # Position 25
        p25 = "u"
        # Position 26-27
        p26to27 = "  "
        # Position 28
        p28 = " "
        # Position 29
        p29 = " "
        # Position 30
        p30 = " "
        # Position 31
        p31 = "0"
        # Position 32
        p32 = " "
        # Positions 33-34
        p33to34 = "  "
        # Construct positions 18-34
        p18to34 = f"{p18to21}{p22to23}{p24}{p25}{p26to27}{p28}{p29}{p30}{p31}{p32}{p33to34}"
    elif pformat == "mix":
        # Positions 18-22
        p18to22 = "     "
        # Position 23
        p23 = " "
        # Positions 24-34
        p24to34 = "          "
        p18to34 = f"{p18to22}{p23}{p24to34}"
    elif pformat == "rec":
        # Positions 18-19
        p18to19 = "  "
        # Position 20
        p20 = "n"
        # Position 21
        p21 = "n"
        # Position 22
        p22 = " "
        # Position 23
        p23 = " "
        # Positions 24-29
        p24to29 = "      "
        # Positions 30-31
        p30to31 = "  "
        # Position 32
        p32 = " "
        # Position 33
        p33 = "n"
        # Position 34
        p34 = " "
        # Construct positions 18-34
        p18to34 = f"{p18to19}{p20}{p21}{p22}{p23}{p24to29}{p30to31}{p32}{p33}{p34}"
    elif pformat == "sco":
        # Positions 18-19
        p18to19 = "  "
        # Position 20
        p20 = "u"
        # Position 21
        p21 = " "
        # Position 22
        p22 = " "
        # Position 23
        p23 = " "
        # Positions 24-29
        p24to29 = "      "
        # Positions 30-31
        p30to31 = "n "
        # Position 32
        p32 = " "
        # Position 33
        p33 = " "
        # Position 34
        p34 = " "
        # Construct positions 18-34
        p18to34 = f"{p18to19}{p20}{p21}{p22}{p23}{p24to29}{p30to31}{p32}{p33}{p34}"
    elif pformat == "vis":
        # Positions 18-20
        p18to20 = "---"
        # Positon 21
        p21 = " "
        # Position 22
        p22 = " "
        # Positions 23 to 27
        p23to27 = "     "
        # Position 28
        p28 = " "
        # Position 29
        p29 = " "
        # Position 30-32
        p30to32 = "   "
        # Position 33
        if leader_p6 == "g":  # Projected Medium
            p33 = "s"  # Slide
        elif leader_p6 == "k":  # 2D nonprojected graphic
            p33 = "i"  # Picture
        elif leader_p6 == "o":  # Kit
            p33 = "b"  # Kit
        elif leader_p6 == "r":  # 3D artifact or naturally occuring object
            p33 = "r"  # Realia
        else:
            p33 = "z"  # Other
        # Position 34
        p34 = "u"
        # Construct positions 18-34
        p18to34 = f"{p18to20}{p21}{p22}{p23to27}{p28}{p29}{p30to32}"
    else:
        p18to34 = "                 "

    # Positions 35-37
    field_041_xml_list, all_langcodes = ead2marc_041(raw)
    if len(all_langcodes) == 0:
        p35to37 = "und"
    elif len(all_langcodes) == 1:
        p35to37 = all_langcodes[0]
    else:
        p35to37 = "mul"
    
    # Positions 38-39
    p38 = " "
    p39 = "d"
    
    # Build field 008
    field_008_content = f"{p0to5}{p6}{p7to10}{p11to14}{p15to17}{p18to34}{p35to37}{p38}{p39}"
    field_008_nb = f"""<controlfield>{field_008_content}</controlfield>"""
    field_008_xml = etree.fromstring(field_008_nb)
    field_008_xml_list.append(field_008_xml)
    # field_008_str = etree.tostring(field_008_xml, pretty_print=True, encoding="unicode")

    # print(field_008_str)
    return field_008_xml_list


def ead2marc_rec(raw):
    '''Runs all MARC field functions in notebook order and assembles a complete record'''
    
    # Comments
    oclc_comment = oclc_check(raw)

    # 0xx fields
    field__02x_03x_05x_08x_xml_list = ead2marc_02x_03x_05x_08x(raw)
    field_040_xml_list = ead2marc_040()
    field_041_xml_list, all_langcodes = ead2marc_041(raw)
    field_049_xml_list = ead2marc_049()
    # field_099_xml_list = ead2marc_099(root, raw)

    # 1xx fields
    field_100_110_xml_list = ead2marc_100_110(creator_names_list)

    # 2xx fields
    field_245_xml_list, title_clean = ead2marc_245(raw)
    field_246_xml_list = ead2marc_246(raw)
    field_264_xml_list = ead2marc_264(raw)

    # 3xx fields
    field_300_xml_list, consumed_physdescs = ead2marc_300(raw)
    field_336_xml_list, ctype_code_list = ead2marc_336(raw)
    field_337_xml_list = ead2marc_337(raw)
    field_338_xml_list = ead2marc_338(raw)
    field_351_xml_list = ead2marc_351(raw)

    # 5xx fields
    field_500_xml_list = ead2marc_500(raw)
    field_506_xml_list = ead2marc_506(raw)
    field_520_xml_list = ead2marc_520(raw)
    field_524_xml_list = ead2marc_524(raw)
    field_535_xml_list = ead2marc_535(raw)
    field_540_xml_list = ead2marc_540(raw)
    field_541_xml_list = ead2marc_541(raw)
    field_544_xml_list = ead2marc_544(raw)
    field_545_xml_list = ead2marc_545(raw)
    field_546_xml_list = ead2marc_546(raw)
    field_555_xml_list = ead2marc_555(vaid_clean)
    field_561_xml_list = ead2marc_561(raw)
    field_583_xml_list = ead2marc_583(raw)
    field_584_xml_list = ead2marc_584(raw)

    # 6xx fields
    field_600_610_630_65x_xml_list = ead2marc_600_610_630_65x(subjs_list)
    field_690_xml_list = ead2marc_690(root)

    # 7xx fields
    field_700_710_xml_list = ead2marc_700_710(creator_names_list)

    # 8xx fields
    field_856_xml_list = ead2marc_856(raw)

    # Control fields (last -- depend on outputs from 245, 336, 041, etc.)
    leader_xml_list, leader_p6, leader_p7 = ead2marc_leader(raw)
    field_008_xml_list = ead2marc_008(raw)

    # Combine all field lists into a single record list
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    rec_list = []
    for field_list in [
        leader_xml_list, field_008_xml_list, 
        field_040_xml_list, field_041_xml_list, field_049_xml_list, field__02x_03x_05x_08x_xml_list, 
        # field_099_xml_list,
        field_100_110_xml_list,
        field_245_xml_list, field_246_xml_list, field_264_xml_list,
        field_300_xml_list, field_336_xml_list, field_337_xml_list,
        field_338_xml_list, field_351_xml_list,
        field_500_xml_list, field_506_xml_list, field_520_xml_list,
        field_524_xml_list, field_535_xml_list, field_540_xml_list,
        field_541_xml_list, field_544_xml_list, field_545_xml_list,
        field_546_xml_list, field_555_xml_list, field_561_xml_list,
        field_583_xml_list, field_584_xml_list,
        field_600_610_630_65x_xml_list, field_690_xml_list,
        field_700_710_xml_list,
        field_856_xml_list,
    ]:
        if field_list is not None:
            rec_list.extend(field_list)

    # Serialize each XML element/comment to string, then combine into record
    # (This portion of code was generated utilizing Claude Opus 4.6)
    rec_raw = "".join(etree.tostring(el, encoding="unicode") for el in rec_list)

    # Add namespace to all opening and closing tags
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    rec_raw_ns = re.sub(r'<([A-Za-z0-9_:-]+)(\s|>)', r'<marc:\1\2', rec_raw)
    rec_raw_ns = re.sub(r'</([A-Za-z0-9_:-]+)>', r'</marc:\1>', rec_raw_ns)
    ns_open = """<marc:record xmlns:marc="http://www.loc.gov/MARC21/slim">"""
    ns_close = """</marc:record>"""
    rec_xml_raw = etree.fromstring(f"{ns_open}{rec_raw_ns}{ns_close}")

    # Add oclc_check comment before first child element
    # (This portion of code was troubleshot utilizing Claude Opus 4.6)
    if oclc_comment is not None:
        rec_xml_raw.insert(0, oclc_comment)
    rec_str = etree.tostring(rec_xml_raw, pretty_print=True, encoding="unicode")
    # Reorder any remaining out-of-order attributes to tag, ind1, ind2
    # (This portion of code was generated utilizing Claude Opus 4.6)
    rec_str = re.sub(r'<(marc:datafield) ind1="(.)" ind2="(.)" tag="(\d+)">', r'<\1 tag="\4" ind1="\2" ind2="\3">', rec_str)
    rec_xml = etree.fromstring(rec_str)
    # print(rec_str)

    # Print progress message
    # (This portion of code was generated utilizing Claude Opus 4.6)
    rec_elapsed = time.time() - rec_start_time
    print(f"Record {rec_index}/{len(result)} completed in {rec_elapsed:.1f}s ({title_clean})")

    return rec_xml



# ============================================================
# MAIN
# ============================================================

# Gets xml file and sets tree and root
tree = etree.parse(r"C:\Users\yello\OneDrive\Documents\EAD2MARC\EAD2MARC_workzone\MC122_ead3.xml")
root = tree.getroot()
2
# Checks that document is EAD3
if 'http://ead3.archivists.org/schema/' in root.tag:

    # Get target <c> tag(s)
    # (This portion of code was generated utilizing Claude Opus 4.6)
    parse_type = ""
    while parse_type not in ("1", "2"):
        parse_type = input('Enter "1" to parse by ID or "2" to parse by hierarchy level: ').strip()
        if parse_type not in ("1", "2"):
            print(f'Invalid input: "{parse_type}". Please enter "1" or "2".')

    if parse_type == "1":
        target_id = input("Enter aspace id of target <c>: ").strip()
        result = root.xpath(
            "//*[(local-name()='c' or (starts-with(local-name(), 'c') and string-length(local-name())=3)) and @id=$t_id]",
            t_id=target_id
        )
    elif parse_type == "2":
        target_level = input("Enter target hierarchy level (collection, item, etc.): ").strip()
        if target_level == "collection":
            # Get archdesc but exclude <dsc> subtree (contains component-level data)
            # (This portion of code was generated utilizing Claude Opus 4.6)
            archdesc = root.xpath("//*[local-name()='archdesc']")[0]
            archdesc_copy = deepcopy(archdesc)
            for dsc in archdesc_copy.xpath(".//*[local-name()='dsc']"):
                dsc.getparent().remove(dsc)
            result = [archdesc_copy]
        else:
            result = root.xpath(
                "//*[(local-name()='c' or (starts-with(local-name(), 'c') and string-length(local-name()) <= 3)) and @level=$t_lvl]",
                t_lvl=target_level
            )
        # Apply record range filter
        # (This portion of code was generated utilizing Claude Opus 4.6)
        print(f"Found {len(result)} records.")
        rec_range = input("Enter record range (e.g. 2-5, 20-25, :-3, 5:, blank for all): ").strip()
        if rec_range:
            try:
                if '-' in rec_range and not rec_range.startswith('-') and ':' not in rec_range:
                    # Handle "2-5" style (1-indexed, inclusive)
                    parts = rec_range.split('-')
                    start = int(parts[0]) - 1
                    end = int(parts[1])
                    result = result[start:end]
                else:
                    # Handle Python slice syntax: ":-3", "5:", "2:5", etc.
                    result = eval(f"result[{rec_range}]")
            except (ValueError, IndexError, SyntaxError):
                print(f"WARNING: Could not parse range '{rec_range}'. Processing all records.")
            print(f"Processing {len(result)} records.")


    # Loop through results, set globals for each, and run ead2marc_rec
    # (This portion of code was generated utilizing Claude Opus 4.6)
    all_rec_xml_list = []
    total_start_time = time.time()
    for rec_index, c0_raw in enumerate(result, 1):
        rec_start_time = time.time()

        vaid_clean = ""
        vaid_fetch = root.xpath(".//*[local-name()='recordid']")
        if vaid_fetch:
            vaid_raw = vaid_fetch[0]
            vaid_fetch = vaid_raw.xpath(".//*[local-name()='descriptivenote']")
            vaid_clean = vaid_raw.xpath("string()").strip(".")
            vaid_head_list = vaid_raw.xpath(".//*[local-name()='head']")
            if vaid_head_list:
                vaid_head = vaid_head_list[0].xpath("string()").strip(".")
                vaid_clean = vaid_clean.replace(vaid_head, "")
            vaid_clean = html.escape(vaid_clean)

        # Set global names lists
        names_list = c0_raw.xpath(".//*[local-name()='origination']") # (Troubleshot using ChatGPT 5.2)

        all_persnames_list = []
        all_corpnames_list = []
        all_famnames_list = []

        creator_names_list = []
        creator_persnames_list = []
        creator_corpnames_list = []
        creator_famnames_list = []

        source_names_list = []
        source_persnames_list = []
        source_corpnames_list = []
        source_famnames_list = []

        for orig in names_list:
            if orig.attrib["label"].lower() == "creator":
                creator_names_list.append(orig)
            elif orig.attrib["label"].lower() == "source":
                source_names_list.append(orig)

        for orig in names_list:
            if orig.xpath(".//*[local-name()='persname']"):
                all_persnames_list.append(orig)
                if orig.attrib["label"].lower() == "creator":
                    creator_persnames_list.append(orig)
                elif orig.attrib["label"].lower() == "source":
                    source_persnames_list.append(orig)
            elif orig.xpath(".//*[local-name()='corpname']"):
                all_corpnames_list.append(orig)
                if orig.attrib["label"].lower() == "creator":
                    creator_corpnames_list.append(orig)
                elif orig.attrib["label"].lower() == "source":
                    source_corpnames_list.append(orig)
            elif orig.xpath(".//*[local-name()='famname']"):
                all_famnames_list.append(orig)
                if orig.attrib["label"].lower() == "creator":
                    creator_famnames_list.append(orig)
                elif orig.attrib["label"].lower() == "source":
                    source_famnames_list.append(orig)

        # Set global subject lists
        subjs_list = []
        subj_persnames_list = []
        subj_corpnames_list = []
        subj_famnames_list = []
        subj_titles_list = []
        subj_geognames_list = []
        subj_function_list = []
        subj_gft_list = []
        subj_occ_list = []
        subj_topic_list = []

        ca_fetch = c0_raw.xpath(".//*[local-name()='controlaccess']")
        if ca_fetch:
            ca_xml = ca_fetch[0]
            for ca_comp in ca_xml:
                subjs_list.append(ca_comp)
                if "persname" in ca_comp.tag:
                    subj_persnames_list.append(ca_comp)
                elif "corpname" in ca_comp.tag:
                    subj_corpnames_list.append(ca_comp)
                elif "famname" in ca_comp.tag:
                    subj_famnames_list.append(ca_comp)
                elif "geogname" in ca_comp.tag:
                    subj_geognames_list.append(ca_comp)
                elif "genreform" in ca_comp.tag:
                    subj_gft_list.append(ca_comp)
                elif "function" in ca_comp.tag:
                    subj_function_list.append(ca_comp)
                elif "occupation" in ca_comp.tag:
                    subj_occ_list.append(ca_comp)
                elif "subject" in ca_comp.tag:
                    subj_topic_list.append(ca_comp)
                elif "title" in ca_comp.tag:
                    subj_titles_list.append(ca_comp)


        rec_xml = ead2marc_rec(c0_raw)
        if rec_xml is not None:
            all_rec_xml_list.append(rec_xml)

    total_elapsed = time.time() - total_start_time
    print(f"\nAll {len(result)} records processed in {total_elapsed:.1f}s (avg {total_elapsed/len(result):.1f}s per record)")

    # Wrap all records in a <marc:collection> element and output
    # (This portion of code was generated utilizing Claude Opus 4.6)
    if all_rec_xml_list:
        print("All records processed. Compiling into a record collection.")
        collection = etree.Element(
            "{http://www.loc.gov/MARC21/slim}collection",
            nsmap={
                "marc": "http://www.loc.gov/MARC21/slim",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
        )
        collection.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"
        )
        for rec in all_rec_xml_list:
            collection.append(rec)
        collection_str = etree.tostring(collection, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("UTF-8")
        # Reorder any remaining out-of-order attributes to tag, ind1, ind2
        # (This portion of code was generated utilizing Claude Opus 4.6)
        collection_str = re.sub(r'<(marc:datafield) ind1="(.)" ind2="(.)" tag="(\d+)">', r'<\1 tag="\4" ind1="\2" ind2="\3">', collection_str)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        with open(f"C:/Users/yello/OneDrive/Documents/EAD2MARC/EAD2MARC_workzone/test_exports/collectiontest_{timestamp}.xml", "w", encoding="UTF-8") as outfile:
            outfile.write(collection_str)
        print(collection_str)

else:
    # Returns error message if document is not EAD3
    print("Uploaded file must be in EAD3 (not EAD 2002 or any other EAD version). Please upload a new file and try again.")
