import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os

# ── CONFIG ──
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Welcome To The Fastest Search Engine",
    page_icon="🌌",
    layout="centered"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:ital,wght@0,300;0,400;0,600;1,300&family=Share+Tech+Mono&display=swap');

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stApp"] { background: transparent !important; cursor: none !important; }

  [data-testid="stAppViewContainer"]::before {
    content: ''; position: fixed; inset: 0; z-index: -4;
    background: #00000f;
  }

  #star-canvas {
    position: fixed; top:0; left:0;
    width:100vw; height:100vh;
    z-index: -1; pointer-events: none;
  }

  /* Custom cursor */
  #cursor-dot {
    position: fixed; width: 10px; height: 10px; border-radius: 50%;
    background: #7be0ff;
    box-shadow: 0 0 12px #7be0ff, 0 0 30px rgba(123,224,255,0.6);
    pointer-events: none; z-index: 99999;
    transform: translate(-50%, -50%);
    transition: width 0.15s, height 0.15s, background 0.15s;
  }
  #cursor-ring {
    position: fixed; width: 36px; height: 36px; border-radius: 50%;
    border: 1.5px solid rgba(123,224,255,0.6);
    pointer-events: none; z-index: 99998;
    transform: translate(-50%, -50%);
    transition: transform 0.08s linear, width 0.2s, height 0.2s, border-color 0.2s;
  }
  #mouse-star-canvas {
    position: fixed; top:0; left:0; width:100vw; height:100vh;
    z-index: 99997; pointer-events: none;
  }

  /* CHROME HIDE */
  #MainMenu, footer, header    { visibility: hidden; }
  [data-testid="stToolbar"]    { display: none; }
  [data-testid="stDecoration"] { display: none; }

  .main .block-container {
    max-width: 900px;
    padding: 1.5rem 2rem 5rem;
    position: relative; z-index: 1;
  }

  * { font-family: 'Exo 2', sans-serif !important; color: #cde0ff !important; }

  /* ── PREVENT ICON LIGATURE BLEED ── */
  span[class*="material-symbols"], .stIcon { 
    font-family: 'Material Symbols Rounded' !important; 
  }

  /* ── HERO ── */
  .hero-wrap { text-align: center; padding: 2.8rem 0 0.5rem; }

  .hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.6rem;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.62rem; letter-spacing: 0.28em; text-transform: uppercase;
    color: #7be0ff !important;
    border: 1px solid rgba(123,224,255,0.3); border-radius: 20px;
    padding: 0.3rem 1.1rem;
    background: rgba(123,224,255,0.05);
    margin-bottom: 1.2rem;
    animation: badge-glow 3s ease-in-out infinite;
    transition: all 0.3s;
  }
  .hero-eyebrow:hover {
    background: rgba(123,224,255,0.12) !important;
    box-shadow: 0 0 30px rgba(123,224,255,0.4), inset 0 0 20px rgba(123,224,255,0.08) !important;
    transform: scale(1.04);
  }
  .hero-eyebrow::before { content:'◈'; animation: spin 5s linear infinite; display:inline-block; }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes badge-glow {
    0%,100% { box-shadow: 0 0 8px rgba(123,224,255,0.2); }
    50%      { box-shadow: 0 0 25px rgba(123,224,255,0.5), 0 0 50px rgba(123,224,255,0.15); }
  }

  .hero-title {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: clamp(1.6rem, 4vw, 3.1rem) !important;
    line-height: 1.15; letter-spacing: 0.03em;
    background: linear-gradient(135deg,#fff 0%,#a5d8ff 18%,#7be0ff 35%,#b197fc 58%,#f783ac 78%,#ffd43b 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    background-size: 300% 300%;
    animation: title-shimmer 5s ease-in-out infinite;
    text-shadow: none !important; margin: 0 !important;
  }
  @keyframes title-shimmer {
    0%,100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
  }

  .hero-sub {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.68rem !important;
    color: rgba(200,224,255,0.4) !important;
    letter-spacing: 0.2em; margin-top: 0.8rem !important;
  }

  /* ── STAT PILLS ── */
  .hero-stats {
    display: flex; justify-content: center; gap: 1.2rem;
    flex-wrap: wrap; margin: 1.8rem 0 0.6rem;
  }
  .stat-pill {
    display: flex; flex-direction: column; align-items: center; gap: 0.12rem;
    padding: 0.6rem 1.2rem;
    background: rgba(10,20,60,0.5);
    border: 1px solid rgba(123,224,255,0.18);
    border-radius: 10px; backdrop-filter: blur(14px);
    transition: all 0.35s; cursor: default;
    position: relative; overflow: hidden;
  }
  .stat-pill::before {
    content:''; position:absolute; inset:0;
    background: linear-gradient(135deg, rgba(123,224,255,0.06), transparent);
    opacity:0; transition: opacity 0.3s;
  }
  .stat-pill:hover::before { opacity:1; }
  .stat-pill:hover {
    border-color: rgba(123,224,255,0.6) !important;
    box-shadow: 0 0 25px rgba(123,224,255,0.25), 0 0 60px rgba(123,224,255,0.08) !important;
    transform: translateY(-4px) scale(1.05) !important;
  }
  .stat-val {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.05rem !important; font-weight:700 !important;
    color: #7be0ff !important;
  }
  .stat-lbl {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.52rem !important; color: rgba(200,224,255,0.38) !important;
    letter-spacing: 0.12em; text-transform: uppercase;
  }

  .hero-rule {
    height: 1px; margin: 1.5rem auto;
    background: linear-gradient(90deg, transparent, #7be0ff, #b197fc, #f783ac, transparent);
    animation: rule-pulse 4s ease-in-out infinite;
  }
  @keyframes rule-pulse { 0%,100%{opacity:0.3;} 50%{opacity:1;} }

  /* ── QUOTES ── */
  .quotes-wrap {
    background: rgba(4,8,30,0.6);
    border: 1px solid rgba(123,224,255,0.15);
    border-radius: 12px;
    padding: 1.2rem 1.5rem 1rem;
    margin: 0.5rem 0 1.4rem;
    backdrop-filter: blur(16px);
    position: relative; overflow: hidden;
    min-height: 95px;
    transition: all 0.4s;
  }
  .quotes-wrap:hover {
    border-color: rgba(123,224,255,0.45) !important;
    box-shadow: 0 0 40px rgba(123,224,255,0.12), 0 0 80px rgba(177,151,252,0.08),
                inset 0 0 30px rgba(123,224,255,0.04) !important;
    background: rgba(6,12,45,0.75) !important;
  }
  .quotes-wrap::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg,#7be0ff,#b197fc,#f783ac,#ffd43b,#7be0ff);
    background-size:300%; animation: bar-scroll 3s linear infinite;
  }
  @keyframes bar-scroll { to { background-position: 300% 0; } }
  .quote-label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.57rem !important; letter-spacing: 0.22em;
    color: rgba(123,224,255,0.5) !important;
    text-transform: uppercase; margin-bottom: 0.5rem;
  }
  .quote-text {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.87rem !important; font-style: italic;
    color: #e2ecff !important; line-height: 1.55; min-height: 2.8rem;
    animation: qfade 0.7s ease;
  }
  @keyframes qfade { from{opacity:0;transform:translateY(8px);} to{opacity:1;transform:translateY(0);} }
  .quote-author {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.58rem !important; color: rgba(177,151,252,0.5) !important;
    margin-top: 0.4rem; letter-spacing: 0.08em;
  }
  .qdots { display:flex; gap:0.38rem; margin-top:0.65rem; }
  .qdot  { width:5px;height:5px;border-radius:50%;background:rgba(123,224,255,0.2);transition:all 0.4s; }
  .qdot.active { background:#7be0ff; box-shadow:0 0 8px #7be0ff,0 0 16px rgba(123,224,255,0.4); transform:scale(1.4); }

  /* ── FACT CARDS ── */
  .fact-row { display:flex; gap:0.85rem; margin:0.4rem 0 1.3rem; }
  .fact-card {
    flex:1; padding:0.85rem 1rem;
    background: rgba(6,12,45,0.55);
    border: 1px solid rgba(123,224,255,0.12);
    border-radius: 10px; backdrop-filter: blur(12px);
    transition: all 0.35s; cursor: default;
    position: relative; overflow: hidden;
  }
  .fact-card::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, #7be0ff, #b197fc);
    transform: scaleX(0); transform-origin: left;
    transition: transform 0.4s ease;
  }
  .fact-card:hover::after { transform: scaleX(1); }
  .fact-card:hover {
    border-color: rgba(123,224,255,0.5) !important;
    background: rgba(10,20,65,0.75) !important;
    box-shadow: 0 0 30px rgba(123,224,255,0.14), 0 8px 32px rgba(0,0,0,0.4) !important;
    transform: translateY(-5px) !important;
  }
  .fact-icon  { font-size:1.3rem; margin-bottom:0.4rem; }
  .fact-title {
    font-family:'Orbitron',sans-serif !important;
    font-size:0.58rem !important; font-weight:700 !important;
    letter-spacing:0.14em; text-transform:uppercase;
    color:#7be0ff !important; margin-bottom:0.32rem;
  }
  .fact-body {
    font-family:'Exo 2',sans-serif !important;
    font-size:0.71rem !important; color:rgba(200,220,255,0.6) !important;
    line-height:1.48;
  }

  /* ── DIVIDER ── */
  hr { border:none !important; border-top:1px solid rgba(123,224,255,0.1) !important; margin:1rem 0 !important; }

  /* ── ALERT ── */
  [data-testid="stAlert"] {
    border-radius:9px !important; border:1px solid rgba(123,224,255,0.22) !important;
    background:rgba(6,14,45,0.7) !important; backdrop-filter:blur(16px) !important;
    font-family:'Share Tech Mono',monospace !important; font-size:0.72rem !important;
    transition: all 0.35s !important;
  }
  [data-testid="stAlert"]:hover {
    border-color: rgba(123,224,255,0.5) !important;
    box-shadow: 0 0 30px rgba(123,224,255,0.15) !important;
  }

  /* ── TABS ── */
  [data-testid="stTabs"] [role="tablist"] {
    gap:0; border-bottom:1px solid rgba(123,224,255,0.14) !important;
    background:transparent !important;
  }
  [data-testid="stTabs"] button[role="tab"] {
    font-family:'Orbitron',sans-serif !important;
    font-size:0.67rem !important; font-weight:700 !important;
    letter-spacing:0.15em !important; text-transform:uppercase !important;
    color:rgba(200,220,255,0.38) !important; background:transparent !important;
    border:none !important; border-bottom:2px solid transparent !important;
    padding:0.8rem 2rem !important; transition:all 0.3s !important;
  }
  [data-testid="stTabs"] button[role="tab"]:hover {
    color:#7be0ff !important; background:rgba(123,224,255,0.06) !important;
    text-shadow: 0 0 20px rgba(123,224,255,0.5) !important;
  }
  [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color:#7be0ff !important; border-bottom:2px solid #7be0ff !important;
    background:rgba(123,224,255,0.08) !important;
    text-shadow: 0 0 20px rgba(123,224,255,0.6) !important;
  }
  [data-testid="stTabsContent"] { padding-top:1.5rem !important; }

  /* ── HEADINGS ── */
  h2,h3 {
    font-family:'Orbitron',sans-serif !important; font-weight:700 !important;
    letter-spacing:0.1em !important; text-transform:uppercase !important;
    color:#ddeeff !important; transition: all 0.3s !important;
  }
  h2 { font-size:0.95rem !important; }
  h3 { font-size:0.88rem !important; }
  h2:hover, h3:hover {
    color:#7be0ff !important;
    text-shadow: 0 0 20px rgba(123,224,255,0.7), 0 0 40px rgba(123,224,255,0.3) !important;
  }

  /* ── CAPTIONS ── */
  [data-testid="stCaptionContainer"] p, small {
    font-family:'Share Tech Mono',monospace !important; font-size:0.64rem !important;
    color:rgba(200,220,255,0.4) !important; letter-spacing:0.07em !important;
  }

  /* ── FILE UPLOADER ── */
  #[data-testid="stFileUploader"] {
  #border:1px dashed rgba(123,224,255,0.28) !important;
  #border-radius:14px !important; background:rgba(6,14,50,0.4) !important;
  #backdrop-filter:blur(12px) !important; transition:all 0.35s !important;
  #}
  [data-testid="stFileUploader"] button svg,
  [data-testid="stFileUploader"] button [class*="stIcon"],
  [data-testid="stFileUploader"] button [data-testid="stIconMaterial"] {
      display: none !important;
  }
  [data-testid="stFileUploader"]:hover {
    border-color:rgba(123,224,255,0.7) !important;
    box-shadow:0 0 35px rgba(123,224,255,0.15), inset 0 0 20px rgba(123,224,255,0.04) !important;
    background:rgba(8,18,60,0.55) !important;
  }
  [data-testid="stFileUploaderDropzone"] { background:transparent !important; }
  [data-testid="stFileUploader"] p {
    font-family:'Share Tech Mono',monospace !important; font-size:0.7rem !important;
  }

  /* ── TEXT INPUT ── */
  [data-testid="stTextInput"] input {
    background:rgba(6,14,50,0.6) !important;
    border:1px solid rgba(123,224,255,0.24) !important;
    border-radius:8px !important; color:#c8d8ff !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:0.8rem !important; letter-spacing:0.04em !important;
    padding:0.7rem 1rem !important; transition:all 0.3s !important;
  }
  [data-testid="stTextInput"] input:hover {
    border-color: rgba(123,224,255,0.5) !important;
    box-shadow: 0 0 20px rgba(123,224,255,0.12) !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color:#7be0ff !important;
    box-shadow:0 0 0 2px rgba(123,224,255,0.14),0 0 30px rgba(123,224,255,0.18) !important;
    outline:none !important; background:rgba(8,18,60,0.7) !important;
  }

  /* ── PRIMARY BUTTON ── */
  [data-testid="stButton"] button[kind="primary"] {
    background:linear-gradient(135deg,#0e1e6e,#0a1248,#160b55) !important;
    border:1px solid rgba(123,224,255,0.5) !important;
    border-radius:8px !important; color:#7be0ff !important;
    font-family:'Orbitron',sans-serif !important;
    font-size:0.67rem !important; font-weight:700 !important;
    letter-spacing:0.18em !important; text-transform:uppercase !important;
    padding:0.72rem 1.3rem !important; transition:all 0.35s ease !important;
    overflow:hidden !important; position:relative !important;
  }
  [data-testid="stButton"] button[kind="primary"]::before {
    content:''; position:absolute; top:-50%; left:-75%; width:50%; height:200%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent);
    transform:skewX(-20deg); transition:left 0.6s ease;
  }
  [data-testid="stButton"] button[kind="primary"]:hover::before { left:150%; }
  [data-testid="stButton"] button[kind="primary"]:hover {
    background:linear-gradient(135deg,#1a2ea0,#101e70,#220d80) !important;
    border-color:#7be0ff !important;
    box-shadow:0 0 35px rgba(123,224,255,0.35),0 0 70px rgba(123,224,255,0.1),0 5px 20px rgba(0,0,0,0.5) !important;
    transform:translateY(-2px) !important; color:#fff !important;
    text-shadow:0 0 15px rgba(123,224,255,0.8) !important;
  }

  /* ── SECONDARY BUTTONS ── */
  [data-testid="stButton"] button[kind="secondary"] {
    background:rgba(6,14,45,0.45) !important;
    border:1px solid rgba(177,151,252,0.28) !important;
    border-radius:6px !important; color:rgba(200,216,255,0.6) !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:0.6rem !important; letter-spacing:0.06em !important;
    padding:0.4rem 0.6rem !important; transition:all 0.25s !important;
  }
  [data-testid="stButton"] button[kind="secondary"]:hover {
    background:rgba(177,151,252,0.14) !important;
    border-color:#b197fc !important; color:#b197fc !important;
    box-shadow:0 0 18px rgba(177,151,252,0.28) !important;
    transform:translateY(-1px) !important;
  }

  /* ── IMAGES ── */
  [data-testid="stImage"] img {
    border-radius:10px !important;
    border:1px solid rgba(123,224,255,0.15) !important;
    transition:all 0.4s ease !important;
  }
  [data-testid="stImage"] img:hover {
    border-color:rgba(123,224,255,0.55) !important;
    box-shadow:0 0 30px rgba(123,224,255,0.22),0 0 60px rgba(123,224,255,0.08) !important;
    transform:scale(1.03) !important;
  }

  /* ── RESULT COLUMNS ── */
  [data-testid="column"] {
    background:rgba(6,14,44,0.45) !important;
    border:1px solid rgba(123,224,255,0.1) !important;
    border-radius:12px !important; padding:0.7rem !important;
    transition:all 0.35s ease !important; backdrop-filter:blur(10px) !important;
  }
  [data-testid="column"]:hover {
    border-color:rgba(123,224,255,0.45) !important;
    background:rgba(10,22,65,0.65) !important;
    box-shadow:0 0 35px rgba(123,224,255,0.16),0 10px 40px rgba(0,0,0,0.4) !important;
    transform:translateY(-6px) !important;
  }

  /* ── MARKDOWN ── */
  [data-testid="stMarkdownContainer"] p { font-size:0.92rem !important; }
  [data-testid="stMarkdownContainer"] strong {
    color:#e8f2ff !important; font-weight:600 !important;
    transition: all 0.3s !important;
  }
  [data-testid="stMarkdownContainer"] strong:hover {
    color:#7be0ff !important;
    text-shadow:0 0 14px rgba(123,224,255,0.7) !important;
  }

  /* ── SCROLLBAR ── */
  ::-webkit-scrollbar { width:4px; }
  ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:rgba(123,224,255,0.2); border-radius:2px; }
  ::-webkit-scrollbar-thumb:hover { background:rgba(123,224,255,0.5); }

  /* ── SPINNER ── */
  [data-testid="stSpinner"] * {
    color:#7be0ff !important;
    font-family:'Share Tech Mono',monospace !important; font-size:0.72rem !important;
  }

  /* ── HOVER GLOW on all interactive text areas ── */
  [data-testid="stTextInput"]:hover label,
  [data-testid="stFileUploader"]:hover label {
    color:#7be0ff !important;
    text-shadow:0 0 14px rgba(123,224,255,0.6) !important;
  }
  p:hover, li:hover {
    color:#d8eeff !important;
    transition: color 0.25s, text-shadow 0.25s !important;
  }
