# Project Tasks

## Current To-Do's

- [ ] Check with L about subfield 5 in 690 (no subfield 5 listed on Bibformats)
- [ ] Ask L if use of 650 vs 690 is correct
- [ ] Ask L about whether to add fields:
  - [ ] 046 (is in MARC AO -- is this needed if we have the 264?)
  - [ ] 099 (is in both MARC AO and ASpace Crosswalk)
  - [ ] 351 (is in ASpace Crosswalk)
  - [ ] 852 (is in both MARC AO and ASpace Crosswalk)

- [ ] Check logic for all fields against ASpace MARCXML Export Map and MARC AO mapper
  - [ ] !!!STOPPING POINT!!! Finished checking ASpace MARCXML Map, checking MARC AO mapper not yet started
- [ ] Check if any min level fiels are missing (see PPT L emailed)
- [ ] Figure out field 555 "raw" variable usage
- [ ] Write more to-do’s (address TODOs in notebook??)
- [ ] Make leader
- [ ] Add back in marc: namespace prefixes at end of conversion
        re.sub(r'<([A-Za-z0-9_:-]+)(\s|>)', r'<marc:\1\2', authority_100_110_str)
        re.sub(r'</([A-Za-z0-9_:-]+)>', r'</marc:\1>', authority_100_110_str)
- [ ] Add in looping logic from attrib_loopbox
- [ ] Create fallbacks for common errors
        Retrying authority file fetches from lccn.loc.gov if first attempt fails
        Moving to non-authority name treatments if fetching from authority file fails multiple times

- [ ] Determine what doesn't work with ASpace version 4 (local test version) vs. version 3 (IU version)
  - [ ] External IDs not in version 4 (affects 02x, 05x, and 08x)

- [ ] Create documentation describing limitations
  - [ ] No support for 648 (Temporal terms don't show up in ASpace EAD exports)
  - [ ] No support for 610 or 65x subfields for non-authorized corpnames/titles/subjects/gfts (subdivisions aren't broken into separate tags in EAD export)

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

## Major Claude Edits

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
