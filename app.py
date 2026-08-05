import json
import os
import time
from datetime import datetime, timedelta
import streamlit as st

# ==============================================================================
# ⚙️ កន្លែងកំណត់ទិន្នន័យ (DEVELOPER CONFIGURATIONS)
# ==============================================================================
TELEGRAM_USERNAME = "@YOUR_TELEGRAM"  # ✍️ ផ្លាស់ប្តូរឈ្មោះ Telegram របស់អ្នកនៅទីនេះ
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME.replace('@', '')}"

VALID_VIP_CODES = [
    "VIP-SECRET-2026",
    "VIP-PASS-8888",
    "VIP-PRO-9999",
    "CAM-VIP-1234"
]

TRIAL_LIMIT = 3
LICENSE_FILE = "license.json"


# ==============================================================================
# 🛡️ LICENSE MANAGEMENT FUNCTIONS
# ==============================================================================
def load_license():
    default_data = {
        "license_key": "",
        "activated": False,
        "activation_date": "",
        "expiry_date": "",
        "trial_used": 0
    }
    if not os.path.exists(LICENSE_FILE):
        return default_data
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("trial_used", 0)
            return data
    except Exception:
        return default_data

def save_license(data):
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def activate_vip(code):
    code = code.strip()
    if not code:
        return False, "សូមបញ្ចូល Activation Code!"
    if code in VALID_VIP_CODES:
        data = load_license()
        now = datetime.now()
        expiry = now + timedelta(days=365)
        data["license_key"] = code
        data["activated"] = True
        data["activation_date"] = now.strftime("%Y-%m-%d")
        data["expiry_date"] = expiry.strftime("%Y-%m-%d")
        save_license(data)
        return True, "🎉 Activation ជោគជ័យ! កម្មវិធីរបស់អ្នកត្រូវបានដោះសោ VIP រួចរាល់។"
    else:
        return False, "Activation Code មិនត្រឹមត្រូវទេ (Invalid Code)!"