</style>

<div id="cursor-dot"></div>
<div id="cursor-ring"></div>

<canvas id="mouse-star-canvas"></canvas>

<canvas id="star-canvas"></canvas>

<script>
/* ════════════════════════════════════════════════════
  1. CUSTOM CURSOR + MOUSE-MOVE TWINKLING STAR SPAWNER
════════════════════════════════════════════════════ */
(function() {
  const dot  = document.getElementById('cursor-dot');
  const ring = document.getElementById('cursor-ring');

  /* ── TWINKLING STAR CANVAS (highest layer) ── */
  const mc   = document.getElementById('mouse-star-canvas');
  const mctx = mc.getContext('2d');

  function resizeMC() {
    mc.width  = window.innerWidth;
    mc.height = window.innerHeight;
  }
  resizeMC();
  window.addEventListener('resize', resizeMC);

  /* ── COLOUR PALETTE for spawned stars ── */
  const STAR_COLORS = [
    '#ffffff','#7be0ff','#a78bfa','#f472b6',
    '#fbbf24','#34d399','#60a5fa','#f9a8d4',
    '#c4b5fd','#6ee7b7','#fde68a','#bfdbfe'
  ];

  /* ── STAR PARTICLE POOL ── */
  let spawnStars = [];   // stars born from mouse movement
  let mx = 0, my = 0;
  let rx = 0, ry = 0;
  let lastSpawnX = -999, lastSpawnY = -999;

  /* helper */
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function rndInt(a, b) { return Math.floor(rnd(a, b)); }
  function pickColor() { return STAR_COLORS[rndInt(0, STAR_COLORS.length)]; }

  /* ── SPAWN a burst of twinkling stars at (x, y) ── */
  function spawnBurst(x, y, count) {
    for (let i = 0; i < count; i++) {
      const isSpark = Math.random() < 0.3;   /* 30% are cross-sparkle type */
      spawnStars.push({
        x: x + rnd(-18, 18),
        y: y + rnd(-18, 18),
        /* outward velocity — stars fly away from cursor */
        vx: rnd(-1.8, 1.8),
        vy: rnd(-2.2, 0.4),
        r:  rnd(0.8, isSpark ? 3.2 : 2.0),
        color: pickColor(),
        alpha: rnd(0.7, 1.0),
        /* each star has its own twinkle phase & speed */
        phase: rnd(0, Math.PI * 2),
        phaseSpeed: rnd(0.08, 0.22),
        /* lifetime: how long before it fully fades */
        life: rnd(0.6, 1.0),
        decay: rnd(0.012, 0.030),
        spark: isSpark,
        spikeLen: isSpark ? rnd(4, 10) : 0,
        /* gravity: slight float upward */
        gravity: rnd(-0.025, 0.01),
      });
    }
  }

  /* ── DRAW a single 4-point sparkle cross ── */
  function drawSparkle(ctx, x, y, len, color, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth   = 0.9;
    /* horizontal */
    ctx.beginPath(); ctx.moveTo(x - len, y); ctx.lineTo(x + len, y); ctx.stroke();
    /* vertical */
    ctx.beginPath(); ctx.moveTo(x, y - len * 0.6); ctx.lineTo(x, y + len * 0.6); ctx.stroke();
    /* diagonal arms (subtle) */
    ctx.lineWidth = 0.5;
    const d = len * 0.45;
    ctx.beginPath(); ctx.moveTo(x-d, y-d); ctx.lineTo(x+d, y+d); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x+d, y-d); ctx.lineTo(x-d, y+d); ctx.stroke();
    ctx.restore();
  }

  /* ── DRAW glow halo behind a star ── */
  function drawHalo(ctx, x, y, r, color, alpha) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 5);
    /* parse hex → rgba */
    const rv = parseInt(color.slice(1,3),16);
    const gv = parseInt(color.slice(3,5),16);
    const bv = parseInt(color.slice(5,7),16);
    g.addColorStop(0,   `rgba(${rv},${gv},${bv},${alpha * 0.85})`);
    g.addColorStop(0.4, `rgba(${rv},${gv},${bv},${alpha * 0.25})`);
    g.addColorStop(1,   `rgba(${rv},${gv},${bv},0)`);
    ctx.beginPath(); ctx.arc(x, y, r * 5, 0, Math.PI * 2);
    ctx.fillStyle = g; ctx.fill();
  }

  /* ── MAIN ANIMATION LOOP for mouse stars ── */
  function animMouseStars() {
    /* clear canvas each frame */
    mctx.clearRect(0, 0, mc.width, mc.height);

    for (let i = spawnStars.length - 1; i >= 0; i--) {
      const s = spawnStars[i];

      /* age the star */
      s.life  -= s.decay;
      s.phase += s.phaseSpeed;
      s.x     += s.vx;
      s.y     += s.vy;
      s.vy    += s.gravity;   /* float / drift */
      s.vx    *= 0.97;        /* air drag */
      s.vy    *= 0.97;

      /* remove dead stars */
      if (s.life <= 0) { spawnStars.splice(i, 1); continue; }

      /* twinkle: sinusoidal brightness on top of life fade */
      const twinkle = 0.5 + 0.5 * Math.sin(s.phase);
      const alpha   = s.life * twinkle;
      const r       = s.r * (0.8 + 0.4 * Math.sin(s.phase * 1.4));

      /* draw */
      drawHalo(mctx, s.x, s.y, r, s.color, alpha * 0.6);

      if (s.spark) {
        /* sparkle cross */
        drawSparkle(mctx, s.x, s.y, s.spikeLen * (0.7 + 0.3 * twinkle), s.color, alpha);
      }

      /* solid star dot */
      mctx.beginPath();
      mctx.arc(s.x, s.y, r, 0, Math.PI * 2);
      const rv = parseInt(s.color.slice(1,3),16);
      const gv = parseInt(s.color.slice(3,5),16);
      const bv = parseInt(s.color.slice(5,7),16);
      mctx.fillStyle = `rgba(${rv},${gv},${bv},${alpha})`;
      mctx.fill();

      /* bright white core */
      mctx.beginPath();
      mctx.arc(s.x, s.y, r * 0.32, 0, Math.PI * 2);
      mctx.fillStyle = `rgba(255,255,255,${alpha * 0.9})`;
      mctx.fill();
    }

    requestAnimationFrame(animMouseStars);
  }
  animMouseStars();

  /* ── MOUSE MOVE → spawn stars ── */
  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;

    /* position the cursor dot */
    dot.style.left = mx + 'px';
    dot.style.top  = my + 'px';

    /* only spawn if mouse actually moved far enough (avoids spam) */
    const dx = mx - lastSpawnX, dy = my - lastSpawnY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist > 8) {
      /* more stars when moving fast */
      const speed   = Math.min(dist, 40);
      const count   = Math.floor(rnd(2, 3) + speed * 0.12);
      spawnBurst(mx, my, count);
      lastSpawnX = mx; lastSpawnY = my;
    }
  });

  /* ── CURSOR RING lags smoothly ── */
  function animRing() {
    rx += (mx - rx) * 0.13;
    ry += (my - ry) * 0.13;
    ring.style.left = rx + 'px';
    ring.style.top  = ry + 'px';
    requestAnimationFrame(animRing);
  }
  animRing();

  /* ── CURSOR SHAPE CHANGE on interactive elements ── */
  document.addEventListener('mouseover', e => {
    const t = e.target;
    const isHot = t.matches(
      'button,input,a,[data-testid="stFileUploader"],' +
      '[data-testid="column"],.fact-card,.stat-pill,.quotes-wrap'
    );
    if (isHot) {
      dot.style.width      = '20px';
      dot.style.height     = '20px';
      dot.style.background = '#f472b6';
      dot.style.boxShadow  = '0 0 22px #f472b6, 0 0 55px rgba(244,114,182,0.55)';
      ring.style.width     = '58px';
      ring.style.height    = '58px';
      ring.style.borderColor = 'rgba(244,114,182,0.75)';
      /* extra burst on entering hot zone */
      spawnBurst(mx, my, 10);
    } else {
      dot.style.width      = '10px';
      dot.style.height     = '10px';
      dot.style.background = '#7be0ff';
      dot.style.boxShadow  = '0 0 12px #7be0ff, 0 0 30px rgba(123,224,255,0.6)';
      ring.style.width     = '36px';
      ring.style.height    = '36px';
      ring.style.borderColor = 'rgba(123,224,255,0.6)';
    }
  });

  /* ── CLICK → big explosion of stars ── */
  document.addEventListener('click', e => {
    spawnBurst(e.clientX, e.clientY, 28);
  });

})();
</script>

