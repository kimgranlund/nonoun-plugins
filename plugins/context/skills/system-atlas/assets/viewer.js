/* system-atlas viewer. Lifted from the working reference page (V1 to V4).
   Artifacts cannot load local scripts, so the page template inlines this same
   code inside a <script> tag. Keep the two copies identical. */
(function(){
  var root=document.documentElement,bs=document.querySelectorAll(".scheme button"),saved="";
  try{saved=localStorage.getItem("atlas-scheme")||"";}catch(e){}
  function setScheme(v){ if(v)root.setAttribute("data-scheme",v); else root.removeAttribute("data-scheme"); bs.forEach(function(b){b.setAttribute("aria-pressed",String(b.dataset.v===v));}); try{localStorage.setItem("atlas-scheme",v);}catch(e){} }
  bs.forEach(function(b){b.addEventListener("click",function(){setScheme(b.dataset.v);});}); setScheme(saved);
})();
(function(){
  var dlg=document.getElementById('viewer'),stage=document.getElementById('vstage'),zl=document.getElementById('vzoom'),ttl=document.getElementById('vtitle');
  var svg=null,w=0,h=0,k=1,x=0,y=0,MIN=0.05,MAX=8;
  function apply(){ if(!svg)return; svg.style.transform='translate('+x+'px,'+y+'px) scale('+k+')'; zl.textContent=Math.round(k*100)+'%'; }
  function zoomAt(f,cx,cy){ var nk=Math.min(MAX,Math.max(MIN,k*f)); f=nk/k; x=cx-(cx-x)*f; y=cy-(cy-y)*f; k=nk; apply(); }
  function center(){ return [stage.clientWidth/2,stage.clientHeight/2]; }
  function fit(mode){ var W=stage.clientWidth,H=stage.clientHeight,pad=mode==='width'?24:64; var kw=(W-pad)/w,kh=(H-pad-56)/h; k=mode==='width'?kw:Math.min(kw,kh); k=Math.min(MAX,Math.max(MIN,k)); x=(W-w*k)/2; y=mode==='width'?64:Math.max(56,(H-h*k)/2+20); apply(); }
  function one(){ var c=center(); k=1; x=c[0]-w/2; y=Math.max(64,c[1]-h/2); apply(); }
  var home=null,keep=null,ph=null;
  function open(canvas){
    var src=canvas.querySelector('pre.mermaid svg')||canvas.querySelector('svg'); if(!src||dlg.open)return;
    var r=src.getBoundingClientRect(); var vb=src.viewBox&&src.viewBox.baseVal;
    w=vb&&vb.width?vb.width:r.width; h=vb&&vb.height?vb.height:r.height;
    home=src.parentNode; keep={style:src.getAttribute('style'),width:src.getAttribute('width'),height:src.getAttribute('height')};
    ph=document.createElement('div'); ph.style.height=r.height+'px'; ph.style.width='100%'; home.insertBefore(ph,src);
    svg=src; stage.textContent=''; stage.appendChild(svg);
    svg.setAttribute('width',w); svg.setAttribute('height',h); svg.removeAttribute('style');
    svg.style.setProperty('width',w+'px','important'); svg.style.setProperty('height',h+'px','important'); svg.style.setProperty('max-width','none','important');
    var h2=canvas.closest('section').querySelector('h2'); ttl.textContent=h2?h2.textContent:'';
    dlg.showModal(); k=1;x=0;y=0;apply();
    var m=svg.getBoundingClientRect(); if(m.width>0&&m.height>0){w=m.width;h=m.height;}
    fit('all');
  }
  function restore(){ if(!svg||!home)return; svg.style.transform='';
    ['style','width','height'].forEach(function(a){ if(keep[a]===null)svg.removeAttribute(a); else svg.setAttribute(a,keep[a]); });
    home.insertBefore(svg,ph); ph.remove(); svg=null;home=null;ph=null; }
  document.querySelectorAll('.canvas').forEach(function(c,i){
    var b=document.createElement('button'); b.type='button'; b.className='expand'; b.id='expand-'+i; b.textContent='Open viewer';
    b.addEventListener('click',function(e){e.stopPropagation();open(c);}); c.appendChild(b);
    c.addEventListener('click',function(){open(c);});
  });
  document.getElementById('vin').onclick=function(){var c=center();zoomAt(1.25,c[0],c[1]);};
  document.getElementById('vout').onclick=function(){var c=center();zoomAt(0.8,c[0],c[1]);};
  document.getElementById('vfit').onclick=function(){fit('all');};
  document.getElementById('vwidth').onclick=function(){fit('width');};
  document.getElementById('v100').onclick=one;
  document.getElementById('vclose').onclick=function(){dlg.close();};
  dlg.addEventListener('close',restore);
  stage.addEventListener('wheel',function(e){e.preventDefault(); var r=stage.getBoundingClientRect(); if(e.ctrlKey||e.metaKey){zoomAt(Math.exp(-e.deltaY*0.01),e.clientX-r.left,e.clientY-r.top);} else if(e.shiftKey||Math.abs(e.deltaX)>0){x-=e.deltaX||e.deltaY; y-=e.shiftKey?0:e.deltaY; apply();} else {zoomAt(Math.exp(-e.deltaY*0.0015),e.clientX-r.left,e.clientY-r.top);} },{passive:false});
  var pts=new Map(),last=null,pd=0;
  stage.addEventListener('pointerdown',function(e){stage.setPointerCapture(e.pointerId);pts.set(e.pointerId,[e.clientX,e.clientY]);stage.classList.add('drag');last=[e.clientX,e.clientY];pd=0;});
  stage.addEventListener('pointermove',function(e){ if(!pts.has(e.pointerId))return; pts.set(e.pointerId,[e.clientX,e.clientY]);
    if(pts.size===1){ x+=e.clientX-last[0]; y+=e.clientY-last[1]; last=[e.clientX,e.clientY]; apply(); }
    else if(pts.size===2){ var a=Array.from(pts.values()),d=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]),r=stage.getBoundingClientRect(); if(pd)zoomAt(d/pd,(a[0][0]+a[1][0])/2-r.left,(a[0][1]+a[1][1])/2-r.top); pd=d; } });
  function up(e){pts.delete(e.pointerId);pd=0;if(pts.size===1){last=Array.from(pts.values())[0];}if(!pts.size)stage.classList.remove('drag');}
  stage.addEventListener('pointerup',up);stage.addEventListener('pointercancel',up);
  stage.addEventListener('dblclick',function(e){var r=stage.getBoundingClientRect();zoomAt(1.6,e.clientX-r.left,e.clientY-r.top);});
  dlg.addEventListener('keydown',function(e){ var c=center(),s=80;
    if(e.key==='+'||e.key==='=')zoomAt(1.25,c[0],c[1]); else if(e.key==='-'||e.key==='_')zoomAt(0.8,c[0],c[1]);
    else if(e.key==='0')fit('all'); else if(e.key==='1')one(); else if(e.key==='w')fit('width');
    else if(e.key==='ArrowLeft'){x+=s;apply();} else if(e.key==='ArrowRight'){x-=s;apply();} else if(e.key==='ArrowUp'){y+=s;apply();} else if(e.key==='ArrowDown'){y-=s;apply();} else return; e.preventDefault(); });
  window.addEventListener('resize',function(){if(dlg.open)fit('all');});
})();
