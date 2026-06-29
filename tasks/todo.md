# Project Tasks

## Current To-Do's

- [ ] Check collection-level test exports and debug any issues
- [ ] Run full item-level test export and send to L to review
- [ ] Write more to-do’s
  
- [ ] Create option to toggle/customize 246 fields

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
  - [X] Address TODOs in .py doc
  - [X] Create UI OR consider making into an ASpace plugin
- [X] Check ISBD punctuation
- [X] Determine what doesn't work with ASpace version 4 (local test version) vs. version 3 (IU version)
  - [X] External IDs not in version 4 (affects 02x, 05x, and 08x)
- [X] Incorporate features into UI:
  - [X] Create some way for user to toggle which name they want to be 100/110 instead of just setting it to first listed creator. (Did not do)
  - [X] Create ways to toggle custom:
    - [X] 035 local collection number syntax
    - [X] cat_code_040
    - [X] lib_code_049
- [X] Create documentation describing limitations
  - [X] No support for 648 (Temporal terms don't show up in ASpace EAD exports)
  - [X] No support for 610 or 65x subfields for non-authorized corpnames/titles/subjects/gfts (subdivisions aren't broken into separate tags in EAD export)
  - [X] No support for 006 or 007 (not in min-record requirements; would require source data not present in EAD)
  - [X] No support for 046 (264 covers this per L's direction) or 852
  - [X] Only EAD3 supported as input (EAD 2002 requires SAA-SDT XSLT pre-transformation; documented in README)
  - [X] Main entry (100/110) always defaults to the FIRST listed creator in the EAD `<origination>` elements; catalogers must manually swap 100↔700 (or 110↔710) in MARCEdit if a different creator should be the main entry
  - [X] Plain `<unitdate>` text-only elements (e.g., `<unitdate>undated</unitdate>` or "circa 1970") are ignored by 008 — only `<unitdatestructured>` with `<datesingle>`/`<daterange>` children feeds 008. Records with only plain `<unitdate>` get `p6=n`, `p7-14=uuuu` ("no dates given"). The text still appears in 264 $c.
  - [X] 008 date positions only reflect dates with `datechar="creation"` in the EAD; copyright/broadcast/publication/deaccession/etc. are filtered out (Path A). Falls back to all non-creation dates only if no creation date exists for the record.
  - [X] LCNAF authority records are used verbatim — missing $d (life dates), $b/$c (corporate subdivisions), etc. are NOT supplemented from EAD source data. If LCNAF doesn't include a subfield, the output won't either (per IUL "LCNAF as-is" policy).
  - [X] Family names (`<famname>`) do not trigger authority lookups; they are always constructed manually from EAD text content
  - [X] VIAF lookups are disabled in the browser version due to CORS incompatibility (VIAF doesn't send `Access-Control-Allow-Origin` headers). Standalone Python users can re-enable by setting `VIAF_ENABLED = True` near the top of the script.
  - [X] HTML markup in EAD note text (e.g., `<strong>`, `<em>`) is stripped during text extraction — emphasis is not preserved in MARC output. Plain text content survives.
  - [X] 300 (physical description) subfield ordering is non-standard (`a, c, a, f` instead of MARC-canonical `a, b, c, e, f`) per IUL convention; some strict MARC validators may flag this
  - [X] 035 (system control number) is emitted only for collection-level records, not for items
  - [X] If id.loc.gov is unreachable or times out (~10s default), the affected authority field falls back to manually-constructed content from the EAD; a NOTE comment is added to the record so catalogers can spot and review
  - [X] Check with L if 541 needs to be broken down into more subfields (see bibformats)
  - [X] Check item-level test exports and debug any issues