<script>
/* ════════════════════════════════════════════════════
  2. STAR FIELD + AURORA + MOUSE-REACTIVE PARTICLES
════════════════════════════════════════════════════ */
(function () {
  const cv  = document.getElementById('star-canvas');
  const ctx = cv.getContext('2d');
  let W, H, stars=[], shooters=[], auroras=[];
  let mouseX=W/2||600, mouseY=H/2||400;

  function rnd(a,b){return a+Math.random()*(b-a);}
  function hexRgba(hex,a){
    const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
    return `rgba(${r},${g},${b},${a})`;
  }
  const PAL=['#ffffff','#c8e6ff','#a0c8ff','#7be0ff','#b197fc','#f783ac','#ffd43b','#69db7c','#ff9ff3'];

  function resize(){
    W=cv.width=window.innerWidth;
    H=cv.height=window.innerHeight;
  }

  /* ── AURORA BANDS ── */
  function mkAurora() {
    return {
      x: rnd(0,W), y: rnd(H*0.1,H*0.5),
      w: rnd(W*0.4,W*0.8), h: rnd(60,140),
      color1: PAL[Math.floor(Math.random()*PAL.length)],
      color2: PAL[Math.floor(Math.random()*PAL.length)],
      phase: rnd(0,Math.PI*2),
      speed: rnd(0.003,0.009),
      opacity: rnd(0.025,0.07),
    };
  }

  function drawAuroras() {
    for (const a of auroras) {
      a.phase += a.speed;
      const waveY = a.y + Math.sin(a.phase)*30;
      const grad = ctx.createLinearGradient(a.x,waveY,a.x+a.w,waveY+a.h);
      grad.addColorStop(0,   hexRgba(a.color1,0));
      grad.addColorStop(0.3, hexRgba(a.color1,a.opacity));
      grad.addColorStop(0.6, hexRgba(a.color2,a.opacity*0.8));
      grad.addColorStop(1,   hexRgba(a.color2,0));
      ctx.save();
      ctx.filter=`blur(${Math.floor(a.h*0.5)}px)`;
      ctx.beginPath();
      ctx.ellipse(a.x+a.w/2, waveY+a.h/2, a.w/2, a.h/2+Math.sin(a.phase*1.3)*20, 0, 0, Math.PI*2);
      ctx.fillStyle=grad; ctx.fill();
      ctx.restore();
    }
  }

  /* ── MOUSE SPOTLIGHT ── */
  function drawSpotlight() {
    const g = ctx.createRadialGradient(mouseX,mouseY,0,mouseX,mouseY,220);
    g.addColorStop(0,   'rgba(123,224,255,0.055)');
    g.addColorStop(0.5, 'rgba(177,151,252,0.025)');
    g.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(mouseX,mouseY,220,0,Math.PI*2);
    ctx.fillStyle=g; ctx.fill();
  }

  /* ── STARS ── */
  function mkStar(){
    const big=Math.random()<0.1;
    return {
      x:rnd(0,W), y:rnd(0,H),
      vx:rnd(-0.07,0.07), vy:rnd(-0.04,0.04),
      r:big?rnd(1.8,3.0):rnd(0.25,1.4),
      baseR:0,
      color:PAL[Math.floor(Math.random()*PAL.length)],
      phase:rnd(0,Math.PI*2), speed:rnd(0.007,0.032),
      big, spike:big?rnd(5,12):0, opacity:rnd(0.4,1.0),
    };
  }

  function init(){
    stars=[];
    const N=Math.floor((W*H)/4500);
    for(let i=0;i<N;i++){const s=mkStar();s.baseR=s.r;stars.push(s);}
    auroras=Array.from({length:5},mkAurora);
    shooters=[];
  }

  function spawnShooter(){
    shooters.push({
      x:rnd(0.05*W,0.95*W), y:rnd(0,0.35*H),
      len:rnd(100,220), speed:rnd(10,20),
      angle:rnd(0.25,0.65),
      life:1.0, decay:rnd(0.01,0.022),
      color:PAL[Math.floor(Math.random()*PAL.length)],
    });
  }

  function drawGlow(x,y,r,color,a){
    const g=ctx.createRadialGradient(x,y,0,x,y,r*7);
    g.addColorStop(0,hexRgba(color,a*0.9));
    g.addColorStop(0.3,hexRgba(color,a*0.3));
    g.addColorStop(1,hexRgba(color,0));
    ctx.beginPath();ctx.arc(x,y,r*7,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  }

  function drawCross(x,y,spike,color,a){
    ctx.save();ctx.globalAlpha=a*0.65;ctx.strokeStyle=color;ctx.lineWidth=0.8;
    ctx.beginPath();ctx.moveTo(x-spike,y);ctx.lineTo(x+spike,y);ctx.stroke();
    ctx.beginPath();ctx.moveTo(x,y-spike*0.55);ctx.lineTo(x,y+spike*0.55);ctx.stroke();
    ctx.restore();
  }

  const LINK=120;
  function drawLinks(){
    for(let i=0;i<stars.length;i++){
      for(let j=i+1;j<stars.length;j++){
        const a=stars[i],b=stars[j];
        const dx=a.x-b.x,dy=a.y-b.y,d=Math.sqrt(dx*dx+dy*dy);
        if(d<LINK){
          const al=(1-d/LINK)*0.22;
          const gr=ctx.createLinearGradient(a.x,a.y,b.x,b.y);
          gr.addColorStop(0,hexRgba(a.color,al));
          gr.addColorStop(1,hexRgba(b.color,al));
          ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
          ctx.strokeStyle=gr;ctx.lineWidth=(1-d/LINK)*0.85;ctx.stroke();
        }
      }
    }
  }

  /* mouse attraction */
  function applyMouseForce(){
    for(const s of stars){
      const dx=mouseX-s.x, dy=mouseY-s.y;
      const d=Math.sqrt(dx*dx+dy*dy);
      if(d<180&&d>0){
        const f=0.00012*(1-d/180);
        s.vx+=dx*f; s.vy+=dy*f;
        /* clamp velocity */
        const spd=Math.sqrt(s.vx*s.vx+s.vy*s.vy);
        if(spd>0.45){s.vx=s.vx/spd*0.45;s.vy=s.vy/spd*0.45;}
      }
    }
  }

  function draw(){
    ctx.clearRect(0,0,W,H);
    drawAuroras();
    drawSpotlight();
    applyMouseForce();
    for(const s of stars){
      s.x+=s.vx;s.y+=s.vy;s.phase+=s.speed;
      if(s.x<-5)s.x=W+5; if(s.x>W+5)s.x=-5;
      if(s.y<-5)s.y=H+5; if(s.y>H+5)s.y=-5;
    }
    drawLinks();
    for(const s of stars){
      const tw=0.5+0.5*Math.sin(s.phase);
      const tw2=0.78+0.27*Math.sin(s.phase*1.8+1.1);
      const r=s.baseR*tw2; const alph=s.opacity*tw;
      if(s.big){drawGlow(s.x,s.y,r,s.color,alph*0.6);drawCross(s.x,s.y,s.spike*tw,s.color,alph);}
      ctx.beginPath();ctx.arc(s.x,s.y,r,0,Math.PI*2);
      ctx.fillStyle=hexRgba(s.color,alph);ctx.fill();
      if(s.big){ctx.beginPath();ctx.arc(s.x,s.y,r*0.3,0,Math.PI*2);ctx.fillStyle=hexRgba('#fff',alph*0.9);ctx.fill();}
    }
    for(let i=shooters.length-1;i>=0;i--){
      const sh=shooters[i];
      sh.x+=Math.cos(sh.angle)*sh.speed; sh.y+=Math.sin(sh.angle)*sh.speed;
      sh.life-=sh.decay;
      if(sh.life<=0){shooters.splice(i,1);continue;}
      const tx=sh.x-Math.cos(sh.angle)*sh.len, ty=sh.y-Math.sin(sh.angle)*sh.len;
      const g=ctx.createLinearGradient(tx,ty,sh.x,sh.y);
      g.addColorStop(0,hexRgba(sh.color,0));
      g.addColorStop(0.65,hexRgba(sh.color,sh.life*0.55));
      g.addColorStop(1,hexRgba('#fff',sh.life*0.95));
      ctx.beginPath();ctx.moveTo(tx,ty);ctx.lineTo(sh.x,sh.y);
      ctx.strokeStyle=g;ctx.lineWidth=1.6;ctx.stroke();
    }
    requestAnimationFrame(draw);
  }

  function maybeShoot(){
    if(Math.random()<0.4)spawnShooter();
    setTimeout(maybeShoot,rnd(1800,5000));
  }

  document.addEventListener('mousemove',e=>{mouseX=e.clientX;mouseY=e.clientY;});

  resize();init();draw();maybeShoot();
  window.addEventListener('resize',()=>{resize();init();});
})();
</script>

<script>
(function(){
  const Q=[
    {t:"Vector databases don't just store data — they understand it. Every search is a journey through a high-dimensional universe of meaning.", a:"— Qdrant Engineering Blog"},
    {t:"Traditional databases ask WHERE is my data. Vector databases ask WHAT is my data closest to. That's the paradigm shift of the decade.", a:"— Weaviate Founders"},
    {t:"CLIP embeds images and language into the same geometric space. To search visually is to navigate by meaning, not metadata.", a:"— OpenAI Research"},
    {t:"ANN search with HNSW graphs returns results in milliseconds across millions of vectors — that's not fast, that's instantaneous.", a:"— Pinecone Docs"},
    {t:"In a 512-dimensional embedding space, cosine similarity measures the angle between two thoughts. Angle zero = identical meaning.", a:"— ML Engineering Handbook"},
    {t:"The future of search is not keywords. It is concepts, colours, shapes and emotions — encoded as vectors and retrieved at the speed of light.", a:"— Meta AI Research"},
    {t:"Every pixel you upload becomes a 512-number fingerprint. Qdrant scans millions of fingerprints to find your twin in under 20 milliseconds.", a:"— This Engine"},
    {t:"Vector search is the infrastructure layer that makes AI products feel magical. The magic is pure mathematics.", a:"— Andrej Karpathy"},
  ];
  let idx=0;
  function set(i){
    const tEl=document.getElementById('qt'),aEl=document.getElementById('qa');
    const dots=document.querySelectorAll('.qdot');
    if(!tEl||!aEl)return;
    tEl.style.animation='none';void tEl.offsetWidth;tEl.style.animation='qfade 0.7s ease';
    tEl.innerText='"'+Q[i].t+'"'; aEl.innerText=Q[i].a;
    dots.forEach((d,k)=>d.classList.toggle('active',k===i));
  }
  function next(){idx=(idx+1)%Q.length;set(idx);setTimeout(next,7500);}
  function tryInit(){
    if(document.getElementById('qt')){set(0);setTimeout(next,7500);}
    else setTimeout(tryInit,300);
  }
  tryInit();
})();
</script>
""", unsafe_allow_html=True)


# ══════════ HERO ══════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">CLIP · QDRANT · COSINE SIMILARITY · v2.1</div>
  <div class="hero-title">Welcome To The Fastest<br>Search Engine</div>
  <p class="hero-sub">POWERED BY NEURAL EMBEDDINGS &amp; VECTOR SPACE MATHEMATICS</p>
  <div class="hero-stats">
    <div class="stat-pill"><span class="stat-val">512</span><span class="stat-lbl">Dimensions</span></div>
    <div class="stat-pill"><span class="stat-val">&lt;20ms</span><span class="stat-lbl">Query Time</span></div>
    <div class="stat-pill"><span class="stat-val">HNSW</span><span class="stat-lbl">Index Type</span></div>
    <div class="stat-pill"><span class="stat-val">ANN</span><span class="stat-lbl">Search Mode</span></div>
    <div class="stat-pill"><span class="stat-val">CLIP</span><span class="stat-lbl">Encoder</span></div>
  </div>
  <div class="hero-rule"></div>
</div>
""", unsafe_allow_html=True)

