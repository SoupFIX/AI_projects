<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Visual Product Search Engine — Live Pipeline</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{
    background:#030010;
    width:100%;min-height:100vh;
    display:flex;align-items:center;justify-content:center;
    overflow:hidden;
  }
  canvas{
    display:block;
    border-radius:18px;
    box-shadow:
      0 0 0 1px rgba(0,255,200,0.12),
      0 0 60px rgba(0,255,200,0.08),
      0 0 120px rgba(180,0,255,0.05),
      0 30px 80px rgba(0,0,0,0.7);
    max-width:100%;
  }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const C=document.getElementById('c');
const cx=C.getContext('2d');
const W=1020,H=570;
C.width=W;C.height=H;

/* ═══════════════════ PALETTE ═══════════════════ */
const P={
  bg:'#04000F',
  pink:'#FF2D78',
  cyan:'#00FFE1',
  gold:'#FFAA00',
  pur:'#C084FC',
  grn:'#34D399',
  blu:'#60A5FA',
  wht:'#FFFFFF',
  dim:'rgba(180,200,255,0.35)'
};

function rgb(h){return[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)]}
function ra(h,a){const[r,g,b]=rgb(h);return`rgba(${r},${g},${b},${a})`}

/* ═══════════════════ LAYOUT ═══════════════════ */
const NY=252;// node center Y
const NODES={
  stl:{x:188,y:NY-90,w:132,h:178,lbl:'STREAMLIT',sub:'localhost:8501',col:P.pink},
  api:{x:360,y:NY-90,w:132,h:178,lbl:'FASTAPI',sub:'localhost:8000',col:P.gold},
  clip:{x:535,y:NY-90,w:140,h:178,lbl:'CLIP MODEL',sub:'ViT-B/32',col:P.pur},
  qdr:{x:722,y:NY-90,w:138,h:178,lbl:'QDRANT DB',sub:'localhost:6333',col:P.cyan},
};
const PX=88,PY=NY;// person center

/* ═══════════════════ TIMING ═══════════════════ */
const CYCLE=17000;
const PHS=[
  {n:'idle',   t0:0,    t1:1200},
  {n:'upload', t0:1200, t1:3400},
  {n:'encode', t0:3400, t1:7000},
  {n:'search', t0:7000, t1:9800},
  {n:'return', t0:9800, t1:12200},
  {n:'display',t0:12200,t1:15500},
  {n:'reset',  t0:15500,t1:17000},
];
function phase(t){
  for(const p of PHS) if(t>=p.t0&&t<p.t1)return{n:p.n,pc:(t-p.t0)/(p.t1-p.t0)};
  return{n:'idle',pc:0};
}

/* ═══════════════════ STARS ═══════════════════ */
const STARS=Array.from({length:220},()=>({
  x:Math.random()*W,y:Math.random()*H,
  r:Math.random()*1.4+0.2,
  ph:Math.random()*Math.PI*2,
  sp:0.0008+Math.random()*0.0025
}));

/* ═══════════════════ PARTICLES ═══════════════════ */
let PARTS=[];
class Pt{
  constructor(fx,fy,tx,ty,col,arc=false){
    this.fx=fx;this.fy=fy;this.tx=tx;this.ty=ty;
    this.col=col;this.arc=arc;
    this.t=0;this.spd=0.006+Math.random()*0.006;
    this.sz=3.5+Math.random()*2.5;
    this.trail=[];this.done=false;
    if(arc){this.mx=(fx+tx)/2;this.my=H-68;}
  }
  pos(t){
    if(this.arc){
      const inv=1-t;
      return{x:inv*inv*this.fx+2*inv*t*this.mx+t*t*this.tx,
             y:inv*inv*this.fy+2*inv*t*this.my+t*t*this.ty};
    }
    return{x:this.fx+(this.tx-this.fx)*t,y:this.fy+(this.ty-this.fy)*t};
  }
  update(){
    this.t+=this.spd;
    if(this.t>=1){this.done=true;return;}
    const p=this.pos(this.t);
    this.trail.unshift(p);
    if(this.trail.length>16)this.trail.pop();
    this.cx=p.x;this.cy=p.y;
  }
  draw(){
    if(!this.trail.length)return;
    const[r,g,b]=rgb(this.col);
    for(let i=0;i<this.trail.length;i++){
      const p=this.trail[i];
      const a=(i/this.trail.length)*0.4;
      const sz=this.sz*(i/this.trail.length)*0.5;
      cx.beginPath();cx.arc(p.x,p.y,sz,0,Math.PI*2);
      cx.fillStyle=`rgba(${r},${g},${b},${a})`;cx.fill();
    }
    const g2=cx.createRadialGradient(this.cx,this.cy,0,this.cx,this.cy,this.sz*5);
    g2.addColorStop(0,`rgba(${r},${g},${b},0.55)`);
    g2.addColorStop(1,'rgba(0,0,0,0)');
    cx.fillStyle=g2;
    cx.beginPath();cx.arc(this.cx,this.cy,this.sz*5,0,Math.PI*2);cx.fill();
    cx.beginPath();cx.arc(this.cx,this.cy,this.sz,0,Math.PI*2);
    cx.fillStyle=`rgba(${r},${g},${b},0.95)`;cx.fill();
    cx.beginPath();cx.arc(this.cx,this.cy,this.sz*0.38,0,Math.PI*2);
    cx.fillStyle='rgba(255,255,255,0.95)';cx.fill();
  }
}

