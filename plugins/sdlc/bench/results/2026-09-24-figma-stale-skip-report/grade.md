hidden_check: fail
exit_code: 1

```
  pass  resolveface
  pass  sweep
  pass  compliance
  pass  regroup
  pass  primevalue
  pass  readfloat
  pass  styles
  pass  fontmodes
  pass  libraryparity
  pass  librarymode
  pass  adoptconsent
  pass  librarygrammar
  pass  fontprimslibrary
  pass  report-static

FAIL: 4 gate failure(s)
  staleskip: a fourth color apply (drop, re-add, drop) reported no skipped names (res4.skipped=undefined): the "_deprecated/" collision must be reported, not silently left live
  staleskipfloat: a fourth float apply (drop, re-add, drop) reported no skipped names (res4f.skipped=undefined): the "_deprecated/" collision must be reported
  staleskipfontprim: a fourth Font Primitives apply (drop, re-add, drop) reported no skipped names (libraryReport.skipped=[]): the "_deprecated/" collision must be reported
  staleskipnotice: a kept stale Type/Geometry breakpoint mode under libraryMode:true produced no "N stale kept" notice: "Applied 1 type/geometry variable across 1 collection"
```
