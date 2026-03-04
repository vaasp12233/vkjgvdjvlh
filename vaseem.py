from streamlit_mic_recorder import speech_to_text
import streamlit as st
import pickle
import re
import hashlib
import html
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Fraud Shield Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SESSION STATE ---
defaults = {
    'input_text': "",
    'analysis_done': False,
    'results': None,
    'speak_alert': False,
    'spoken_for_hash': None,
    'last_analyzed_text': "",      # to detect manual changes
    'auto_voice_enabled': True,    # user preference
    'show_sidebar': True,           # sidebar toggle
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- CUSTOM CSS (with additions for sidebar toggle & circular mic) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

/* ── BASE (unchanged) ── */
:root {
    --bg:        #080c14;
    --surface:   #0d1424;
    --panel:     #111a2e;
    --border:    #1e2d4a;
    --accent:    #00e5ff;
    --accent2:   #7b2fff;
    --safe:      #00e676;
    --warn:      #ffb300;
    --danger:    #ff1744;
    --text:      #e2eaf5;
    --text-soft: #a8bdd4;
    --muted:     #6b8aaa;
    --font-head: 'Syne', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1280px !important; }

/* ── SIDEBAR with toggle support ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    transition: width 0.3s ease, min-width 0.3s ease !important;
    overflow-x: hidden !important;
}
[data-testid="stSidebar"][aria-expanded="true"] {
    min-width: 280px !important;
    width: auto !important;
}
/* When sidebar is "hidden", we collapse it via content visibility */
.sidebar-collapsed [data-testid="stSidebar"] {
    width: 0 !important;
    min-width: 0 !important;
    border-right: none !important;
}
/* Buttons inside sidebar */
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Sidebar content wrapper – hidden when collapsed */
.sidebar-content {
    display: block;
    width: 280px;
}
.sidebar-collapsed .sidebar-content {
    display: none;
}

/* Sidebar header */
.sidebar-brand {
    text-align: center;
    padding: 1.5rem 0 1rem;
}
.sidebar-brand .shield-icon {
    font-size: 2.8rem;
    display: block;
    margin-bottom: .4rem;
    filter: drop-shadow(0 0 14px var(--accent));
    animation: pulse-icon 3s ease-in-out infinite;
}
@keyframes pulse-icon {
    0%,100% { filter: drop-shadow(0 0 10px var(--accent)); }
    50%      { filter: drop-shadow(0 0 24px var(--accent)); }
}
.sidebar-brand h2 {
    font-family: var(--font-head);
    font-weight: 800;
    font-size: 1.15rem;
    letter-spacing: .06em;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.sidebar-brand p {
    font-family: var(--font-body);
    font-size: .8rem;
    color: var(--muted) !important;
    letter-spacing: .04em;
    margin-top: .3rem;
}

/* Helpline box */
.helpline-box {
    background: linear-gradient(135deg, rgba(255,23,68,.12), rgba(255,23,68,.06));
    border: 1px solid rgba(255,23,68,.35);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    text-align: center;
    margin: .5rem 0 1.2rem;
}
.helpline-box .hl-label {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: .75rem;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--danger) !important;
    margin-bottom: .3rem;
}
.helpline-box .hl-number {
    font-family: var(--font-head);
    font-weight: 800;
    font-size: 2rem;
    color: #fff !important;
    letter-spacing: .05em;
    text-shadow: 0 0 18px var(--danger);
    line-height: 1.2;
}
.helpline-box a {
    font-family: var(--font-body);
    font-size: .8rem;
    color: var(--accent) !important;
    text-decoration: none;
}
.helpline-box a:hover { text-decoration: underline; }

/* Sidebar section titles */
.sidebar-section-title {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: .75rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted) !important;
    padding: .6rem 0 .35rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: .7rem;
}

/* Sidebar metric cards */
.stat-row {
    display: flex;
    gap: .5rem;
    margin-bottom: .6rem;
}
.stat-card {
    flex: 1;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: .7rem .8rem;
    text-align: center;
}
.stat-card .sv {
    font-family: var(--font-head);
    font-weight: 800;
    font-size: 1.15rem;
    color: var(--accent) !important;
}
.stat-card .sl {
    font-family: var(--font-body);
    font-size: .72rem;
    color: var(--muted) !important;
    margin-top: .15rem;
}