/* ═══════════════════ HELPERS ═══════════════════ */
function rr(x,y,w,h,r){
  cx.beginPath();
  cx.moveTo(x+r,y);cx.lineTo(x+w-r,y);cx.arcTo(x+w,y,x+w,y+r,r);
  cx.lineTo(x+w,y+h-r);cx.arcTo(x+w,y+h,x+w-r,y+h,r);
  cx.lineTo(x+r,y+h);cx.arcTo(x,y+h,x,y+h-r,r);
  cx.lineTo(x,y+r);cx.arcTo(x,y,x+r,y,r);
  cx.closePath();
}
function glow(x,y,radius,col,a){
  const[r,g,b]=rgb(col);
  const gr=cx.createRadialGradient(x,y,0,x,y,radius);
  gr.addColorStop(0,`rgba(${r},${g},${b},${a})`);
  gr.addColorStop(1,'rgba(0,0,0,0)');
  cx.fillStyle=gr;cx.beginPath();cx.arc(x,y,radius,0,Math.PI*2);cx.fill();
}

/* ═══════════════════ BACKGROUND ═══════════════════ */
function drawBG(now){
  cx.fillStyle=P.bg;cx.fillRect(0,0,W,H);

  // Aurora left (pink)
  const a1=cx.createRadialGradient(W*0.18,H*0.4,0,W*0.18,H*0.4,360);
  a1.addColorStop(0,'rgba(200,0,80,0.07)');a1.addColorStop(1,'rgba(0,0,0,0)');
  cx.fillStyle=a1;cx.fillRect(0,0,W,H);
  // Aurora right (cyan)
  const a2=cx.createRadialGradient(W*0.78,H*0.55,0,W*0.78,H*0.55,320);
  a2.addColorStop(0,'rgba(0,180,210,0.06)');a2.addColorStop(1,'rgba(0,0,0,0)');
  cx.fillStyle=a2;cx.fillRect(0,0,W,H);
  // Aurora center (purple)
  const a3=cx.createRadialGradient(W*0.5,H*0.3,0,W*0.5,H*0.3,250);
  a3.addColorStop(0,'rgba(140,0,220,0.04)');a3.addColorStop(1,'rgba(0,0,0,0)');
  cx.fillStyle=a3;cx.fillRect(0,0,W,H);

  // Grid
  cx.strokeStyle='rgba(80,80,180,0.055)';cx.lineWidth=0.5;
  for(let x=0;x<W;x+=55){cx.beginPath();cx.moveTo(x,0);cx.lineTo(x,H);cx.stroke();}
  for(let y=0;y<H;y+=55){cx.beginPath();cx.moveTo(0,y);cx.lineTo(W,y);cx.stroke();}

  // Stars
  for(const s of STARS){
    const a=0.1+0.7*Math.abs(Math.sin(now*s.sp+s.ph));
    cx.beginPath();cx.arc(s.x,s.y,s.r,0,Math.PI*2);
    cx.fillStyle=`rgba(255,255,255,${a})`;cx.fill();
  }

  // Scanline overlay
  for(let y=0;y<H;y+=3){
    cx.fillStyle='rgba(0,0,0,0.04)';
    cx.fillRect(0,y,W,1);
  }
}

/* ═══════════════════ TITLE ═══════════════════ */
function drawTitle(){
  const now=performance.now();
  // Shimmer gradient text
  const shimX=(Math.sin(now*0.001)*0.5+0.5);
  const tg=cx.createLinearGradient(W*0.1,0,W*0.9,0);
  tg.addColorStop(0,P.pink);
  tg.addColorStop(shimX*0.5,P.wht);
  tg.addColorStop(shimX,P.cyan);
  tg.addColorStop(shimX+0.3,P.pur);
  tg.addColorStop(1,P.gold);

  cx.font='bold 15px "Orbitron",monospace';
  cx.textAlign='center';
  cx.fillStyle=tg;
  cx.fillText('⚡  VISUAL PRODUCT SEARCH ENGINE — REAL-TIME PIPELINE',W/2,34);

  cx.font='9.5px "Share Tech Mono",monospace';
  cx.fillStyle=ra(P.cyan,0.45);
  cx.fillText('CLIP ViT-B/32  ·  QDRANT VECTOR DB  ·  FASTAPI  ·  STREAMLIT  ·  512-DIM EMBEDDINGS  ·  COSINE SIMILARITY',W/2,52);

  // Divider line
  const dl=cx.createLinearGradient(0,0,W,0);
  dl.addColorStop(0,'rgba(0,0,0,0)');dl.addColorStop(0.2,ra(P.pink,0.5));
  dl.addColorStop(0.5,ra(P.cyan,0.5));dl.addColorStop(0.8,ra(P.gold,0.5));
  dl.addColorStop(1,'rgba(0,0,0,0)');
  cx.strokeStyle=dl;cx.lineWidth=1;
  cx.beginPath();cx.moveTo(60,60);cx.lineTo(W-60,60);cx.stroke();
}

