# Project Tasks

## Current Sprint

- [ ] Write 524
- [ ] Write 535
- [ ] Write 540
- [ ] Write 541
- [ ] Write 544
- [ ] Write 545
- [ ] Write 555
- [ ] Write 561
- [ ] Write 583
- [ ] Write 584
- [ ] Write 520
- [ ] Write 020
- [ ] Write 028
- [ ] Move physdesc notes from 300 to 5xx
        See aspace_784a34c3013035deb6e33ad4f9c5934f for example
- [ ] Check logic for all fields against ASpace MARCXML Export Map and MARC AO mapper
- [ ] Write other relevant identifer (02x) fields
- [ ] Write more to-do’s (address TODOs in notebook??)
- [ ] Make leader
- [ ] Add back in marc: namespace prefixes at end of conversion
        re.sub(r'<([A-Za-z0-9_:-]+)(\s|>)', r'<marc:\1\2', authority_100_110_str)
        re.sub(r'</([A-Za-z0-9_:-]+)>', r'</marc:\1>', authority_100_110_str)
- [ ] Add in looping logic from attrib_loopbox
- [ ] Create fallbacks for common errors
        Retrying authority file fetches from lccn.loc.gov if first attempt fails
        Moving to non-authority name treatments if fetching from authority file fails multiple times
- [ ] Go through ASpace MARCXML Export Map and MARC AO mapper and add fields not currently implemented

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
- [X] Figure out how to parse a EAD export and create MARCXML for only collection- and item-level records (or, even better, let user toggle what hierarchy level(s) they want!). Consider: .attrib[level] = “item” -- SEE attrib.loopbox
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
- [X] Write 690
- [X] Write 500
- [X] Route physdecs to 300 or 500 depending on content
- [X] Write 520
- [X] Add header removal logic to 5xx functions (see ead2marc_520)
- [X] Write 506

## Review Notes