/* Sidebar quick‑test buttons */
[data-testid="stSidebar"] .stButton > button {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-soft) !important;
    font-family: var(--font-body) !important;
    font-size: .85rem !important;
    font-weight: 500 !important;
    border-radius: 7px !important;
    padding: .5rem .8rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: all .2s ease !important;
    margin-bottom: .25rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(0,229,255,.06) !important;
    box-shadow: 0 0 12px rgba(0,229,255,.12) !important;
}

/* Sidebar checkboxes */
[data-testid="stSidebar"] .stCheckbox label {
    font-family: var(--font-body) !important;
    font-size: .875rem !important;
    color: var(--text-soft) !important;
}
[data-testid="stSidebar"] .stCheckbox { margin-bottom: .3rem; }

/* Main hero header */
.hero-section {
    position: relative;
    padding: 2.5rem 0 1.8rem;
    overflow: hidden;
}
.hero-bg-lines {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(0,229,255,.04) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 79px, rgba(0,229,255,.03) 80px);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: .8rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: .7rem;
    opacity: .9;
}
.hero-title {
    font-family: var(--font-head);
    font-weight: 800;
    font-size: clamp(2rem, 4vw, 3.2rem);
    line-height: 1.05;
    letter-spacing: -.01em;
    margin: 0 0 .6rem;
    background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-family: var(--font-body);
    font-size: .9rem;
    color: var(--muted);
    letter-spacing: .04em;
}

/* Input area */
.stTextArea label {
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: .8rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
.stTextArea textarea {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-size: .95rem !important;
    line-height: 1.7 !important;
    padding: 1rem 1.2rem !important;
    caret-color: var(--accent) !important;
    transition: border-color .25s ease, box-shadow .25s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.12), 0 0 24px rgba(0,229,255,.08) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: var(--muted) !important; opacity: .7 !important; }

/* Analyze button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent2) 0%, var(--accent) 100%) !important;
    border: none !important;
    color: #080c14 !important;
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    padding: .85rem 2rem !important;
    cursor: pointer !important;
    box-shadow: 0 4px 24px rgba(0,229,255,.3) !important;
    transition: all .25s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,229,255,.45), 0 0 0 3px rgba(0,229,255,.15) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Metric cards row */
.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 1.2rem 1.1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color .3s ease, transform .3s ease;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: .5;
}
.metric-card .mc-value {
    font-family: var(--font-head);
    font-weight: 800;
    font-size: 2rem;
    line-height: 1.1;
    margin-bottom: .35rem;
}
.metric-card .mc-label {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: .78rem;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--muted);
}
.mc-safe    { color: var(--safe);   }
.mc-warn    { color: var(--warn);   }
.mc-danger  { color: var(--danger); }
.mc-accent  { color: var(--accent); }
.mc-accent2 { color: var(--accent2);}
.mc-white   { color: #fff;          }

/* Verdict banner */
.verdict-banner {
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    display: flex;
    align-items: flex-start;
    gap: 1.2rem;
    margin: 1.2rem 0;
    position: relative;
    overflow: hidden;
}
.vb-safe   { background: rgba(0,230,118,.08);  border: 1px solid rgba(0,230,118,.3);  }
.vb-warn   { background: rgba(255,179,0,.08);  border: 1px solid rgba(255,179,0,.3);  }
.vb-danger { background: rgba(255,23,68,.1);   border: 1px solid rgba(255,23,68,.4);  animation: danger-pulse 2s ease-in-out infinite; }
@keyframes danger-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(255,23,68,.0);  }
    50%      { box-shadow: 0 0 0 6px rgba(255,23,68,.12); }
}
.vb-icon  { font-size: 2.4rem; flex-shrink: 0; margin-top: .1rem; }
.vb-title { font-family: var(--font-head); font-weight: 800; font-size: 1.25rem; margin-bottom: .4rem; }
.vb-body  {
    font-family: var(--font-body);
    font-size: .9rem;
    color: var(--text-soft);
    line-height: 1.65;
}

