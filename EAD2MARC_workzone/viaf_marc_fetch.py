#!/usr/bin/env python3
"""
viaf_marc_fetch.py

Usage:
  python viaf_marc_fetch.py 120307688

What it does:
- Tries a set of likely URL patterns for the per-record MARCXML that VIAF serves.
- Follows redirects and checks Content-Type (and content) to verify MARCXML.
- Saves the file and prints the final URL.
- If no pattern works, optionally falls back to streaming the VIAF bulk MARCXML dump
  and returns the single MARCXML record for the VIAF id.

Only dependency: requests (pip install requests)
"""

import sys
import os
import requests
from urllib.parse import urljoin

# === Configuration ===
VIAF_ID = sys.argv[1] if len(sys.argv) > 1 else "120307688"
OUT_DIR = "."
OUT_BASENAME = f"viaf_{VIAF_ID}_marc21.xml"
OUT_PATH = os.path.join(OUT_DIR, OUT_BASENAME)

# Candidate URL suffixes to try (order matters: most likely first)
CANDIDATE_SUFFIXES = [
    "/marc21.xml?download=1",
    "/marc21.xml",
    "/marc21?download=1",
    "/marc21",
    "/marcxml?download=1",
    "/marcxml",
    "/marc?download=1",
    "/marc",
    "/marcxml.xml",
    "/marc21.mrc?download=1",
    "/marc21.mrc",
    "/cluster.xml",          # less likely but harmless to try
    "/cluster",              # fallback
]

BASE = f"https://viaf.org/viaf/{VIAF_ID}"

HEADERS = {
    "User-Agent": "python-requests/viaf-marc-fetcher (contact: you@yourdomain.example)"
}

# MIME types that indicate MARCXML or XML MARC payload
ACCEPTABLE_CONTENT_TYPES = [
    "application/xml",
    "text/xml",
    "application/marcxml+xml",
    "application/marc21+xml",
    "application/octet-stream",  # sometimes downloads are octet-stream
    "application/x-gzip",
    "application/zip",
    "application/x-binary",
    "text/plain",
]

# simple heuristic to spot MARCXML in body bytes
MARCXML_SNIPPETS = [b"<record", b"<collection", b"<controlfield", b"<datafield", b"<marc:record"]

def looks_like_marcxml(content_bytes: bytes) -> bool:
    # fast check: does it contain expected MARCXML markers in first chunk?
    head = content_bytes[:4096].lower()
    for s in MARCXML_SNIPPETS:
        if s in head:
            return True
    return False

def try_candidate_urls():
    session = requests.Session()
    session.headers.update(HEADERS)
    for suffix in CANDIDATE_SUFFIXES:
        url = BASE + suffix
        try:
            # use stream=True so we can inspect a little of the body without downloading everything
            with session.get(url, stream=True, allow_redirects=True, timeout=30) as r:
                status = r.status_code
                if status >= 400:
                    # not found / server error -> skip
                    # print(f"Trying {url}: HTTP {status} -> skip")
                    continue

                ctype = r.headers.get("Content-Type", "").split(";")[0].strip().lower()
                # read a small chunk to inspect
                chunk = b""
                try:
                    chunk = r.raw.read(4096) or b""
                except Exception:
                    # fallback: read via iter_content
                    for piece in r.iter_content(1024):
                        chunk += piece
                        if len(chunk) >= 4096:
                            break

                # If content-type suggests XML or we detect MARCXML in bytes, treat as success
                if any(t in ctype for t in ACCEPTABLE_CONTENT_TYPES) or looks_like_marcxml(chunk):
                    # Save full content (streaming)
                    print(f"[OK] Candidate URL: {url}  (Content-Type: {ctype or 'unknown'})")
                    # write the chunk we already read and then stream the rest
                    with open(OUT_PATH, "wb") as out:
                        out.write(chunk)
                        for data in r.iter_content(chunk_size=8192):
                            if data:
                                out.write(data)
                    print("Saved file to:", OUT_PATH)
                    return url
                else:
                    # Not obviously MARCXML; skip
                    # print(f"Trying {url}: content-type {ctype} and first bytes do not look like MARCXML -> skip")
                    continue

        except requests.exceptions.RequestException as e:
            # network error / timeout -> skip candidate
            # print(f"Trying {url}: request exception {e} -> skip")
            continue
    return None

# --- Fallback: stream the bulk MARCXML dump and search for VIAF id ---
# (Large file but streaming avoids full download; change DUMP_URL if VIAF posts a newer dump)
DUMP_URL = "https://viaf.org/viaf/data/viaf-20240804-clusters-marc21.xml.gz"

def fallback_search_dump(viaf_id: str):
    import gzip
    import io

    print("Fallback: streaming VIAF MARCXML dump and searching for VIAF id:", viaf_id)
    # we'll attempt to stream via requests and a GzipFile wrapper
    try:
        with requests.get(DUMP_URL, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            # wrap resp.raw (a file-like object) with gzip
            # requests' raw is not buffered - wrap with io.BufferedReader for better performance
            raw = resp.raw
            buf = io.BufferedReader(raw)
            gz = gzip.GzipFile(fileobj=buf)
            target = viaf_id.encode("utf-8")
            i = 0
            for raw_line in gz:
                i += 1
                if target in raw_line:
                    try:
                        rec_text = raw_line.decode("utf-8")
                    except Exception:
                        rec_text = raw_line.decode("latin1", errors="replace")
                    with open(OUT_PATH, "w", encoding="utf-8") as f:
                        f.write(rec_text)
                    print(f"Found record in dump (approx line {i}); saved to {OUT_PATH}")
                    # no single URL here — this returns the MARCXML record itself
                    return "DUMP_MATCH"
                if (i % 200000) == 0:
                    print(f"  scanned ~{i} records...")
    except Exception as e:
        print("Error streaming dump:", e)
        return None
    print("VIAF id not found in dump or dump unavailable.")
    return None

def main():
    print("VIAF id:", VIAF_ID)
    print("Trying candidate URLs at:", BASE)
    url = try_candidate_urls()
    if url:
        print("SUCCESS. Use this URL to download the MARCXML in future:", url)
        return

    # Candidate approaches didn't find a direct downloadable MARCXML link.
    # Try fallback (bulk dump)
    res = fallback_search_dump(VIAF_ID)
    if res:
        if res == "DUMP_MATCH":
            print("SUCCESS via dump. No single per-record URL available; file saved at", OUT_PATH)
        else:
            print("Fallback returned:", res)
        return

    print("\nAll attempts failed.")
    print("If the VIAF page generates the MARC link purely in browser JS, the only way")
    print("to get the *same* downloadable URL programmatically is to run a browser engine")
    print("to allow the page JS to execute (Selenium or Playwright). If you want, I can")
    print("provide a short Playwright or Selenium script that extracts the exact href and downloads the file.")

if __name__ == "__main__":
    main()