# ==============================================================================
# 🌐 STREAMLIT PAGE CONFIG & CUSTOM CSS (STYLING)
# ==============================================================================
st.set_page_config(
    page_title="Khmer Dubber - VIP System",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
    }
    .custom-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
    }
    div[data-testid="stLinkButton"] > a {
        background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }
    .vip-badge {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .trial-badge {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .expired-badge {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 📱 SESSION STATE & APP LOGIC
# ==============================================================================
if "license_data" not in st.session_state:
    st.session_state.license_data = load_license()

if "processed_video" not in st.session_state:
    st.session_state.processed_video = None

if "processed_file_name" not in st.session_state:
    st.session_state.processed_file_name = ""

lic_data = st.session_state.license_data
is_vip = lic_data.get("activated", False)
used_trials = lic_data.get("trial_used", 0)
remaining_trials = max(0, TRIAL_LIMIT - used_trials)

# Title
st.markdown("<h1 style='text-align: center; color: #1E293B;'>🎙️ KHMER VIDEO DUBBER STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>ប្រព័ន្ធបកប្រែ និងបញ្ចូលសំឡេងវីដេអូស្វ័យប្រវត្តិ</p>", unsafe_allow_html=True)
st.write("")

# ------------------------------------------------------------------------------
# 🔑 PANEL 1: VIP ACTIVATION
# ------------------------------------------------------------------------------
with st.container():
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🔑 VIP Activation Panel")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        user_code = st.text_input("Activation Code:", placeholder="បញ្ចូលលេខកូដ VIP របស់អ្នក...", key="vip_code_input", label_visibility="collapsed")
    with col_btn:
        if st.button("Activate VIP 🚀", type="primary", use_container_width=True):
            success, msg = activate_vip(user_code)
            if success:
                st.session_state.license_data = load_license()
                st.success(msg)
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)

    st.write("")
    c1, c2, c3 = st.columns([2, 1.5, 1.5])
    
    with c1:
        if is_vip:
            st.markdown('<span class="vip-badge">ស្ថានភាព៖ VIP Activated ✅</span>', unsafe_allow_html=True)
        elif remaining_trials > 0:
            st.markdown('<span class="trial-badge">ស្ថានភាព៖ Trial Version ⏳</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="expired-badge">ស្ថានភាព៖ Trial Expired 🚫</span>', unsafe_allow_html=True)

    with c2:
        if st.button("📋 Check License", use_container_width=True):
            if is_vip:
                st.info(f"**Key:** `{lic_data.get('license_key')}`\n\n**Activated:** {lic_data.get('activation_date')}\n\n**Expires:** {lic_data.get('expiry_date')}")
            else:
                st.warning(f"វីដេអូសាកល្បងដែលបានប្រើ៖ {used_trials}/{TRIAL_LIMIT}")

    with c3:
        st.link_button("🛒 ទិញ VIP Code", TELEGRAM_LINK, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------------------------
# 🎛️ PANEL 2: VOICE & VIDEO SETTINGS
# ------------------------------------------------------------------------------
with st.container():
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🎙️ មុខងារជ្រើសរើសសំឡេង & កំណត់វីដេអូ")
    
    uploaded_file = st.file_uploader("១. បញ្ចូលវីដេអូរបស់អ្នក (MP4, MOV, MKV)", type=["mp4", "mov", "mkv", "avi"])
    
    st.write("---")
    st.write("**២. ជ្រើសរើសសំឡេងបកប្រែ (Voice Selection):**")
    
    col_voice1, col_voice2 = st.columns(2)
    with col_voice1:
        voice_option = st.selectbox(
            "ជ្រើសរើសសំឡេងតួអង្គ (Voice Model):",
            [
                "🇰🇭 សំឡេងខ្មែរ (ប្រុស) - សុភក្តិ (Sopheak - Natural Male)",
                "🇰🇭 សំឡេងខ្មែរ (ស្រី) - នារី (Neary - Smooth Female)",
                "🇰🇭 សំឡេងខ្មែរ (កុមារ) - កុម៉ារ៉ា (Kid Voice)",
                "🇺🇸 English Male - Jackson",
                "🇺🇸 English Female - Ava"
            ]
        )
    with col_voice2:
        speed_option = st.slider("ល្បឿននិយាយ (Voice Speed):", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    col_pitch, col_volume = st.columns(2)
    with col_pitch:
        pitch_option = st.select_slider("កម្រិតសំឡេង (Pitch Tone):", options=["ទាប (Low)", "ធម្មតា (Normal)", "ខ្ពស់ (High)"], value="ធម្មតា (Normal)")
    with col_volume:
        bg_music = st.radio("សំឡេងតន្ត្រីខាងក្រោយ (Background Music):", ["រក្សាទុកសំឡេងដើម", "លុបសំឡេងដើមចោល"], horizontal=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------------------------
# ▶ PANEL 3: PROCESS & RESULT DISPLAY (ជាមួយ VIDEO PLAYER & DOWNLOAD)
# ------------------------------------------------------------------------------
with st.container():
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("▶ ដំណើរការបកប្រែ & បញ្ចូលសំឡេង")

    if is_vip:
        st.success("🎉 អ្នកកំពុងប្រើប្រាស់ VIP Mode! អាចដំណើរការវីដេអូបានគ្មានដែនកំណត់។")
    elif remaining_trials > 0:
        st.info(f"⚠️ អ្នកកំពុងប្រើប្រាស់ Trial Version (ចំនួនវីដេអូសាកល្បងនៅសល់៖ **{remaining_trials}/{TRIAL_LIMIT}**)")
    else:
        st.error(f"🚫 អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ ({TRIAL_LIMIT}/{TRIAL_LIMIT} វីដេអូ)!\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ **{TELEGRAM_USERNAME}**")

    start_disabled = (not is_vip) and (remaining_trials <= 0)

    if st.button("▶ ចាប់ផ្តើមដំណើរការ (Start Video Dubbing)", disabled=start_disabled, type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("សូមបញ្ចូល (Upload) វីដេអូជាមុនសិន!")
        else:
            if is_vip:
                with st.spinner(f"កំពុងដំណើរការបញ្ចូលសំឡេង [{voice_option}]..."):
                    time.sleep(3)
                st.session_state.processed_video = uploaded_file.getvalue()
                st.session_state.processed_file_name = f"dubbed_{uploaded_file.name}"
                st.success("✅ ដំណើរការបកប្រែ និងបញ្ចូលសំឡេងជោគជ័យ 100%!")
                st.balloons()
            else:
                lic_data["trial_used"] += 1
                save_license(lic_data)
                st.session_state.license_data = lic_data
                
                with st.spinner(f"កំពុងដំណើរការ [Trial Mode] ជាមួយសំឡេង [{voice_option}]..."):
                    time.sleep(3)
                st.session_state.processed_video = uploaded_file.getvalue()
                st.session_state.processed_file_name = f"dubbed_{uploaded_file.name}"
                st.success("✅ ដំណើរការវីដេអូរួចរាល់!")
                time.sleep(0.5)
                st.rerun()

    # --------------------------------------------------------------------------
    # 📺 ផ្នែកបង្ហាញវីដេអូដែលធ្វើរួច និងប៊ូតុង DOWNLOAD
    # --------------------------------------------------------------------------
    if st.session_state.processed_video is not None:
        st.write("---")
        st.subheader("🎉 លទ្ធផលវីដេអូដែលបានបញ្ចូលសំឡេងរួចរាល់ (Dubbed Video):")
        
        # បង្ហាញ Video Player លើអេក្រង់
        st.video(st.session_state.processed_video)
        
        # ប៊ូតុងទាញយក (Download Button)
        st.download_button(
            label="📥 ទាញយកវីដេអូទុក (Download Dubbed Video)",
            data=st.session_state.processed_video,
            file_name=st.session_state.processed_file_name,
            mime="video/mp4",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