# ══════════ QUOTES ══════════
st.markdown("""
<div class="quotes-wrap">
  <div class="quote-label">✦ Vector Intelligence</div>
  <div class="quote-text" id="qt">Loading insight…</div>
  <div class="quote-author" id="qa"></div>
  <div class="qdots">
    <div class="qdot active"></div><div class="qdot"></div><div class="qdot"></div>
    <div class="qdot"></div><div class="qdot"></div><div class="qdot"></div>
    <div class="qdot"></div><div class="qdot"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════ FACT CARDS ══════════
st.markdown("""
<div class="fact-row">
  <div class="fact-card">
    <div class="fact-icon">⚡</div>
    <div class="fact-title">ANN Search</div>
    <div class="fact-body">Approximate Nearest Neighbour via HNSW graphs. Millisecond results across tens of millions of vectors.</div>
  </div>
  <div class="fact-card">
    <div class="fact-icon">🧠</div>
    <div class="fact-title">CLIP Embedding</div>
    <div class="fact-body">OpenAI CLIP encodes images and text into a shared 512-dim latent space for cross-modal similarity.</div>
  </div>
  <div class="fact-card">
    <div class="fact-icon">🎯</div>
    <div class="fact-title">Cosine Similarity</div>
    <div class="fact-body">Measures the angle between two vectors. Score of 1.0 = identical meaning, regardless of magnitude.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════ RESULTS ══════════
def show_results(results: list, total: int):
    if not results:
        st.info("No results found in the vector space.")
        return
    st.divider()
    st.subheader(f"✦ Top {total} Neural Matches")

    cols = st.columns(len(results))
    for i, item in enumerate(results):
        with cols[i]:
            try:
                browser_url = f"http://localhost:8000{item['image_path']}"
                st.image(browser_url, use_container_width=True)
            except Exception:
                st.warning("⚠ Signal lost")
            score_pct = round(item["score"] * 100, 1)
            st.caption(f"**#{item['rank']}** · {score_pct}% match")
            filename = item["image_path"].split("/")[-1]
            label = filename.replace(".png","").split("_",1)[-1].replace("_"," ")
            st.caption(f"_{label}_")


# ══════════ SERVER STATUS ══════════
try:
    res = requests.get(f"{API_BASE}/", timeout=3)
    if res.status_code == 200:
        st.success("🟢  FastAPI online  ·  Vector engine hot  ·  HNSW index ready")
    else:
        st.error("🔴  Server returned an error")
except Exception:
    st.error("🔴  Cannot connect to FastAPI at localhost:8000 — run `uvicorn app:server --reload` first")

st.divider()

# ══════════ TABS ══════════
tab1, tab2 = st.tabs(["  📷  SEARCH BY IMAGE  ", "  💬  SEARCH BY TEXT  "])

with tab1:
    st.subheader("Upload an image")
    st.caption("Your image → 512-dim CLIP vector → ANN query → top-k nearest neighbours in Qdrant")
    uploaded_file = st.file_uploader(
        label="", type=["png","jpg","jpeg","webp"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(uploaded_file, caption="Query image", use_container_width=True)
        with col2:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {round(uploaded_file.size/1024,1)} KB")
            search_clicked = st.button("⟳  Find Similar Products", use_container_width=True, type="primary")
        if search_clicked:
            with st.spinner("Traversing vector space…"):
                try:
                    uploaded_file.seek(0)
                    files = {"file":(uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_BASE}/search", files=files, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        show_results(data["results"], data["total_results"])
                    else:
                        st.error(f"Search failed: {response.text[:300]}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the server. Is FastAPI running?")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

with tab2:
    st.subheader("Describe what you're looking for")
    st.caption("Text → CLIP tokenizer → same 512-dim space as images → semantic cross-modal retrieval")
    st.write("**Quick examples:**")
    examples = ["white sneakers","black ankle boots","leather handbag","blue trousers","grey pullover"]
    ex_cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with ex_cols[i]:
            if st.button(example, use_container_width=True):
                st.session_state["text_query"] = example
    query = st.text_input(
        label="Search query",
        placeholder="e.g. red running shoes, blue denim jacket…",
        value=st.session_state.get("text_query",""),
        label_visibility="collapsed"
    )
    if st.button("⟳  Search by Text", use_container_width=True, type="primary"):
        if not query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner(f'Encoding "{query}" into vector space…'):
                try:
                    response = requests.post(
                        f"{API_BASE}/search-by-text",
                        params={"query": query}, timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        show_results(data["results"], data["total_results"])
                    else:
                        st.error(f"Search failed: {response.text[:300]}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the server. Is FastAPI running?")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