/* ═══════════════════ PERSON ═══════════════════ */
function drawPerson(ph,pc){
  const x=PX,y=PY;
  cx.save();

  // Chair (back)
  cx.strokeStyle=ra(P.pink,0.2);cx.lineWidth=2;
  cx.beginPath();cx.moveTo(x-22,y+45);cx.lineTo(x-22,y-20);cx.stroke();
  cx.beginPath();cx.moveTo(x-22,y-20);cx.lineTo(x+10,y-20);cx.stroke();

  // Desk
  cx.strokeStyle=ra(P.pink,0.18);cx.lineWidth=2.5;
  cx.beginPath();cx.moveTo(x-50,y+62);cx.lineTo(x+92,y+62);cx.stroke();
  cx.strokeStyle=ra(P.pink,0.1);cx.lineWidth=1.5;
  cx.beginPath();cx.moveTo(x-50,y+62);cx.lineTo(x-50,y+85);cx.stroke();
  cx.beginPath();cx.moveTo(x+92,y+62);cx.lineTo(x+92,y+85);cx.stroke();

  // Laptop base
  cx.fillStyle=ra('#0a0030',0.95);
  rr(x,y+42,78,10,3);cx.fill();
  cx.strokeStyle=ra(P.pink,0.55);cx.lineWidth=1.5;
  rr(x,y+42,78,10,3);cx.stroke();

  // Laptop hinge
  cx.fillStyle=ra(P.pink,0.3);cx.fillRect(x+10,y+41,4,3);
  cx.fillRect(x+64,y+41,4,3);

  // Screen bezel
  cx.fillStyle=ra('#06001C',0.98);
  rr(x+2,y+5,74,37,5);cx.fill();
  cx.strokeStyle=ra(P.pink,0.65);cx.lineWidth=1.5;
  rr(x+2,y+5,74,37,5);cx.stroke();

  // Screen inner
  const sx=x+5,sy=y+8,sw=68,sh=31;
  cx.fillStyle='#020010';rr(sx,sy,sw,sh,3);cx.fill();

  // Screen content
  if(ph==='idle'||ph==='upload'){
    const a=ph==='idle'?0.85:Math.max(0.05,1-pc*1.8);
    // Upload UI on screen
    cx.strokeStyle=ra(P.pink,0.4*a);cx.setLineDash([2,2]);cx.lineWidth=0.7;
    rr(sx+4,sy+3,sw-8,sh-6,2);cx.stroke();cx.setLineDash([]);
    cx.fillStyle=ra(P.pink,0.7*a);
    cx.font='bold 11px monospace';cx.textAlign='center';
    cx.fillText('↑',sx+sw/2,sy+17);
    cx.font='5.5px "Share Tech Mono",monospace';
    cx.fillStyle=ra(P.pink,0.5*a);
    cx.fillText('DROP IMAGE',sx+sw/2,sy+27);
  } else if(ph==='display'||ph==='reset'){
    // Results grid
    const cols=5,bw=(sw-6)/cols,bh=(sh-6)/2;
    const rc=[P.pink,P.gold,P.cyan,P.pur,P.grn,P.blu,P.pink,P.gold,P.cyan,P.pur];
    for(let i=0;i<10;i++){
      const ri=Math.floor(i/cols),ci=i%cols;
      const bx2=sx+3+ci*bw,by=sy+3+ri*bh;
      const d=i*0.06;
      const al=Math.max(0,Math.min(1,(pc-d)*7));
      if(al>0){
        cx.fillStyle=ra(rc[i],al*0.65);
        rr(bx2,by,bw-1,bh-1,1);cx.fill();
        cx.strokeStyle=ra(rc[i],al*0.9);cx.lineWidth=0.4;
        rr(bx2,by,bw-1,bh-1,1);cx.stroke();
      }
    }
  } else {
    // Processing screen
    cx.fillStyle=ra('#00ffe1',0.07);rr(sx,sy,sw,sh,3);cx.fill();
    const dp=(performance.now()*0.003)%1;
    const dots='.'.repeat(Math.floor(dp*4));
    cx.fillStyle=ra(P.gold,0.55);
    cx.font='6px "Share Tech Mono",monospace';cx.textAlign='center';
    cx.fillText('processing'+dots,sx+sw/2,sy+sh/2+2);
  }

  // Screen reflection
  const ref=cx.createLinearGradient(sx,sy,sx+sw*0.4,sy+sh*0.6);
  ref.addColorStop(0,'rgba(255,255,255,0.04)');
  ref.addColorStop(1,'rgba(255,255,255,0)');
  cx.fillStyle=ref;rr(sx,sy,sw,sh,3);cx.fill();

  // ── BODY ──
  const hx=x+30,hy=y-102;
  glow(hx,hy,24,P.pink,0.22);

  // Head
  cx.beginPath();cx.arc(hx,hy,16,0,Math.PI*2);
  cx.fillStyle=ra(P.pink,0.92);cx.fill();
  cx.strokeStyle=ra(P.pink,0.45);cx.lineWidth=1.5;cx.stroke();

  // Hair
  cx.beginPath();cx.arc(hx,hy-8,14,Math.PI,Math.PI*2,false);
  cx.fillStyle=ra('#220044',0.95);cx.fill();
  cx.strokeStyle=ra(P.pur,0.5);cx.lineWidth=1;cx.stroke();

  // Face
  cx.fillStyle=ra('#000010',0.9);
  cx.beginPath();cx.arc(hx-5.5,hy-1,2.2,0,Math.PI*2);cx.fill();
  cx.beginPath();cx.arc(hx+5.5,hy-1,2.2,0,Math.PI*2);cx.fill();
  // Smile
  cx.strokeStyle=ra('#000010',0.9);cx.lineWidth=1.5;
  cx.beginPath();cx.arc(hx,hy+3,6,0.15,Math.PI-0.15);cx.stroke();

  // Neck
  cx.strokeStyle=ra(P.pink,0.8);cx.lineWidth=3.5;
  cx.beginPath();cx.moveTo(hx,hy+16);cx.lineTo(hx,hy+24);cx.stroke();

  // Torso (shirt)
  cx.strokeStyle=ra(P.pink,0.8);cx.lineWidth=3.5;
  cx.beginPath();cx.moveTo(hx,hy+24);cx.lineTo(hx,hy+60);cx.stroke();
  // Shoulders
  cx.beginPath();cx.moveTo(hx-20,hy+30);cx.lineTo(hx+20,hy+30);cx.stroke();

  // Left arm (resting)
  cx.beginPath();cx.moveTo(hx-20,hy+30);cx.lineTo(hx-24,hy+54);cx.stroke();
  cx.beginPath();cx.moveTo(hx-24,hy+54);cx.lineTo(hx-14,hy+60);cx.stroke();

  // Right arm (reaching to laptop)
  cx.beginPath();cx.moveTo(hx+20,hy+30);cx.lineTo(hx+40,hy+45);cx.stroke();
  cx.beginPath();cx.moveTo(hx+40,hy+45);cx.lineTo(hx+56,hy+42);cx.stroke();
  // Hand dot
  cx.beginPath();cx.arc(hx+60,hy+41,3,0,Math.PI*2);
  cx.fillStyle=ra(P.pink,0.85);cx.fill();

  // Legs (sitting)
  cx.beginPath();cx.moveTo(hx,hy+60);cx.lineTo(hx-22,hy+82);cx.lineTo(hx-20,hy+95);cx.stroke();
  cx.beginPath();cx.moveTo(hx,hy+60);cx.lineTo(hx+18,hy+82);cx.lineTo(hx+16,hy+95);cx.stroke();

  cx.restore();
}

