"""
AI Fraud Shield Pro — v4.0
Full UI/UX polish + circular mic button + all visual fixes.
Sidebar is now static (always visible).
"""

import streamlit as st
import pickle
import re
import time
import hashlib
import html as html_module

st.set_page_config(
    page_title="AI Fraud Shield Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for k, v in {
    "input_text": "",
    "analysis_done": False,
    "results": None,
    "spoken_for_hash": None,
    "sidebar_checks": [False, False, False, False],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══ ROOT VARS ═══ */
:root {
    --bg:        #05080f;
    --surface:   #090e1a;
    --panel:     #0e1525;
    --panel2:    #121c30;
    --border:    #192840;
    --border2:   #1f3354;
    --accent:    #00d4ff;
    --accent-dim:#00d4ff22;
    --accent2:   #7c3aff;
    --safe:      #00e676;
    --safe-dim:  #00e67615;
    --warn:      #ffb300;
    --warn-dim:  #ffb30015;
    --danger:    #ff1744;
    --danger-dim:#ff174415;
    --text:      #dce8f5;
    --text-soft: #8facc7;
    --muted:     #4d6a88;
    --fh: 'Syne', sans-serif;
    --fb: 'DM Sans', sans-serif;
    --fm: 'JetBrains Mono', monospace;
    --r8: 8px; --r12: 12px; --r16: 16px; --r999: 999px;
}

/* ═══ RESET ═══ */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--fb) !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding: 1.5rem 1.2rem 5rem !important;
    max-width: 1200px !important;
}
@media(min-width:768px){ .block-container{ padding: 2rem 2.5rem 5rem !important; } }

/* ═══ SCROLLBAR ═══ */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ═══ SIDEBAR ═══ */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; font-family: var(--fb) !important; }

/* Sidebar checkboxes — fix white box */
[data-testid="stSidebar"] .stCheckbox > label {
    background: transparent !important;
    color: var(--text-soft) !important;
    font-size: .875rem !important;
    gap: .5rem;
}
[data-testid="stSidebar"] .stCheckbox span[data-testid="stCheckbox"] {
    background: var(--panel2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 4px !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-soft) !important;
    font-family: var(--fb) !important;
    font-size: .84rem !important;
    border-radius: var(--r8) !important;
    padding: .5rem .9rem !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: .3rem !important;
    transition: all .18s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
    box-shadow: 0 0 14px rgba(0,212,255,.1) !important;
}

/* ═══ SIDEBAR BRAND ═══ */
.sb-brand {
    text-align: center;
    padding: 1.8rem 1rem 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
}
.sb-brand .sb-icon {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    margin: 0 auto .75rem;
    box-shadow: 0 0 32px rgba(0,212,255,.25), 0 0 64px rgba(124,58,255,.15);
    animation: sb-pulse 4s ease-in-out infinite;
}
@keyframes sb-pulse {
    0%,100%{ box-shadow: 0 0 24px rgba(0,212,255,.2), 0 0 48px rgba(124,58,255,.1); }
    50%    { box-shadow: 0 0 40px rgba(0,212,255,.4), 0 0 80px rgba(124,58,255,.2); }
}
.sb-brand h2 {
    font-family: var(--fh) !important;
    font-weight: 800; font-size: 1rem;
    letter-spacing: .1em; text-transform: uppercase;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 .25rem;
}
.sb-brand p { font-size: .76rem; color: var(--muted) !important; margin: 0; }

/* ═══ HELPLINE BOX ═══ */
.helpline {
    background: linear-gradient(135deg, rgba(255,23,68,.1), rgba(255,23,68,.04));
    border: 1px solid rgba(255,23,68,.3);
    border-radius: var(--r12);
    padding: .9rem 1rem;
    text-align: center;
    margin-bottom: 1rem;
}
.helpline .hl-tag {
    font-size: .7rem; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: var(--danger) !important;
    margin-bottom: .2rem;
}
.helpline .hl-num {
    font-family: var(--fh) !important; font-weight: 800; font-size: 1.9rem;
    color: #fff !important; text-shadow: 0 0 20px var(--danger);
    line-height: 1.1; margin-bottom: .2rem;
}
.helpline a { font-size: .78rem; color: var(--accent) !important; text-decoration: none; }
.helpline a:hover { text-decoration: underline; }

/* ═══ SECTION TITLES (sidebar) ═══ */
.sb-title {
    font-size: .68rem; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: var(--muted) !important;
    padding: .7rem 0 .4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: .75rem;
}

