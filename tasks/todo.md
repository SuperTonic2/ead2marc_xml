# Project Tasks

## Current To-Do's

- [ ] After MC122 batch completes, audit records with `uuuu` in 008 p7-14 against their EAD source — confirm whether plain `<unitdate>` text-only elements were the only date info present (if so, Option B text-parsing fallback may be worth implementing as v1.84)
- [ ] Check with L if 541 needs to be broken down into more subfields (see bibformats)

- [ ] Address TODOs in .py doc
- [ ] Check item-level test exports and debug any issues
- [ ] Run full item-level test export and send to Laikin to review
- [ ] Write more to-do’s

- [ ] Check ISBD punctuation
- [ ] Determine what doesn't work with ASpace version 4 (local test version) vs. version 3 (IU version)
  - [ ] External IDs not in version 4 (affects 02x, 05x, and 08x)
- [ ] Create UI OR consider making into an ASpace plugin
- [ ] Incorporate features into UI:
  - [ ] Create some way for user to toggle which name they want to be 100/110 instead of just setting it to first listed creator.

- [ ] Create documentation describing limitations
  - [ ] No support for 648 (Temporal terms don't show up in ASpace EAD exports)
  - [ ] No support for 610 or 65x subfields for non-authorized corpnames/titles/subjects/gfts (subdivisions aren't broken into separate tags in EAD export)
- [ ] Add ChatGPT and Claude chat logs into folder in repo

## Backlog

## Completed

- [X] Write 245
- [X] Update 264 in spreadsheet
- [X] Write 264
- [X] Explore marcao plugin (in plugins folder, not in config)
        <https://github.com/pulibrary/dacs_handbook/blob/main/aspace_4_docker.md>
        <https://github.com/hudmol/as_marcao>
        <https://github.com/hudmol/user_defined_in_basic>
- [X] Explore full tischler marcao export
- [X] Explore converting marcao mapper into Python
- [X] Cross-check current fields against marcao mapper logic
- [X] Finish 100_110
- [X] Ask L about adding dates in 046 in addition to 264? (just do 264)
- [X] Figure out how to fecth MARC/XML for VIAF records like what's been done for LCNAF
- [X] Finish 100
- [X] Finish 110
- [X] Figure out how to parse a EAD export and create MARCXML for only collection- and item-level records (or, even better, let user toggle what hierarchy level(s) they want!). Consider: .attrib[level] = “item”
        SEE attrib.loopbox
- [X] Write 700
- [X] Write 710
- [X] Write 300
- [X] Write 041
- [X] Write 546
- [X] Check 300 field syntax with L (specifically subfield f)
- [X] Check 041 field syntax with L (specifically subfield 2)
- [X] Check 546 field syntax with L (specifically whether to use v1 or v2) (use v1)
- [X] Ask L if IU Libraries leader already exists in MARC/XML
- [X] Write 655
- [X] Add looping and xml_list logic from 655 to repeatable fields
        700
        710
        264
        300
        546
- [X] Write 650
- [X] Write 500
- [X] Route physdecs to 300 or 500 depending on content
- [X] Write 520
- [X] Add header removal logic to 5xx functions (see ead2marc_520)
- [X] Write 506
- [X] Write 524
- [X] Write 535
- [X] Write 540
- [X] Write 544
- [X] Write 545
- [X] Write 584
- [X] Write 555
- [X] Write 541
- [X] Write 561
- [X] Write 583
- [X] Test all 5xx fields
- [X] Write 02x fields
  - [X] 020
  - [X] 022
  - [X] 023
  - [X] 024
  - [X] 026
  - [X] 027
  - [X] 028
- [X] Write 050
- [X] Write 086
- [X] Write 082
- [X] Add 05x and 08x fields (for items with preexisting call numbers -- see aspace_3795e2a9a60bc1eb393119f147bf4b7e)
- [X] Write 8xx fields in ASpace map
  - [X] 856
- [X] Write 6xx fields in ASpace map
  - [X] 600
  - [X] 610
  - [X] 630
  - [X] 650
  - [X] 651
  - [X] 656
  - [X] 657
- [X] Write 690
- [X] Update 506 to pull from the collection-level note if there is none at the component level (idea from MARC AO 506 comment)
  - Is in code but commented out as majority of collection-level notes reference full collections, making them inappropriate for an item-level record
- [X] Create a function that lists all records that already have OCLC no. unitids
- [X] Go through ASpace MARCXML Export Map and MARC AO mapper and check for fields not currently implemented
- [X] Add subdivision $v, $x, $y, $z to 6xx
- [X] Move physdesc notes from 300 to 5xx
  - See aspace_784a34c3013035deb6e33ad4f9c5934f for example
- [X] Create default restriction message for field 506 (idea from MARCO AO mapper)
- [X] Check logic for all fields against ASpace MARCXML Export Map and MARC AO mapper
- [X] Check if any min level fiels are missing (see PPT L emailed)
- [X] Figure out field 555 "raw" variable usage
- [X] Check with L about subfield 5 in 690 (no subfield 5 listed on Bibformats)
- [X] Ask L if use of 650 vs 690 is correct
- [X] Ask L about whether to add fields:
  - [X] 046 (is in MARC AO -- is this needed if we have the 264?) (no)
  - [X] 099 (is in both MARC AO and ASpace Crosswalk) (maybe for collection-level only)
  - [X] 351 (is in ASpace Crosswalk) (test how arrangement and fileplan tags export in EAD)
  - [X] 852 (is in both MARC AO and ASpace Crosswalk) (no)
- [X] Add fields 336, 337, and 338
- [X] Add and clean up comments and docstrings
- [X] FINISH updating 041
  - [X] Create second 041 with ind2 "7" and $2 if code isn't in marc code list or iso639t_to_marc (ie. zgh)
- [X] Address TODOs in notebook
- [X] Make leader
- [X] Add 00x fields (!!!Make sure 00x map as < controlfield > and not data fields (per L)!!!)
- [X] Make crtype identification in 336 more robust (search gft and physdescs)
- [X] Make 099 and 351 for collection-level records only
- [X] Add support for p15to17 and p18to34 in 008
- [X] Add back in marc: namespace prefixes at end of conversion
        re.sub(r'<([A-Za-z0-9_:-]+)(\s|>)', r'<marc:\1\2', authority_100_110_str)
        re.sub(r'</([A-Za-z0-9_:-]+)>', r'</marc:\1>', authority_100_110_str)
- [X] Add in looping logic from attrib_loopbox
  - [X] Give user option to toggle between selecting specific ID or looping through hierarchy level
- [X] Create fallbacks for common errors
        Retrying authority file fetches from lccn.loc.gov if first attempt fails
        Moving to non-authority name treatments if fetching from authority file fails multiple times
- [X] Add more progress messages
  - [X] When final marc xml collection is being compiled (already created manually)
  - [X] Time elapsed between record creation
  - [X] Total time elapsed from start to finish
- [X] Check leader with L
  - [X] Should Elvl (p17) be "3", "5", or "7" (or something else)? (A: 7)
  - [X] Shold Desc be "u" or "i" (or something else)? (A: changed from u to i)
- [X] Check 008 with L
  - [X] Is " " correct character for noting blank characters?
  - [X] What is supposed to go in 008 bytes 00 to 05 ?? (A: Put date of generation)
  - [X] Is current approach for positions 18-34 (for positions where accurate population based on EAD alone is not possible, codes are set statically to the default code, "not specified", or "unknown") appropriate?
- [X] Check with L if fields 006 and/or 007 is needed (at a glance seems like it would be tough to code and aren't listed on the requirements for minimum records PPT)
- [X] Check with L if having MC and VAE numbers in both 035 and 099 is appropriate (see TODO in v1.81.py)
- [X] Check with L if ISBD punctuation on 300 field is correct
- [X] Check collection-level exports and refine against constant data workform
  - [X] Add 035 for collection-level VAE and MC numbers
  - [X] Add 246 fields for alternate collection title nameforms
  - [X] Incorporate certainty into date expression in 264
        (make sure this won't break other stuff like DtSt in leader/008)
  - [X] Consider removing subfield f in 300 and putting everything in subfield a (see bibformats)
  - [X] HTML escape 540? (and other 500 notes?)
  - [X] Check leader and 008

## Major Claude Edits

### 2026-06-03: v1.83.py — Fix IndexError on Plain `<unitdate>` Text Elements

**What was done:** Crash report on MC122 batch (records 41-60), record 11/20 throwing `IndexError: list index out of range` at line 4789 in `ead2marc_008`.

**Root cause:** Line 4767's xpath `".//*[starts-with(local-name(), 'unitdate')]"` matched both `<unitdatestructured>` (the structured variant with `<datesingle>`/`<daterange>` children) AND plain `<unitdate>` (the EAD3 non-structured variant whose date is just text content with no children). Path A's filter at line 4773 preserves either variant since `datechar` is an attribute, not a child. When a plain `<unitdate>` reached the date-extraction code, the downstream `xpath(...)[0]` on `<datesingle>` or `<daterange>` returned an empty list, and `[0]` threw IndexError. All branches in the date block (lines 4785-4844) had the same vulnerability — record 11 just happened to hit the single-unitdate-single-date branch first.

**Option A applied (minimal fix):** Changed the xpath to only match `<unitdatestructured>`:

```python
unitdates_list = raw.xpath(".//*[local-name()='unitdatestructured']")
```

Plain `<unitdate>` elements are now ignored by `ead2marc_008`. Records whose only date info is in plain `<unitdate>` form will get `p6=n`, `p7-14=uuuu` in 008. Data loss is bounded and recoverable — Option B (parse year from plain `<unitdate>` text content using existing `re.search(r'\b\d{4}\b', ...)` pattern) is the follow-up for v1.84 if MC122 audit shows meaningful data was lost.

**Follow-up to-do added under Current To-Do's:** audit `uuuu` records against EAD source after the MC122 batch completes to quantify the impact.

**Function affected:** `ead2marc_008` (file: EAD2MARC_workzone/EAD2MARCv1.83.py)

---

### 2026-06-03: v1.83.py — Distinguish Missing-Authority-ID from Connection Timeout in Notes

**What was done:** The 10 authority-fetching functions (100, 110, 600, 610, 630, 650, 651, 655, 700, 710) emit an HTML comment when the LCNAF/VIAF fetch fails, but the message was always `<!-- NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. -->` — even when `timeout_authfile_no` was `None` (because the EAD record had no authority ID at all). Result: misleading `Authority None could not be fetched (connection timeout)` notes when the real cause was "no ID to look up, no fetch attempted."

Replaced the `etree.Comment(...)` call across all 10 sites with a Python ternary:

```python
etree.Comment(
    f" NOTE: Authority {timeout_authfile_no} could not be fetched (connection timeout). Field was constructed manually. "
    if timeout_authfile_no
    else " NOTE: Authority lookup skipped (no ID in EAD); field constructed manually. "
)
```

Real timeouts (where `timeout_authfile_no` holds a valid LCNAF ID like `n 79100200`) still get the original "connection timeout" message; missing-ID cases get the new "lookup skipped (no ID in EAD)" message. Both still note that the field was constructed manually, so catalogers know to double-check.

**Implementation note:** Used Edit's `replace_all=true` because the modified part of the line is identical across all 10 sites (only the `result_XXX.append(...)` variable name differs, which is *before* the changed expression). Single attribution comment added at the first site (`ead2marc_100`) noting the pattern applies to the other 9 functions identically; per-site attribution would have been redundant noise.

**Functions affected:** `ead2marc_100`, `ead2marc_110`, `ead2marc_600`, `ead2marc_610`, `ead2marc_630`, `ead2marc_650`, `ead2marc_651`, `ead2marc_655`, `ead2marc_700`, `ead2marc_710`

---

### 2026-06-02: v1.83.py — Fix 856 URL Separator and Strip Trailing Whitespace from 555/856 $u

**What was done:** Two related URL fixes in the finding-aid-link subfields, surfaced by reviewing the MC122 test export.

1. **`ead2marc_856` $u missing separator:** Line `faid_uri = f"""https://archives.iu.edu/catalog/{vaid_clean}{cid_clean}"""` produced concatenated URLs like `.../catalog/VAE4896aspace_28d3...` (no separator between the VA collection ID and the ASpace component ID). User confirmed the correct IUL archives URL pattern uses `_` as a separator. Added `_` to the f-string.

2. **Trailing whitespace in `$u` for 555 and 856:** Both `ead2marc_555` and `ead2marc_856` constructed their $u as `f"""<subfield code="u">{faid_uri} </subfield>"""` — note the trailing space before `</subfield>`. The space was there from the moment the functions were first written in v1.70 (confirmed via `git log -S` — not added later as a workaround). User confirmed via direct test that the trailing space breaks the URL: `archives.iu.edu/catalog/VAE4896_aspace_xxx%20` returns 404 (browsers URL-encode the space as %20). Removed the trailing space from both functions.

**Functions affected:** `ead2marc_555`, `ead2marc_856` (file: EAD2MARC_workzone/EAD2MARCv1.83.py)

---

### 2026-06-02: v1.83.py — Fix 351 Multi-Note Loss and 500 Cross-Record Reference

**What was done:** Two small fixes surfaced by a pre-MC122 bug scan.

1. **`ead2marc_351` last-arrangement-note bug:** The `for arrnote in arrnote_list:` loop built `a_351` per iteration, but the `<datafield>` assembly (lines `field_351_str_nb = ...`, `etree.fromstring(...)`, `field_351_xml_list.append(...)`) was indented one level less and sat *outside* the loop. So collections with multiple `<arrangement>` notes produced exactly one 351 field containing only the last note. Moved the assembly block inside the loop (bumped indent from 8 to 12 spaces). Now each arrangement note produces its own 351 field — 351 is a repeatable MARC tag, so this is the correct shape.

2. **`ead2marc_500` cross-record reference:** Line 2300 was calling `ead2marc_300(c0_raw)` instead of `ead2marc_300(raw)`. Worked in practice because at this call site `raw == c0_raw`, but it was inconsistent with every other `ead2marc_300(raw)` call in `ead2marc_rec` and would silently desync if `ead2marc_500` were ever invoked on a sub-element. One-character fix.

**Functions affected:** `ead2marc_351`, `ead2marc_500` (file: EAD2MARC_workzone/EAD2MARCv1.83.py)

**Pre-MC122 scan also verified clean:** operator-precedence traps (only the one already fixed), `sorted()`-returning-list bugs (only the one already fixed), lxml Element truthiness checks (only the one already fixed), off-by-one slicing on fixed-width MARC sub-fields. The remaining IDE "not accessed" warnings (`field_336_xml_list`, `field_041_xml_list`, `all_langcodes`, `leader_xml_list`, `leader_p6`) are non-issues — the output-producing calls happen in `ead2marc_rec`; the flagged calls inside `ead2marc_008` and `ead2marc_leader` are for internal computation only. `leader_p7` is genuinely dead code (computed and returned but never read) — left as-is per user request.

---

### 2026-06-02: v1.83.py — Fix lxml Truthiness and Date Zero-Padding in 008

**What was done:** Two related bug fixes in `ead2marc_008`, surfaced by running v1.83 against `test2_ead3.xml` (record 4, "questionable date test", date range 456-477).

1. **lxml truthiness fix (single-unitdate range branch):** The check `if todate_raw:` was using a bare lxml Element in a boolean context. In lxml, Elements are truthy only if they have child elements — text content alone is not enough. So records whose only unitdate was a `<daterange>` with a `<todate>` containing just text (the normal case) were silently falling through to the `else` branch and getting `p11to14 = "    "` instead of the actual end date. Replaced with `if todate_list:` (checking the xpath result list, where Python's normal "non-empty list is truthy" rule applies).

2. **Zero-padding for short numeric dates:** Dates like `"456"` were being written into the 008 controlfield as 3 chars wide, shifting every position after them left by one. Added two layers: (a) `.zfill(4)` on `date_list.append` calls in the multi-unitdate branch, so `min`/`max` lex-compare correctly when dates differ in width (e.g. `["456", "1970"]` → `["0456", "1970"]` so `min` returns `"0456"` chronologically, not `"1970"` lexicographically); (b) a final `if p7to10.isdigit(): p7to10 = p7to10.zfill(4)` normalization right before the controlfield is assembled, to catch the single-unitdate paths without adding `.zfill(4)` to every individual assignment. `isdigit()` returns True only for non-empty all-digit strings, so it skips `"uuuu"` (no-dates placeholder) and blank-space placeholders.

**Function affected:** `ead2marc_008` (file: EAD2MARC_workzone/EAD2MARCv1.83.py)

---

### 2026-06-02: v1.83.py — Filter Non-Creation Dates from 008 p6/p7-14

**What was done:** Resolved the long-standing TODO at line 4767 in `ead2marc_008` (now line 4763 in v1.83). EAD3 `<unitdatestructured>` elements carry a `datechar` attribute (creation, copyright, broadcast, publication, etc.) but the function previously treated all of them identically, mixing copyright dates into the inclusive-date span computed for 008 positions 7-14. Added a list-comprehension filter immediately after `unitdates_list` is built:

```python
creation_unitdates = [u for u in unitdates_list if u.get("datechar") == "creation"]
if creation_unitdates:
    unitdates_list = creation_unitdates
```

Behavior:

- Record has creation dates → only those are used for 008 p6/p7-14; copyright/broadcast/etc. are filtered out (still preserved in 264 via `ead2marc_264`).
- Record has only copyright (or other non-creation) dates → falls back to existing logic, which yields `p6 = i` and min/max for multi-date records — matches user's stated preference for the copyright-only case.
- Record has no dates → unchanged (`p6 = n`, dates `uuuu`).

**Versioning:** Copied v1.82.py to `archived EAD2MARC/EAD2MARCv1.82.py` (preserves the three bug fixes from earlier today as the v1.82 final state). New work file is `EAD2MARC_workzone/EAD2MARCv1.83.py`.

**Function affected:** `ead2marc_008` (file: EAD2MARC_workzone/EAD2MARCv1.83.py)

---

### 2026-06-02: Fix Three In-Progress TODO Resolutions in v1.82.py

**What was done:** Repaired three buggy TODO resolutions left half-finished in v1.82.py.

1. **`ead2marc_300` (line 1904, subfield c period logic):** Changed `if dimensions_clean[-2:] == "ft" or "in":` to `if dimensions_clean[-2:] in ("ft", "in"):`. Original was an operator-precedence trap — Python read it as `(... == "ft") or ("in")`, and a non-empty string is truthy, so the condition was permanently True and a period was being appended to every dimension (including cm).

2. **`ead2marc_351` (line 2273-2277, head-stripping logic):** Reverted a half-finished `arrnote_clean` → `arrnote_cleanish` rename. The new name was only assigned inside `if arrnote_head_list:`, so any arrangement note without a `<head>` child would raise `NameError` on the downstream `" ".join(arrnote_clean.split())` call.

3. **`ead2marc_008` (lines 4875-4879, illustration code aggregation):** Rewrote to use a `set()` for dedup, `dict.items()` for cleaner iteration, `"".join(sorted(...))` for alphabetization, and `(ills_raw + "    ")[:4]` for padded-to-exactly-4-chars slicing. Original was three problems compounding: `sorted()` returns a list (would TypeError on the next iteration's string concatenation), no dedup, and `[:5]` was wrong since MARC 008 p18-21 is a 4-character field.

**Latent issue flagged (not fixed):** `ead2marc_351` builds `a_351` inside a `for arrnote in arrnote_list:` loop but assembles the `<datafield>` outside the loop, so collections with multiple `<arrangement>` notes only get the last one written. Pre-existing, not introduced by this fix.

**Functions affected:** `ead2marc_300`, `ead2marc_351`, `ead2marc_008` (file: EAD2MARC_workzone/EAD2MARCv1.82.py)

---

### 2026-03-26: Parse Type Toggle and Looping Logic in Setup Cell

**What was done:** Incorporated the parse_type toggle from attrib_loopbox into the main notebook (v1.8) setup cell. Users now choose between parsing by ID (option "1") or by hierarchy level (option "2"). For hierarchy level, "collection" targets `<archdesc>`, while other levels (e.g., "item") target `<c>` elements with the matching `@level` attribute. Wrapped all global variable setup (vaid, names lists, subject lists) and the `ead2marc_rec()` call inside a `for c0_raw in result:` loop so multiple matching records are processed sequentially.

**Cell affected:** Setup cell 0 (`eb783a5d`) in EAD2MARCv1.8.ipynb

---

### 2026-03-26: Timeout Warning Comments Included in Returned XML

**What was done:** Changed all 10 authority sub-functions so timeout warning comments are included in the returned XML, not just in the printed string. Previously, the `<!-- NOTE: Authority ... -->` comment was prepended to the string for printing but the returned XML element didn't include it. Now each function returns a list: `[comment_xml, field_xml]` when there's a timeout, or `[field_xml]` when there isn't. Comment nodes are created with `etree.Comment()`. Updated all 3 sorter functions to use `.extend()` instead of `.append()` to handle the list returns.

**Sub-functions affected (10):** ead2marc_100, ead2marc_110, ead2marc_600, ead2marc_610, ead2marc_630, ead2marc_650, ead2marc_651, ead2marc_655, ead2marc_700, ead2marc_710

**Sorter functions affected (3):** ead2marc_100_110, ead2marc_600_610_630_65x, ead2marc_700_710

---

### 2026-03-26: Priority-Based Leader Position 06 Selection in ead2marc_leader

**What was done:** Replaced the frequency-based p6 code selection with a priority-based approach. When multiple content types are detected by ead2marc_336 (e.g., "txt" and "ntm"), the old logic picked the most frequent code, with ties going to the first occurrence — meaning generic "text" (`a`) would win over specific "score" (`c`). New logic uses a priority dictionary where more specific types always override more generic ones: text(0) < mixed(1) < computer(2) < cartographic(3) < 2D graphic(4) < 3D artifact(5) < moving image(6) < nonmusical sound(7) < musical sound(8) < notated music(9). Selection is now `max(p6_code_list, key=lambda c: p6_priority.get(c, 0))`.

**Cell affected:** ead2marc_leader (`30f45d55`)

---

### 2026-03-26: Script Detection for 008 Position 33 in ead2marc_008

**What was done:** Implemented Unicode script detection for 008 position 33 (Alph) in the `cnr` format block of ead2marc_008. Uses `unicodedata.name()` to identify character scripts in the 245 $a title text and maps them to MARC Alph codes (a=basic Roman, b=extended Roman, c=Cyrillic, d=Japanese, e=Chinese, f=Arabic, g=Greek, h=Hebrew, i=Thai, j=Devanagari, k=Korean, l=Tamil, z=mixed, u=unknown). Also fixed three bugs: `field_300_xml` reference (should be `field_245_xml`), `ead2marc_245` return value treated as list (returns single element), and missing `p34` variable definition.

**Cell affected:** ead2marc_008 (`b5580904`)

---

### 2026-03-12: Fix physdesc Keyword Detection in ead2marc_336

**What was done:** Fixed two bugs preventing `<physdesc>` text from being searched for content type keywords:

1. `physdesc.xpath(".//*[local-name()='physdesc']")` was looking for a `<physdesc>` *descendant inside* the current element (never matches since physdesc doesn't nest). Changed to check if the current element itself is a plain `<physdesc>` using `physdesc.tag.endswith('physdesc') and not physdesc.tag.endswith('physdescstructured')`.
2. `raw.xpath(".//*[local-name()='unittype']")[0]` and `raw.xpath(".//*[local-name()='physdesc']")[0]` always grabbed the first element in the whole record. Changed to use the current loop element (`physdesc.xpath(...)` for unittype, `physdesc` directly for physdesc text).

**Cell affected:** ead2marc_336 (`2b29157e`)

---

### 2026-03-12: Whitespace Normalization for 02x/05x/08x Functions

**What was done:** Added `unitid_str = " ".join(unitid_str.split())` after `.strip()` in all 10 sub-functions called by ead2marc_02x_05x_08x. This collapses internal whitespace (newlines, tabs, multiple spaces from EAD XML formatting) into single spaces, preventing line breaks from appearing inside subfield content in MARC output.

**Cells affected (10 total):** ead2marc_020 (`3f387954`), ead2marc_022 (`2cee8f87`), ead2marc_023 (`9875d7ba`), ead2marc_024 (`8431e35b`), ead2marc_026 (`7bd2ad3f`), ead2marc_027 (`f4021706`), ead2marc_028 (`42f6b7a0`), ead2marc_050 (`89ee752e`), ead2marc_082 (`db8f2790`), ead2marc_086 (`7ee88fd8`)

---

### 2026-03-12: Tag 110 Fallback for ead2marc_100 and Family Name Handling for ead2marc_600/700

**What was done:** Synchronized missing features across ead2marc_100, ead2marc_600, and ead2marc_700 so all three functions have consistent handling.

**ead2marc_100** — Added tag 110 fallback (already present in 600 and 700). If the LCNAF authority record contains tag 110 instead of tag 100, the code now falls back to fetching tag 110. Added in both the direct LCNAF path and the VIAF→LCNAF path.

**ead2marc_600 and ead2marc_700** — Added family name handling (already present in 100):

- Indicator 1: Sets `ind1 = "3"` when `name.tag.endswith('famname')`
- Subfield D: Skips date subfield for family names (dates are not separated from family name strings)
- Subfield A: Preserves full name string without comma splitting for family names

**Note:** Uses `name.tag.endswith('famname')` only (not `or name in creator_famnames_list`) since `creator_famnames_list` is specific to the 100 field routing context.

**Cells affected:** ead2marc_100 (`42cf188f`), ead2marc_600 (`6f32d57f`), ead2marc_700 (`832762d0`)

---

### 2026-03-06: Timeout Fallback for Authority Fetches

**What was done:** Wrapped all `lccn.loc.gov` `requests.get()` calls in `try/except (requests.exceptions.ConnectionError, requests.exceptions.Timeout)` with `timeout=10`. On timeout, the function falls back to manual field construction and prepends an XML comment (`<!-- NOTE: Authority {authfile_no} could not be fetched (connection timeout). Field was constructed manually. -->`) to the output.

**Cells affected (9 total):** ead2marc_110 (`1acc3c99`), ead2marc_600 (`6f32d57f`), ead2marc_610 (`f7ac1c05`), ead2marc_630 (`be6c4944`), ead2marc_650 (`2faad90d`), ead2marc_651 (`c8e8c2e2`), ead2marc_655 (`a25265ed`), ead2marc_700 (`832762d0`), ead2marc_710 (`7a066500`)

**Note:** ead2marc_100 (`42cf188f`) was updated with the same pattern in a prior session.

**Structural change in 630/650/651/655:** Changed `else:` to `if not authfile_no:` so the manual fallback also runs when a timeout clears `authfile_no`.

---

### 2026-03-06: ISBD Comma Punctuation for Manually Constructed Name Fields

**What was done:** Added trailing comma logic to subfield content in manually constructed (non-authority) name fields, matching ISBD punctuation conventions. Subfield definitions were reordered (E before D before A) so later subfields are defined first, allowing earlier subfields to check if a following subfield exists and append a comma accordingly.

- **Personal name fields (600, 700):** `$d` gets comma if `$e` exists; `$a` gets comma if `$d` exists
- **Corporate name fields (110, 610, 710):** `$a` gets comma if `$e` exists

**Cells affected:** ead2marc_100 (`42cf188f`, user-edited), ead2marc_110 (`1acc3c99`), ead2marc_600 (`6f32d57f`), ead2marc_610 (`f7ac1c05`), ead2marc_700 (`832762d0`), ead2marc_710 (`7a066500`)

---

### 2026-03-05: LC suggest2 API for Subject Heading Lookup (630, 650, 651, 655)

**What was done:** Rewrote the 630, 650, 651, and 655 functions to use the LC suggest2 API to look up authorized subject headings from id.loc.gov, fetch the authority MARC/XML from lccn.loc.gov, and convert the authority tag to the corresponding 6XX tag (130→630, 150→650, 151→651, 155→655). Headings with subdivisions (split on " -- ") are handled by looking up each subdivision via suggest2 and checking the authority record's MARC tag to classify it: 185→$v (form), 181→$z (geographic), 182→$y (chronological), 180→$x (general).

**API endpoints used:**

- 630: `authorities/names/suggest2` (uniform titles)
- 650: `authorities/subjects/suggest2`
- 651: `authorities/names/suggest2` (geographic names)
- 655: `authorities/genreForms/suggest2` (LCGFT), `authorities/subjects/suggest2` (LCSH)

**Cells affected:** ead2marc_630 (`be6c4944`), ead2marc_650 (`2faad90d`), ead2marc_651 (`c8e8c2e2`), ead2marc_655 (`a25265ed`)

---

### 2026-03-05: Whitespace Normalization and Attribute Reorder for 6XX Subject Fields

**What was done:** Added `" ".join(text.split())` whitespace normalization to 630, 650, 651, 655 (EAD XML contains embedded whitespace/newlines pulled through by `xpath("string()")`). Added attribute reorder regex `re.sub(r'<datafield ind1="(.)" ind2="(.)" tag="(\d+)">', ...)` to ensure `tag` appears before `ind1`/`ind2` in output.

**Cells affected:** ead2marc_630 (`be6c4944`), ead2marc_650 (`2faad90d`), ead2marc_651 (`c8e8c2e2`), ead2marc_655 (`a25265ed`)

---

### 2026-03-05: ASpace Identifier Guard for Name Authority Cells

**What was done:** Added `not name.get("identifier", "").startswith("aspace_")` guard to all 6 name authority cells to prevent attempting to fetch authority records using ASpace-internal local identifiers (e.g., `aspace_784a34c3...`).

**Cells affected:** ead2marc_100 (`42cf188f`), ead2marc_110 (`1acc3c99`), ead2marc_600 (`6f32d57f`), ead2marc_610 (`f7ac1c05`), ead2marc_700 (`832762d0`), ead2marc_710 (`7a066500`)

---

### 2026-03-05: Authority/Indicator 2/Subfield $2 Pattern for ead2marc_610

**What was done:** Copied the `authority_raw`/`authority` variable pattern, full indicator 2 section (lcsh→0, cyac→1, mesh→2, nal→3, empty→4, cash→5, rvm→6, else→7), and subfield $2 logic from ead2marc_600 to ead2marc_610. Replaced direct `name.get("source")` usage with the `authority` variable throughout.

**Cell affected:** ead2marc_610 (`f7ac1c05`)

---

### 2026-02-19: Whitespace Normalization Fix for 5xx Functions

**What was done:** Added whitespace normalization (`xxx_clean = " ".join(xxx_clean.split())`) to 11 of the 12 5xx function cells, immediately before the `html.escape()` call. This collapses any runs of whitespace (spaces, tabs, newlines) extracted from EAD XML into single spaces.

**Cells updated (11 total):**

- `bb5beb43` (ead2marc_500) - `gnote_clean`
- `da4311dc` (ead2marc_506) - `ranote_clean`
- `46e74fa2` (ead2marc_520) - `snote_clean`
- `9b1d35fc` (ead2marc_524) - `prefercite_clean`
- `551945aa` (ead2marc_535) - `ldnote_clean`
- `7830b0e7` (ead2marc_540) - `tgurnote_clean`
- `bfdadbe3` (ead2marc_541) - `acqnote_clean`
- `336ec17e` (ead2marc_544) - `loamnote_clean`
- `5515fa99` (ead2marc_545) - `bhnote_clean`
- `61fe70d1` (ead2marc_546) - `langnote_clean`
- `924a0a1b` (ead2marc_584) - `afunote_clean`

**Cell skipped (1):**

- `17aae9da` (ead2marc_555) - This function does not have an `html.escape()` call or a text-cleaning `_clean` variable pattern; it constructs a URI-based field directly, so no whitespace normalization was needed.

---

### 2026-02-19: XPath 1.0 `in` Operator Fix in ead2marc_500

**What was done:** Fixed `local-name() in $variable` (invalid in XPath 1.0) to use individual `or` conditions in ead2marc_500.

**Cell affected:** ead2marc_500 (cell `bb5beb43`)

---

### 2026-02-12: Tag='110' Fallback and 110→710 Routing in ead2marc_700

**What was done:** Fixed IndexError when processing names like "Milwaukee Symphony Orchestra" tagged as `<persname>` in EAD but having tag='110' (corporate name) in the LCNAF authority record. Added fallback to check `tag='110'` when `tag='100'` returns empty, in both the direct LCNAF path and the VIAF-with-LC-link path. Per user decision, the fallback routes these to tag='710' (not '700'), prioritizing the authority record's classification over the EAD tagging. Also added missing `return field_700_xml` statement.

**Cell affected:** ead2marc_700 (cell `832762d0-df3f-4a46-8467-a814fe994cbe`)

---

### 2026-02-12: ead2marc_300 Rewrite for Paired physdesc Processing

**What was done:** Rewrote ead2marc_300 to pair `<physdescstructured>` elements with their following `<physdesc>` siblings using `following-sibling::*[local-name()='physdesc'][1]` XPath. Previously, all elements starting with "physdesc" were processed individually, resulting in separate 300 fields. Now the structured data (quantity, unittype, dimensions) and the container summary are combined into a single 300 field. Standalone `<physdesc>` elements not paired with a `<physdescstructured>` are routed to ead2marc_500 instead. Function returns `(field_300_xml_list, consumed_physdescs)` tuple so ead2marc_500 can skip already-processed elements.

**Cell affected:** ead2marc_300 (cell `f92b3136`)

---

### 2026-02-12: LC suggest2 API Identifier Lookup

**What was done:** Added logic to ead2marc_100, 110, 700, and 710 to look up LCNAF identifiers when the EAD `<persname>` or `<corpname>` has `source="lcnaf"` or `source="naf"` but no `identifier` attribute. Uses the LC suggest2 API (`https://id.loc.gov/authorities/names/suggest2?q={name_str}`) to search by name string, matching on `aLabel` to find the authority file number.

**Cells affected:** ead2marc_100, ead2marc_110, ead2marc_700, ead2marc_710

---

### 2026-02-12: VIAF SRU Search for Identifier Lookup

**What was done:** Added logic to ead2marc_100, 110, 700, and 710 to look up VIAF IDs when the EAD name has `source="viaf"` but no `identifier` attribute. Uses the VIAF SRU search endpoint (`https://viaf.org/viaf/search?query=local.personalNames+all+%22{name_str}%22...` for personal names, `local.corporateNames` for corporate names) with `Accept: application/xml` header. Matches on main heading text to find the correct VIAF cluster.

**Note:** VIAF JSON endpoints were found to return HTML instead of JSON, so SRU XML search was used instead.

**Cells affected:** ead2marc_100, ead2marc_110, ead2marc_700, ead2marc_710

---

### 2026-02-12: 041 $2 Subfield Placement Fix

**What was done:** Fixed ead2marc_041 so that `$2 iso639-2b` appears once at the end of the 041 field rather than after each `$a` subfield. MARC 041 $2 is non-repeatable.

**Cell affected:** ead2marc_041 (cell `adf6cbfd`)

---

### 2026-02-12: 041 and 655 XMLSyntaxError Fix

**What was done:** Fixed XMLSyntaxError caused by multiple root elements when parsing MARC XML strings. Changed to a parse-each-element-individually pattern instead of trying to parse concatenated XML strings.

**Cells affected:** ead2marc_041, ead2marc_655

---

### 2026-02-12: XPath 1.0 `ends-with()` Compatibility Fix

**What was done:** Replaced `ends-with()` (XPath 2.0 only) with substring-based alternatives compatible with lxml's XPath 1.0 support.

**Cells affected:** Multiple cells

---

### Pre-2026-02-06: VIAF Authority Fetch with LC Link Detection

**What was done:** Added logic to ead2marc_100, 110, 700, and 710 so that when a VIAF cluster is fetched, the code first checks if the cluster has a linked LCNAF source (`//*[local-name()="source" and starts-with(text(), "LC|")]`). If found, it extracts the LC ID and fetches the authority record from LCNAF instead. This produces higher-quality MARC output since LCNAF records have proper subfield coding. Falls back to parsing the VIAF cluster directly (extracting main heading, birth/death dates, etc.) when no LC link exists.

**Note:** Already present in v1.6 by Feb 6 commit (3446715).

**Cells affected:** ead2marc_100, ead2marc_110, ead2marc_700, ead2marc_710
