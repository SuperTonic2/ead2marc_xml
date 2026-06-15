"""Build EAD2MARC_XML browser bundle.

Reads:
  - workzone/EAD2MARCv2.0.py        (the converter script)
  - browser_ui/ead2marc_stage2.html  (the picker-version UI)

Writes:
  - browser_ui/ead2marc_stage2_bundled.html
  - docs/index.html  (the GitHub Pages deployment copy)

What it does:
  Takes the converter script's function definitions (everything before the
  top-level `tree = etree.parse(...)` execution block), base64-encodes them,
  and embeds them directly in a copy of the Stage 2 HTML. The resulting file
  is fully self-contained — no separate script picker needed — and is what
  you would distribute to catalogers or deploy to GitHub Pages.

Re-run this script any time EAD2MARCv2.0.py changes, so the bundle stays
in sync with the latest converter logic.

Usage:
  python build_bundle.py

The script uses paths relative to its own location, so it works no matter
where you invoke it from.
"""

import base64
import sys
from pathlib import Path

# Paths relative to this script's location, not the current working directory.
HERE = Path(__file__).resolve().parent          # .../browser_ui
REPO_ROOT = HERE.parent                         # repo root
WORKZONE = REPO_ROOT / "workzone"      # converter script lives here

SCRIPT_PATH = WORKZONE / "EAD2MARCv2.0.py"
HTML_PICKER_PATH = HERE / "ead2marc_stage2.html"
HTML_BUNDLED_PATH = HERE / "ead2marc_stage2_bundled.html"
# (This portion of code was generated utilizing Claude Opus 4.7)
PAGES_INDEX_PATH = REPO_ROOT / "docs" / "index.html"

# Marker that separates function definitions (above) from top-level execution
# (below). Everything before this line is what we embed in the bundle.
BOUNDARY_MARKER = b"tree = etree.parse("


def read_script_definitions() -> bytes:
    """Returns the function-definitions portion of v2.0.py as bytes."""
    if not SCRIPT_PATH.exists():
        sys.exit(f"ERROR: converter script not found at {SCRIPT_PATH}")
    raw = SCRIPT_PATH.read_bytes()
    idx = raw.find(BOUNDARY_MARKER)
    if idx == -1:
        sys.exit(
            f"ERROR: could not find boundary marker {BOUNDARY_MARKER!r} in "
            f"{SCRIPT_PATH}. Has the top-level execution block moved or "
            f"been renamed?"
        )
    return raw[:idx]