/* ═══ STAT ROW ═══ */
.stat-row { display: flex; gap: .5rem; margin-bottom: .5rem; }
.stat-card {
    flex: 1; background: var(--panel2); border: 1px solid var(--border);
    border-radius: var(--r8); padding: .65rem .6rem; text-align: center;
}
.stat-card .sv {
    font-family: var(--fh) !important; font-weight: 800; font-size: 1.1rem;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-card .sl { font-size: .68rem; color: var(--muted) !important; margin-top: .1rem; }
.stat-note { font-size: .68rem; color: var(--muted) !important; margin: .2rem 0 .5rem; font-style: italic; }

/* ═══ HERO ═══ */
.hero {
    position: relative;
    padding: 2.8rem 0 2rem;
    overflow: hidden;
    margin-bottom: .5rem;
}
.hero-grid {
    position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(0,212,255,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.03) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: .5rem;
    font-size: .72rem; font-weight: 600; letter-spacing: .2em;
    text-transform: uppercase; color: var(--accent);
    background: var(--accent-dim);
    border: 1px solid rgba(0,212,255,.2);
    border-radius: var(--r999);
    padding: .3rem .85rem;
    margin-bottom: 1.1rem;
}
.hero-title {
    font-family: var(--fh) !important; font-weight: 800;
    font-size: clamp(1.9rem, 4.5vw, 3.4rem);
    line-height: 1.0; letter-spacing: -.02em;
    margin: 0 0 .7rem;
    background: linear-gradient(135deg, #fff 20%, var(--accent) 60%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-family: var(--fm) !important;
    font-size: .78rem; color: var(--muted);
    letter-spacing: .12em; text-transform: uppercase;
}

/* ═══ SECTION LABEL ═══ */
.sec-label {
    display: flex; align-items: center; gap: .7rem;
    font-size: .7rem; font-weight: 700; letter-spacing: .16em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: .9rem;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: var(--border); display: block; }

/* ═══ INPUT AREA ═══ */
.input-wrapper {
    background: var(--panel);
    border: 1px solid var(--border2);
    border-radius: var(--r16);
    padding: 1rem 1rem .6rem;
    transition: border-color .25s, box-shadow .25s;
    margin-bottom: .5rem;
}
.input-wrapper:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0,212,255,.1), 0 0 28px rgba(0,212,255,.06);
}
.input-wrapper .stTextArea textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    color: var(--text) !important;
    font-family: var(--fb) !important;
    font-size: .95rem !important;
    line-height: 1.7 !important;
    caret-color: var(--accent) !important;
    resize: none !important;
}
.input-wrapper .stTextArea textarea::placeholder { color: var(--muted) !important; }
.input-wrapper .stTextArea textarea:focus { outline: none !important; box-shadow: none !important; }
.input-wrapper .stTextArea label { display: none !important; }
[data-testid="stTextArea"] > label { display: none !important; }

/* ═══ CIRCULAR MIC BUTTON ═══ */
/* Targets the mic recorder's iframe/button container */
.mic-row { display: flex; align-items: center; gap: .75rem; padding-top: .4rem; }
.mic-label { font-size: .76rem; color: var(--muted); font-style: italic; }

/* Override the white square box from streamlit_mic_recorder */
[data-testid="stColumn"] > div:has(iframe) iframe,
.mic-wrap iframe {
    border-radius: 50% !important;
    border: none !important;
    background: transparent !important;
}

/* The mic button itself — force circle via CSS injection into component */
.mic-wrap {
    width: 48px !important;
    height: 48px !important;
    border-radius: 50% !important;
    overflow: hidden !important;
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    box-shadow: 0 0 20px rgba(0,212,255,.25) !important;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    animation: mic-idle 3s ease-in-out infinite;
}
@keyframes mic-idle {
    0%,100%{ box-shadow: 0 0 16px rgba(0,212,255,.2); }
    50%    { box-shadow: 0 0 30px rgba(0,212,255,.4), 0 0 60px rgba(124,58,255,.2); }
}
.mic-wrap iframe {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    border-radius: 50% !important;
    background: transparent !important;
    opacity: 0 !important;  /* invisible, still clickable */
}
/* Visible mic emoji overlay */
.mic-wrap::after {
    content: "🎤";
    font-size: 1.3rem;
    pointer-events: none;
    z-index: 1;
}

/* ═══ CHAR COUNTER ═══ */
.char-row {
    display: flex; justify-content: flex-end; align-items: center;
    gap: .5rem; margin-top: .3rem;
}
.char-count { font-family: var(--fm) !important; font-size: .72rem; color: var(--muted); }
.char-count.over { color: var(--warn); }

