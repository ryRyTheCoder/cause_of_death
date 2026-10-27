"""Rebuild cemetery_dashboard.html from results/dashboard_data.json.

Run it from submissions/juan_zavala after running the notebook:

    python dashboard_src/build_dashboard.py

The page is assembled from head.html (styles) and body.html (layout and script) in this folder, with the
burial rows embedded and the numbers quoted in its text filled in from results/facts.json, so the finished file works offline in any browser. Fonts load from Google Fonts when
online and fall back to the system font otherwise.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent

data = json.loads((ROOT / 'results' / 'dashboard_data.json').read_text(encoding='utf-8'))
payload = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
assert '</' not in payload, 'the data would close the <script> tag'
facts = json.loads((ROOT / 'results' / 'facts.json').read_text(encoding='utf-8'))['text']
head = (SRC / 'head.html').read_text(encoding='utf-8')
body = (SRC / 'body.html').read_text(encoding='utf-8')
body = re.sub(r'\{\{([a-z0-9_]+)\}\}', lambda m: str(facts[m.group(1)]), body)   # numbers quoted in the text
body = body.replace('__DATA__', payload)

page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + '</head>\n<body>\n' + body + '</body>\n</html>\n')
out = ROOT / 'cemetery_dashboard.html'
out.write_text(page, encoding='utf-8')
print(f'wrote {out.name} ({len(page.encode("utf-8")) / 1e6:.2f} MB, {data["n"]:,} burials)')

# optional: the same page without the document skeleton, for hosts that add their own (used to publish it)
if len(sys.argv) > 2 and sys.argv[1] == '--fragment':
    Path(sys.argv[2]).write_text(head + body, encoding='utf-8')
