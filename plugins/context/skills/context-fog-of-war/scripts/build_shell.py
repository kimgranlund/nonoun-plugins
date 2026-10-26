#!/usr/bin/env python3
"""Maintainer-only shell rebuild. End users need only fog.py and the shipped shell."""
import argparse
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--kit',type=Path,required=True,help='Authoritative base-ui skill directory')
p.add_argument('--node',default='node')
a=p.parse_args()
with tempfile.TemporaryDirectory() as folder:
    out=Path(folder)/'shell.html'
    subprocess.run([a.node,str(a.kit/'scripts/build.mjs'),str(root/'assets/fragment.html'),str(out)],check=True)
    text=out.read_text().replace('<title>UI specimen</title>','<title>Context Fog-of-War</title>')
    text=text.replace('/*__FOG_CSS__*/',(root/'assets/tokens.css').read_text()+'\n'+(root/'assets/app.css').read_text())
    text=text.replace('/*__FOG_JS__*/',(root/'assets/shell-controls.js').read_text()+'\n'+(root/'assets/exposure.js').read_text()+'\n'+(root/'assets/payloads.js').read_text()+'\n'+(root/'assets/atlas.js').read_text()+'\n'+(root/'assets/diagnostics.js').read_text()+'\n'+(root/'assets/story.js').read_text()+'\n'+(root/'assets/charts.js').read_text()+'\n'+(root/'assets/workflow.js').read_text()+'\n'+(root/'assets/app.js').read_text())
    (root/'assets/shell.html').write_text(text)
