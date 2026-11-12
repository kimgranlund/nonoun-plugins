"""Local dashboard renderer; inserts data through textContent, not HTML."""
import json, subprocess
from pathlib import Path

def render(report,output,kit=None):
    """kit: optional UI kit directory exposing scripts/api.mjs; without one the dashboard is plain HTML."""
    css='';api=kit/'scripts/api.mjs' if kit else None
    if api and api.exists():
        code='const a=await import('+json.dumps(api.as_uri())+');const identity=a.describeKit();process.stdout.write(JSON.stringify({identity,css:a.getAssetBundle().css}));'
        try:
            p=subprocess.run(['node','--input-type=module','-e',code],capture_output=True,text=True,timeout=15,check=True)
            data=json.loads(p.stdout);css=data['css'];report['styling']={'state':'ui-kit','identity':data['identity']}
        except (OSError,subprocess.SubprocessError,ValueError,KeyError):report['styling']={'state':'plain-html','reason':'Verified UI kit CSS unavailable; no download attempted.'}
    else:report['styling']={'state':'plain-html','reason':'No UI kit supplied; plain HTML.'}
    (output/'kit.css').write_text(css)
    data=json.dumps(report).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    source=(Path(__file__).resolve().parents[1]/'assets/dashboard.html').read_text()
    (output/'index.html').write_text(source.replace('__REPORT_DATA__',data))