/* ═══════════════════ BOX NODE ═══════════════════ */
function drawBox(n,gs){
  const{x,y,w,h,lbl,sub,col}=n;
  const bx=x+w/2;

  glow(bx,y+h/2,Math.max(w,h)*0.85,col,gs*0.16);

  // Fill
  const bg=cx.createLinearGradient(x,y,x,y+h);
  bg.addColorStop(0,ra(col,0.14));bg.addColorStop(1,ra(col,0.04));
  cx.fillStyle=bg;rr(x,y,w,h,10);cx.fill();

  // Border
  cx.strokeStyle=ra(col,0.6);cx.lineWidth=1.5;
  rr(x,y,w,h,10);cx.stroke();

  // Top accent
  const tg=cx.createLinearGradient(x,0,x+w,0);
  tg.addColorStop(0,'rgba(0,0,0,0)');tg.addColorStop(0.25,ra(col,0.9));
  tg.addColorStop(0.75,ra(col,0.9));tg.addColorStop(1,'rgba(0,0,0,0)');
  cx.strokeStyle=tg;cx.lineWidth=2.5;
  cx.beginPath();cx.moveTo(x+10,y+1.25);cx.lineTo(x+w-10,y+1.25);cx.stroke();

  // Corner markers
  const cm=[[x+3,y+3],[x+w-3,y+3],[x+3,y+h-3],[x+w-3,y+h-3]];
  for(const[cx2,cy2]of cm){
    cx.strokeStyle=ra(col,gs*0.6);cx.lineWidth=1.2;
    cx.beginPath();cx.arc(cx2,cy2,5,0,Math.PI*2);cx.stroke();
  }

  // Label
  cx.fillStyle=col;cx.font='bold 10px "Orbitron",monospace';cx.textAlign='center';
  cx.fillText(lbl,bx,y+22);

  // Sub
  cx.fillStyle=ra(col,0.48);cx.font='8px "Share Tech Mono",monospace';
  cx.fillText(sub,bx,y+35);

  // Active pulse dot
  if(gs>0.5){
    const da=0.4+0.6*Math.abs(Math.sin(performance.now()*0.007));
    glow(x+w-14,y+14,8,col,da*0.5);
    cx.beginPath();cx.arc(x+w-14,y+14,3.5,0,Math.PI*2);
    cx.fillStyle=ra(col,da);cx.fill();
  }
}

/* ═══════════════════ CONNECTORS ═══════════════════ */
function drawConnectors(){
  const mY=NY;
  const conns=[
    {x1:PX+78,y1:mY,x2:NODES.stl.x,y2:mY,col:P.pink,lbl:''},
    {x1:NODES.stl.x+NODES.stl.w,y1:mY,x2:NODES.api.x,y2:mY,col:P.gold,lbl:'POST /search'},
    {x1:NODES.api.x+NODES.api.w,y1:mY,x2:NODES.clip.x,y2:mY,col:P.pur,lbl:'encode()'},
    {x1:NODES.clip.x+NODES.clip.w,y1:mY,x2:NODES.qdr.x,y2:mY,col:P.cyan,lbl:'query_points()'},
  ];
  const off=(performance.now()*0.028)%18;
  for(const c of conns){
    cx.save();
    cx.strokeStyle=ra(c.col,0.18);cx.lineWidth=1.5;
    cx.setLineDash([7,5]);cx.lineDashOffset=-off;
    cx.beginPath();cx.moveTo(c.x1,c.y1);cx.lineTo(c.x2,c.y2);cx.stroke();
    cx.setLineDash([]);

    // Arrowhead
    const dx=c.x2-c.x1,dy=0,len=Math.abs(dx);
    const ux=dx/len;
    const ax=c.x2-ux*10;
    cx.beginPath();cx.moveTo(c.x2,c.y2);
    cx.lineTo(ax-5,c.y2-4);cx.lineTo(ax-5,c.y2+4);cx.closePath();
    cx.fillStyle=ra(c.col,0.28);cx.fill();

    cx.restore();
  }
}

