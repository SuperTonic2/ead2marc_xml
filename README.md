# EAD2MARC

A web-based tool for converting EAD (Encoded Archival Description) finding aids to MARC (Machine-Readable Cataloging) records.

## What It Does

- **Upload** EAD XML files (EAD2002 or EAD3)
- **Convert** archival metadata to MARC21 format
- **Download** resulting MARC records for import into library catalogs

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