/* Highlighted message box */
.highlight-box {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    font-family: var(--font-body);
    font-size: .92rem;
    line-height: 2;
    word-break: break-word;
    color: var(--text);
}

/* Tips list */
.tip-item {
    background: var(--panel);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0;
    padding: .85rem 1.1rem;
    margin-bottom: .6rem;
    font-family: var(--font-body);
    font-size: .9rem;
    line-height: 1.65;
    color: var(--text-soft);
    transition: border-color .2s, background .2s;
}
.tip-item:hover {
    background: rgba(0,229,255,.04);
    border-left-color: var(--accent2);
    color: var(--text);
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    letter-spacing: .03em !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 1.2rem !important;
}

/* Report support box */
.report-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
}
.report-card .rc-title {
    font-family: var(--font-body);
    font-weight: 700;
    font-size: .78rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .7rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: .45rem;
}
.report-card p { font-family: var(--font-body); font-size: .88rem; margin: .35rem 0; color: var(--text-soft); }
.report-card a { color: var(--accent); text-decoration: none; }
.report-card a:hover { text-decoration: underline; color: var(--accent2); }

/* Share buttons */
div[data-testid="column"] .stButton > button {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    font-family: var(--font-body) !important;
    font-size: .85rem !important;
    border-radius: 8px !important;
    transition: all .2s ease !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(0,229,255,.05) !important;
}

/* Footer */
.app-footer {
    text-align: center;
    padding: 1.5rem 0 .5rem;
}
.app-footer .af-brand {
    font-family: var(--font-head);
    font-weight: 700;
    font-size: .9rem;
    letter-spacing: .1em;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: .3rem;
}
.app-footer .af-copy {
    font-family: var(--font-body);
    font-size: .78rem;
    color: var(--muted);
    letter-spacing: .03em;
}