/* ═══ ANALYZE BUTTON — override Streamlit primary ═══ */
div[data-testid="column"] > div > div > div > .stButton > button,
.analyze-btn .stButton > button,
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent2) 0%, var(--accent) 100%) !important;
    border: none !important;
    color: #05080f !important;
    font-family: var(--fh) !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    border-radius: var(--r999) !important;
    padding: .85rem 2rem !important;
    box-shadow: 0 4px 30px rgba(0,212,255,.25) !important;
    transition: all .2s ease !important;
    width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 40px rgba(0,212,255,.4) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* ═══ PROGRESS BAR ═══ */
[data-testid="stProgressBar"] > div { background: var(--panel2) !important; border-radius: 99px !important; }
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent2), var(--accent)) !important;
    border-radius: 99px !important;
    transition: width .1s linear !important;
}

/* ═══ METRIC CARDS ═══ */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: .8rem;
    margin-bottom: 1rem;
}
@media(min-width: 700px){
    .cards-grid { grid-template-columns: repeat(4, 1fr); }
}
.mc {
    background: var(--panel);
    border: 1px solid var(--border2);
    border-radius: var(--r16);
    padding: 1.4rem 1rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform .25s ease, border-color .25s ease;
}
.mc::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0; transition: opacity .3s;
}
.mc:hover { transform: translateY(-4px); border-color: var(--accent); }
.mc:hover::before { opacity: 1; }
.mc .mv {
    font-family: var(--fh) !important; font-weight: 800;
    font-size: 1.8rem; line-height: 1.1; margin-bottom: .3rem;
}
.mc .ml {
    font-size: .7rem; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: var(--muted);
}
.mc .mv.small { font-size: 1rem; padding-top: .5rem; }
.c-safe   { color: var(--safe)   !important; }
.c-warn   { color: var(--warn)   !important; }
.c-danger { color: var(--danger) !important; }
.c-accent { color: var(--accent) !important; }
.c-a2     { color: var(--accent2)!important; }

/* ═══ VERDICT BANNER ═══ */
.verdict {
    display: flex; gap: 1.2rem; align-items: flex-start;
    border-radius: var(--r16); padding: 1.6rem 1.8rem;
    margin: 1.2rem 0;
    position: relative; overflow: hidden;
}
.verdict::before {
    content: ''; position: absolute; inset: 0;
    background: repeating-linear-gradient(
        45deg,
        transparent, transparent 20px,
        rgba(255,255,255,.01) 20px, rgba(255,255,255,.01) 21px
    );
    pointer-events: none;
}
.v-safe   { background: var(--safe-dim);   border: 1px solid rgba(0,230,118,.3); }
.v-warn   { background: var(--warn-dim);   border: 1px solid rgba(255,179,0,.3); }
.v-danger { background: var(--danger-dim); border: 1px solid rgba(255,23,68,.4);
            animation: dpulse 2.5s ease-in-out infinite; }
@keyframes dpulse {
    0%,100%{ box-shadow: 0 0 0 0 rgba(255,23,68,0);    }
    50%    { box-shadow: 0 0 0 8px rgba(255,23,68,.08); }
}
.v-icon  { font-size: 2.4rem; flex-shrink: 0; }
.v-title { font-family: var(--fh) !important; font-weight: 800; font-size: 1.2rem; margin-bottom: .35rem; }
.v-body  { font-size: .9rem; color: var(--text-soft); line-height: 1.65; }

/* ═══ HIGHLIGHT BOX ═══ */
.hl-box {
    background: var(--panel2);
    border: 1px solid var(--border2);
    border-radius: var(--r12);
    padding: 1.3rem 1.4rem;
    font-size: .92rem; line-height: 2.1;
    word-break: break-word;
    color: var(--text);
    font-family: var(--fb) !important;
}

/* ═══ TIP ITEMS ═══ */
.tip {
    background: var(--panel2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 0 var(--r12) var(--r12) 0;
    padding: .8rem 1.1rem;
    margin-bottom: .55rem;
    font-size: .88rem; line-height: 1.6;
    color: var(--text-soft);
    transition: all .18s ease;
}
.tip:hover {
    border-left-color: var(--accent);
    background: rgba(0,212,255,.04);
    color: var(--text);
    transform: translateX(3px);
}

/* ═══ EXPANDERS ═══ */
[data-testid="stExpander"] {
    background: var(--panel) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r12) !important;
    margin-bottom: .7rem !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: var(--panel) !important;
    color: var(--text) !important;
    font-family: var(--fb) !important;
    font-weight: 600 !important;
    font-size: .875rem !important;
    padding: .9rem 1.1rem !important;
    border-radius: var(--r12) !important;
}
[data-testid="stExpander"] summary:hover { background: var(--panel2) !important; }
[data-testid="stExpander"] > div:last-child {
    background: var(--panel) !important;
    border-top: 1px solid var(--border) !important;
    padding: 1rem 1.1rem !important;
}

