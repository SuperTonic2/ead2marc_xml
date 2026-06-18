# EAD2MARC_XML

A browser-based tool that converts ArchivesSpace **EAD3** finding aids into **MARCXML** records for use in MARCEdit or ingest.

Originally built by Sarah Helen Carter for the Indiana University Cook Music Library.

## Quick start

1. Open **[supertonic2.github.io/ead2marc_xml](https://supertonic2.github.io/ead2marc_xml/)**. Should work in any browser, but tested most extensively with Firefox.
2. Pick the EAD3 XML file you want to convert (e.g., a finding aid exported from ArchivesSpace)
3. Choose how you want to parse it:
   - **By record ID** — convert one specific record
   - **By hierarchy level** — convert all records at a given level (collection, file, item, etc.)
4. (Optional) Customize codes used in 035/040/049
5. Click **Convert** and download the resulting MARCXML

The first run will take a moment while your browser downloads Pyodide (the in-browser Python interpreter). Subsequent runs are faster.

## What it does

- **Reads** EAD3 XML (one record, or every record at a chosen hierarchy level)
- **Maps** archival metadata to MARC21 fields (008, 040, 1XX, 245, 264, 300, 5XX, 6XX, 7XX, 856, etc.)
- **Looks up** authority records from id.loc.gov to populate name/subject/genre fields (LCNAF, LCSH, LCGFT)
- **Writes** valid MARCXML, ready to import into a library catalog management system

`id.loc.gov` is the only external service the tool calls. No metadata or finding-aid content is sent anywhere else.

## Fields produced

The converter generates the following MARC fields when the EAD3 source contains the data to populate them. Subfield lists show what the script emits via its manual-construction path; authority-fetched headings (LCNAF/LCSH/LCGFT lookups) may carry additional subfields beyond those listed when the authority record contains them.

### Leader and control fields

| Element | OCLC Bibformats name |
| --- | --- |
| Leader | Leader (all 24 positions populated; no subfields) |
| 008 | Fixed-Length Data Elements (all 40 positions populated; creation dates only — see Limitations) |

### Numbers and codes (0XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 020 | $a | International Standard Book Number |
| 022 | $a | International Standard Serial Number |
| 023 | $a | Cluster ISSN |
| 024 | $a, $2 | Other Standard Identifier |
| 026 | $e | Fingerprint Identifier |
| 027 | $a | Standard Technical Report Number |
| 028 | $a | Publisher or Distributor Number |
| 035 | $a | System Control Number (collection-level only) |
| 040 | $a, $b, $c, $e | Cataloging Source |
| 041 | $a, $2 | Language Code |
| 049 | $a | Local Holdings |
| 050 | $a, $b | Library of Congress Call Number |
| 082 | $a, $b | Dewey Decimal Classification Number |
| 086 | $a | Government Document Classification Number |

### Main entries (1XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 100 | $a, $d, $e (+ authority-fetched) | Main Entry — Personal Name |
| 110 | $a, $e (+ authority-fetched) | Main Entry — Corporate Name |

### Title and date (2XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 245 | $a | Title Statement |
| 246 | $a | Varying Form of Title |
| 264 | $c | Production, Publication, Distribution, Manufacture, and Copyright Notice (multiple instances with different indicator 2 values per source) |

### Physical description and content (3XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 300 | $a, $c, $f | Physical Description (IUL ordering — see Limitations) |
| 336 | $a, $b, $2 | Content Type |
| 337 | $a, $b, $2 | Media Type |
| 338 | $a, $b, $2 | Carrier Type |
| 351 | $a | Organization and Arrangement of Materials |

### Notes (5XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 500 | $a | General Note (built from `<odd>`, `<dimensions>`, `<physdesc>`, `<materialspec>`, `<physloc>`, `<phystech>`, `<physfacet>`, `<processinfo>`, `<separatedmaterial>`) |
| 506 | $a | Restrictions on Access Note |
| 520 | $a | Summary, Etc. |
| 524 | $a | Preferred Citation of Described Materials Note |
| 535 | $a | Location of Originals/Duplicates Note |
| 540 | $a | Terms Governing Use and Reproduction Note |
| 541 | $a | Immediate Source of Acquisition Note |
| 544 | $n | Location of Other Archival Materials Note |
| 545 | $a | Biographical or Historical Data |
| 546 | $a | Language Note |
| 555 | $a, $u | Cumulative Index/Finding Aids Note |
| 561 | $a | Ownership and Custodial History |
| 583 | $a | Action Note |
| 584 | $a | Accumulation and Frequency of Use Note |

### Subject access (6XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 600 | $a, $d, $e, $2 (+ authority-fetched) | Subject Added Entry — Personal Name |
| 610 | $a, $e, $2 (+ authority-fetched) | Subject Added Entry — Corporate Name |
| 630 | $a, $2, $v/$x/$y/$z (+ authority-fetched) | Subject Added Entry — Uniform Title |
| 650 | $a, $2, $v/$x/$y/$z (+ authority-fetched) | Subject Added Entry — Topical Term |
| 651 | $a, $2, $v/$x/$y/$z (+ authority-fetched) | Subject Added Entry — Geographic Name |
| 655 | $a, $2, $v/$x/$y/$z (+ authority-fetched) | Index Term — Genre/Form |
| 656 | $a, $2 | Index Term — Occupation |
| 657 | $a, $2 | Index Term — Function |
| 690 | $a, $2, $5 | Local Subject Added Entry — Topical Term |

### Added entries (7XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 700 | $a, $d, $e (+ authority-fetched) | Added Entry — Personal Name |
| 710 | $a, $e (+ authority-fetched) | Added Entry — Corporate Name |

### Electronic location (8XX)

| Tag | Subfields | OCLC Bibformats name |
| --- | --- | --- |
| 856 | $3, $u | Electronic Location and Access (finding aid URL) |

## Does the conversion process involve AI or Large Language Models (LLMs)?

**No.** The actual conversion process does not utilize any AI agents or LLMs. It is run through a Python script. When you use the tool, no AI is invoked. Your EAD file and the resulting MARCXML stay between your browser and id.loc.gov. No finding-aid content is sent to OpenAI, Anthropic, or any other AI service.

AI tools were used in the creation of this tool for development support purposes. Primary uses were debugging Python scripts, drafting documentation, and building the browser UI. Specifically, ChatGPT-5 was used in the early stages of the process for debugging, and Claude Opus (versions 4.5, 4.6, and 4.7) was utilized throughout the majority of the project. All information created by AI has been manually reviewed/revised. A log of major AI-assisted edits is available in `ai_changelog.md`.

## Have EAD 2002 files?

This tool reads **EAD3** only. EAD 2002 (deprecated by SAA in 2014) needs to be transformed to EAD3 first. Two ways to do that:

- **From ArchivesSpace** — ASpace v2.2.0 and onward include an EAD3 export option. If you have finding aids in ASpace, just export them as EAD3 directly by checking Export &#8594; Download EAD &#8594; &#9745; EAD3 schema. For additional information, see the [ASpace Documentation on Exporting EAD](https://docs.atlas-sys.com/archivesspace/importing-and-exporting/export-ead).
- **From raw EAD 2002 XML files** — use the official Society of American Archivists [EAD2002toEAD3 stylesheet](https://github.com/SAA-SDT/EAD2002toEAD3) to transform your file.

## Limitations

- **Main entry defaults to first creator.** The first `<origination>` element in the EAD becomes the 100/110. Catalogers must manually swap 100↔700 (or 110↔710) in MARCEdit if a different creator should be the main entry.
- **LCNAF used as-is.** When an authority record is fetched, missing subfields like `$d` (life dates) are NOT supplemented from EAD source data. Per IUL's "LCNAF as-is" policy.
- **Family names skip authority lookups.** `<famname>` elements are always constructed manually from EAD text content — no id.loc.gov lookup is attempted.
- **VIAF disabled in the browser version.** VIAF doesn't send CORS headers, so the in-browser tool cannot fall back to VIAF when LCNAF returns nothing. The standalone Python script can re-enable VIAF by setting `VIAF_ENABLED = True` at the top.
- **No 006, 007, 046, 852, or 648.** Not in IUL's minimum-record requirements (and 648 temporal terms don't appear in ASpace EAD exports).
- **6XX subdivisions only for authorized headings.** Non-authorized corpnames/titles/subjects/genre-form terms aren't broken into separate subfields because the EAD export doesn't separate them.
- **Plain `<unitdate>` text ignored by 008.** Only `<unitdatestructured>` elements (with `<datesingle>`/`<daterange>` children) feed 008. Plain text dates like "circa 1970" still appear in 264 $c but produce `uuuu` in 008.
- **008 reflects creation dates only.** Dates with `datechar="creation"` feed 008 positions 7-14; copyright/broadcast/publication dates are filtered out. Falls back to all non-creation dates if no creation date exists.
- **300 subfield order non-standard.** Order is `a, c, a, f` (instead of MARC-canonical `a, b, c, e, f`) per IUL convention; some strict MARC validators may flag this.
- **035 collection-level only.** The 035 system control number is emitted for collection-level records, not for items.
- **HTML markup in notes stripped.** `<strong>`, `<em>`, and similar inline markup inside EAD notes are removed during text extraction; plain text content survives.
- **id.loc.gov timeout fallback.** If id.loc.gov is unreachable or slow (default 10-second timeout), the affected field falls back to manually-constructed content and a `<!-- NOTE: ... -->` comment is added to the record so catalogers can spot and review.

## Running the Python script locally

If you would prefer to run the underlying Python locally using the command line:

```bash
# Clone the repo
git clone https://github.com/SuperTonic2/EAD2MARC_XML.git
cd EAD2MARC_XML

# (Optional but recommended) set up a virtual environment
python -m venv venv
venv\Scripts\activate           # Windows
source venv/bin/activate        # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Edit the input path at the bottom of the script, then run:
python workzone/EAD2MARCv2.0.py
```

## Rebuilding the browser bundle

The browser version (`docs/index.html`) is built from the Python script (`EAD2MARCv2.0.py`) and an HTML shell (`ead2marc_stage2.html`). To rebuild after editing the Python script:

```bash
python browser_ui/build_bundle.py
```

This writes the bundled HTML to two locations:

- `browser_ui/ead2marc_stage2_bundled.html` — for local testing (open from disk)
- `docs/index.html` — the file GitHub Pages serves

Commit and push both files. `docs/index.html` is what updates the live site; keeping `ead2marc_stage2_bundled.html` in sync prevents stale-bundle confusion on future rebuilds.

## References

- [EAD Official Site (Library of Congress)](https://www.loc.gov/ead/)
- [MARC21 Format for Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
- [id.loc.gov Authorities](https://id.loc.gov/)
- [ArchivesSpace](https://archivesspace.org/)
- [Pyodide](https://pyodide.org/)
- [marc_ao](https://github.com/hudmol/as_marcao)

## License

[MIT](https://opensource.org/license/mit)

Copyright 2026 Sarah Helen Carter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
