"""Regression controls for standalone rendering; browser execution is checked separately."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from atlas_build import build

ROOT = Path(__file__).resolve().parent.parent

class RendererTests(unittest.TestCase):
    def test_requires_pinned_renderer_and_initialization(self):
        page = build(json.loads((ROOT / 'assets/atlas.example.json').read_text()))
        cases = [
            (page, 0),
            (re.sub(r'<script id="atlas-mermaid-renderer".*?</script>', '', page, flags=re.S), 1),
            (page.replace('await mermaid.run(', 'await missing.run('), 1),
            (page.replace('data-sha256="', 'data-sha256="0', 1), 1),
            (re.sub(r'(<script id="atlas-mermaid-renderer"[^>]*>)', r'\1/* modified */', page, count=1), 1),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for index, (content, expected) in enumerate(cases):
                path = Path(tmp) / f'{index}.html'
                path.write_text(content)
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/atlas_check.py'), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout)

if __name__ == '__main__':
    unittest.main()