/* ═══ REPORT CARDS ═══ */
.rep-card {
    background: var(--panel2); border: 1px solid var(--border2);
    border-radius: var(--r12); padding: 1rem 1.1rem;
}
.rep-card .rt {
    font-size: .7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
    color: var(--muted); border-bottom: 1px solid var(--border);
    padding-bottom: .5rem; margin-bottom: .65rem;
}
.rep-card p { font-size: .86rem; margin: .3rem 0; color: var(--text-soft); }
.rep-card a { color: var(--accent); text-decoration: none; }
.rep-card a:hover { color: var(--accent2); text-decoration: underline; }

/* ═══ SHARE BUTTONS ═══ */
.stLinkButton > a,
.share-row .stButton > button {
    background: var(--panel2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-soft) !important;
    font-family: var(--fb) !important;
    font-size: .84rem !important;
    border-radius: var(--r8) !important;
    text-align: center !important;
    transition: all .18s ease !important;
    text-decoration: none !important;
}
.stLinkButton > a:hover,
.share-row .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
}

/* ═══ SPEAK BUTTON ═══ */
.speak-btn .stButton > button {
    background: var(--panel2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-soft) !important;
    font-size: .84rem !important;
    border-radius: var(--r999) !important;
    transition: all .18s ease !important;
}
.speak-btn .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
    box-shadow: 0 0 16px rgba(0,212,255,.15) !important;
}

/* ═══ TOAST FIX ═══ */
[data-testid="stToast"] {
    background: var(--panel2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--r12) !important;
}

/* ═══ ALERTS ═══ */
[data-testid="stAlert"] {
    background: var(--panel2) !important;
    border-radius: var(--r12) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
}

/* ═══ DIVIDER ═══ */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ═══ SUCCESS MSG ═══ */
[data-testid="stAlert"][data-baseweb="notification"] {
    color: var(--text) !important;
}

/* ═══ FOOTER ═══ */
.ft {
    text-align: center; padding: 2rem 0 .5rem;
}
.ft-brand {
    font-family: var(--fh) !important; font-weight: 800; font-size: .9rem;
    letter-spacing: .12em; text-transform: uppercase;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: .4rem;
}
.ft-copy { font-size: .75rem; color: var(--muted); letter-spacing: .03em; line-height: 1.8; }

/* ═══ SPINNER ═══ */
.stSpinner > div > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ── FLOATING SIDEBAR TOGGLE (white chevron) ─────────────────────────────
st.markdown("""
<div style="
    position: fixed;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    z-index: 99999;
    background: rgba(20, 30, 50, 0.9);
    backdrop-filter: blur(4px);
    border: 1px solid #2a3a5a;
    border-left: none;
    border-radius: 0 30px 30px 0;
    padding: 12px 8px 12px 12px;
    box-shadow: 2px 4px 20px rgba(0,0,0,0.5);
    cursor: pointer;
    transition: 0.2s;
    color: white;
    font-size: 24px;
    font-weight: bold;
    line-height: 1;
" id="sidebarToggleBtn" onclick="toggleSidebarFromOutside()">
    ❯
</div>

<script>
function toggleSidebarFromOutside() {
    const parentDoc = window.parent.document;
    
    // Try to find the expand button (visible when sidebar is collapsed)
    const expandBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]');
    if (expandBtn) {
        expandBtn.click();
        return;
    }
    
    // If expand button not found, sidebar is probably open – find its close button
    const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        const closeBtn = sidebar.querySelector('button[kind="closeSidebar"]');
        if (closeBtn) {
            closeBtn.click();
            return;
        }
    }
    
    // Fallback: try to click the header hamburger (if header visible)
    const hamburger = parentDoc.querySelector('[data-testid="stSidebarNav"] button');
    if (hamburger) hamburger.click();
}
</script>
""", unsafe_allow_html=True)
# ── MODEL LOADING ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI models…")
def load_models():
    mdl = {"ok": False, "type_model_available": False}
    for key, fname in {"model_risk": "model_risk.pkl", "tfidf": "tfidf_vectorizer.pkl", "label_encoder": "label_encoder.pkl"}.items():
        try:
            with open(fname, "rb") as f:
                mdl[key] = pickle.load(f)
        except FileNotFoundError:
            st.error(f"⚠️ Missing: **{fname}** — ensure all .pkl files are in the app directory.")
            return mdl
    mdl["ok"] = True
    try:
        with open("model_type.pkl", "rb") as f:
            mdl["model_type"] = pickle.load(f)
        mdl["type_model_available"] = True
    except FileNotFoundError:
        pass
    return mdl

models = load_models()


