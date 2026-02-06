# Project Tasks

## Current Sprint

- [ ] Check 300 field syntax with L (specifically subfield f)
- [ ] Check 041 field syntax with L (specifically subfield 2)
- [ ] Check 546 field syntax with L (specifically whether to use v1 or v2)
- [ ] Ask L if IU Libraries leader already exists in MARC/XML

- [ ] Write 655
- [ ] Write 690
- [ ] Write 500
- [ ] Write 020
- [ ] Write 028
- [ ] Write other relevant identifer fields
- [ ] Write more to-do’s (address TODOs in notebook??)
- [ ] Add back in marc: namespace prefixes at end of conversion
        re.sub(r'<([A-Za-z0-9_:-]+)(\s|>)', r'<marc:\1\2', authority_100_110_str)
        re.sub(r'</([A-Za-z0-9_:-]+)>', r'</marc:\1>', authority_100_110_str)
- [ ] Add in looping logic from attrib_loopbox

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

## Review Notes