/* Section label */
.section-label {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: .75rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .8rem;
    display: flex;
    align-items: center;
    gap: .6rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* Alerts / warnings */
.stAlert { border-radius: 10px !important; font-family: var(--font-body) !important; font-size: .88rem !important; line-height: 1.55 !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ===== NEW STYLES FOR MICROPHONE & SIDEBAR TOGGLE ===== */
/* Circular mic button */
div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button {
    width: 48px !important;
    height: 48px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.5rem !important;
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 12px rgba(0,229,255,.2) !important;
}

/* Sidebar toggle button container */
.sidebar-toggle-btn {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.5rem;
}
.sidebar-toggle-btn .stButton > button {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-soft) !important;
    border-radius: 8px !important;
    padding: 0.3rem 0.8rem !important;
    font-size: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- APPLY SIDEBAR COLLAPSE CLASS BASED ON SESSION STATE ---
if not st.session_state.show_sidebar:
    st.markdown('<style>.sidebar-collapsed [data-testid="stSidebar"] { width: 0 !important; min-width: 0 !important; border-right: none !important; }</style>', unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource(show_spinner="Loading AI models...")
def load_models():
    models = {}
    model_dir = Path(__file__).parent
    try:
        models['model_risk'] = pickle.load(open(model_dir / 'model_risk.pkl', 'rb'))
        models['tfidf'] = pickle.load(open(model_dir / 'tfidf_vectorizer.pkl', 'rb'))
        models['label_encoder'] = pickle.load(open(model_dir / 'label_encoder.pkl', 'rb'))
    except FileNotFoundError as e:
        st.error(f"⚠️ Missing model file: {e}. Please ensure model_risk.pkl, tfidf_vectorizer.pkl, and label_encoder.pkl are in the app directory.")
        return None
    try:
        models['model_type'] = pickle.load(open(model_dir / 'model_type.pkl', 'rb'))
        models['type_model_available'] = True
    except FileNotFoundError:
        models['type_model_available'] = False
        st.warning("ℹ️ Fraud type model not found. Using rule‑based fallback.")
    return models

models = load_models()

# --- TEXT CLEANING ---
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' URL ', text)
    text = re.sub(r'\b\d{10}\b', ' PHONE ', text)
    text = re.sub(r'rs\.?\s*\d+|\d+\s*(lakh|crore|thousand)|₹\s*\d+', ' AMOUNT ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- KEYWORD HIGHLIGHTING (with HTML escaping) ---
def highlight_keywords(text):
    keywords = {
        'upi': '#00e5ff', 'gpay': '#00e5ff', 'phonepe': '#00e5ff',
        'pin': '#ff1744', 'otp': '#ff1744',
        'lottery': '#ffb300', 'won': '#ffb300', 'prize': '#ffb300', 'kbc': '#ffb300',
        'job': '#00e676', 'salary': '#00e676', 'work from home': '#00e676',
        'kyc': '#7b2fff', 'update': '#7b2fff', 'verify': '#7b2fff', 'link': '#7b2fff',
        'bank': '#00bcd4', 'account': '#00bcd4', 'blocked': '#ff1744', 'suspended': '#ff1744',
        'courier': '#ff9800', 'parcel': '#ff9800', 'dhl': '#ff9800', 'fedex': '#ff9800',
        'netflix': '#e040fb', 'amazon prime': '#e040fb', 'subscription': '#e040fb',
        'matrimony': '#f06292', 'shaadi': '#f06292', 'caste': '#f06292',
        'education': '#26c6da', 'scholarship': '#26c6da', 'exam': '#26c6da'
    }
    # Escape HTML in original text to prevent injection
    escaped = html.escape(text)
    for word, color in keywords.items():
        pattern = re.compile(f'({re.escape(word)})', re.IGNORECASE)
        escaped = pattern.sub(
            f'<span style="background:rgba(0,0,0,.35);color:{color};border-radius:3px;padding:1px 5px;font-weight:700;border-bottom:2px solid {color};">\\1</span>',
            escaped
        )
    return escaped

# --- FALLBACK RULE‑BASED FRAUD TYPE CLASSIFIER (updated with courier) ---
def rule_based_fraud_type(message):
    msg = message.lower()
    if any(k in msg for k in ['upi', 'gpay', 'phonepe', 'pin', 'otp', 'bank', 'account', 'atm']):
        return 'UPI Fraud'
    elif any(k in msg for k in ['job', 'work from home', 'salary', 'part time', 'earning']):
        return 'Job Scam'
    elif any(k in msg for k in ['lottery', 'won', 'prize', 'kbc', 'winner']):
        return 'Lottery Scam'
    elif any(k in msg for k in ['kyc', 'update', 'verify', 'aadhaar', 'pan', 'link', 'click']):
        return 'Phishing'
    elif any(k in msg for k in ['courier', 'parcel', 'dhl', 'fedex', 'customs']):
        return 'Courier Scam'
    else:
        return 'Others'

# --- PREVENTIVE TIPS (added Courier Scam) ---
def get_preventive_tips(fraud_type):
    tips = {
        "UPI Fraud": [
            "❌ NEVER share UPI PIN or OTP with anyone",
            "✅ Always check VPA/UPI ID before making payment",
            "⚠️ Banks NEVER ask for KYC via SMS links",
            "📞 Report suspicious UPI transactions to **1930** immediately"
        ],
        "Job Scam": [
            "❌ No genuine job asks for registration fees",
            "✅ Verify company on LinkedIn before applying",
            "⚠️ Be cautious of 'work from home' jobs promising high income",
            "📞 Report job scams on [cybercrime.gov.in](https://www.cybercrime.gov.in)"
        ],
        "Lottery Scam": [
            "❌ You cannot win a lottery you never entered",
            "✅ KBC/Amazon never inform winners via SMS",
            "⚠️ Never pay 'processing fees' to claim prizes",
            "📞 Report lottery scams to **1930**"
        ],
        "Phishing": [
            "❌ Banks never ask for passwords or OTP via SMS",
            "✅ Always type bank URLs manually, don't click links",
            "⚠️ Check for spelling mistakes in URLs",
            "📞 Report phishing to [report.phishing@gmail.com](mailto:report.phishing@gmail.com)"
        ],
        "Courier Scam": [
            "❌ Genuine courier companies never ask for customs payment via SMS links",
            "✅ Track your parcel using official website only",
            "⚠️ Be wary of unexpected parcel notifications",
            "📞 Report courier scams to **1930**"
        ],
        "Others": [
            "❌ Don't click on unknown links",
            "✅ Verify sender identity before responding",
            "⚠️ Never share personal information via SMS",
            "📞 Report suspicious messages to **1930**"
        ]
    }
    return tips.get(fraud_type, tips["Others"])

# --- SAMPLE MESSAGES ---
SAMPLE_MESSAGES = {
    "UPI Fraud":    "Your UPI payment of Rs.5000 to Flipkart is pending. Click tinyurl.com/complete to pay now",
    "Job Scam":     "Work from home job: Earn Rs.5000/day typing data. Contact on Telegram @jobs_india",
    "Lottery Scam": "Congratulations! You won Rs.25 lakhs in KBC Lucky Draw. Claim: rebrand.ly/claim-now",
    "Phishing":     "Your Aadhaar card will be deactivated in 24 hours. Update now: uidai-update.com",
    "Courier Scam": "Your FedEx courier from USA is held at customs. Pay Rs.5000 to release: bit.ly/pay-now",
    "Safe Message": "Hi, how are you? Let's meet for dinner at 8 pm tonight"
}

# ══════════════════════════════════════════════════════
# SIDEBAR (toggleable content)
# ══════════════════════════════════════════════════════
with st.sidebar:
    # Only show full content if sidebar is toggled ON
    if st.session_state.show_sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <span class="shield-icon">🛡️</span>
            <h2>FRAUD SHIELD PRO</h2>
            <p>AI-Powered Cyber Protection</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="helpline-box">
            <div class="hl-label">🚨 Official Cyber Helpline</div>
            <div class="hl-number">1930</div>
            <a href="https://www.cybercrime.gov.in" target="_blank">cybercrime.gov.in →</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">Safety Checklist</div>', unsafe_allow_html=True)
        safe1 = st.checkbox("Never share OTP")
        safe2 = st.checkbox("Never share UPI PIN")
        safe3 = st.checkbox("Check links before clicking")
        safe4 = st.checkbox("Verify sender identity")
        if safe1 and safe2 and safe3 and safe4:
            st.success("✅ You're following all safety practices!")

        st.markdown('<div class="sidebar-section-title" style="margin-top:.8rem">Model Performance</div>', unsafe_allow_html=True)
        if models and models.get('model_risk'):
            st.markdown("""
            <div class="stat-row">
                <div class="stat-card"><div class="sv">99.9%</div><div class="sl">Binary Accuracy</div></div>
                <div class="stat-card"><div class="sv">94.5%</div><div class="sl">Type Accuracy</div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title" style="margin-top:.8rem">Quick Test Messages</div>', unsafe_allow_html=True)

        if st.button("📧 UPI Fraud Sample"):
            st.session_state.input_text = SAMPLE_MESSAGES["UPI Fraud"]
            st.session_state.analysis_done = False
            st.rerun()
        if st.button("💼 Job Scam Sample"):
            st.session_state.input_text = SAMPLE_MESSAGES["Job Scam"]
            st.session_state.analysis_done = False
            st.rerun()
        if st.button("🎲 Lottery Scam Sample"):
            st.session_state.input_text = SAMPLE_MESSAGES["Lottery Scam"]
            st.session_state.analysis_done = False
            st.rerun()
        if st.button("🔗 Phishing Sample"):
            st.session_state.input_text = SAMPLE_MESSAGES["Phishing"]
            st.session_state.analysis_done = False
            st.rerun()
        if st.button("📦 Courier Scam Sample"):
            st.session_state.input_text = SAMPLE_MESSAGES["Courier Scam"]
            st.session_state.analysis_done = False
            st.rerun()
        if st.button("✅ Safe Message Sample"):
            st.session_state.input_text = SAMPLE_MESSAGES["Safe Message"]
            st.session_state.analysis_done = False
            st.rerun()

        # Auto voice toggle
        st.markdown('<div class="sidebar-section-title" style="margin-top:.8rem">Preferences</div>', unsafe_allow_html=True)
        st.session_state.auto_voice_enabled = st.checkbox("🔊 Auto voice alert", value=st.session_state.auto_voice_enabled)

# ══════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════
# Sidebar toggle button (outside sidebar)
col_toggle, _ = st.columns([0.1, 0.9])
with col_toggle:
    if st.button("☰", help="Toggle sidebar"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.rerun()

st.markdown("""
<div class="hero-section">
    <div class="hero-bg-lines"></div>
    <div class="hero-eyebrow">⬡ Real-Time Threat Intelligence</div>
    <div class="hero-title">AI Fraud Shield Pro</div>
    <div class="hero-sub">SMS / MESSAGE FRAUD RISK ANALYSIS ENGINE · v2.0</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Input Message</div>', unsafe_allow_html=True)

# ── VOICE INPUT ──
col_mic, col_text = st.columns([1, 6])

with col_mic:
    text_from_voice = speech_to_text(
        language='en',
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True
    )
    if text_from_voice and text_from_voice != st.session_state.input_text:
        st.session_state.input_text = text_from_voice
        st.rerun()

with col_text:
    # Use a text area with a unique key, but we also need to detect changes.
    # We'll store previous value in session state and compare after widget rendering.
    # Streamlit automatically updates st.session_state.input_text when user types.
    st.text_area(
        "Paste the message you received:",
        height=130,
        placeholder="Type, paste, or speak a suspicious message here...",
        key="input_text",
        label_visibility="collapsed"
    )

# Check if input text changed since last analysis (user typed manually)
if st.session_state.input_text != st.session_state.last_analyzed_text:
    st.session_state.analysis_done = False
    st.session_state.results = None

col1, col2, col3 = st.columns([1.5, 2, 1.5])
with col2:
    analyze_clicked = st.button("🔍  Analyze Message", type="primary", use_container_width=True)

# ── ANALYSIS ──
if analyze_clicked:
    if not st.session_state.input_text or len(st.session_state.input_text.strip()) < 10:
        st.warning("⚠️ Please enter a valid message (at least 10 characters).")
    elif models is None:
        st.error("Models not loaded. Please check model files.")
    else:
        with st.spinner("🔬 Scanning message through AI engine..."):
            # (No fake progress bar – just spinner)
            cleaned  = clean_text(st.session_state.input_text)
            vec      = models['tfidf'].transform([cleaned])
            prob_spam = models['model_risk'].predict_proba(vec)[0][1] * 100

            if prob_spam < 30:
                risk = "Safe"
            elif prob_spam < 75:
                risk = "Suspicious"
            else:
                risk = "High Risk"

            if risk == "Safe":
                fraud_type = "None"
            else:
                if models.get('type_model_available'):
                    type_encoded  = models['model_type'].predict(vec)[0]
                    detailed_type = models['label_encoder'].inverse_transform([type_encoded])[0]
                    fraud_type    = detailed_type
                else:
                    fraud_type = rule_based_fraud_type(st.session_state.input_text)

            highlighted = highlight_keywords(st.session_state.input_text)
            tips        = get_preventive_tips(fraud_type if risk != "Safe" else "Others")

            st.session_state.analysis_done = True
            st.session_state.results = {
                'prob_spam':   prob_spam,
                'risk':        risk,
                'fraud_type':  fraud_type,
                'highlighted': highlighted,
                'tips':        tips
            }
            st.session_state.last_analyzed_text = st.session_state.input_text

# ── RESULTS ──
if st.session_state.analysis_done and st.session_state.results:
    res = st.session_state.results

    st.markdown("---")
    st.markdown('<div class="section-label">Analysis Results</div>', unsafe_allow_html=True)

    # Metric cards
    prob_color = "mc-safe" if res['risk']=="Safe" else ("mc-warn" if res['risk']=="Suspicious" else "mc-danger")
    action     = "No Action" if res['risk'] == "Safe" else ("Report Now" if res['risk'] == "High Risk" else "Be Cautious")
    action_col = "mc-safe" if res['risk']=="Safe" else ("mc-danger" if res['risk']=="High Risk" else "mc-warn")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-value {prob_color}">{res['prob_spam']:.1f}%</div>
            <div class="mc-label">Scam Probability</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-value {prob_color}">{res['risk']}</div>
            <div class="mc-label">Risk Level</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-value mc-accent2" style="font-size:1.1rem;padding-top:.3rem">{res['fraud_type']}</div>
            <div class="mc-label">Fraud Type</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-value {action_col}" style="font-size:1rem;padding-top:.3rem">{action}</div>
            <div class="mc-label">Recommended Action</div>
        </div>""", unsafe_allow_html=True)

    # Verdict banner
    if res['risk'] == "Safe":
        st.markdown(f"""
        <div class="verdict-banner vb-safe" style="margin-top:1.2rem">
            <span class="vb-icon">✅</span>
            <div>
                <div class="vb-title" style="color:#00e676">Safe Message</div>
                <div class="vb-body">This message appears legitimate. However, always stay vigilant and verify before sharing personal information.</div>
            </div>
        </div>""", unsafe_allow_html=True)
    elif res['risk'] == "Suspicious":
        st.markdown(f"""
        <div class="verdict-banner vb-warn" style="margin-top:1.2rem">
            <span class="vb-icon">⚠️</span>
            <div>
                <div class="vb-title" style="color:#ffb300">Suspicious Message</div>
                <div class="vb-body">This message shows suspicious patterns. Do not engage with the sender or click any links until verified.</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-banner vb-danger" style="margin-top:1.2rem">
            <span class="vb-icon">🚨</span>
            <div>
                <div class="vb-title" style="color:#ff1744">HIGH RISK — SCAM DETECTED</div>
                <div class="vb-body">This is highly likely a <strong style="color:#ff6b6b">{res['fraud_type']}</strong>. DO NOT respond, call back, or click any links. Report immediately to 1930.</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ========== AUTOMATIC VOICE ALERT (if enabled) ==========
    if st.session_state.auto_voice_enabled:
        current_hash = hashlib.md5(f"{res['risk']}_{res['fraud_type']}".encode()).hexdigest()
        if st.session_state.spoken_for_hash != current_hash:
            st.session_state.spoken_for_hash = current_hash
            if res['risk'] == "High Risk":
                repeat = 3
                message = f"High risk scam detected. Fraud type: {res['fraud_type']}. Do not respond."
            elif res['risk'] == "Suspicious":
                repeat = 1
                message = f"Suspicious message detected. Fraud type: {res['fraud_type']}. Be cautious."
            else:
                repeat = 1
                message = "Message appears safe. Stay vigilant."
            message_js = message.replace("'", "\\'").replace('"', '&quot;')
            js_code = f"""
            <script>
            (function() {{
                var msg = "{message_js}";
                var times = {repeat};
                function speak(i) {{
                    if (i >= times) return;
                    var utterance = new SpeechSynthesisUtterance(msg);
                    utterance.rate = 0.9;
                    utterance.pitch = 1;
                    utterance.volume = 1;
                    utterance.onend = function() {{ speak(i+1); }};
                    utterance.onerror = function() {{}};
                    window.speechSynthesis.speak(utterance);
                }}
                speak(0);
            }})();
            </script>
            """
            st.components.v1.html(js_code, height=0)

    # ========== MANUAL VOICE ALERT BUTTON (fixed double rerun) ==========
    col_speak, _ = st.columns([1, 5])
    with col_speak:
        # Use on_click to set a flag, then trigger JS in the main flow
        def trigger_manual_alert():
            st.session_state.speak_alert = True

        st.button("🔊 Speak Alert", on_click=trigger_manual_alert, use_container_width=True)

    # Trigger manual alert if flag is set (and then clear it without extra rerun)
    if st.session_state.get('speak_alert'):
        # Choose message based on risk
        if res['risk'] == "High Risk":
            manual_message = f"Alert! {res['risk']} scam detected. Fraud type: {res['fraud_type']}. Do not respond to this message."
        elif res['risk'] == "Suspicious":
            manual_message = f"Alert! {res['risk']} message detected. Fraud type: {res['fraud_type']}. Be cautious."
        else:
            manual_message = "This message appears safe. Stay vigilant."
        manual_js = manual_message.replace("'", "\\'").replace('"', '&quot;')
        st.components.v1.html(
            f"""
            <script>
            var utterance = new SpeechSynthesisUtterance("{manual_js}");
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 1;
            utterance.onerror = function() {{}};
            window.speechSynthesis.speak(utterance);
            </script>
            """,
            height=0
        )
        # Clear flag without rerunning
        st.session_state.speak_alert = False
        # No st.rerun() here

    # Pattern analysis expander
    with st.expander("🔍  Pattern Analysis — Highlighted Keywords", expanded=True):
        st.markdown(f'<div class="highlight-box">{res["highlighted"]}</div>', unsafe_allow_html=True)

    # Preventive guidance expander
    with st.expander("💡  Preventive Guidance", expanded=True):
        for tip in res['tips']:
            st.markdown(f'<div class="tip-item">{tip}</div>', unsafe_allow_html=True)

    # Report & support expander
    with st.expander("📞  Report & Support Resources"):
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div class="report-card">
                <div class="rc-title">🌐 Online Reporting</div>
                <p>📞 <strong>1930</strong> — National Cyber Helpline (24×7)</p>
                <p>🔗 <a href="https://www.cybercrime.gov.in" target="_blank">cybercrime.gov.in</a></p>
            </div>""", unsafe_allow_html=True)
        with rc2:
            st.markdown("""
            <div class="report-card">
                <div class="rc-title">🚔 Emergency Contacts</div>
                <p>📞 <strong>100</strong> — Local Police</p>
                <p>📞 <strong>112</strong> — Mobile Emergency</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-label">Share This Analysis</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)

    # Prepare share text
    share_text = f"🔍 AI Fraud Shield Analysis:\nRisk: {res['risk']} ({res['prob_spam']:.1f}% scam probability)\nFraud Type: {res['fraud_type']}\nMessage: {st.session_state.input_text[:100]}..."
    share_url = "https://your-app-url.com"  # Replace with actual app URL if deployed

    with s1:
        # Email
        email_subject = "Fraud Alert Analysis"
        email_body = share_text.replace(" ", "%20").replace("\n", "%0A")
        st.markdown(f'<a href="mailto:?subject={email_subject}&body={email_body}" target="_blank"><button style="width:100%; background:var(--panel); border:1px solid var(--border); color:var(--muted); border-radius:8px; padding:0.5rem;">📧 Email</button></a>', unsafe_allow_html=True)
    with s2:
        # WhatsApp
        wa_text = share_text.replace(" ", "%20").replace("\n", "%0A")
        st.markdown(f'<a href="https://wa.me/?text={wa_text}" target="_blank"><button style="width:100%; background:var(--panel); border:1px solid var(--border); color:var(--muted); border-radius:8px; padding:0.5rem;">📱 WhatsApp</button></a>', unsafe_allow_html=True)
    with s3:
        # Twitter
        tweet_text = share_text.replace(" ", "%20").replace("\n", "%0A")
        st.markdown(f'<a href="https://twitter.com/intent/tweet?text={tweet_text}" target="_blank"><button style="width:100%; background:var(--panel); border:1px solid var(--border); color:var(--muted); border-radius:8px; padding:0.5rem;">🐦 Twitter</button></a>', unsafe_allow_html=True)
    with s4:
        # Copy link (simulate copy via JavaScript alert)
        if st.button("📋 Copy Link", use_container_width=True):
            st.info("Link copied to clipboard (simulated). In a real app, you'd use JavaScript.")
            # Actual copy would require JS, but we can show a message.

# ── FOOTER ──
st.markdown("---")
st.markdown("""
<div class="app-footer">
    <div class="af-brand">🛡️ AI FRAUD SHIELD PRO</div>
    <div class="af-copy">Powered by Machine Learning · Report Suspicious Messages to 1930 · © 2025 Hackathon Project</div>
</div>
""", unsafe_allow_html=True)
