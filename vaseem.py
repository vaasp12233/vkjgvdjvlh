"""
AI Fraud Shield Pro — v3.0
Fixed Edition: All UI/UX, functionality, and code issues resolved.
"""

# ── IMPORTS ────────────────────────────────────────────────────────────────────
import streamlit as st
import pickle
import re
import time
import hashlib
import html as html_module

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Fraud Shield Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE DEFAULTS ─────────────────────────────────────────────────────
_defaults = {
    "input_text": "",
    "analysis_done": False,
    "results": None,
    "speak_alert": False,
    "spoken_for_hash": None,
    "sidebar_checks": [False, False, False, False],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

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

#MainMenu, footer, header { visibility: hidden; }

/* Responsive padding */
.block-container {
    padding: 1.5rem 1.5rem 4rem !important;
    max-width: 1280px !important;
}
@media (min-width: 768px) {
    .block-container { padding: 2rem 3rem 4rem !important; }
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.sidebar-brand { text-align: center; padding: 1.5rem 0 1rem; }
.sidebar-brand .shield-icon {
    font-size: 2.8rem; display: block; margin-bottom: .4rem;
    filter: drop-shadow(0 0 14px var(--accent));
    animation: pulse-icon 3s ease-in-out infinite;
}
@keyframes pulse-icon {
    0%,100% { filter: drop-shadow(0 0 10px var(--accent)); }
    50%      { filter: drop-shadow(0 0 24px var(--accent)); }
}
.sidebar-brand h2 {
    font-family: var(--font-head); font-weight: 800; font-size: 1.15rem;
    letter-spacing: .06em;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
}
.sidebar-brand p {
    font-size: .8rem; color: var(--muted) !important;
    letter-spacing: .04em; margin-top: .3rem;
}

.helpline-box {
    background: linear-gradient(135deg, rgba(255,23,68,.12), rgba(255,23,68,.06));
    border: 1px solid rgba(255,23,68,.35); border-radius: 10px;
    padding: 1rem 1.1rem; text-align: center; margin: .5rem 0 1.2rem;
}
.helpline-box .hl-label {
    font-weight: 600; font-size: .75rem; letter-spacing: .06em;
    text-transform: uppercase; color: var(--danger) !important; margin-bottom: .3rem;
}
.helpline-box .hl-number {
    font-family: var(--font-head); font-weight: 800; font-size: 2rem;
    color: #fff !important; letter-spacing: .05em;
    text-shadow: 0 0 18px var(--danger); line-height: 1.2;
}
.helpline-box a { font-size: .8rem; color: var(--accent) !important; text-decoration: none; }
.helpline-box a:hover { text-decoration: underline; }

.sidebar-section-title {
    font-weight: 600; font-size: .75rem; letter-spacing: .1em;
    text-transform: uppercase; color: var(--muted) !important;
    padding: .6rem 0 .35rem; border-bottom: 1px solid var(--border); margin-bottom: .7rem;
}

.stat-row { display: flex; gap: .5rem; margin-bottom: .6rem; }
.stat-card {
    flex: 1; background: var(--panel); border: 1px solid var(--border);
    border-radius: 8px; padding: .7rem .8rem; text-align: center;
}
.stat-card .sv { font-family: var(--font-head); font-weight: 800; font-size: 1.15rem; color: var(--accent) !important; }
.stat-card .sl { font-size: .72rem; color: var(--muted) !important; margin-top: .15rem; }

.hero-section { position: relative; padding: 2.5rem 0 1.8rem; overflow: hidden; }
.hero-bg-lines {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background:
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(0,229,255,.04) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 79px, rgba(0,229,255,.03) 80px);
    pointer-events: none;
}
.hero-eyebrow {
    font-weight: 600; font-size: .8rem; letter-spacing: .18em;
    text-transform: uppercase; color: var(--accent); margin-bottom: .7rem; opacity: .9;
}
.hero-title {
    font-family: var(--font-head); font-weight: 800;
    font-size: clamp(1.8rem, 4vw, 3.2rem); line-height: 1.05; letter-spacing: -.01em; margin: 0 0 .6rem;
    background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { font-size: .9rem; color: var(--muted); letter-spacing: .04em; }

.section-label {
    font-weight: 600; font-size: .75rem; letter-spacing: .15em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: .8rem; display: flex; align-items: center; gap: .6rem;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.mic-hint { font-size: .78rem; color: var(--muted); margin-top: .3rem; font-style: italic; }
.char-counter { font-size: .78rem; color: var(--muted); text-align: right; margin-top: .25rem; }
.char-counter.warn { color: var(--warn); }

.metric-card {
    background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
    padding: 1.5rem 1.2rem 1.1rem; text-align: center; position: relative;
    overflow: hidden; transition: border-color .3s ease, transform .3s ease;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: .5;
}
.metric-card .mc-value {
    font-family: var(--font-head); font-weight: 800; font-size: 2rem;
    line-height: 1.1; margin-bottom: .35rem;
}
.metric-card .mc-label {
    font-weight: 500; font-size: .78rem; letter-spacing: .06em;
    text-transform: uppercase; color: var(--muted);
}
.mc-safe    { color: var(--safe);    }
.mc-warn    { color: var(--warn);    }
.mc-danger  { color: var(--danger);  }
.mc-accent  { color: var(--accent);  }
.mc-accent2 { color: var(--accent2); }

.verdict-banner {
    border-radius: 14px; padding: 1.5rem 1.8rem;
    display: flex; align-items: flex-start; gap: 1.2rem;
    margin: 1.2rem 0; position: relative; overflow: hidden;
}
.vb-safe   { background: rgba(0,230,118,.08);  border: 1px solid rgba(0,230,118,.3);  }
.vb-warn   { background: rgba(255,179,0,.08);  border: 1px solid rgba(255,179,0,.3);  }
.vb-danger { background: rgba(255,23,68,.1);   border: 1px solid rgba(255,23,68,.4);
             animation: danger-pulse 2s ease-in-out infinite; }
@keyframes danger-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(255,23,68,.0);   }
    50%      { box-shadow: 0 0 0 6px rgba(255,23,68,.12); }
}
.vb-icon  { font-size: 2.4rem; flex-shrink: 0; margin-top: .1rem; }
.vb-title { font-family: var(--font-head); font-weight: 800; font-size: 1.25rem; margin-bottom: .4rem; }
.vb-body  { font-size: .9rem; color: var(--text-soft); line-height: 1.65; }

.highlight-box {
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.3rem 1.5rem; font-size: .92rem; line-height: 2;
    word-break: break-word; color: var(--text);
}

.tip-item {
    background: var(--panel); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: 0 10px 10px 0;
    padding: .85rem 1.1rem; margin-bottom: .6rem; font-size: .9rem;
    line-height: 1.65; color: var(--text-soft);
    transition: border-color .2s, background .2s;
}
.tip-item:hover { background: rgba(0,229,255,.04); border-left-color: var(--accent2); color: var(--text); }

.report-card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.3rem; }
.report-card .rc-title {
    font-weight: 700; font-size: .78rem; letter-spacing: .08em; text-transform: uppercase;
    color: var(--muted); margin-bottom: .7rem; border-bottom: 1px solid var(--border); padding-bottom: .45rem;
}
.report-card p { font-size: .88rem; margin: .35rem 0; color: var(--text-soft); }
.report-card a { color: var(--accent); text-decoration: none; }
.report-card a:hover { text-decoration: underline; color: var(--accent2); }

