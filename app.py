import streamlit as st
import os
from datetime import datetime

# =======================================================
# 1. ផ្នែក Config (កន្លែងដែលអ្នកកែតែម្ដង)
# =======================================================
OWNER_TELEGRAM = "@YOUR_TELEGRAM" # ប្តូរទៅឈ្មោះ Telegram អ្នក

# បញ្ជីលេខកូដសម្រាប់អតិថិជន (គ្មាន Machine ID)
LICENSE_DATABASE = {
    "VIP-2026-ABCD": {"uses": 100, "expiry": "2026-12-31"}, # កូដសម្រាប់អ្នក
    "ADMIN-9999":    {"uses": 999, "expiry": "2030-01-01"}, # កូដសាកល្បង
    # បន្ថែមអតិថិជនថ្មីដូចនេះ៖
    # "SOKHA-VIP-001": {"uses": 5, "expiry": "2026-08-30"}, 
}

# កំណត់ឈ្មោះឯកសារលទ្ធផលពី AI
OUTPUT_VIDEO_NAME = "output_video.mp4"

# =======================================================
# 2. កំណត់រចនាសម្ព័ន្ធទំព័រ & CSS ឡូយៗ
# =======================================================
st.set_page_config(page_title="AI Dubbing System", layout="wide", page_icon="🎬")

if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'current_key' not in st.session_state:
    st.session_state.current_key = None

