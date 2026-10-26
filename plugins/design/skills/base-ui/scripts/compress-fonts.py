"""Maintainer-only WOFF2 conversion/check; requires fonttools[woff]. No downloads."""
import hashlib,json,sys,tempfile
from pathlib import Path
import fontTools,brotli
from fontTools.ttLib import TTFont,woff2
from fontTools.pens.recordingPen import RecordingPen
root=Path(__file__).resolve().parents[1]/'assets/fonts'
manifest=json.loads((root/'manifest.json').read_text())
check='--check' in sys.argv
results=[]
for face in manifest['faces']:
 source=face.get('source') or {k:face[k] for k in ['file','url','sha256','bytes']}
 src=root/source['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==source['sha256']
 with tempfile.TemporaryDirectory() as tmp:
  output=Path(tmp)/'font.woff2';woff2.compress(src,output)
  a,b=TTFont(src),TTFont(output)
  assert a.getGlyphOrder()==b.getGlyphOrder()
  assert a.getBestCmap()==b.getBestCmap()
  assert a['hmtx'].metrics==b['hmtx'].metrics
  for tag in set(a.keys())-{'GlyphOrder','head','loca','glyf','hmtx','DSIG'}:
   assert a.getTableData(tag)==b.getTableData(tag),(source['file'],tag)
  ga,gb=a.getGlyphSet(),b.getGlyphSet()
  for name in a.getGlyphOrder():
   pa,pb=RecordingPen(),RecordingPen();ga[name].draw(pa);gb[name].draw(pb);assert pa.value==pb.value,(source['file'],name)
  data=output.read_bytes();file=str(Path(source['file']).with_suffix('.woff2'))
  updated={k:face[k] for k in ['family','weight','style']}
  updated.update(file=file,format='woff2',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),source=source)
  if check:assert face==updated and (root/file).read_bytes()==data
  else:(root/file).write_bytes(data);face.clear();face.update(updated)
  results.append({'file':file,'sourceBytes':source['bytes'],'woff2Bytes':len(data),'glyphs':len(a.getGlyphOrder()),'fidelity':'glyph outlines, cmap, metrics and remaining tables equal (head/loca representation and invalidated DSIG signature excluded)'})
manifest['conversion']={'tool':'fontTools.ttLib.woff2.compress','fontTools':fontTools.__version__,'brotli':brotli.__version__,'subset':False}
if not check:(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'result':'PASS WOFF2 conversion fidelity','faces':results,'sourceBytes':sum(x['sourceBytes'] for x in results),'woff2Bytes':sum(x['woff2Bytes'] for x in results)},indent=2))