def patch_html(html: str, source_b64: str) -> str:
    """Applies the four bundling substitutions to the picker-version HTML."""

    # 0. Inject a "do not edit" banner just after the doctype.
    # (This portion of code was generated utilizing Claude Opus 4.7)
    generated_banner = (
        "<!--\n"
        "  GENERATED FILE — DO NOT EDIT.\n"
        "  Source: browser_ui/ead2marc_stage2.html + workzone/EAD2MARCv2.0.py\n"
        "  Rebuild: python browser_ui/build_bundle.py\n"
        "-->"
    )
    html = html.replace("<!DOCTYPE html>", f"<!DOCTYPE html>\n{generated_banner}")

    # 1. Remove the script picker UI block.
    picker_ui_old = (
        '<div class="field">\n'
        '      <span class="field-label">Select your <code>EAD2MARCv2.0.py</code> '
        'file (one folder up from this HTML):</span>\n'
        '      <input type="file" id="scriptPicker" accept=".py" disabled>\n'
        '    </div>\n'
        '    <div id="scriptStatus" class="status pending hidden">Waiting for script…</div>'
    )
    picker_ui_new = (
        '<div id="scriptStatus" class="status pending hidden">'
        'Bundled script will load automatically.</div>'
    )
    assert picker_ui_old in html, "picker_ui_old block not found in HTML"
    html = html.replace(picker_ui_old, picker_ui_new)

    # 2. Inject the base64-encoded source + a small UTF-8-safe decoder helper
    #    immediately before the existing `let pyodide = null;` line.
    js_marker_old = "let pyodide = null;"
    js_marker_new = (
        f'const V184_SOURCE_B64 = "{source_b64}";\n\n'
        f"    function decodeBundledSource() {{\n"
        f"      const bytes = Uint8Array.from("
        f"atob(V184_SOURCE_B64), c => c.charCodeAt(0));\n"
        f"      return new TextDecoder('utf-8').decode(bytes);\n"
        f"    }}\n\n"
        f"    let pyodide = null;"
    )
    assert js_marker_old in html, "let pyodide = null; line not found"
    html = html.replace(js_marker_old, js_marker_new)

    # 3. Replace the file-picker event listener with a bundled-source loader.
    picker_handler_old = (
        "document.getElementById('scriptPicker').addEventListener('change', async (e) => {\n"
        "      const file = e.target.files[0];\n"
        "      if (!file) return;\n"
        "      setScriptStatus(`Loading ${file.name}…`, 'pending');\n"
        "      try {\n"
        "        const src = await file.text();\n"
        "        const marker = 'tree = etree.parse(';\n"
        "        const idx = src.indexOf(marker);\n"
        "        if (idx === -1) {\n"
        "          setScriptStatus('Could not find boundary marker in script. Wrong file?', 'fail');\n"
        "          return;\n"
        "        }\n"
        "        const defsOnly = src.slice(0, idx);\n"
        "\n"
        "        pyodide.globals.set('script_src', defsOnly);\n"
        "        await pyodide.runPythonAsync(`exec(script_src, globals())`);\n"
        "\n"
        "        // Define the convert function in the same globals namespace\n"
        "        await pyodide.runPythonAsync(CONVERTER_PY);\n"
        "\n"
        "        scriptLoaded = true;\n"
        "        setScriptStatus(\n"
        "          `Loaded ${defsOnly.length.toLocaleString()} chars of definitions from ${file.name}. ` +\n"
        "          `Ready to convert.`,\n"
        "          'pass'\n"
        "        );\n"
        "        maybeEnableConvert();\n"
        "      } catch (err) {\n"
        "        setScriptStatus('Script load failed: ' + err.message, 'fail');\n"
        "      }\n"
        "    });"
    )
    picker_handler_new = (
        "async function loadBundledScript() {\n"
        "      const status = document.getElementById('scriptStatus');\n"
        "      status.classList.remove('hidden');\n"
        "      setScriptStatus('Decoding bundled EAD2MARCv2.0.py source…', 'pending');\n"
        "      try {\n"
        "        const defsOnly = decodeBundledSource();\n"
        "        pyodide.globals.set('script_src', defsOnly);\n"
        "        await pyodide.runPythonAsync(`exec(script_src, globals())`);\n"
        "        await pyodide.runPythonAsync(CONVERTER_PY);\n"
        "        scriptLoaded = true;\n"
        "        setScriptStatus(\n"
        "          `Loaded ${defsOnly.length.toLocaleString()} chars of bundled script. Ready to convert.`,\n"
        "          'pass'\n"
        "        );\n"
        "        maybeEnableConvert();\n"
        "      } catch (err) {\n"
        "        setScriptStatus('Bundled script failed to load: ' + err.message, 'fail');\n"
        "      }\n"
        "    }"
    )
    assert picker_handler_old in html, "picker_handler_old block not found"
    html = html.replace(picker_handler_old, picker_handler_new)

    # 4. At the end of bootstrap(), call loadBundledScript instead of waiting
    #    for the user to use the file picker.
    bootstrap_end_old = (
        "setSetupStatus(`Pyodide ${pyodide.version} ready. "
        "Now select your EAD2MARCv2.0.py file.`, 'pass');\n"
        "        document.getElementById('scriptPicker').disabled = false;\n"
        "        maybeEnableConvert();"
    )
    bootstrap_end_new = (
        "setSetupStatus(`Pyodide ${pyodide.version} ready. "
        "Loading bundled script…`, 'pass');\n"
        "        await loadBundledScript();\n"
        "        maybeEnableConvert();"
    )
    assert bootstrap_end_old in html, "bootstrap_end_old block not found"
    html = html.replace(bootstrap_end_old, bootstrap_end_new)

    return html


def main():
    if not HTML_PICKER_PATH.exists():
        sys.exit(f"ERROR: picker HTML not found at {HTML_PICKER_PATH}")

    defs = read_script_definitions()
    source_b64 = base64.b64encode(defs).decode("ascii")

    picker_html = HTML_PICKER_PATH.read_text(encoding="utf-8")
    bundled_html = patch_html(picker_html, source_b64)

    HTML_BUNDLED_PATH.write_text(bundled_html, encoding="utf-8")
    # (This portion of code was generated utilizing Claude Opus 4.7)
    PAGES_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAGES_INDEX_PATH.write_text(bundled_html, encoding="utf-8")

    print(f"Read  {SCRIPT_PATH.name}:         {len(defs):,} bytes (definitions only)")
    print(f"Read  {HTML_PICKER_PATH.name}:     {len(picker_html):,} chars")
    print(f"Wrote {HTML_BUNDLED_PATH.name}: {len(bundled_html):,} chars "
          f"(base64 source: {len(source_b64):,} chars)")
    print(f"Wrote docs/index.html:                same content (GitHub Pages copy)")


if __name__ == "__main__":
    main()