/* ═══════════════════ RETURN ARC ═══════════════════ */
function drawReturnArc(ph,pc){
  const fx=NODES.qdr.x+NODES.qdr.w/2;
  const fy=NODES.qdr.y+NODES.qdr.h;
  const tx=PX+70;const ty=NY;
  const mx=(fx+tx)/2,my=H-58;

  // Faint base
  cx.save();
  cx.strokeStyle=ra(P.grn,0.1);cx.lineWidth=1.5;
  cx.setLineDash([9,7]);
  cx.beginPath();cx.moveTo(fx,fy);cx.quadraticCurveTo(mx,my,tx,ty);cx.stroke();

  if(ph==='return'||ph==='display'){
    const a=ph==='return'?0.65:Math.max(0,0.65-(pc*0.5));
    const off=(performance.now()*0.022)%22;
    cx.strokeStyle=ra(P.grn,a);cx.lineWidth=2;
    cx.setLineDash([6,5]);cx.lineDashOffset=-off;
    cx.beginPath();cx.moveTo(fx,fy);cx.quadraticCurveTo(mx,my,tx,ty);cx.stroke();
    cx.setLineDash([]);

    // Label
    cx.fillStyle=ra(P.grn,a);cx.font='bold 9px "Share Tech Mono",monospace';cx.textAlign='center';
    cx.fillText('↩  10 results returning',mx,my+18);

    // Result label badges
    if(ph==='return'&&pc>0.3){
      const scores=['0.98','0.96','0.93'];
      for(let i=0;i<3;i++){
        const t2=(pc-0.3-i*0.1)*3;
        if(t2<=0)continue;
        const a2=Math.min(1,t2);
        const bx2=mx-60+i*55,by2=my-18;
        cx.fillStyle=ra('#000020',0.8*a2);
        rr(bx2-16,by2-9,32,16,4);cx.fill();
        cx.strokeStyle=ra(P.grn,0.7*a2);cx.lineWidth=0.8;
        rr(bx2-16,by2-9,32,16,4);cx.stroke();
        cx.fillStyle=ra(P.grn,a2);cx.font='bold 8px "Share Tech Mono",monospace';cx.textAlign='center';
        cx.fillText(scores[i],bx2,by2+3);
      }
    }
  }
  cx.setLineDash([]);
  cx.restore();
}

/* ═══════════════════ STREAMLIT CONTENT ═══════════════════ */
function drawStreamlit(ph,pc){
  const n=NODES.stl,{x,y,w,h,col}=n;
  const bx=x+w/2,wy=y+44,wh2=h-54;

  // Mini browser
  cx.fillStyle=ra('#000015',0.75);rr(x+7,wy,w-14,wh2,5);cx.fill();
  cx.strokeStyle=ra(col,0.22);cx.lineWidth=0.8;rr(x+7,wy,w-14,wh2,5);cx.stroke();

  // Dots
  const dc=[P.pink,P.gold,P.grn];
  for(let i=0;i<3;i++){
    cx.beginPath();cx.arc(x+15+i*11,wy+8,3,0,Math.PI*2);
    cx.fillStyle=ra(dc[i],0.7);cx.fill();
  }
  // URL bar
  cx.fillStyle=ra('#ffffff',0.04);rr(x+42,wy+4,w-56,9,3);cx.fill();
  cx.fillStyle=ra(col,0.35);cx.font='5.5px "Share Tech Mono",monospace';cx.textAlign='left';
  cx.fillText('localhost:8501',x+45,wy+11);

  if(ph==='idle'||ph==='upload'){
    const a=ph==='idle'?0.85:Math.max(0.05,1-pc*1.8);
    cx.strokeStyle=ra(col,0.38*a);cx.setLineDash([3,2]);cx.lineWidth=0.7;
    rr(x+12,wy+17,w-24,wh2-22,3);cx.stroke();cx.setLineDash([]);
    cx.fillStyle=ra(col,0.65*a);cx.font='12px monospace';cx.textAlign='center';
    cx.fillText('↑',bx,wy+32);
    cx.font='6px "Share Tech Mono",monospace';cx.fillStyle=ra(col,0.45*a);
    cx.fillText('Drop image here',bx,wy+44);
    // Filename
    if(ph==='upload'&&pc>0.2){
      cx.fillStyle=ra(P.gold,(pc-0.2)*1.2);cx.font='5.5px "Share Tech Mono",monospace';
      cx.fillText('sneaker.jpg',bx,wy+55);
    }
  } else if(ph==='display'||ph==='reset'){
    const cols=5,bw2=(w-20)/cols,bh2=(wh2-22)/2;
    const rc=[P.pink,P.gold,P.cyan,P.pur,P.grn,P.blu,P.pink,P.gold,P.cyan,P.pur];
    for(let i=0;i<10;i++){
      const ri2=Math.floor(i/cols),ci=i%cols;
      const bx2=x+8+ci*bw2,by=wy+17+ri2*bh2;
      const d=i*0.05;
      const al=Math.max(0,Math.min(1,(pc-d)*8));
      if(al>0){
        cx.fillStyle=ra(rc[i],al*0.55);rr(bx2,by,bw2-2,bh2-2,1);cx.fill();
        cx.strokeStyle=ra(rc[i],al*0.8);cx.lineWidth=0.4;
        rr(bx2,by,bw2-2,bh2-2,1);cx.stroke();
      }
    }
  } else {
    cx.fillStyle=ra(P.gold,0.35);cx.font='6.5px "Share Tech Mono",monospace';cx.textAlign='center';
    const dt=Math.floor(performance.now()/500)%4;
    cx.fillText('processing'+'.'.repeat(dt),bx,wy+40);
  }
}

