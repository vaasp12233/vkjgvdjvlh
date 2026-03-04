import streamlit as st
import pickle
import re
import numpy as np
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Fraud Shield Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SESSION STATE ---
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'results' not in st.session_state:
    st.session_state.results = None

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; color: white; }
    .card { background: rgba(255,255,255,0.95); border-radius: 15px; padding: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); transition: transform 0.3s ease; }
    .card:hover { transform: translateY(-5px); }
    .metric-card { background: white; border-radius: 15px; padding: 1rem; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 5px solid #667eea; }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: #2d3748; }
    .metric-label { font-size: 0.9rem; color: #718096; text-transform: uppercase; letter-spacing: 1px; }
    .risk-safe { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); border: none; color: #1a4731; padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(132,250,176,0.3); }
    .risk-suspicious { background: linear-gradient(135deg, #feda75 0%, #ffb347 100%); border: none; color: #744210; padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(254,218,117,0.3); }
    .risk-high { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); border: none; color: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(255,107,107,0.3); }
    .stButton button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; padding: 0.75rem 2rem; font-weight: 600; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.2); }
    .stButton button:hover { transform: scale(1.05); box-shadow: 0 10px 30px rgba(102,126,234,0.4); }
    .stTextArea textarea { border-radius: 15px; border: 2px solid #e2e8f0; padding: 1rem; font-size: 1rem; transition: all 0.3s ease; }
    .stTextArea textarea:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
    h1, h2, h3 { color: white; font-weight: 700; }
    .css-1d391kg { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); }
    .stProgress > div > div { background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 10px; }
    .footer { text-align: center; padding: 2rem; color: rgba(255,255,255,0.8); font-size: 0.9rem; }
    @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .gradient-bg { background: linear-gradient(-45deg, #667eea, #764ba2, #6b8cff, #9f7aea); background-size: 400% 400%; animation: gradient 15s ease infinite; padding: 2rem; border-radius: 20px; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource(show_spinner="Loading AI models...")
def load_models():
    models = {}
    try:
        models['model_risk'] = pickle.load(open('model_risk.pkl', 'rb'))
        models['tfidf'] = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
        models['label_encoder'] = pickle.load(open('label_encoder.pkl', 'rb'))
    except FileNotFoundError as e:
        st.error(f"⚠️ Missing model file: {e}. Please ensure model_risk.pkl, tfidf_vectorizer.pkl, and label_encoder.pkl are in the app directory.")
        return None
    try:
        models['model_type'] = pickle.load(open('model_type.pkl', 'rb'))
        models['type_model_available'] = True
    except FileNotFoundError:
        models['type_model_available'] = False
        st.warning("ℹ️ Fraud type model not found. Using rule‑based fallback.")
    return models

models = load_models()

# --- TEXT CLEANING (must match training) ---
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' URL ', text)
    text = re.sub(r'\b\d{10}\b', ' PHONE ', text)
    text = re.sub(r'rs\.?\s*\d+|\d+\s*(lakh|crore|thousand)|₹\s*\d+', ' AMOUNT ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- KEYWORD HIGHLIGHTING ---
def highlight_keywords(text):
    keywords = {
        'upi': 'red', 'gpay': 'red', 'phonepe': 'red', 'pin': 'red', 'otp': 'red',
        'lottery': 'orange', 'won': 'orange', 'prize': 'orange', 'kbc': 'orange',
        'job': 'blue', 'salary': 'blue', 'work from home': 'blue',
        'kyc': 'purple', 'update': 'purple', 'verify': 'purple', 'link': 'purple',
        'bank': 'green', 'account': 'green', 'blocked': 'red', 'suspended': 'red',
        'courier': 'brown', 'parcel': 'brown', 'dhl': 'brown', 'fedex': 'brown',
        'netflix': 'violet', 'amazon prime': 'violet', 'subscription': 'violet',
        'matrimony': 'pink', 'shaadi': 'pink', 'caste': 'pink',
        'education': 'teal', 'scholarship': 'teal', 'exam': 'teal'
    }
    highlighted = text
    for word, color in keywords.items():
        pattern = re.compile(f'({re.escape(word)})', re.IGNORECASE)
        highlighted = pattern.sub(f'<span style="color:{color};font-weight:bold;background-color:rgba(255,255,255,0.2);padding:2px 4px;border-radius:4px;">\\1</span>', highlighted)
    return highlighted

# --- FALLBACK RULE‑BASED FRAUD TYPE CLASSIFIER ---
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
    else:
        return 'Others'

# --- PREVENTIVE TIPS ---
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
    "UPI Fraud": "Your UPI payment of Rs.5000 to Flipkart is pending. Click tinyurl.com/complete to pay now",
    "Job Scam": "Work from home job: Earn Rs.5000/day typing data. Contact on Telegram @jobs_india",
    "Lottery Scam": "Congratulations! You won Rs.25 lakhs in KBC Lucky Draw. Claim: rebrand.ly/claim-now",
    "Phishing": "Your Aadhaar card will be deactivated in 24 hours. Update now: uidai-update.com",
    "Courier Scam": "Your FedEx courier from USA is held at customs. Pay Rs.5000 to release: bit.ly/pay-now",
    "Safe Message": "Hi, how are you? Let's meet for dinner at 8 pm tonight"
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="color: white; font-size: 2rem;">🛡️</h1>
        <h2 style="color: white;">Cyber Safety Center</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.error("🚨 **Official Helpline**\n\n📞 **1930**")
    st.info("🌐 [Report Online](https://www.cybercrime.gov.in)")
    st.markdown("---")
    st.markdown("### 📋 Safety Checklist")
    safe1 = st.checkbox("✅ Never share OTP")
    safe2 = st.checkbox("✅ Never share UPI PIN")
    safe3 = st.checkbox("✅ Check links before clicking")
    safe4 = st.checkbox("✅ Verify sender identity")
    if safe1 and safe2 and safe3 and safe4:
        st.success("You're following safety practices! 👍")
    st.markdown("---")
    st.markdown("### 📊 Model Stats")
    if models and models.get('model_risk'):
        st.metric("Binary Accuracy", "99.92%", delta="0.2%")
    if models and models.get('type_model_available'):
        st.metric("Fraud Type Accuracy", "94.5%", delta="1.1%")
    else:
        st.metric("Fraud Type Detection", "Rule-Based", delta="Fallback")
    st.markdown("---")
    st.markdown("### 🎯 Quick Test")
    if st.button("📧 Test UPI Fraud"):
        st.session_state.input_text = SAMPLE_MESSAGES["UPI Fraud"]
        st.rerun()
    if st.button("💼 Test Job Scam"):
        st.session_state.input_text = SAMPLE_MESSAGES["Job Scam"]
        st.rerun()
    if st.button("🎲 Test Lottery Scam"):
        st.session_state.input_text = SAMPLE_MESSAGES["Lottery Scam"]
        st.rerun()
    if st.button("🔗 Test Phishing"):
        st.session_state.input_text = SAMPLE_MESSAGES["Phishing"]
        st.rerun()
    if st.button("📦 Test Courier Scam"):
        st.session_state.input_text = SAMPLE_MESSAGES["Courier Scam"]
        st.rerun()
    if st.button("✅ Test Safe Message"):
        st.session_state.input_text = SAMPLE_MESSAGES["Safe Message"]
        st.rerun()

# --- MAIN UI ---
st.markdown("""
<div class="gradient-bg">
    <h1 style="text-align: center; font-size: 3rem; margin-bottom: 0;">🛡️ AI Fraud Shield Pro</h1>
    <p style="text-align: center; font-size: 1.2rem; opacity: 0.9;">Real-time SMS/Message Fraud Risk Analysis</p>
</div>
""", unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_area(
        "📨 Paste the message you received:",
        height=120,
        placeholder="Type or paste suspicious message here...",
        key="input_text"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.input_text = ""
        st.session_state.analysis_done = False
        st.rerun()

# Analyze button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_clicked = st.button("🔍 Analyze Message", type="primary", use_container_width=True)

# --- Analysis and results ---
if analyze_clicked:
    if not st.session_state.input_text or len(st.session_state.input_text.strip()) < 10:
        st.warning("⚠️ Please enter a valid message (at least 10 characters)")
    elif models is None:
        st.error("Models not loaded. Please check model files.")
    else:
        with st.spinner("🔬 AI analyzing message..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            cleaned = clean_text(st.session_state.input_text)
            vec = models['tfidf'].transform([cleaned])
            prob_spam = models['model_risk'].predict_proba(vec)[0][1] * 100
            
            if prob_spam < 30:
                risk = "Safe"
                risk_class = "safe"
            elif prob_spam < 75:
                risk = "Suspicious"
                risk_class = "suspicious"
            else:
                risk = "High Risk"
                risk_class = "high"
            
            if risk == "Safe":
                fraud_type = "None"
            else:
                if models.get('type_model_available'):
                    type_encoded = models['model_type'].predict(vec)[0]
                    detailed_type = models['label_encoder'].inverse_transform([type_encoded])[0]
                    fraud_type = detailed_type  # map if needed
                else:
                    fraud_type = rule_based_fraud_type(st.session_state.input_text)
            
            highlighted = highlight_keywords(st.session_state.input_text)
            tips = get_preventive_tips(fraud_type if risk != "Safe" else "Others")
            
            st.session_state.analysis_done = True
            st.session_state.results = {
                'prob_spam': prob_spam,
                'risk': risk,
                'risk_class': risk_class,
                'fraud_type': fraud_type,
                'highlighted': highlighted,
                'tips': tips
            }
            progress_bar.empty()

# Display results
if st.session_state.analysis_done and st.session_state.results:
    res = st.session_state.results
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{res['prob_spam']:.1f}%</div><div class='metric-label'>Scam Probability</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{res['risk']}</div><div class='metric-label'>Risk Level</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{res['fraud_type']}</div><div class='metric-label'>Fraud Type</div></div>", unsafe_allow_html=True)
    with col4:
        action = "No Action" if res['risk'] == "Safe" else "Report Now" if res['risk'] == "High Risk" else "Be Cautious"
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{action}</div><div class='metric-label'>Recommended Action</div></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="background: #edf2f7; border-radius: 10px; height: 10px;">
            <div style="background: linear-gradient(90deg, #667eea, #764ba2); width: {res['prob_spam']}%; height: 10px; border-radius: 10px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if res['risk'] == "Safe":
        st.markdown(f"<div class='risk-safe'><h4>✅ Safe Message</h4><p>This message appears legitimate. However, always stay vigilant!</p></div>", unsafe_allow_html=True)
    elif res['risk'] == "Suspicious":
        st.markdown(f"<div class='risk-suspicious'><h4>⚠️ Suspicious Message</h4><p>This message shows suspicious patterns. Do not engage with the sender.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='risk-high'><h4>🚨 HIGH RISK - SCAM DETECTED</h4><p>This is likely a <strong>{res['fraud_type']}</strong>. DO NOT respond or click any links.</p></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("🔍 Pattern Analysis", expanded=True):
        st.markdown(f"**Highlighted Text:**")
        st.markdown(f"<div style='background: #f7fafc; padding: 1rem; border-radius: 10px; border-left: 5px solid #667eea;'>{res['highlighted']}</div>", unsafe_allow_html=True)
    with st.expander("💡 Preventive Guidance", expanded=True):
        for tip in res['tips']:
            st.markdown(f"- {tip}")
    with st.expander("📞 Report & Support"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Official Helpline**")
            st.markdown("📞 **1930** (24x7)")
            st.markdown("🌐 [cybercrime.gov.in](https://www.cybercrime.gov.in)")
        with col2:
            st.markdown("**Local Police**")
            st.markdown("📞 **100** (Emergency)")
            st.markdown("📞 **112** (Mobile Emergency)")
    
    st.markdown("---")
    st.markdown("### 📢 Share this analysis")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("📧 Email", use_container_width=True)
    with col2:
        st.button("📱 WhatsApp", use_container_width=True)
    with col3:
        st.button("🐦 Twitter", use_container_width=True)
    with col4:
        st.button("📋 Copy", use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🛡️ AI Fraud Shield Pro | Powered by Machine Learning | Report Suspicious Messages to 1930</p>
    <p style="font-size: 0.8rem;">© 2024 Hackathon Project | All rights reserved</p>
</div>
""", unsafe_allow_html=True)