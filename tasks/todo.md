# Project Tasks

## Current Sprint

- [ ] Finish 100
- [ ] Finish 110
- [ ] Figure out how to parse a EAD export and create MARCXML for only collection- and item-level records (or, even better, let user toggle what hierarchy level(s) they want!)
- [ ] Consider: .attrib[level] = “item”
- [ ] Ask L about adding dates in 046 in addition to 264?
- [ ] Make more to-do’s
- [ ] Add back in marc: namespace prefixes at end of conversion
        re.sub(r'<([A-Za-z0-9_:-]+)(\s|>)', r'<marc:\1\2', authority_100_110_str)
        re.sub(r'</([A-Za-z0-9_:-]+)>', r'</marc:\1>', authority_100_110_str)


## Backlog

## Completed

- [X] Write 245
- [X] Update 264 in spreadsheet
- [X] Write 264
- [X] Explore marcao plugin (in plugins folder, not in config)
        https://github.com/pulibrary/dacs_handbook/blob/main/aspace_4_docker.md 
        https://github.com/hudmol/as_marcao 
        https://github.com/hudmol/user_defined_in_basic 
- [X] Explore full tischler marcao export
- [X] Explore converting marcao mapper into Python
- [X] Cross-check current fields against marcao mapper logic
- [X] Finish 100_110

## Review Notes

---
*Updated by Claude Code*