/* ═══════════════════ FASTAPI CONTENT ═══════════════════ */
function drawFastapi(ph,pc){
  const n=NODES.api,{x,y,w,h,col}=n;
  const bx=x+w/2;

  const eps=[
    {m:'POST',p:'/search', a:ph==='upload'||ph==='encode'},
    {m:'POST',p:'/text',   a:false},
    {m:'GET', p:'/health', a:ph==='idle'},
  ];

  for(let i=0;i<eps.length;i++){
    const ep=eps[i],ly=y+47+i*33;
    const a=ep.a?0.92:0.2;
    const mc=ep.m==='POST'?P.gold:P.blu;

    cx.fillStyle=ra(mc,a*0.22);rr(x+8,ly,28,13,3);cx.fill();
    cx.fillStyle=ra(mc,a);cx.font='bold 6.5px monospace';cx.textAlign='center';
    cx.fillText(ep.m,x+22,ly+9);

    cx.fillStyle=ra(P.wht,a*0.6);cx.font='7.5px "Share Tech Mono",monospace';cx.textAlign='left';
    cx.fillText(ep.p,x+40,ly+9);

    if(ep.a){
      const da=0.4+0.6*Math.abs(Math.sin(performance.now()*0.007));
      cx.beginPath();cx.arc(x+w-12,ly+6.5,3.5,0,Math.PI*2);
      cx.fillStyle=ra(P.grn,da);cx.fill();
    }
  }

  if(ph==='encode'){
    const pct2=Math.round(pc*100);
    cx.fillStyle=ra(P.gold,0.8);cx.font='7px "Share Tech Mono",monospace';cx.textAlign='center';
    cx.fillText(`encoding… ${pct2}%`,bx,y+h-10);
    // Progress bar
    cx.fillStyle=ra(P.gold,0.12);rr(x+10,y+h-22,w-20,5,2);cx.fill();
    cx.fillStyle=ra(P.gold,0.7);rr(x+10,y+h-22,(w-20)*pc,5,2);cx.fill();
  }
}

/* ═══════════════════ CLIP NEURAL NET ═══════════════════ */
function drawCLIP(ph,pc){
  const n=NODES.clip,{x,y,w,h,col}=n;
  const topY=y+44,botY=y+h-6,netH=botY-topY;

  const layers=[
    {lx:x+16,cnt:4},{lx:x+42,cnt:6},{lx:x+70,cnt:6},
    {lx:x+98,cnt:4},{lx:x+124,cnt:1}
  ];
  const active=ph==='encode'||ph==='search'||ph==='return';
  const fp=active?(ph==='encode'?pc:1):0;

  // Connections
  for(let l=0;l<layers.length-1;l++){
    const la=layers[l],lb=layers[l+1];
    const lf=Math.max(0,Math.min(1,fp*layers.length-l));
    for(let i=0;i<la.cnt;i++){
      const ay=topY+netH*(i+1)/(la.cnt+1);
      for(let j=0;j<lb.cnt;j++){
        const by=topY+netH*(j+1)/(lb.cnt+1);
        cx.strokeStyle=ra(col,0.04+lf*0.22);cx.lineWidth=0.45;
        cx.beginPath();cx.moveTo(la.lx,ay);cx.lineTo(lb.lx,by);cx.stroke();
      }
    }
  }

  // Nodes
  const now=performance.now();
  for(let l=0;l<layers.length;l++){
    const la=layers[l];
    const lf=Math.max(0,Math.min(1,fp*layers.length-l));
    const isOut=l===layers.length-1;
    const nr=isOut?8:3.8;
    for(let i=0;i<la.cnt;i++){
      const ny=topY+netH*(i+1)/(la.cnt+1);
      const pulse=isOut&&active?0.5+0.5*Math.sin(now*0.01):0;
      const a=0.18+lf*0.82;
      if(lf>0.15)glow(la.lx,ny,nr*(isOut?6:4),col,lf*(isOut?0.55:0.3));
      cx.beginPath();cx.arc(la.lx,ny,nr*(1+pulse*0.15),0,Math.PI*2);
      cx.fillStyle=ra(col,a);cx.fill();
      if(lf>0.5){
        cx.beginPath();cx.arc(la.lx,ny,nr*0.35,0,Math.PI*2);
        cx.fillStyle=ra(P.wht,lf*0.8);cx.fill();
      }
    }
  }

  // Output label "512"
  if(active&&fp>0.7){
    const ox=layers[layers.length-1].lx+12,oy=topY+netH/2;
    const a2=(fp-0.7)/0.3;
    glow(ox+12,oy,18,col,a2*0.3);
    cx.fillStyle=ra(col,a2);cx.font='bold 11px "Orbitron",monospace';cx.textAlign='left';
    cx.fillText('512',ox,oy+4);
    cx.font='6.5px "Share Tech Mono",monospace';cx.fillStyle=ra(col,a2*0.7);
    cx.fillText('dims',ox,oy+15);
  }
}

/* ═══════════════════ QDRANT CONTENT ═══════════════════ */
function drawQdrant(ph,pc){
  const n=NODES.qdr,{x,y,w,h,col}=n;
  const bx=x+w/2,topY=y+44,botY=y+h-6,barH=botY-topY;
  const bcnt=9,gap=barH/bcnt,maxW=w-24;
  const bws=[0.82,0.55,0.91,0.38,0.72,0.58,0.80,0.45,0.65];

  const scanning=ph==='search';
  const scanY=scanning?topY+barH*pc:-1;

  for(let i=0;i<bcnt;i++){
    const by=topY+i*gap+gap/2;
    const bw2=maxW*bws[i];
    const isScanned=scanning&&by<scanY;
    const isTop=isScanned&&i<3;
    const c=isTop?P.grn:col;
    const a=isTop?0.92:isScanned?0.5:0.18;

    cx.fillStyle=ra(c,a);rr(x+10,by-3.5,bw2,7,2);cx.fill();
    if(isTop){
      cx.strokeStyle=ra(P.grn,0.85);cx.lineWidth=0.9;
      rr(x+10,by-3.5,bw2,7,2);cx.stroke();
      cx.fillStyle=ra(P.grn,0.9);cx.font='bold 7px "Share Tech Mono",monospace';cx.textAlign='right';
      cx.fillText(['0.98','0.95','0.91'][i],x+w-8,by+2.5);
    }
  }

  // Scan line
  if(scanning&&scanY>0){
    glow(bx,scanY,45,P.gold,0.28);
    cx.strokeStyle=ra(P.gold,0.85);cx.lineWidth=1.8;
    cx.beginPath();cx.moveTo(x+8,scanY);cx.lineTo(x+w-8,scanY);cx.stroke();
    // Scan label
    cx.fillStyle=ra(P.gold,0.7);cx.font='6.5px "Share Tech Mono",monospace';cx.textAlign='left';
    cx.fillText(`scanning ${Math.round(pc*100)}%…`,x+12,scanY-5);
  }

  if(ph==='search'&&pc>0.6){
    const a=(pc-0.6)/0.4;
    cx.fillStyle=ra(P.grn,a);cx.font='bold 7px "Share Tech Mono",monospace';cx.textAlign='center';
    cx.fillText('✓ top-10 found',bx,y+h-2);
  }
}