# ── UTILITIES ──────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"(https?://|ftp://|www\.)\S+|\b\w+\.(com|in|org|net|io)\S*", " URL ", text)
    text = re.sub(r"\b\d{10,12}\b", " PHONE ", text)
    text = re.sub(r"(rs\.?\s*\d[\d,]*|\d[\d,]*\s*(lakh|crore|thousand|k)|₹\s*\d[\d,]*)", " AMOUNT ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sanitize_and_highlight(raw: str) -> str:
    safe = html_module.escape(raw)
    kw = {
        "upi":"#00d4ff","gpay":"#00d4ff","phonepe":"#00d4ff","neft":"#00d4ff","imps":"#00d4ff",
        "pin":"#ff1744","otp":"#ff1744","click":"#ff1744","urgent":"#ff1744","immediately":"#ff1744",
        "blocked":"#ff1744","suspended":"#ff1744","deactivated":"#ff1744",
        "lottery":"#ffb300","won":"#ffb300","prize":"#ffb300","kbc":"#ffb300","winner":"#ffb300","congratulations":"#ffb300",
        "job":"#00e676","salary":"#00e676","work from home":"#00e676","earn":"#00e676","hiring":"#00e676",
        "kyc":"#a855f7","update":"#a855f7","verify":"#a855f7","link":"#a855f7","aadhaar":"#a855f7","pan":"#a855f7",
        "bank":"#22d3ee","account":"#22d3ee","atm":"#22d3ee",
        "courier":"#fb923c","parcel":"#fb923c","customs":"#fb923c","dhl":"#fb923c","fedex":"#fb923c",
        "netflix":"#e879f9","subscription":"#e879f9","amazon prime":"#e879f9",
        "matrimony":"#f472b6","shaadi":"#f472b6",
        "scholarship":"#34d399","exam":"#34d399",
    }
    for word, color in kw.items():
        safe = re.compile(f"({re.escape(word)})", re.IGNORECASE).sub(
            f'<span style="background:rgba(0,0,0,.4);color:{color};border-radius:4px;'
            f'padding:1px 6px;font-weight:700;border-bottom:2px solid {color}80;">\\1</span>', safe
        )
    return safe


def rule_based_type(msg: str) -> str:
    m = msg.lower()
    if any(k in m for k in ["courier","parcel","customs","dhl","fedex","package","cargo"]): return "Courier Scam"
    if any(k in m for k in ["netflix","amazon prime","subscription","recharge","renewal","ott"]): return "Subscription Scam"
    if any(k in m for k in ["matrimony","shaadi","bride","groom","marriage"]): return "Romance / Matrimony Scam"
    if any(k in m for k in ["upi","gpay","phonepe","pin","otp","bank","account","atm","neft","imps"]): return "UPI / Banking Fraud"
    if any(k in m for k in ["job","work from home","salary","part time","earning","vacancy","hiring"]): return "Job Scam"
    if any(k in m for k in ["lottery","won","prize","kbc","winner","lucky draw","congratulations"]): return "Lottery Scam"
    if any(k in m for k in ["kyc","update","verify","aadhaar","pan","link","click","deactivat","suspended"]): return "Phishing"
    return "Other Fraud"


def get_tips(ftype: str) -> list:
    tips = {
        "UPI / Banking Fraud":     ["❌ NEVER share your UPI PIN or OTP — not even with bank employees","✅ Always verify the recipient ID before confirming any payment","⚠️ Real banks NEVER ask for passwords or KYC via SMS","📞 Report to **1930** immediately if you suspect fraud"],
        "Job Scam":                ["❌ No genuine employer charges a registration or security deposit","✅ Verify the company on LinkedIn and their official website","⚠️ 'Earn ₹50k/day from home' offers are almost always scams","📞 Report at [cybercrime.gov.in](https://www.cybercrime.gov.in)"],
        "Lottery Scam":            ["❌ You cannot win a lottery you never entered","✅ KBC and Amazon NEVER announce winners via SMS","⚠️ Never pay any 'processing fee' to claim a prize","📞 Report to **1930**"],
        "Phishing":                ["❌ Banks never request passwords, OTP, or Aadhaar via SMS links","✅ Always type your bank's URL manually — never follow SMS links","⚠️ Look for subtle misspellings in URLs like 'sbi-secure-update.com'","📞 Call the National Cyber Helpline: **1930**"],
        "Courier Scam":            ["❌ Real courier companies never charge customs fees via SMS","✅ Check delivery issues only on the courier's official website","⚠️ Never pay via UPI or crypto to 'release' a package","📞 Report to **1930** or local police"],
        "Subscription Scam":       ["❌ Netflix/Amazon never ask you to pay via a link in SMS","✅ Always renew subscriptions through the official app","⚠️ Phishing sites closely mimic OTT platforms — check the URL","📞 Report to **1930**"],
        "Romance / Matrimony Scam":["❌ Never send money to someone you've only met online","✅ Always video-call verify before trusting someone","⚠️ Scammers often fake medical or travel emergencies to create urgency","📞 Report at [cybercrime.gov.in](https://www.cybercrime.gov.in)"],
        "Other Fraud":             ["❌ Don't click on shortened or unfamiliar links","✅ Verify the sender's identity through official channels","⚠️ Never share Aadhaar, PAN, or bank details over SMS/WhatsApp","📞 Report suspicious messages to **1930**"],
    }
    for k in tips:
        if k.lower() in ftype.lower() or ftype.lower() in k.lower():
            return tips[k]
    return tips["Other Fraud"]


SAMPLES = {
    "UPI Fraud":    "Your UPI payment of Rs.5000 to Flipkart is pending. Click tinyurl.com/complete to pay now",
    "Job Scam":     "Work from home job: Earn Rs.5000/day typing data. Contact on Telegram @jobs_india",
    "Lottery Scam": "Congratulations! You won Rs.25 lakhs in KBC Lucky Draw. Claim: rebrand.ly/claim-now",
    "Phishing":     "Your Aadhaar card will be deactivated in 24 hours. Update now: uidai-update.com",
    "Courier Scam": "Your FedEx courier from USA is held at customs. Pay Rs.5000 to release: bit.ly/pay-now",
    "Safe Message": "Hi, how are you? Let's meet for dinner at 8 pm tonight",
}


def speak(msg: str, repeat: int = 1) -> None:
    safe = msg.replace("\\","\\\\").replace("'","\\'").replace("\n"," ").replace("\r","")
    st.components.v1.html(f"""
    <script>(function(){{
        if(!window.speechSynthesis)return;
        var m='{safe}',n={repeat};
        function s(i){{if(i>=n)return;var u=new SpeechSynthesisUtterance(m);u.rate=0.9;u.pitch=1;u.volume=1;u.onend=function(){{s(i+1);}};window.speechSynthesis.cancel();window.speechSynthesis.speak(u);}}
        setTimeout(function(){{s(0);}},300);
    }})();</script>""", height=1)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-icon">🛡️</div>
        <h2>Fraud Shield Pro</h2>
        <p>AI-Powered Cyber Protection</p>
    </div>
    <div class="helpline">
        <div class="hl-tag">🚨 Cyber Helpline</div>
        <div class="hl-num">1930</div>
        <a href="https://www.cybercrime.gov.in" target="_blank">cybercrime.gov.in →</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-title">Safety Checklist</div>', unsafe_allow_html=True)
    chks = [
        st.checkbox("Never share OTP",            value=st.session_state.sidebar_checks[0], key="c0"),
        st.checkbox("Never share UPI PIN",         value=st.session_state.sidebar_checks[1], key="c1"),
        st.checkbox("Check links before clicking", value=st.session_state.sidebar_checks[2], key="c2"),
        st.checkbox("Verify sender identity",      value=st.session_state.sidebar_checks[3], key="c3"),
    ]
    st.session_state.sidebar_checks = chks
    if all(chks):
        st.success("✅ All safety practices followed!")

    if models.get("ok"):
        st.markdown('<div class="sb-title" style="margin-top:.8rem">Model Performance</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="stat-row">
            <div class="stat-card"><div class="sv">99.9%</div><div class="sl">Binary Acc.</div></div>
            <div class="stat-card"><div class="sv">94.5%</div><div class="sl">Type Acc.</div></div>
        </div>
        <div class="stat-note">Trained on Indian SMS fraud dataset</div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sb-title" style="margin-top:.8rem">Quick Test Messages</div>', unsafe_allow_html=True)
    for label, key in [("📧 UPI Fraud","UPI Fraud"),("💼 Job Scam","Job Scam"),("🎲 Lottery Scam","Lottery Scam"),("🔗 Phishing","Phishing"),("📦 Courier Scam","Courier Scam"),("✅ Safe Message","Safe Message")]:
        if st.button(label, key=f"sb_{key}"):
            st.session_state.input_text = SAMPLES[key]
            st.session_state.analysis_done = False
            st.session_state.results = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-grid"></div>
    <div class="hero-eyebrow">⬡ Real-Time Threat Intelligence</div>
    <div class="hero-title">AI Fraud Shield Pro</div>
    <div class="hero-sub">SMS · Message · Fraud Risk Analysis Engine · v4.0</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec-label">Input Message</div>', unsafe_allow_html=True)

# ── VOICE INPUT ──
voice_text = None
try:
    from streamlit_mic_recorder import speech_to_text as _stt
    mic_col, hint_col = st.columns([1, 9])
    with mic_col:
        # Wrap in div to apply circular styling
        st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
        voice_text = _stt(language="en", start_prompt="🎤", stop_prompt="⏹️", just_once=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with hint_col:
        st.markdown('<div style="padding-top:.6rem;font-size:.78rem;color:var(--muted);font-style:italic">🎤 Tap to dictate &nbsp;·&nbsp; or type / paste below</div>', unsafe_allow_html=True)
    if voice_text and voice_text.strip() and voice_text.strip() != st.session_state.input_text.strip():
        st.session_state.input_text = voice_text.strip()
        st.session_state.analysis_done = False
        st.rerun()
except ImportError:
    st.caption("ℹ️ Install `streamlit-mic-recorder` to enable voice input.")

# ── TEXT AREA wrapped in styled div ──
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
st.text_area(
    "msg",
    value=st.session_state.input_text,
    height=140,
    placeholder="Paste or type the suspicious message here…",
    label_visibility="collapsed",
    key="input_text",
)
st.markdown('</div>', unsafe_allow_html=True)

# ── CHAR COUNTER ──
cc = len(st.session_state.input_text)
st.markdown(
    f'<div class="char-row"><span class="char-count{"  over" if cc > 500 else ""}">{cc} chars</span></div>',
    unsafe_allow_html=True
)

# ── ANALYZE BUTTON ──
_, btn_col, _ = st.columns([1.5, 2, 1.5])
with btn_col:
    go = st.button("🔍  Analyze Message", type="primary", use_container_width=True)


# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if go:
    raw = st.session_state.input_text.strip()
    if len(raw) < 10:
        st.warning("⚠️ Please enter at least 10 characters.")
    elif not models.get("ok"):
        st.error("❌ Models not loaded. Check your .pkl files.")
    else:
        pb = st.progress(0)
        st_txt = st.empty()
        try:
            for p in range(0, 101, 5):
                time.sleep(0.018)
                pb.progress(p)
                st_txt.caption(f"🔬 Scanning… {p}%")
            vec = models["tfidf"].transform([clean_text(raw)])
            proba = models["model_risk"].predict_proba(vec)
            prob = float(proba[0][1]) * 100 if proba.shape[1] >= 2 else (85.0 if int(models["model_risk"].predict(vec)[0]) else 10.0)
            risk = "Safe" if prob < 30 else ("Suspicious" if prob < 70 else "High Risk")
            if risk == "Safe":
                ftype = "None"
            elif models.get("type_model_available"):
                try:
                    ftype = models["label_encoder"].inverse_transform([models["model_type"].predict(vec)[0]])[0]
                except Exception:
                    ftype = rule_based_type(raw)
            else:
                ftype = rule_based_type(raw)
            st.session_state.analysis_done = True
            st.session_state.results = {
                "prob": prob, "risk": risk, "ftype": ftype,
                "hl": sanitize_and_highlight(raw),
                "tips": get_tips(ftype if risk != "Safe" else "Other Fraud"),
            }
        except Exception as e:
            st.error(f"❌ Analysis error: {e}")
        finally:
            pb.empty(); st_txt.empty()


# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.analysis_done and st.session_state.results:
    r = st.session_state.results

    st.markdown("---")
    st.markdown('<div class="sec-label">Analysis Results</div>', unsafe_allow_html=True)

    pc   = "c-safe" if r["risk"]=="Safe" else ("c-warn" if r["risk"]=="Suspicious" else "c-danger")
    act  = "No Action"  if r["risk"]=="Safe" else ("Report Now" if r["risk"]=="High Risk" else "Be Cautious")
    ac   = "c-safe"     if r["risk"]=="Safe" else ("c-danger"   if r["risk"]=="High Risk" else "c-warn")
    long = len(r["ftype"]) > 10

    st.markdown(f"""
    <div class="cards-grid">
        <div class="mc">
            <div class="mv {pc}">{r["prob"]:.1f}%</div>
            <div class="ml">Scam Probability</div>
        </div>
        <div class="mc">
            <div class="mv {pc}">{r["risk"]}</div>
            <div class="ml">Risk Level</div>
        </div>
        <div class="mc">
            <div class="mv c-a2{"  small" if long else ""}">{r["ftype"]}</div>
            <div class="ml">Fraud Type</div>
        </div>
        <div class="mc">
            <div class="mv {ac}{"  small" if len(act)>8 else ""}">{act}</div>
            <div class="ml">Recommended Action</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Verdict
    vmap = {
        "Safe":     ("v-safe",   "✅","#00e676","Safe Message","This message appears legitimate. Stay vigilant and never share personal information unless you can verify the sender."),
        "Suspicious":("v-warn",  "⚠️","#ffb300","Suspicious Message","Suspicious patterns detected. Do not click any links or respond until you can verify the sender through an official channel."),
        "High Risk": ("v-danger","🚨","#ff1744","HIGH RISK — SCAM DETECTED",f"This is highly likely a <strong style='color:#ff8080'>{r['ftype']}</strong>. DO NOT respond, call back, or click any links. Report to 1930 immediately."),
    }
    vc, vi, vcolor, vtitle, vbody = vmap[r["risk"]]
    st.markdown(f"""
    <div class="verdict {vc}">
        <span class="v-icon">{vi}</span>
        <div>
            <div class="v-title" style="color:{vcolor}">{vtitle}</div>
            <div class="v-body">{vbody}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Auto TTS (once per unique result)
    rhash = hashlib.md5(f"{r['risk']}_{r['ftype']}_{r['prob']:.0f}".encode()).hexdigest()
    if st.session_state.spoken_for_hash != rhash:
        st.session_state.spoken_for_hash = rhash
        if r["risk"] == "High Risk":
            speak(f"High risk scam detected. Fraud type: {r['ftype']}. Do not respond.", repeat=2)
        elif r["risk"] == "Suspicious":
            speak(f"Suspicious message. Possible {r['ftype']}. Be cautious.", repeat=1)
        else:
            speak("Message appears safe. Stay vigilant.", repeat=1)

    # Manual speak
    st.markdown('<div class="speak-btn">', unsafe_allow_html=True)
    sc, _ = st.columns([1,5])
    with sc:
        if st.button("🔊 Speak Alert", use_container_width=True, key="btn_speak"):
            speak(f"{'High risk scam' if r['risk']=='High Risk' else ('Suspicious message' if r['risk']=='Suspicious' else 'Safe message')}. {'Fraud type: ' + r['ftype'] + '. Do not respond.' if r['risk']!='Safe' else 'Stay vigilant.'}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Expanders
    with st.expander("🔍  Pattern Analysis — Highlighted Keywords", expanded=True):
        st.markdown(f'<div class="hl-box">{r["hl"]}</div>', unsafe_allow_html=True)

    with st.expander("💡  Preventive Guidance", expanded=True):
        for tip in r["tips"]:
            st.markdown(f'<div class="tip">{tip}</div>', unsafe_allow_html=True)

    with st.expander("📞  Report & Support Resources"):
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""<div class="rep-card"><div class="rt">🌐 Online Reporting</div>
            <p>📞 <strong>1930</strong> — National Cyber Helpline (24×7)</p>
            <p>🔗 <a href="https://www.cybercrime.gov.in" target="_blank">cybercrime.gov.in</a></p></div>""", unsafe_allow_html=True)
        with rc2:
            st.markdown("""<div class="rep-card"><div class="rt">🚔 Emergency</div>
            <p>📞 <strong>100</strong> — Local Police</p>
            <p>📞 <strong>112</strong> — Mobile Emergency</p></div>""", unsafe_allow_html=True)

    # Share
    st.markdown("---")
    st.markdown('<div class="sec-label">Share This Analysis</div>', unsafe_allow_html=True)
    share = f"Fraud Alert\nRisk: {r['risk']} ({r['prob']:.0f}%)\nType: {r['ftype']}\nReport: 1930 | cybercrime.gov.in"
    enc   = share.replace("\n","%0A").replace(" ","%20")

    st.markdown('<div class="share-row">', unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    with s1: st.link_button("📧 Email",    f"mailto:?subject=Fraud%20Alert&body={enc}", use_container_width=True)
    with s2: st.link_button("📱 WhatsApp", f"https://wa.me/?text={enc}",                use_container_width=True)
    with s3: st.link_button("🐦 X / Twitter", f"https://twitter.com/intent/tweet?text={enc[:240]}", use_container_width=True)
    with s4:
        if st.button("📋 Copy", use_container_width=True, key="btn_copy"):
            safe_copy = share.replace("`","'").replace("\\","\\\\")
            st.components.v1.html(f"<script>navigator.clipboard.writeText(`{safe_copy}`).catch(()=>{{}});</script>",height=1)
            st.toast("✅ Copied!", icon="📋")
    st.markdown('</div>', unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="ft">
    <div class="ft-brand">🛡️ AI Fraud Shield Pro</div>
    <div class="ft-copy">
        Powered by Machine Learning &nbsp;·&nbsp; Report Suspicious Messages to 1930<br>
        Always verify before sharing personal information &nbsp;·&nbsp; © 2025 Hackathon Project
    </div>
</div>
""", unsafe_allow_html=True)