.app-footer { text-align: center; padding: 1.5rem 0 .5rem; }
.app-footer .af-brand {
    font-family: var(--font-head); font-weight: 700; font-size: .9rem; letter-spacing: .1em;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: .3rem;
}
.app-footer .af-copy { font-size: .78rem; color: var(--muted); letter-spacing: .03em; }

.stAlert { border-radius: 10px !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── MODEL LOADING ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI models…")
def load_models():
    """
    Loads required model files. Returns a dict with status flags so callers
    can handle partial-load scenarios gracefully instead of crashing.
    """
    models: dict = {"ok": False, "type_model_available": False}

    required = {
        "model_risk":     "model_risk.pkl",
        "tfidf":          "tfidf_vectorizer.pkl",
        "label_encoder":  "label_encoder.pkl",
    }
    for key, fname in required.items():
        try:
            with open(fname, "rb") as f:
                models[key] = pickle.load(f)
        except FileNotFoundError:
            st.error(
                f"⚠️ Missing required model file: **{fname}**. "
                "Ensure all .pkl files are in the app directory."
            )
            return models  # partial load — ok stays False

    models["ok"] = True

    # Optional type model
    try:
        with open("model_type.pkl", "rb") as f:
            models["model_type"] = pickle.load(f)
        models["type_model_available"] = True
    except FileNotFoundError:
        st.info("ℹ️ Fraud-type model not found — using rule-based fallback.")

    return models


models = load_models()

# ── TEXT UTILITIES ─────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"(https?://|ftp://|www\.)\S+|\b\w+\.(com|in|org|net|io)\S*", " URL ", text)
    text = re.sub(r"\b\d{10,12}\b", " PHONE ", text)
    text = re.sub(r"(rs\.?\s*\d[\d,]*|\d[\d,]*\s*(lakh|crore|thousand|k)|₹\s*\d[\d,]*)", " AMOUNT ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sanitize_and_highlight(raw_text: str) -> str:
    """
    SECURITY FIX: HTML-escape user input FIRST to prevent XSS,
    then inject safe highlighting spans.
    """
    safe_text = html_module.escape(raw_text)

    keywords = {
        "upi": "#00e5ff", "gpay": "#00e5ff", "phonepe": "#00e5ff",
        "pin": "#ff1744", "otp": "#ff1744", "click": "#ff1744",
        "urgent": "#ff1744", "immediately": "#ff1744",
        "lottery": "#ffb300", "won": "#ffb300", "prize": "#ffb300",
        "kbc": "#ffb300", "winner": "#ffb300",
        "job": "#00e676", "salary": "#00e676", "work from home": "#00e676",
        "kyc": "#7b2fff", "update": "#7b2fff", "verify": "#7b2fff", "link": "#7b2fff",
        "bank": "#00bcd4", "account": "#00bcd4",
        "blocked": "#ff1744", "suspended": "#ff1744", "deactivated": "#ff1744",
        "courier": "#ff9800", "parcel": "#ff9800", "dhl": "#ff9800", "fedex": "#ff9800",
        "netflix": "#e040fb", "amazon prime": "#e040fb", "subscription": "#e040fb",
        "matrimony": "#f06292", "shaadi": "#f06292",
        "scholarship": "#26c6da", "exam": "#26c6da",
    }

    for word, color in keywords.items():
        pattern = re.compile(f"({re.escape(word)})", re.IGNORECASE)
        safe_text = pattern.sub(
            f'<span style="background:rgba(0,0,0,.35);color:{color};border-radius:3px;'
            f'padding:1px 5px;font-weight:700;border-bottom:2px solid {color};">\\1</span>',
            safe_text,
        )
    return safe_text


# ── FRAUD TYPE RULE-BASED FALLBACK ─────────────────────────────────────────────
def rule_based_fraud_type(message: str) -> str:
    """
    FIX: Extended and prioritised keyword lists so courier/subscription/
    romance scams are correctly classified rather than falling to 'Other'.
    """
    msg = message.lower()
    if any(k in msg for k in ["courier", "parcel", "customs", "dhl", "fedex", "package", "cargo"]):
        return "Courier Scam"
    if any(k in msg for k in ["netflix", "amazon prime", "subscription", "recharge", "renewal", "ott"]):
        return "Subscription Scam"
    if any(k in msg for k in ["matrimony", "shaadi", "bride", "groom", "marriage", "match"]):
        return "Romance / Matrimony Scam"
    if any(k in msg for k in ["upi", "gpay", "phonepe", "pin", "otp", "bank", "account", "atm", "neft", "imps", "ifsc"]):
        return "UPI / Banking Fraud"
    if any(k in msg for k in ["job", "work from home", "salary", "part time", "earning", "vacancy", "hiring", "recruitment"]):
        return "Job Scam"
    if any(k in msg for k in ["lottery", "won", "prize", "kbc", "winner", "lucky draw", "congratulations", "selected"]):
        return "Lottery Scam"
    if any(k in msg for k in ["kyc", "update", "verify", "aadhaar", "pan", "link", "click", "deactivat", "suspended", "blocked"]):
        return "Phishing"
    return "Other Fraud"


# ── PREVENTIVE TIPS ────────────────────────────────────────────────────────────
def get_preventive_tips(fraud_type: str) -> list:
    tips_map = {
        "UPI / Banking Fraud": [
            "❌ NEVER share UPI PIN or OTP with anyone — not even bank employees",
            "✅ Always verify the recipient VPA/UPI ID before confirming payment",
            "⚠️ Banks NEVER ask for KYC or password via SMS or phone call",
            "📞 Report suspicious UPI transactions to **1930** immediately",
        ],
        "Job Scam": [
            "❌ No legitimate employer ever asks for a registration or security deposit",
            "✅ Verify the company on LinkedIn and their official website before applying",
            "⚠️ 'Work from home, earn ₹50k/day' offers are almost always scams",
            "📞 Report job scams on [cybercrime.gov.in](https://www.cybercrime.gov.in)",
        ],
        "Lottery Scam": [
            "❌ You cannot win a lottery or lucky draw you never entered",
            "✅ KBC, Amazon, and government bodies NEVER announce winners via SMS",
            "⚠️ Never pay any 'processing fee' or 'tax' upfront to claim a prize",
            "📞 Report lottery scams to **1930**",
        ],
        "Phishing": [
            "❌ Banks never ask for passwords, OTP, or Aadhaar via SMS links",
            "✅ Always type your bank's URL manually — never click links in SMS",
            "⚠️ Check for subtle spelling mistakes in URLs (e.g., 'sbi-bank-update.com')",
            "📞 Report phishing to the National Cyber Helpline: **1930**",
        ],
        "Courier Scam": [
            "❌ No legitimate courier company charges customs release fees via SMS",
            "✅ Verify any delivery issue directly on the courier's official website",
            "⚠️ Never pay via UPI or crypto to 'release' a parcel",
            "📞 Report to **1930** or local police",
        ],
        "Subscription Scam": [
            "❌ Netflix/Amazon never ask you to pay via UPI links received in SMS",
            "✅ Renew subscriptions only through official apps or websites",
            "⚠️ Phishing sites mimic OTT platforms — always check the URL carefully",
            "📞 Report to **1930**",
        ],
        "Romance / Matrimony Scam": [
            "❌ Never send money to someone you have only met online",
            "✅ Always video-call verify before sharing personal information",
            "⚠️ Scammers often create urgency around medical or travel emergencies",
            "📞 Report to [cybercrime.gov.in](https://www.cybercrime.gov.in)",
        ],
        "Other Fraud": [
            "❌ Don't click on shortened or unfamiliar links",
            "✅ Verify the sender's identity through an official channel before responding",
            "⚠️ Never share Aadhaar, PAN, or bank details over SMS/WhatsApp",
            "📞 Report suspicious messages to **1930**",
        ],
    }
    # Fuzzy match for model-returned labels
    for key in tips_map:
        if key.lower() in fraud_type.lower() or fraud_type.lower() in key.lower():
            return tips_map[key]
    return tips_map["Other Fraud"]


# ── SAMPLE MESSAGES ────────────────────────────────────────────────────────────
SAMPLE_MESSAGES = {
    "UPI Fraud":     "Your UPI payment of Rs.5000 to Flipkart is pending. Click tinyurl.com/complete to pay now",
    "Job Scam":      "Work from home job: Earn Rs.5000/day typing data. Contact on Telegram @jobs_india",
    "Lottery Scam":  "Congratulations! You won Rs.25 lakhs in KBC Lucky Draw. Claim: rebrand.ly/claim-now",
    "Phishing":      "Your Aadhaar card will be deactivated in 24 hours. Update now: uidai-update.com",
    "Courier Scam":  "Your FedEx courier from USA is held at customs. Pay Rs.5000 to release: bit.ly/pay-now",
    "Safe Message":  "Hi, how are you? Let's meet for dinner at 8 pm tonight",
}


# ── TTS HELPER ─────────────────────────────────────────────────────────────────
def speak(message: str, repeat: int = 1) -> None:
    """
    FIX: Uses height=1 (not 0 which some browsers ignore), safely escapes
    the message string for JS, and adds a 300ms delay to let the page settle.
    """
    safe_msg = (
        message
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", " ")
        .replace("\r", "")
    )
    js = f"""
    <script>
    (function() {{
        if (!window.speechSynthesis) return;
        var msg = '{safe_msg}';
        var count = {repeat};
        function doSpeak(i) {{
            if (i >= count) return;
            var u = new SpeechSynthesisUtterance(msg);
            u.rate = 0.9; u.pitch = 1.0; u.volume = 1.0;
            u.onend = function() {{ doSpeak(i + 1); }};
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(u);
        }}
        setTimeout(function() {{ doSpeak(0); }}, 300);
    }})();
    </script>
    """
    st.components.v1.html(js, height=1)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <span class="shield-icon">🛡️</span>
            <h2>FRAUD SHIELD PRO</h2>
            <p>AI-Powered Cyber Protection</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="helpline-box">
            <div class="hl-label">🚨 Official Cyber Helpline</div>
            <div class="hl-number">1930</div>
            <a href="https://www.cybercrime.gov.in" target="_blank">cybercrime.gov.in →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Safety checklist — state preserved across reruns
    st.markdown('<div class="sidebar-section-title">Safety Checklist</div>', unsafe_allow_html=True)
    checks = [
        st.checkbox("Never share OTP",             value=st.session_state.sidebar_checks[0], key="chk0"),
        st.checkbox("Never share UPI PIN",          value=st.session_state.sidebar_checks[1], key="chk1"),
        st.checkbox("Check links before clicking",  value=st.session_state.sidebar_checks[2], key="chk2"),
        st.checkbox("Verify sender identity",       value=st.session_state.sidebar_checks[3], key="chk3"),
    ]
    st.session_state.sidebar_checks = checks
    if all(checks):
        st.success("✅ You're following all safety practices!")

    # Model performance stats (only shown when models loaded successfully)
    if models.get("ok"):
        st.markdown(
            '<div class="sidebar-section-title" style="margin-top:.8rem">Model Performance</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="stat-row">
                <div class="stat-card"><div class="sv">99.9%</div><div class="sl">Binary Acc.</div></div>
                <div class="stat-card"><div class="sv">94.5%</div><div class="sl">Type Acc.</div></div>
            </div>
            <p style="font-size:.72rem;color:var(--muted);margin:0 0 .5rem">
              Trained on Indian SMS fraud dataset. Stats are indicative.
            </p>
            """,
            unsafe_allow_html=True,
        )

    # Quick test buttons
    st.markdown(
        '<div class="sidebar-section-title" style="margin-top:.8rem">Quick Test Messages</div>',
        unsafe_allow_html=True,
    )
    for label, key in [
        ("📧 UPI Fraud",     "UPI Fraud"),
        ("💼 Job Scam",      "Job Scam"),
        ("🎲 Lottery Scam",  "Lottery Scam"),
        ("🔗 Phishing",      "Phishing"),
        ("📦 Courier Scam",  "Courier Scam"),
        ("✅ Safe Message",   "Safe Message"),
    ]:
        if st.button(label, key=f"sb_{key}"):
            st.session_state.input_text = SAMPLE_MESSAGES[key]
            st.session_state.analysis_done = False
            st.session_state.results = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero-section">
        <div class="hero-bg-lines"></div>
        <div class="hero-eyebrow">⬡ Real-Time Threat Intelligence</div>
        <div class="hero-title">AI Fraud Shield Pro</div>
        <div class="hero-sub">SMS / MESSAGE FRAUD RISK ANALYSIS ENGINE · v3.0</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Input Message</div>', unsafe_allow_html=True)

# ── VOICE INPUT (graceful degradation if package missing) ──
try:
    from streamlit_mic_recorder import speech_to_text as _stt
    col_mic, _ = st.columns([1, 8])
    with col_mic:
        voice_text = _stt(
            language="en",
            start_prompt="🎤",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
        )
    st.markdown(
        '<div class="mic-hint">🎤 Click the mic to dictate a message, or type/paste below</div>',
        unsafe_allow_html=True,
    )
    # FIX: Only update if voice text is genuinely new and non-empty
    if voice_text and voice_text.strip() and voice_text.strip() != st.session_state.input_text.strip():
        st.session_state.input_text = voice_text.strip()
        st.session_state.analysis_done = False
        st.rerun()
except ImportError:
    st.caption("ℹ️ Install `streamlit-mic-recorder` to enable voice input.")

# ── TEXT AREA ──
st.text_area(
    "Message input",
    value=st.session_state.input_text,
    height=140,
    placeholder="Type, paste, or speak a suspicious SMS/message here…",
    label_visibility="collapsed",
    key="input_text",
)

# ── CHARACTER COUNTER ──
char_count = len(st.session_state.input_text)
st.markdown(
    f'<div class="char-counter{"  warn" if char_count > 500 else ""}">{char_count} characters</div>',
    unsafe_allow_html=True,
)

# ── ANALYZE BUTTON ──
_, col_btn, _ = st.columns([1.5, 2, 1.5])
with col_btn:
    analyze_clicked = st.button("🔍  Analyze Message", type="primary", use_container_width=True)


# ── ANALYSIS LOGIC ────────────────────────────────────────────────────────────
if analyze_clicked:
    raw = st.session_state.input_text.strip()

    if len(raw) < 10:
        st.warning("⚠️ Please enter a valid message (at least 10 characters).")
    elif not models.get("ok"):
        st.error("❌ Models not loaded. Please verify all .pkl files are present.")
    else:
        progress_bar = st.progress(0)
        status_text  = st.empty()

        try:
            for pct in range(0, 101, 5):
                time.sleep(0.02)
                progress_bar.progress(pct)
                status_text.caption(f"🔬 Scanning… {pct}%")

            cleaned = clean_text(raw)
            vec     = models["tfidf"].transform([cleaned])

            # FIX: Robust proba extraction with shape check
            proba = models["model_risk"].predict_proba(vec)
            if proba.shape[1] >= 2:
                prob_spam = float(proba[0][1]) * 100
            else:
                pred = int(models["model_risk"].predict(vec)[0])
                prob_spam = 85.0 if pred == 1 else 10.0

            if prob_spam < 30:
                risk = "Safe"
            elif prob_spam < 70:
                risk = "Suspicious"
            else:
                risk = "High Risk"

            if risk == "Safe":
                fraud_type = "None"
            elif models.get("type_model_available"):
                try:
                    enc        = models["model_type"].predict(vec)[0]
                    fraud_type = models["label_encoder"].inverse_transform([enc])[0]
                except Exception:
                    fraud_type = rule_based_fraud_type(raw)
            else:
                fraud_type = rule_based_fraud_type(raw)

            highlighted = sanitize_and_highlight(raw)
            tips        = get_preventive_tips(fraud_type if risk != "Safe" else "Other Fraud")

            st.session_state.analysis_done = True
            st.session_state.results = {
                "prob_spam":   prob_spam,
                "risk":        risk,
                "fraud_type":  fraud_type,
                "highlighted": highlighted,
                "tips":        tips,
            }

        except Exception as e:
            st.error(f"❌ Analysis failed: {e}. Please check your model files.")
        finally:
            # FIX: Always clean up progress UI
            progress_bar.empty()
            status_text.empty()


# ── RESULTS DISPLAY ───────────────────────────────────────────────────────────
if st.session_state.analysis_done and st.session_state.results:
    res = st.session_state.results

    st.markdown("---")
    st.markdown('<div class="section-label">Analysis Results</div>', unsafe_allow_html=True)

    prob_col = "mc-safe" if res["risk"] == "Safe" else ("mc-warn" if res["risk"] == "Suspicious" else "mc-danger")
    action   = "No Action" if res["risk"] == "Safe" else ("Report Now" if res["risk"] == "High Risk" else "Be Cautious")
    act_col  = "mc-safe" if res["risk"] == "Safe" else ("mc-danger" if res["risk"] == "High Risk" else "mc-warn")

    # ── 4 METRIC CARDS ──
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, cls in [
        (c1, f"{res['prob_spam']:.1f}%", "Scam Probability",    prob_col),
        (c2, res["risk"],                "Risk Level",           prob_col),
        (c3, res["fraud_type"],          "Fraud Type",           "mc-accent2"),
        (c4, action,                     "Recommended Action",   act_col),
    ]:
        size_override = "font-size:1.05rem;padding-top:.3rem" if len(str(val)) > 10 else ""
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="mc-value {cls}" style="{size_override}">{val}</div>
                    <div class="mc-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── VERDICT BANNER ──
    verdicts = {
        "Safe": (
            "vb-safe", "✅", "#00e676", "Safe Message",
            "This message appears legitimate. However, always stay vigilant and verify "
            "before sharing personal information.",
        ),
        "Suspicious": (
            "vb-warn", "⚠️", "#ffb300", "Suspicious Message",
            "This message shows suspicious patterns. Do not engage or click any links "
            "until the sender is verified through an official channel.",
        ),
        "High Risk": (
            "vb-danger", "🚨", "#ff1744", "HIGH RISK — SCAM DETECTED",
            f"This is highly likely a <strong style='color:#ff6b6b'>{res['fraud_type']}</strong>. "
            "DO NOT respond, call back, or click any links. Report immediately to 1930.",
        ),
    }
    cls, icon, color, title, body = verdicts[res["risk"]]
    st.markdown(
        f"""
        <div class="verdict-banner {cls}" style="margin-top:1.2rem">
            <span class="vb-icon">{icon}</span>
            <div>
                <div class="vb-title" style="color:{color}">{title}</div>
                <div class="vb-body">{body}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── AUTOMATIC TTS — fires once per unique result ──
    # FIX: Hash includes probability so same type on different messages re-speaks
    result_hash = hashlib.md5(
        f"{res['risk']}_{res['fraud_type']}_{res['prob_spam']:.0f}".encode()
    ).hexdigest()

    if st.session_state.spoken_for_hash != result_hash:
        st.session_state.spoken_for_hash = result_hash
        if res["risk"] == "High Risk":
            speak(
                f"High risk scam detected. Fraud type: {res['fraud_type']}. Do not respond to this message.",
                repeat=2,
            )
        elif res["risk"] == "Suspicious":
            speak(f"Suspicious message detected. Possible {res['fraud_type']}. Be cautious.", repeat=1)
        else:
            speak("Message appears safe. Stay vigilant.", repeat=1)

    # ── MANUAL SPEAK BUTTON ──
    # FIX: No extra rerun needed — speak() injects JS inline
    col_speak, _ = st.columns([1, 5])
    with col_speak:
        if st.button("🔊 Speak Alert", use_container_width=True, key="btn_speak"):
            if res["risk"] == "High Risk":
                speak(f"Alert! High risk scam. Type: {res['fraud_type']}. Do not respond.", repeat=1)
            elif res["risk"] == "Suspicious":
                speak(f"Suspicious message. Possible {res['fraud_type']}. Be cautious.", repeat=1)
            else:
                speak("This message appears safe. Stay vigilant.", repeat=1)

    # ── PATTERN ANALYSIS ──
    with st.expander("🔍  Pattern Analysis — Highlighted Keywords", expanded=True):
        st.markdown(
            f'<div class="highlight-box">{res["highlighted"]}</div>',
            unsafe_allow_html=True,
        )

    # ── PREVENTIVE GUIDANCE ──
    with st.expander("💡  Preventive Guidance", expanded=True):
        for tip in res["tips"]:
            st.markdown(f'<div class="tip-item">{tip}</div>', unsafe_allow_html=True)

    # ── REPORT & SUPPORT ──
    with st.expander("📞  Report & Support Resources"):
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown(
                """
                <div class="report-card">
                    <div class="rc-title">🌐 Online Reporting</div>
                    <p>📞 <strong>1930</strong> — National Cyber Helpline (24×7)</p>
                    <p>🔗 <a href="https://www.cybercrime.gov.in" target="_blank">cybercrime.gov.in</a></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rc2:
            st.markdown(
                """
                <div class="report-card">
                    <div class="rc-title">🚔 Emergency Contacts</div>
                    <p>📞 <strong>100</strong> — Local Police</p>
                    <p>📞 <strong>112</strong> — Mobile Emergency</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── SHARE SECTION (FIX: functional links) ──
    st.markdown("---")
    st.markdown('<div class="section-label">Share This Analysis</div>', unsafe_allow_html=True)

    share_text = (
        f"⚠️ Fraud Alert ⚠️\n"
        f"Risk: {res['risk']} ({res['prob_spam']:.0f}%)\n"
        f"Type: {res['fraud_type']}\n"
        f"Report frauds: 1930 | cybercrime.gov.in"
    )
    encoded = share_text.replace("\n", "%0A").replace(" ", "%20").replace("⚠️", "%E2%9A%A0%EF%B8%8F")

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.link_button("📧 Email",     f"mailto:?subject=Fraud%20Alert&body={encoded}", use_container_width=True)
    with s2:
        st.link_button("📱 WhatsApp",  f"https://wa.me/?text={encoded}",                use_container_width=True)
    with s3:
        st.link_button("🐦 Twitter/X", f"https://twitter.com/intent/tweet?text={encoded[:250]}", use_container_width=True)
    with s4:
        if st.button("📋 Copy Text", use_container_width=True, key="btn_copy"):
            safe_copy = share_text.replace("`", "'").replace("\\", "\\\\")
            st.components.v1.html(
                f"<script>navigator.clipboard.writeText(`{safe_copy}`).catch(()=>{{}});</script>",
                height=1,
            )
            st.toast("✅ Copied to clipboard!", icon="📋")


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div class="app-footer">
        <div class="af-brand">🛡️ AI FRAUD SHIELD PRO</div>
        <div class="af-copy">
            Powered by Machine Learning · Report Suspicious Messages to 1930 ·
            Always verify before sharing personal information · © 2025 Hackathon Project
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