/* ═══════════════════ VECTOR DISPLAY ═══════════════════ */
function drawVectorDisplay(ph,pc){
  if(ph!=='encode'||pc<0.4)return;
  const fade=Math.min(1,(pc-0.4)/0.25);
  const vx=NODES.api.x,vy=NODES.api.y+NODES.api.h+8;
  const t=Math.floor(performance.now()/55);

  cx.save();cx.globalAlpha=fade;
  cx.fillStyle=ra('#000018',0.88);rr(vx,vy,340,22,4);cx.fill();
  cx.strokeStyle=ra(P.pur,0.5);cx.lineWidth=0.8;rr(vx,vy,340,22,4);cx.stroke();

  const nums=Array.from({length:16},(_,i)=>{
    const v=Math.sin(i*1.73+t*0.08)*0.99;
    return v.toFixed(2);
  });
  cx.fillStyle=ra(P.cyan,0.75);cx.font='7px "Share Tech Mono",monospace';cx.textAlign='left';
  cx.fillText('['+nums.join(', ')+'…]',vx+6,vy+14);
  cx.restore();
}

/* ═══════════════════ PHASE STATUS ═══════════════════ */
function drawPhaseBar(ph,pc){
  const phs=['idle','upload','encode','search','return','display'];
  const lbls=['IDLE','UPLOAD','ENCODE','SEARCH','RETURN','DISPLAY'];
  const cols=[P.dim,P.pink,P.pur,P.cyan,P.grn,P.gold];

  const bw=620,bh=22,bx=(W-bw)/2,by=H-33;

  cx.fillStyle=ra('#000018',0.55);rr(bx,by,bw,bh,7);cx.fill();
  cx.strokeStyle=ra(P.wht,0.07);cx.lineWidth=0.8;rr(bx,by,bw,bh,7);cx.stroke();

  const sw=bw/phs.length,ci=phs.indexOf(ph);
  for(let i=0;i<phs.length;i++){
    const sx=bx+i*sw;
    const isCur=i===ci,isPast=i<ci;
    const c=cols[i];
    const a=isCur?0.92:isPast?0.45:0.2;

    if(isCur){
      cx.fillStyle=ra(c,0.22);
      const iw=sw*pc-2;if(iw>0){
        rr(sx+1,by+1,Math.min(iw,sw-2),bh-2,i===0?7:2);cx.fill();
      }
    }
    cx.fillStyle=ra(c,a);
    cx.font=(isCur?'bold ':'')+`7.5px "Share Tech Mono",monospace`;
    cx.textAlign='center';
    cx.fillText(lbls[i],sx+sw/2,by+14);
    if(i>0){
      cx.strokeStyle=ra(P.wht,0.07);cx.lineWidth=0.5;
      cx.beginPath();cx.moveTo(sx,by+3);cx.lineTo(sx,by+bh-3);cx.stroke();
    }
  }

  // Time dot
  const tdot=cx.createLinearGradient(bx+bw-80,0,bx+bw,0);
  tdot.addColorStop(0,'rgba(0,0,0,0)');tdot.addColorStop(1,ra(P.cyan,0.07));
  cx.fillStyle=tdot;rr(bx+bw-80,by,80,bh,7);cx.fill();
}

/* ═══════════════════ ARROW LABELS ═══════════════════ */
function drawArrowLabels(ph,pc){
  const mY=NY-15;
  const show=(p)=>({show:ph===p,a:1});

  const labels=[
    {x:(PX+78+NODES.stl.x)/2, txt:'image.jpg', col:P.pink, show:ph==='upload', a:Math.min(1,pc*3)},
    {x:(NODES.stl.x+NODES.stl.w+NODES.api.x)/2, txt:'POST /search', col:P.gold, show:ph==='upload'&&pc>0.4, a:Math.min(1,(pc-0.4)*4)},
    {x:(NODES.api.x+NODES.api.w+NODES.clip.x)/2, txt:'encode(img)', col:P.pur, show:ph==='encode', a:Math.min(1,pc*4)},
    {x:(NODES.clip.x+NODES.clip.w+NODES.qdr.x)/2, txt:'query_points(v)', col:P.cyan, show:ph==='search', a:Math.min(1,pc*4)},
  ];

  for(const lbl of labels){
    if(!lbl.show||lbl.a<=0)continue;
    cx.save();cx.globalAlpha=lbl.a;
    const tw=cx.measureText(lbl.txt).width+16;
    cx.fillStyle=ra('#000018',0.8);rr(lbl.x-tw/2,mY-10,tw,14,4);cx.fill();
    cx.strokeStyle=ra(lbl.col,0.55);cx.lineWidth=0.8;rr(lbl.x-tw/2,mY-10,tw,14,4);cx.stroke();
    cx.fillStyle=ra(lbl.col,0.9);cx.font='7px "Share Tech Mono",monospace';cx.textAlign='center';
    cx.fillText(lbl.txt,lbl.x,mY+1);
    cx.restore();
  }
}

