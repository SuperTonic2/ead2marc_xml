# EAD2MARC_XML

Originally built by Sarah Helen Carter for the Indiana University Cook Music Library.

A browser-based tool that converts ArchivesSpace **EAD3** finding aids into **MARCXML** records for ingest into a library catalog.

## Quick start

1. Open **[supertonic2.github.io/EAD2MARC_XML](https://supertonic2.github.io/EAD2MARC_XML/)**. Should work in any browser, but tested most extensively with Firefox.
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

## Does the conversion process involve AI or Large Language Models (LLMs)?

**No.** The actual conversion process does not utilize any AI agents or LLMs. It is run through a Python script. When you use the tool, no AI is invoked. Your EAD file and the resulting MARCXML stay between your browser and id.loc.gov. No finding-aid content is sent to OpenAI, Anthropic, or any other AI service.

AI tools were used in the creation of this tool for development support purposes. Primary uses were debugging Python scripts, drafting documentation, and building the browser UI. Specifically, ChatGPT-5 was used in the early stages of the process for debugging, and Claude Opus (versions 4.5, 4.6, and 4.7) was utilized throughout the majority of the project. All information created by AI has been manually reviewed/revised. A log of major AI-assisted edits is available in `ai_changelog.md`.

## Have EAD 2002 files?

This tool reads **EAD3** only. EAD 2002 (deprecated by SAA in 2014) needs to be transformed to EAD3 first. Two ways to do that:

- **From ArchivesSpace** — most ASpace versions (v2.6+ I believe, and definitely v3 and v4) include an **EAD3 export option** alongside the EAD 2002 one. If you have finding aids in ASpace, just export them as EAD3 directly — no transformation step needed.
- **From raw EAD 2002 XML files** — use the official Society of American Archivists [EAD2002toEAD3 stylesheet](https://github.com/SAA-SDT/EAD2002toEAD3) to transform first, then feed the output to this tool. One-liner with `xsltproc` (or any XSLT 1.0/2.0 processor):

  ```bash
  xsltproc ead2002toead3.xsl input_ead2002.xml > output_ead3.xml
  ```

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

If you'd rather skip the browser and run the converter on the command line (useful for batch jobs or for extending the script), you can run the underlying Python directly.

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
python EAD2MARC_workzone/EAD2MARCv2.0.py
```

## Rebuilding the browser bundle

The browser version (`docs/index.html`) is built from the Python script (`EAD2MARCv2.0.py`) and an HTML shell (`ead2marc_stage2.html`). To rebuild after editing the Python script:

```bash
python EAD2MARC_workzone/sandboxes/build_bundle.py
```

This writes the bundled HTML to two locations:

- `EAD2MARC_workzone/sandboxes/ead2marc_stage2_bundled.html` — for local testing (open from disk)
- `docs/index.html` — the file GitHub Pages serves

Commit and push both files. `docs/index.html` is what updates the live site; keeping `ead2marc_stage2_bundled.html` in sync prevents stale-bundle confusion on future rebuilds.

## References

- [EAD Official Site (Library of Congress)](https://www.loc.gov/ead/)
- [MARC21 Format for Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
- [id.loc.gov Authorities](https://id.loc.gov/)
- [ArchivesSpace](https://archivesspace.org/)
- [Pyodide](https://pyodide.org/)

## License

[MIT](https://opensource.org/license/mit)

Copyright 2026 Sarah Helen Carter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
