# EAD2MARC


A web-based tool for converting EAD (Encoded Archival Description) finding aids to MARC (Machine-Readable Cataloging) records.

## What It Does

- **Upload** EAD3 XML files (for EAD 2002, see [the note below](#have-ead-2002-files))
- **Convert** archival metadata to MARC21 format
- **Download** resulting MARC records for import into library catalogs

## Have EAD 2002 files?

This tool reads **EAD3** only. EAD 2002 (deprecated by SAA in 2014) needs to be transformed to EAD3 first. Two ways to do that:

- **From ArchivesSpace** — most ASpace versions (v2.6+ I believe, and definitely v3 and v4) include an **EAD3 export option** alongside the EAD 2002 one. If you have finding aids in ASpace, just export them as EAD3 directly — no transformation step needed.
- **From raw EAD 2002 XML files** — use the official Society of American Archivists [EAD2002toEAD3 stylesheet](https://github.com/SAA-SDT/EAD2002toEAD3) to transform first, then feed the output to this tool. One-liner with `xsltproc` (or any XSLT 1.0/2.0 processor):

  ```bash
  xsltproc ead2002toead3.xsl input_ead2002.xml > output_ead3.xml
  ```

## Tech Stack

- **Python 3.11+** — core conversion logic
- **Flask** — web interface
- **lxml** — XML parsing
- **pymarc** — MARC record generation
- **Vercel** — hosting

## Local Development

```bash
# Clone the repo
git clone git@github.com:plcarterco/EAD2MARC.git
cd EAD2MARC

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
flask run
```

Then visit http://localhost:5000

## Project Structure

```
EAD2MARC/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel deployment config
├── templates/          # HTML templates
├── static/             # CSS, JS, images
└── converter/          # EAD→MARC conversion logic
```

## Deployment

This repo is connected to Vercel. Pushing to `main` automatically deploys to production.

## References

- [EAD Official Site (Library of Congress)](https://www.loc.gov/ead/)
- [MARC21 Format for Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
- [pymarc Documentation](https://pymarc.readthedocs.io/)

## License

MIT