/* ═══════════════════ ANNOUNCEMENT BANNER ═══════════════════ */
const BANNERS={
  idle:   {txt:'⬤  System Idle — Ready for input',        col:P.dim},
  upload: {txt:'⬆  Uploading image → Streamlit UI',        col:P.pink},
  encode: {txt:'🧠  CLIP encoding image → 512-dim vector', col:P.pur},
  search: {txt:'🔍  Qdrant ANN search in progress…',       col:P.cyan},
  return: {txt:'⬇  Top-10 results returning to user',     col:P.grn},
  display:{txt:'✓  10 similar products displayed!',        col:P.gold},
  reset:  {txt:'↺  Resetting pipeline…',                  col:P.dim},
};
function drawBanner(ph,pc){
  const b=BANNERS[ph];if(!b)return;
  let a=1;
  if(ph==='reset')a=Math.max(0,1-pc*3);
  if(ph==='idle')a=0.5+0.4*Math.abs(Math.sin(performance.now()*0.002));

  cx.save();cx.globalAlpha=a;
  const tw=cx.measureText(b.txt).width+28;
  const bx=(W-tw)/2,by=480,bh=22;
  cx.fillStyle=ra('#000018',0.7);rr(bx,by,tw,bh,6);cx.fill();
  cx.strokeStyle=ra(b.col,0.5);cx.lineWidth=1;rr(bx,by,tw,bh,6);cx.stroke();
  // Pulse edge
  const pe=(0.3+0.4*Math.abs(Math.sin(performance.now()*0.005)));
  cx.strokeStyle=ra(b.col,pe);cx.lineWidth=0.5;
  rr(bx-2,by-2,tw+4,bh+4,8);cx.stroke();
  cx.fillStyle=ra(b.col,0.9);cx.font='bold 9px "Share Tech Mono",monospace';cx.textAlign='center';
  cx.fillText(b.txt,(W)/2,by+14);
  cx.restore();
}

/* ═══════════════════ CORNER DECO ═══════════════════ */
function drawCornerDeco(){
  const sz=22,c=P.cyan,a=0.18;
  const corners=[[8,8],[W-8,8],[8,H-8],[W-8,H-8]];
  const angles=[[0,Math.PI/2],[Math.PI/2,Math.PI],[Math.PI*1.5,Math.PI*2],
                 [Math.PI,Math.PI*1.5]];
  for(let i=0;i<4;i++){
    const[cx2,cy]=corners[i],[a1,a2]=angles[i];
    cx.strokeStyle=ra(c,a);cx.lineWidth=1.5;
    cx.beginPath();cx.arc(cx2,cy,sz,a1,a2);cx.stroke();
  }
}

/* ═══════════════════ SPAWN PARTICLES ═══════════════════ */
function spawnParticles(ph,pc){
  const mY=NY,r=Math.random;

  if(ph==='upload'){
    if(r()<0.22)PARTS.push(new Pt(PX+78,mY,NODES.stl.x,mY,P.pink));
    if(pc>0.45&&r()<0.18)PARTS.push(new Pt(NODES.stl.x+NODES.stl.w,mY,NODES.api.x,mY,P.gold));
  }
  if(ph==='encode'&&r()<0.18)
    PARTS.push(new Pt(NODES.api.x+NODES.api.w,mY,NODES.clip.x,mY,P.pur));
  if(ph==='search'&&r()<0.18)
    PARTS.push(new Pt(NODES.clip.x+NODES.clip.w,mY,NODES.qdr.x,mY,P.cyan));
  if(ph==='return'&&r()<0.2)
    PARTS.push(new Pt(NODES.qdr.x+NODES.qdr.w/2,NODES.qdr.y+NODES.qdr.h,PX+70,mY,P.grn,true));
}

/* ═══════════════════ MAIN LOOP ═══════════════════ */
const GS={
  idle:   [0.35,0.3,0.25,0.25],
  upload: [0.95,0.6,0.2, 0.2 ],
  encode: [0.3, 0.8,1.05,0.2 ],
  search: [0.2, 0.2,0.5, 1.05],
  return: [0.7, 0.2,0.2, 0.55],
  display:[1.05,0.6,0.2, 0.2 ],
  reset:  [0.3, 0.3,0.3, 0.3 ],
};

function render(){
  const now=performance.now();
  const t=now%CYCLE;
  const{n:ph,pc}=phase(t);

  PARTS=PARTS.filter(p=>!p.done);
  PARTS.forEach(p=>p.update());
  spawnParticles(ph,pc);

  drawBG(now);
  drawTitle();
  drawCornerDeco();
  drawConnectors();
  drawReturnArc(ph,pc);
  drawArrowLabels(ph,pc);

  const gs=GS[ph]||[0.3,0.3,0.3,0.3];
  drawBox(NODES.stl,gs[0]);
  drawBox(NODES.api,gs[1]);
  drawBox(NODES.clip,gs[2]);
  drawBox(NODES.qdr,gs[3]);

  drawStreamlit(ph,pc);
  drawFastapi(ph,pc);
  drawCLIP(ph,pc);
  drawQdrant(ph,pc);
  drawVectorDisplay(ph,pc);
  drawPerson(ph,pc);

  PARTS.forEach(p=>p.draw());

  drawBanner(ph,pc);
  drawPhaseBar(ph,pc);

  requestAnimationFrame(render);
}

render();
</script>
</body>
</html>
