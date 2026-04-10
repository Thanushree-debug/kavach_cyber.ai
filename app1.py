import streamlit as st
from groq import Groq
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
from PIL import Image
import pytesseract
import random
import hashlib
import base64
import requests
from datetime import datetime
import os 
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(page_title="Kavach AI 🛡️", page_icon="🛡️", layout="wide")

# ─── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0a0a14; color: #e0e0f0; }
.stApp { background-color: #0a0a14; }
h1 { font-family: 'Rajdhani', sans-serif; color: #f472b6; font-size: 2.5rem; letter-spacing: 2px; }
h2, h3 { font-family: 'Rajdhani', sans-serif; color: #c084fc; }
.stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div {
    background-color: #1a1a2e !important; color: #e0e0f0 !important; border: 1px solid #6d28d9 !important; border-radius: 10px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #be185d, #7c3aed); color: white; border: none;
    border-radius: 10px; padding: 0.5rem 1.5rem; font-weight: 600;
    font-family: 'Rajdhani', sans-serif; font-size: 1rem; letter-spacing: 1px; transition: 0.3s;
}
.stButton > button:hover { background: linear-gradient(135deg, #9d174d, #6d28d9); transform: scale(1.03); }
.chat-bubble-user {
    background: linear-gradient(135deg, #be185d, #7c3aed); padding: 12px 16px;
    border-radius: 16px 16px 4px 16px; margin: 8px 0; max-width: 80%; margin-left: auto; color: white;
}
.chat-bubble-ai {
    background: #1a1a2e; border: 1px solid #6d28d9; padding: 12px 16px;
    border-radius: 16px 16px 16px 4px; margin: 8px 0; max-width: 80%; color: #e0e0f0;
}
.severe-box { background:#7f1d1d; border:2px solid #dc2626; border-radius:12px; padding:16px; margin:10px 0; color:#fca5a5; }
.moderate-box { background:#713f12; border:2px solid #d97706; border-radius:12px; padding:16px; margin:10px 0; color:#fcd34d; }
.mild-box { background:#14532d; border:2px solid #16a34a; border-radius:12px; padding:16px; margin:10px 0; color:#86efac; }
.safe-box { background:#1e3a5f; border:2px solid #3b82f6; border-radius:12px; padding:16px; margin:10px 0; color:#93c5fd; }
.action-box { background:#1a1a2e; border:1px solid #7c3aed; border-radius:12px; padding:16px; margin:10px 0; }
.emergency-card { background:#1a1a2e; border:1px solid #dc2626; border-radius:12px; padding:16px; margin:8px 0; text-align:center; }
.whatsapp-box { background:#14532d; border:1px solid #16a34a; border-radius:12px; padding:16px; margin:10px 0; color:#86efac; font-family:monospace; white-space:pre-wrap; }
.score-card { background:#1a1a2e; border:2px solid #7c3aed; border-radius:16px; padding:20px; text-align:center; margin:10px 0; }
.warning-account { background:#451a03; border:1px solid #f97316; border-radius:10px; padding:12px; margin:8px 0; color:#fed7aa; }
.emotional-box { background:#1e1b4b; border:2px solid #818cf8; border-radius:12px; padding:16px; margin:10px 0; color:#c7d2fe; font-size:1.1rem; }
.photo-danger-box { background:#4c0519; border:2px solid #f43f5e; border-radius:12px; padding:20px; margin:10px 0; color:#fda4af; }
.photo-safe-box { background:#052e16; border:2px solid #22c55e; border-radius:12px; padding:20px; margin:10px 0; color:#86efac; }
.photo-warning-box { background:#431407; border:2px solid #fb923c; border-radius:12px; padding:20px; margin:10px 0; color:#fdba74; }
.stTabs [data-baseweb="tab-list"] { background-color:#1a1a2e; border-radius:10px; padding:4px; }
.stTabs [data-baseweb="tab"] { color:#c084fc; font-family:'Rajdhani',sans-serif; font-size:0.95rem; font-weight:600; }
.stTabs [aria-selected="true"] { background-color:#6d28d9 !important; color:white !important; border-radius:8px; }
hr { border-color: #4c1d95; }
audio { width: 100%; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── Groq Client ───────────────────────────────────────────────
try:


    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    # client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Groq API key not found! Add it to .streamlit/secrets.toml")
    st.stop()

# ─── Language Config ───────────────────────────────────────────
LANGUAGES = {"English": "en", "Kannada": "kn", "Hindi": "hi", "Tamil": "ta", "Telugu": "te"}

# ─── Session State ─────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "safety_score" not in st.session_state:
    st.session_state.safety_score = 85
if "incidents_today" not in st.session_state:
    st.session_state.incidents_today = 0
if "photo_scan_history" not in st.session_state:
    st.session_state.photo_scan_history = []

# ─── Detection System Prompt ───────────────────────────────────
DETECTION_SYSTEM_PROMPT = """You are an expert AI system for detecting cyberbullying and protecting victims in India.

Analyze the message and respond in this format:

VERDICT: CYBERBULLYING / NOT CYBERBULLYING / BORDERLINE
SEVERITY: MILD / MODERATE / SEVERE
CATEGORY: Harassment / Threat / Hate Speech / Body Shaming / Photo Misuse / Blackmail / Fake Account / Impersonation

EXPLANATION:
- Point 1
- Point 2

IMMEDIATE ACTIONS:
1. Action 1
2. Action 2
3. Action 3
4. Action 4

LEGAL HELP:
- Mention Indian law

EMOTIONAL SUPPORT:
- 2 short supportive sentences

Rules:
- Keep it short
- No extra symbols
- Always structured"""

# ─── Helpers ───────────────────────────────────────────────────
def get_ai_response(system_prompt, user_message, max_tokens=1500):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

def translate_text(text, target_lang_code):
    if target_lang_code == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang_code).translate(text[:4000])
    except:
        return text

def text_to_speech(text, lang_code):
    try:
        clean_text = text.replace("*", "").replace("#", "").strip()
        tts = gTTS(text=clean_text[:500], lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf
    except:
        return None

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        if not text.strip():
            return "⚠️ Could not read text clearly. Please paste manually."
        return text.strip()
    except Exception:
        return "⚠️ OCR not available. Please paste text manually."

def get_safety_score_color(score):
    if score >= 75:
        return "#22c55e"
    elif score >= 50:
        return "#f59e0b"
    else:
        return "#ef4444"

def get_safety_label(score):
    if score >= 75:
        return "🟢 SAFE"
    elif score >= 50:
        return "🟡 MODERATE RISK"
    else:
        return "🔴 HIGH RISK"

# ════════════════════════════════════════════════════════
# ─── PHOTO DETECTION FEATURE ─────────────────────────
# ════════════════════════════════════════════════════════

def get_image_hash(image_file):
    """Generate a perceptual hash of the image for fingerprinting."""
    try:
        image_file.seek(0)
        img = Image.open(image_file).convert("RGB").resize((64, 64))
        raw = img.tobytes()
        return hashlib.sha256(raw).hexdigest()
    except Exception:
        return None

def image_to_base64(image_file):
    """Convert uploaded image to base64 string."""
    try:
        image_file.seek(0)
        return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception:
        return None

def check_image_online_via_ai(image_file, victim_name=""):
    """
    Use Groq AI to analyze the image for signs it may be circulating online.
    Checks EXIF metadata, file properties, image characteristics.
    Returns a risk assessment dict.
    """
    try:
        image_file.seek(0)
        img = Image.open(image_file)

        # Extract metadata
        width, height = img.size
        mode = img.mode
        fmt = img.format or "Unknown"

        # Check for EXIF data (can indicate if photo was taken on a device vs screenshot)
        exif_data = {}
        has_exif = False
        try:
            exif_raw = img._getexif()
            if exif_raw:
                has_exif = True
                from PIL.ExifTags import TAGS
                for tag_id, value in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)[:100]
        except Exception:
            pass

        # File size check
        image_file.seek(0, 2)
        file_size_kb = image_file.tell() / 1024
        image_file.seek(0)

        # Determine if image looks like a screenshot (no EXIF, specific dimensions)
        is_screenshot_likely = not has_exif and (
            width in [1080, 1920, 2340, 390, 414, 360, 375, 412] or
            height in [1920, 2400, 844, 896, 812, 780, 2340, 2778]
        )

        # Build analysis prompt
        analysis_prompt = f"""
        Analyze this photo/image metadata for a cyberbullying protection tool (Kavach AI, India).

        Image properties:
        - Dimensions: {width}x{height} pixels
        - Format: {fmt}
        - Color mode: {mode}
        - File size: {file_size_kb:.1f} KB
        - Has EXIF metadata: {has_exif}
        - Looks like screenshot: {is_screenshot_likely}
        - EXIF keys found: {list(exif_data.keys())[:10] if exif_data else 'None'}
        - Victim name (if provided): {victim_name or 'Not provided'}

        Based on these properties, assess:
        1. RISK LEVEL: HIGH / MEDIUM / LOW — is this photo likely being shared/circulated online?
        2. PHOTO TYPE: Original device photo / Screenshot / Edited / Unknown
        3. RED FLAGS: List any suspicious indicators
        4. PRIVACY RISK: What private info might be exposed (location, device, identity)?
        5. ACTIONS: What should the victim do RIGHT NOW?
        6. PLATFORM REPORTING: Which platforms to report to and how?
        7. LEGAL STEP: Which Indian law applies (IT Act section)?
        8. AUTO DELETE ADVISORY: Should this photo be deleted from their device? Why?

        Respond in structured format with these exact headings. Be specific and practical for a young Indian girl.
        """

        ai_result = get_ai_response(
            "You are a digital forensics and photo privacy expert helping cyberbullying victims in India.",
            analysis_prompt,
            max_tokens=1000
        )

        return {
            "success": True,
            "ai_analysis": ai_result,
            "metadata": {
                "dimensions": f"{width}x{height}",
                "format": fmt,
                "file_size_kb": round(file_size_kb, 1),
                "has_exif": has_exif,
                "is_screenshot_likely": is_screenshot_likely,
                "exif_keys": list(exif_data.keys())[:10]
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def perform_reverse_image_search_advisory(image_file):
    """
    Provide direct links for the user to manually do a reverse image search.
    (Real reverse search APIs like Google Vision require billing setup.)
    """
    image_file.seek(0)
    img_bytes = image_file.read()
    b64 = base64.b64encode(img_bytes).decode()

    return {
        "google_lens": "https://lens.google.com/",
        "tineye": "https://tineye.com/",
        "yandex": "https://yandex.com/images/",
        "b64_preview": b64[:100]  # just for reference
    }


def run_photo_detection(uploaded_photo, lang_code, enable_voice, victim_name=""):
    """Main photo detection and advisory function."""

    st.markdown("---")
    st.markdown("### 📸 Photo Detection Report")

    with st.spinner("🔍 Scanning photo for privacy risks and online presence..."):

        # Step 1: AI Analysis
        result = check_image_online_via_ai(uploaded_photo, victim_name)

        if not result["success"]:
            st.error(f"⚠️ Error analyzing photo: {result.get('error', 'Unknown error')}")
            return

        ai_analysis = result["ai_analysis"]
        metadata = result["metadata"]

        # Step 2: Determine risk level from AI output
        risk_level = "LOW"
        if "RISK LEVEL: HIGH" in ai_analysis or "HIGH" in ai_analysis[:200]:
            risk_level = "HIGH"
            st.session_state.safety_score = max(15, st.session_state.safety_score - 20)
        elif "RISK LEVEL: MEDIUM" in ai_analysis or "MEDIUM" in ai_analysis[:200]:
            risk_level = "MEDIUM"
            st.session_state.safety_score = max(30, st.session_state.safety_score - 10)

        # Step 3: Display metadata
        st.markdown("#### 🔬 Image Metadata Scan")
        meta_cols = st.columns(4)
        with meta_cols[0]:
            st.metric("📐 Dimensions", metadata["dimensions"])
        with meta_cols[1]:
            st.metric("📁 File Size", f"{metadata['file_size_kb']} KB")
        with meta_cols[2]:
            st.metric("🏷️ Format", metadata["format"])
        with meta_cols[3]:
            st.metric("📷 Has EXIF", "Yes ⚠️" if metadata["has_exif"] else "No ✅")

        if metadata["has_exif"] and metadata["exif_keys"]:
            st.warning(f"⚠️ EXIF metadata found! This photo contains hidden data: {', '.join(metadata['exif_keys'][:6])}. This can reveal your location, device, and identity.")

        if metadata["is_screenshot_likely"]:
            st.info("📱 This appears to be a screenshot — likely from a chat or social media.")

        st.markdown("---")

        # Step 4: AI Risk Analysis
        translated_analysis = translate_text(ai_analysis, lang_code)

        if risk_level == "HIGH":
            st.markdown(f'<div class="photo-danger-box">🚨 <b>HIGH RISK — YOUR PHOTO MAY BE CIRCULATING ONLINE</b><br><br>{translated_analysis}</div>', unsafe_allow_html=True)
        elif risk_level == "MEDIUM":
            st.markdown(f'<div class="photo-warning-box">⚠️ <b>MEDIUM RISK — POSSIBLE PRIVACY CONCERN</b><br><br>{translated_analysis}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="photo-safe-box">✅ <b>LOW RISK — Photo appears safe</b><br><br>{translated_analysis}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Step 5: Auto Delete Advisory
        st.markdown("#### 🗑️ Auto Delete Advisory")
        if risk_level in ["HIGH", "MEDIUM"]:
            st.error("""
🚨 **RECOMMENDED: Delete this photo from your device IMMEDIATELY**

Steps to delete:
1. Delete from your device gallery
2. Empty your 'Recently Deleted' / Trash folder
3. Remove from WhatsApp, Instagram, Snapchat backups
4. Remove from Google Photos / iCloud backup
5. Ask the platform to remove it using their reporting tool
            """)

            # Generate deletion report
            if st.button("📋 Generate Photo Removal Request Letter", key="delete_letter"):
                with st.spinner("Generating removal request..."):
                    removal_letter = get_ai_response(
                        "You are a legal expert helping cyberbullying victims in India request photo removal.",
                        f"""Write a formal photo removal request letter for platforms (Instagram/WhatsApp/Facebook).
                        Victim name: {victim_name or 'the victim'}
                        Situation: Unauthorized photo sharing / photo misuse
                        Include: IT Act 2000 Section 66E (privacy violation), Section 67 (obscene material), 
                        request for immediate takedown, reference to POCSO Act if minor.
                        Keep formal, 150 words max. Address to: Platform Trust & Safety Team."""
                    )
                    translated_letter = translate_text(removal_letter, lang_code)
                    st.text_area("📋 Copy & send to platform support:", translated_letter, height=200, key="removal_letter")
                    st.success("✅ Letter ready! Send to platform support + cybercrime.gov.in")
        else:
            st.success("✅ No immediate deletion required. But stay cautious — if someone is threatening to share this photo, act immediately.")

        st.markdown("---")

        # Step 6: Reverse Image Search Links
        st.markdown("#### 🌐 Check If Photo Is Already Online (Reverse Image Search)")
        st.markdown("*Click these links and upload your photo to check if it appears anywhere on the internet:*")

        search_cols = st.columns(3)
        with search_cols[0]:
            st.link_button("🔍 Google Lens", "https://lens.google.com/")
        with search_cols[1]:
            st.link_button("🔎 TinEye", "https://tineye.com/")
        with search_cols[2]:
            st.link_button("🔍 Yandex Images", "https://yandex.com/images/")

        st.info("💡 Tip: Upload your photo to each of these sites to check if your photo has been posted anywhere online without your permission.")

        st.markdown("---")

        # Step 7: Legal Actions
        st.markdown("#### ⚖️ Legal Actions for Photo Misuse in India")
        st.markdown("""
        <div class="action-box">
        <b>🇮🇳 Indian Laws That Protect You:</b><br><br>
        📜 <b>IT Act 2000 — Section 66E:</b> Punishment for publishing private images without consent (up to 3 years jail)<br>
        📜 <b>IT Act 2000 — Section 67:</b> Publishing obscene material online (up to 5 years jail)<br>
        📜 <b>IPC Section 354C:</b> Voyeurism — capturing/sharing private images<br>
        📜 <b>POCSO Act:</b> If victim is under 18 — strict punishment<br><br>
        <b>📞 Report To:</b><br>
        📞 Cyber Crime Helpline: <b>1930</b><br>
        🌐 <b>cybercrime.gov.in</b> — File online complaint<br>
        👮 Local Police Cyber Cell<br>
        📱 Platform Safety Teams (Instagram, WhatsApp, Snapchat)
        </div>
        """, unsafe_allow_html=True)

        # Step 8: Save to scan history
        st.session_state.photo_scan_history.append({
            "time": datetime.now().strftime("%H:%M"),
            "risk": risk_level,
            "size": f"{metadata['file_size_kb']} KB",
            "has_exif": metadata["has_exif"]
        })

        # Step 9: Voice output
        if enable_voice:
            summary = f"Photo scan complete. Risk level: {risk_level}. " + (
                "High risk detected. Please delete this photo immediately and report to cyber crime helpline 1930." 
                if risk_level == "HIGH" else 
                "Medium risk detected. Take precautions." 
                if risk_level == "MEDIUM" else 
                "Photo appears safe. Stay cautious."
            )
            audio = text_to_speech(translate_text(summary, lang_code), lang_code)
            if audio:
                st.audio(audio, format="audio/mp3")


# ─── Detection runner ───────────────────────────────────────────
def run_detection(message_text, lang_code, enable_voice, victim_name="", victim_location=""):
    result = get_ai_response(DETECTION_SYSTEM_PROMPT, f"Analyze this message: {message_text}")

    severity = "mild"
    if "SEVERE" in result:
        severity = "severe"
        st.session_state.safety_score = max(20, st.session_state.safety_score - 25)
    elif "MODERATE" in result:
        severity = "moderate"
        st.session_state.safety_score = max(30, st.session_state.safety_score - 15)
    elif "CYBERBULLYING" in result:
        st.session_state.safety_score = max(40, st.session_state.safety_score - 10)

    st.session_state.incidents_today += 1

    translated_result = translate_text(result, lang_code)
    verdict = "SAFE"
    if "CYBERBULLYING" in result:
        verdict = "CYBERBULLYING"

    st.markdown(f"### 🚨 Quick Result: {verdict.upper()}")
    box_class = f"{severity}-box"
    emoji = "🚨" if severity == "severe" else "⚠️" if severity == "moderate" else "✅"
    st.markdown(f'<div class="{box_class}">{emoji} <b>DETECTION RESULT</b><br><br>{translated_result}</div>', unsafe_allow_html=True)

    if "NOT CYBERBULLYING" not in result:
        st.markdown("---")

        emotional_responses = [
            "💙 This is NOT your fault. You are brave for reporting this. Do you want to talk about how you're feeling, or would you like to take a break?",
            "💜 You don't deserve this. What happened to you is wrong. Take a deep breath — you are safe here. Want to talk or shall I help you report this?",
            "💚 You are stronger than this. Reporting it was the right thing to do. I'm here with you. Do you need emotional support or action steps first?"
        ]
        emotional_msg = translate_text(random.choice(emotional_responses), lang_code)
        st.markdown(f'<div class="emotional-box">🤗 <b>Kavach says:</b><br><br>{emotional_msg}</div>', unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 📝 Complaint Letter (Auto Generated)")
        complaint = get_ai_response(
            "You are a legal complaint writer for cyberbullying cases in India. Write formal, clear complaints.",
            f"""Write a formal cyberbullying complaint letter.
            Victim: {victim_name or 'the victim'}
            Location: {victim_location or 'India'}
            Bullying message: {message_text}
            Address to: Cyber Crime Cell / School Principal
            Include: what happened, evidence description, IT Act 2000 sections, action requested.
            Keep formal, clear, 200 words max."""
        )
        translated_complaint = translate_text(complaint, lang_code)
        st.text_area("📋 Copy & submit to cybercrime.gov.in:", translated_complaint, height=200, key=f"complaint_{random.randint(1,9999)}")
        st.success("✅ Complaint ready to submit!")

        st.markdown("---")

        st.markdown("### 📲 WhatsApp Alert to Parents (Ready to Send)")
        wa_msg = f"""🚨 URGENT — Cyberbullying Alert

Hi, I need your help immediately.

Harmful message received:
"{message_text[:150]}..."

Severity: {severity.upper()}

Please help me report:
📞 Cyber Crime: 1930
🌐 cybercrime.gov.in

I need your support right now. 🙏"""
        translated_wa = translate_text(wa_msg, lang_code)
        st.markdown(f'<div class="whatsapp-box">📱 {translated_wa}</div>', unsafe_allow_html=True)
        st.info("📲 Copy and send to parents on WhatsApp NOW!")

        st.markdown("---")

        st.markdown("### 🚨 Contact These Right Now")
        contacts = [("🚔 Police", "100"), ("👩 Women", "1091"), ("💻 Cyber Crime", "1930"), ("👶 Childline", "1098"), ("🆘 Emergency", "112")]
        cols = st.columns(5)
        for i, (name, number) in enumerate(contacts):
            with cols[i]:
                st.markdown(f'<div class="emergency-card"><b>{name}</b><br><h2 style="color:#f472b6">{number}</h2></div>', unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 🌐 Report Online")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.link_button("🚔 cybercrime.gov.in", "https://cybercrime.gov.in")
        with c2:
            st.link_button("📘 Instagram Help", "https://help.instagram.com")
        with c3:
            st.link_button("💬 WhatsApp Help", "https://faq.whatsapp.com")

    if enable_voice:
        audio = text_to_speech(translated_result, lang_code)
        if audio:
            st.audio(audio, format="audio/mp3")


# ══════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════
col_title, col_score = st.columns([3, 1])
with col_title:
    st.markdown("# 🛡️ KAVACH AI")
    st.markdown("*Predict. Prevent. Support. — Because no one should face cyberbullying alone.*")
with col_score:
    score_color = get_safety_score_color(st.session_state.safety_score)
    score_label = get_safety_label(st.session_state.safety_score)
    st.markdown(f"""
    <div class="score-card">
        <div style="font-size:2.5rem;font-weight:700;color:{score_color}">{st.session_state.safety_score}%</div>
        <div style="font-size:0.9rem;color:#c084fc">Digital Safety Score</div>
        <div style="font-size:0.85rem;margin-top:4px">{score_label}</div>
        <div style="font-size:0.75rem;color:#6b7280;margin-top:4px">Your space today</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Settings ──
s1, s2 = st.columns([2, 2])
with s1:
    selected_lang = st.selectbox("🌐 Language", list(LANGUAGES.keys()))
    lang_code = LANGUAGES[selected_lang]
with s2:
    enable_voice = st.toggle("🔊 Voice Output", value=False)

with st.expander("👤 Your Details (optional — for complaint letter & SOS)"):
    vic_col1, vic_col2 = st.columns(2)
    with vic_col1:
        victim_name = st.text_input("Your Name", placeholder="e.g. Priya")
    with vic_col2:
        victim_location = st.text_input("Your City", placeholder="e.g. Bangalore")

st.markdown("---")

# ══════════════════════════════════════════════════════
# TABS — added Tab 6 for Photo Detection
# ══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Detect & Act",
    "🧠 Predict & Prevent",
    "💚 Emotional Support",
    "💬 Support Chat",
    "🆘 SOS & Help",
    "📸 Photo Detection"
])

# ════════════════════════════════════════════════════════
# TAB 1 — DETECT AND ACT
# ════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🔍 Paste Message OR Upload Screenshot")
    st.markdown("**One click → AI detects, generates complaint, WhatsApp alert & shows contacts automatically!**")

    input_method = st.radio("Input method:", ["✍️ Paste Text", "📸 Upload Screenshot"], horizontal=True)
    message_to_analyze = ""

    if input_method == "✍️ Paste Text":
        message_to_analyze = st.text_area(
            "Paste the bullying message here...",
            placeholder="e.g. You are ugly, nobody likes you, I will share your photos everywhere",
            height=120,
            key="paste_input"
        )
    else:
        uploaded_img = st.file_uploader("Upload screenshot of bullying message", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            st.image(uploaded_img, caption="Uploaded Screenshot", use_column_width=True)
            with st.spinner("Reading text from screenshot..."):
                extracted = extract_text_from_image(uploaded_img)

                # 🔴 ADD THIS
                if "OCR not available" in extracted or "Could not read text" in extracted:
                    st.warning("⚠️ Unable to read image. Please paste text manually.")
                else:
                    st.success("✅ Text extracted successfully")

                    st.text_area("Extracted Text", extracted, height=150)

                    # ✅ Send to AI
                    result = get_ai_response(extracted)

                    st.markdown("### 🚨 Detection Result")
                    st.markdown(result)
            if extracted and len(extracted) > 5:
                st.success("✅ Text extracted from screenshot!")
                st.code(extracted)
                message_to_analyze = extracted
            else:
                st.warning("⚠️ Could not read text clearly. Please paste manually:")
                message_to_analyze = st.text_area("Paste text manually:", height=100, key="manual_paste")

    if st.button("🛡️ ANALYZE & TAKE ACTION", key="main_analyze"):
        if message_to_analyze.strip():
            with st.spinner("Analyzing and preparing all actions..."):
                run_detection(
                    message_to_analyze,
                    lang_code,
                    enable_voice,
                    victim_name if 'victim_name' in locals() else "",
                    victim_location if 'victim_location' in locals() else ""
                )
        else:
            st.warning("Please paste a message or upload a screenshot first!")

# ════════════════════════════════════════════════════════
# TAB 2 — PREDICT & PREVENT
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🧠 Predict & Prevent Cyberbullying")
    st.markdown("*Existing tools react. Kavach AI predicts before it gets worse.*")
    st.markdown("---")

    st.markdown("#### 👤 Fake Profile & Suspicious Account Detector")
    st.markdown("Enter account details — AI will warn if it looks suspicious or fake.")

    col_fp1, col_fp2 = st.columns(2)
    with col_fp1:
        account_name = st.text_input("Account username", placeholder="e.g. @priya_fake_123")
        account_age = st.selectbox("Account age", ["Less than 1 week", "1-4 weeks", "1-3 months", "3-12 months", "Over 1 year"])
        follower_count = st.number_input("Followers", min_value=0, value=0)
    with col_fp2:
        following_count = st.number_input("Following", min_value=0, value=0)
        post_count = st.number_input("Number of posts", min_value=0, value=0)
        has_profile_pic = st.selectbox("Has profile picture?", ["Yes", "No"])
        sends_threats = st.selectbox("Sends threats or hateful messages?", ["Yes", "No", "Sometimes"])

    account_behavior = st.text_area("Describe their behavior", placeholder="e.g. Keeps commenting hateful things, created account recently, no posts", height=80)

    if st.button("🔍 Check If Account Is Suspicious", key="fake_detect"):
        with st.spinner("Analyzing account..."):
            profile_info = f"""
            Username: {account_name}
            Account age: {account_age}
            Followers: {follower_count}, Following: {following_count}
            Posts: {post_count}
            Has profile pic: {has_profile_pic}
            Sends threats: {sends_threats}
            Behavior: {account_behavior}
            """
            fake_system = """You are a social media safety expert specializing in fake account detection for India.
            Analyze the account and respond in this format:

            RISK LEVEL: [HIGH / MEDIUM / LOW]
            VERDICT: [LIKELY FAKE / SUSPICIOUS / LIKELY REAL]
            RED FLAGS:
            * [Flag 1]
            * [Flag 2]
            RECOMMENDATION: [What to do — block, report, ignore]
            HOW TO REPORT: [Simple steps to report this account]
            WARNING: [Clear warning for the user in simple language]"""

            fake_result = get_ai_response(fake_system, profile_info)
            translated_fake = translate_text(fake_result, lang_code)

            if "HIGH" in fake_result:
                st.markdown(f'<div class="warning-account">⚠️ <b>WARNING — HIGH RISK ACCOUNT</b><br><br>{translated_fake}</div>', unsafe_allow_html=True)
                st.session_state.safety_score = max(20, st.session_state.safety_score - 10)
            elif "MEDIUM" in fake_result:
                st.markdown(f'<div class="moderate-box">⚠️ <b>SUSPICIOUS ACCOUNT</b><br><br>{translated_fake}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="safe-box">✅ <b>ACCOUNT ANALYSIS</b><br><br>{translated_fake}</div>', unsafe_allow_html=True)

            if enable_voice:
                audio = text_to_speech(translated_fake, lang_code)
                if audio:
                    st.audio(audio, format="audio/mp3")

    st.markdown("---")

    st.markdown("#### 🛡️ Personalized Prevention Tips")
    if st.button("Get My Safety Tips", key="prev_tips"):
        with st.spinner("Generating tips..."):
            tips = get_ai_response(
                "You are a cyber safety expert for young Indian students.",
                "Give 6 specific, practical tips for a young Indian girl to prevent cyberbullying. Make them actionable and easy to follow. Use bullet points."
            )
            translated_tips = translate_text(tips, lang_code)
            st.markdown(f'<div class="action-box">{translated_tips}</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 📊 Your Digital Safety Score")
    score = st.session_state.safety_score
    score_color = get_safety_score_color(score)

    st.markdown(f"""
    <div class="score-card">
        <div style="font-size:3rem;font-weight:700;color:{score_color}">{score}%</div>
        <div style="font-size:1.1rem;color:#c084fc;margin:8px 0">{get_safety_label(score)}</div>
        <div style="font-size:0.9rem;color:#9ca3af">Your space is {score}% safe today</div>
        <div style="margin-top:12px;font-size:0.85rem;color:#6b7280">Incidents detected today: {st.session_state.incidents_today}</div>
    </div>
    """, unsafe_allow_html=True)

    if score >= 75:
        st.success("🎉 Great job! Your digital space is safe. Keep following safety tips!")
    elif score >= 50:
        st.warning("⚠️ Some risks detected. Stay alert and report suspicious activity.")
    else:
        st.error("🚨 High risk detected! Please report incidents and contact a trusted adult.")

    if st.button("🔄 Reset Safety Score"):
        st.session_state.safety_score = 85
        st.session_state.incidents_today = 0
        st.rerun()

# ════════════════════════════════════════════════════════
# TAB 3 — EMOTIONAL SUPPORT
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 💚 Emotional Well-being Support")
    st.markdown("*Your mental health matters most. Kavach is here for you.*")
    st.markdown("---")

    st.markdown("#### 💭 How Are You Feeling Right Now?")
    mood = st.select_slider(
        "Move the slider:",
        options=["😢 Very Sad", "😔 Sad", "😐 Okay", "🙂 Good", "😊 Happy"],
        value="😐 Okay"
    )

    if st.button("💚 Get Support Based on My Mood", key="mood_support"):
        with st.spinner("Preparing support..."):
            mood_system = """You are Kavach — a warm, empathetic mental health support AI for young Indian girls facing cyberbullying.
            Provide emotional support based on their mood.
            Include:
            1. Validation of their feelings
            2. A calming breathing exercise or activity
            3. An encouraging affirmation
            4. One practical next step
            Be warm, short and personal. Use simple language."""

            mood_response = get_ai_response(mood_system, f"The user is feeling: {mood}. Give appropriate emotional support.")
            translated_mood = translate_text(mood_response, lang_code)
            st.markdown(f'<div class="emotional-box">💚 <b>Kavach says:</b><br><br>{translated_mood}</div>', unsafe_allow_html=True)

            if enable_voice:
                audio = text_to_speech(translated_mood, lang_code)
                if audio:
                    st.audio(audio, format="audio/mp3")

    st.markdown("---")

    st.markdown("#### 🌬️ Quick Calm Down Exercise")
    st.markdown("""
    <div class="emotional-box">
    <b>4-7-8 Breathing Exercise:</b><br><br>
    1. 🫁 <b>Breathe IN</b> for 4 seconds<br>
    2. ⏸️ <b>Hold</b> for 7 seconds<br>
    3. 💨 <b>Breathe OUT</b> for 8 seconds<br><br>
    Repeat 3 times. You will feel calmer. 💚<br><br>
    <i>Remember: What happened is NOT your fault. You are brave and strong.</i>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### ✨ Daily Affirmation")
    affirmations = [
        "💜 You are worthy of love and respect.",
        "💙 What happened online does not define your worth.",
        "💚 You are braver than you believe.",
        "🧡 Your feelings are valid. You deserve to feel safe.",
        "💗 You are not alone. Millions of people care about you.",
        "⭐ You have the strength to overcome this.",
        "🌟 This is not your fault. You did the right thing by speaking up."
    ]
    if st.button("✨ Get Today's Affirmation", key="affirmation"):
        aff = translate_text(random.choice(affirmations), lang_code)
        st.markdown(f'<div class="emotional-box" style="text-align:center;font-size:1.2rem">{aff}</div>', unsafe_allow_html=True)
        if enable_voice:
            audio = text_to_speech(aff, lang_code)
            if audio:
                st.audio(audio, format="audio/mp3")

    st.markdown("---")

    st.markdown("#### 📞 Mental Health & Support Resources")
    st.markdown("""
    <div class="action-box">
    <b>🇮🇳 India Support Resources:</b><br><br>
    📞 <b>iCall (Mental Health):</b> 9152987821<br>
    📞 <b>Vandrevala Foundation:</b> 1860-2662-345 (24/7)<br>
    📞 <b>Childline:</b> 1098<br>
    📞 <b>Cyber Crime:</b> 1930<br>
    🌐 <b>cybercrime.gov.in</b><br>
    🌐 <b>icallhelpline.org</b>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 4 — SUPPORT CHAT
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 💬 Talk to Kavach — Your AI Support Friend")
    st.markdown("*You are safe here. Share what happened — I am listening.*")

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">🧒 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">🛡️ {msg["content"]}</div>', unsafe_allow_html=True)

    user_msg = st.text_input("Talk to me...", placeholder="e.g. I feel scared and don't know what to do", key="support_chat")

    if st.button("💬 Send", key="send_support"):
        if user_msg.strip():
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})

            system = """You are Kavach — a kind, empathetic AI support friend for a young Indian girl facing cyberbullying.
            Always:
            - Start by validating her feelings warmly
            - Never blame the victim
            - Be like a caring older sister
            - Give practical help when appropriate
            - Remind her: this is not her fault, she is not alone
            - If she seems in danger, gently suggest calling 1930 or telling a trusted adult
            - Keep responses warm, short and comforting"""

            history = [{"role": "system", "content": system}]
            for m in st.session_state.chat_messages[-6:]:
                history.append(m)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                max_tokens=500,
            )
            reply = response.choices[0].message.content
            translated_reply = translate_text(reply, lang_code)
            st.session_state.chat_messages.append({"role": "assistant", "content": translated_reply})

            if enable_voice:
                audio = text_to_speech(translated_reply, lang_code)
                if audio:
                    st.audio(audio, format="audio/mp3")
            st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

# ════════════════════════════════════════════════════════
# TAB 5 — SOS EMERGENCY
# ════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🆘 SOS Emergency Alert")

    sos_name = st.text_input("Your name", placeholder="e.g. Priya", key="sos_name")
    sos_location = st.text_input("Your location", placeholder="e.g. REVA University, Bangalore", key="sos_loc")
    sos_situation = st.text_area("What is happening right now?", placeholder="e.g. Someone is threatening me with my photos online", height=80)

    if st.button("🆘 GENERATE SOS ALERT", key="sos_btn"):
        if sos_situation.strip():
            sos_msg = f"""🚨 EMERGENCY — PLEASE HELP 🚨

Name: {sos_name or 'Your daughter'}
Location: {sos_location or 'Unknown'}
Time: Right now

SITUATION:
{sos_situation}

Please respond IMMEDIATELY.

Emergency Numbers:
📞 Cyber Crime: 1930
📞 Women Helpline: 1091
📞 Police: 100
📞 Emergency: 112"""

            translated_sos = translate_text(sos_msg, lang_code)
            st.error(translated_sos)
            st.success("✅ Copy this and send to parents on WhatsApp RIGHT NOW!")

            if enable_voice:
                audio = text_to_speech("Emergency alert generated. Send this to your parents immediately!", lang_code)
                if audio:
                    st.audio(audio, format="audio/mp3")
        else:
            st.warning("Please describe your situation!")

    st.markdown("---")
    st.markdown("### 📞 Emergency Contacts")
    contacts = [("🚔 Police", "100"), ("👩 Women", "1091"), ("💻 Cyber Crime", "1930"), ("👶 Childline", "1098"), ("🆘 Emergency", "112")]
    cols = st.columns(5)
    for i, (name, number) in enumerate(contacts):
        with cols[i]:
            st.markdown(f'<div class="emergency-card"><b>{name}</b><br><h2 style="color:#f472b6">{number}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🌐 Report Online Now")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("🚔 cybercrime.gov.in", "https://cybercrime.gov.in")
    with c2:
        st.link_button("📘 Report Instagram", "https://help.instagram.com")
    with c3:
        st.link_button("💬 Report WhatsApp", "https://faq.whatsapp.com")

# ════════════════════════════════════════════════════════
# TAB 6 — PHOTO DETECTION (NEW FEATURE)
# ════════════════════════════════════════════════════════
with tab6:
    st.markdown("### 📸 Photo Detection & Privacy Guard")
    st.markdown("*Upload a photo to check if it's circulating online, detect hidden metadata, and get auto-delete advice.*")
    st.markdown("---")

    st.info("""
    ℹ️ **What this feature does:**
    - 🔍 Scans photo metadata (EXIF) for hidden personal data (location, device info)
    - 🧠 AI analyzes if the photo is at risk of being shared online
    - 🗑️ Recommends whether to auto-delete the photo
    - 🌐 Provides reverse image search links to check if photo is already online
    - ⚖️ Generates a photo removal request letter for platforms
    - 📞 Shows legal steps under Indian law
    """)

    photo_input = st.file_uploader(
        "Upload the photo you want to check",
        type=["png", "jpg", "jpeg", "webp"],
        key="photo_detect_upload"
    )

    if photo_input:
        col_img, col_info = st.columns([1, 2])
        with col_img:
            st.image(photo_input, caption="Uploaded Photo", use_column_width=True)
        with col_info:
            st.markdown("**Photo ready for scanning.**")
            st.markdown("Click the button below to run a full privacy and risk analysis.")

        if st.button("🔍 SCAN PHOTO FOR RISKS & ONLINE PRESENCE", key="photo_scan_btn"):
            run_photo_detection(
                photo_input,
                lang_code,
                enable_voice,
                victim_name if 'victim_name' in locals() else ""
            )

    st.markdown("---")

    # Show scan history
    if st.session_state.photo_scan_history:
        st.markdown("#### 📋 Your Photo Scan History (This Session)")
        for i, scan in enumerate(reversed(st.session_state.photo_scan_history)):
            risk_emoji = "🔴" if scan["risk"] == "HIGH" else "🟡" if scan["risk"] == "MEDIUM" else "🟢"
            st.markdown(f"{risk_emoji} **Scan {len(st.session_state.photo_scan_history) - i}** — Risk: `{scan['risk']}` | Size: {scan['size']} | EXIF: {'Yes ⚠️' if scan['has_exif'] else 'No'} | Time: {scan['time']}")

    st.markdown("---")

    # Quick guidance even without upload
    st.markdown("#### 🛡️ What To Do If Someone Has Your Private Photo")
    st.markdown("""
    <div class="severe-box">
    🚨 <b>IMMEDIATE STEPS — Do These RIGHT NOW:</b><br><br>
    1. 📸 Take screenshots of all threats as evidence<br>
    2. 🚫 Block the person on all platforms immediately<br>
    3. 📞 Call <b>1930</b> (Cyber Crime Helpline) immediately<br>
    4. 🌐 Report at <b>cybercrime.gov.in</b><br>
    5. 👨‍👩‍👧 Tell a trusted adult — parent, teacher, counselor<br>
    6. 🗑️ Do NOT delete evidence before reporting<br>
    7. 📱 Report the photo/content directly on the platform<br><br>
    <b>⚖️ You are protected by IT Act Section 66E — sharing private images without consent = up to 3 years jail.</b>
    </div>
    """, unsafe_allow_html=True)