st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #1e293b; color: #ffffff; }
    section[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }
    .stButton > button { border-radius: 10px; font-weight: 600; border: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s; width: 100%; height: 3.2em; }
    .stButton > button:hover { transform: translateY(-2px); }
    .stButton.green-btn > button { background-color: #10b981 !important; color: white !important; height: 4.5em; font-size: 20px; }
    .stButton.trial-btn > button { background-color: #f59e0b !important; color: white !important; height: 4em; font-size: 18px; border: 2px solid white; }
    div[data-testid="stFileUploader"] { width: 100%; }
    div[data-testid="stFileUploader"] section { padding: 0; border: none; background: transparent; }
    div[data-testid="stFileUploader"] button { background-color: #3b82f6 !important; color: white !important; border-radius: 10px; width: 100%; height: 3.2em; font-weight: bold; border: none; }
    .stTextInput > div > div > input { border-radius: 10px; border: 1px solid #cbd5e1; padding: 12px; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# =======================================================
# 3. ផ្នែក SIDEBAR
# =======================================================
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    st.markdown("---")
    
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាពប្រើប្រាស់:** `{status_text}`")
    if st.session_state.is_activated:
        st.caption(f"កូដបច្ចុប្បន្ន៖ `{st.session_state.current_key}`")
    
    st.markdown("---")
    st.markdown("#### 📞 ត្រូវការជំនួយ?")
    st.markdown(f"[![Telegram](https://img.shields.io/badge/Telegram-{OWNER_TELEGRAM}-blue?style=for-the-badge&logo=telegram)](https://t.me/{OWNER_TELEGRAM.replace('@', '')})")
    
    st.markdown("---")
    if st.button("🔄 Reset License (Debug)", use_container_width=True):
        st.session_state.is_activated = False
        st.session_state.current_key = None
        st.success("បាន Reset ស្ថានភាពវិញ!")

# =======================================================
# 4. ផ្នែក MAIN UI
# =======================================================
st.markdown("<h1 style='text-align: center;'>🎬 AI Video Dubbing System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>ឌឹបសំឡេងវីដេអូដោយ AI យ៉ាងរហ័ស</p>", unsafe_allow_html=True)
st.markdown("---")

# 4.1 ផ្នែកផ្ទុកវីដេអូ
col1, col2 = st.columns(2)
with col1:
    uploaded_video = st.file_uploader("Browse Video", type=['mp4', 'avi', 'mov', 'mkv'], label_visibility="collapsed")
    if uploaded_video is not None:
        st.caption(f"ឯកសារ៖ `{uploaded_video.name}`")
with col2:
    st.button("📄 BROWSE SRT", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4.2 ផ្នែកជ្រើសរើសសម្លេង
voice_option = st.selectbox("ជ្រើសរើសសម្លេង (Select Voice)", ["ស្រី (Female)", "ប្រុស (Male)", "SREY MOM", "PIDETH"])
st.markdown("<br>", unsafe_allow_html=True)

# 4.3 ប៊ូតុងសាកល្បងដំបូង (មិនបាច់ Activate)
st.markdown("### 🎁 សាកល្បងដោយឥតគិតថ្លៃ (Free Trial)")
st.markdown('<div class="trial-btn">', unsafe_allow_html=True)
if st.button("🎬 សាកល្បងវីដេអូដំបូង (Trial)", use_container_width=True):
    if uploaded_video is None:
        st.warning("សូមផ្ទុក (Upload) វីដេអូជាមុនសិន!")
    else:
        st.success(f"✅ កំពុងសាកល្បងដំណើរការ Dubbing ជាមួយសម្លេង: {voice_option}")
        
        # ចំណាំ៖ នៅទីនេះអ្នកត្រូវបញ្ចូល AI Logic (កូដជំនួសសម្លេង) របស់អ្នក!
        # ឧទាហរណ៍៖ output_file = run_ai_dubbing(uploaded_video, voice_option)

        # ដោយសារខ្ញុំមិនទាន់មាន AI Logic ពិត ខ្ញុំក្លែងធ្វើជារកឃើញឯកសារលទ្ធផលដើម្បីបង្ហាញជូន
        if os.path.exists(OUTPUT_VIDEO_NAME):
            st.markdown("### 🎬 លទ្ធផលសាកល្បង")
            with open(OUTPUT_VIDEO_NAME, "rb") as f:
                video_bytes = f.read()
                st.video(video_bytes)
                st.download_button(
                    label="📥 ទាញយកវីដេអូ (Download)",
                    data=video_bytes,
                    file_name="trial_dubbed_result.mp4",
                    mime="video/mp4"
                )
        else:
            st.info("⏳ (សាកល្បង) កំពុងរង់ចាំ AI បង្កើតវីដេអូ... សូមរង់ចាំបន្តិច។")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 4.4 ផ្នែក Activate សម្រាប់ការប្រើប្រាស់ពេញ (Full Version)
st.markdown("### 🔑 បើកសិទ្ធិប្រើប្រាស់ពេញលេញ (VIP)")
if st.session_state.is_activated:
    st.success("🎉 ប្រព័ន្ធ VIP ត្រូវបាន Activate រួចរាល់ហើយ! អ្នកអាចប្រើប្រាស់មុខងារពេញលេញបាន។")
else:
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        act_code_input = st.text_input("បញ្ចូល Activation Code ដើម្បីបើកពេញ", placeholder="ឧ. VIP-2026-ABCD", label_visibility="collapsed")
    with c_btn:
        if st.button("✅ Activate VIP", type="primary", use_container_width=True):
            if not act_code_input or act_code_input.strip() == "":
                st.error("❌ សូមបញ្ចូលលេខកូដជាមុនសិន។")
            else:
                if act_code_input in LICENSE_DATABASE:
                    details = LICENSE_DATABASE[act_code_input]
                    try:
                        today = datetime.now().date()
                        expiry_date = datetime.strptime(details['expiry'], "%Y-%m-%d").date()
                        
                        if today > expiry_date:
                            st.error("❌ លេខកូដនេះបានផុតកំណត់ហើយ!")
                        elif details['uses'] <= 0:
                            st.error("❌ លេខកូដនេះត្រូវបានប្រើអស់ចំនួនកំណត់ហើយ!")
                        else:
                            st.session_state.is_activated = True
                            st.session_state.current_key = act_code_input
                            LICENSE_DATABASE[act_code_input]['uses'] -= 1
                            st.success("🎉 Activate ជោគជ័យ! សូមរីករាយប្រើប្រាស់។")
                            st.rerun()
                    except ValueError:
                        st.error("❌ កំហុសក្នុងទម្រង់កាលបរិច្ឆេទនៃលេខកូដនេះ។")
                else:
                    st.error("❌ លេខកូដមិនត្រឹមត្រូវ! សូមទាក់ទង Telegram របស់យើងដើម្បីទិញ License។")

st.markdown("<br>", unsafe_allow_html=True)

# 4.5 ប៊ូតុង START ដើម (តម្រូវឲ្យ Activate ទើបប្រើបាន)
st.markdown("### 🚀 ដំណើរការពេញ (Full Process)")
st.markdown('<div class="green-btn">', unsafe_allow_html=True)
if st.button("🚀 START (Full Version)", use_container_width=True):
    if not st.session_state.is_activated:
        st.warning("សូម Activate VIP ជាមុនសិន ទើបអាចប្រើប្រាស់មុខងារ START នេះបាន!")
    elif uploaded_video is None:
        st.warning("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
    else:
        st.success(f"✅ ចុច START ដោយជោគជ័យ! (សម្លេងពេញ: {voice_option})")
        
        # នៅទីនេះអ្នកត្រូវបញ្ចូលកូដ AI Dubbing ពេញសម្រាប់ VIP
        # output_file = run_ai_dubbing_vip(uploaded_video, voice_option)

        if os.path.exists(OUTPUT_VIDEO_NAME):
            st.markdown("### 🎬 លទ្ធផលវីដេអូពេញ")
            with open(OUTPUT_VIDEO_NAME, "rb") as f:
                video_bytes = f.read()
                st.video(video_bytes)
                st.download_button(
                    label="📥 ទាញយកវីដេអូ (Download)",
                    data=video_bytes,
                    file_name="vip_dubbed_result.mp4",
                    mime="video/mp4"
                )
        else:
            st.info("⏳ រង់ចាំឲ្យ AI ដំណើរការបង្កើតវីដេអូរួចសិន...")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.button("📂 OPEN FOLDER", type="secondary", use_container_width=True)
