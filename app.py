import streamlit as st
import os
import time
from datetime import datetime

# =======================================================
# 1. ផ្នែក Config (កន្លែងដែលអ្នកកែតែម្ដង)
# =======================================================
OWNER_TELEGRAM = "t.me/bunyimyoem" # ប្តូរទៅឈ្មោះ Telegram អ្នក

# បញ្ជីលេខកូដសម្រាប់អតិថិជន (គ្មាន Machine ID)
LICENSE_DATABASE = {
    "VIP-2026-ABCD": {"uses": 100, "expiry": "2026-12-31"}, # កូដសម្រាប់អ្នក
    "ADMIN-9999":    {"uses": 999, "expiry": "2030-01-01"}, # កូដសាកល្បង
    # បន្ថែមអតិថិជនថ្មីដូចនេះ៖
    # "SOKHA-VIP-001": {"uses": 5, "expiry": "2026-08-30"}, 
}

# =======================================================
# 2. កំណត់រចនាសម្ព័ន្ធទំព័រ & CSS ឡូយៗ
# =======================================================
st.set_page_config(page_title="AI Dubbing System", layout="wide", page_icon="🎬")

# កំណត់ Session State (ផ្នែកចងចាំ)
if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'current_key' not in st.session_state:
    st.session_state.current_key = None
if 'trial_done' not in st.session_state:
    st.session_state.trial_done = False
if 'trial_video_data' not in st.session_state:
    st.session_state.trial_video_data = None

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
# 3. ផ្នែក SIDEBAR (ខាងឆ្វេង)
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
# 4. ផ្នែក MAIN UI (កណ្តាល)
# =======================================================
st.markdown("<h1 style='text-align: center;'>🎬 AI Video Dubbing System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>ឌឹបសំឡេងវីដេអូដោយ AI យ៉ាងរហ័ស</p>", unsafe_allow_html=True)
st.markdown("---")

# 4.1 ផ្នែកផ្ទុកវីដេអូ (Upload)
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

# =======================================================
# 5. ផ្នែក FREE TRIAL (សាកល្បងដោយមិនចាំបាច់ Activate)
# =======================================================
st.markdown("### 🎁 សាកល្បងដោយឥតគិតថ្លៃ (Free Trial)")
st.markdown('<div class="trial-btn">', unsafe_allow_html=True)

if st.button("🎬 សាកល្បងវីដេអូដំបូង (Trial)", use_container_width=True):
    if uploaded_video is None:
        st.warning("សូមផ្ទុក (Upload) វីដេអូជាមុនសិន!")
    else:
        st.session_state.trial_done = False
        
        # ក្លែងធ្វើដំណើរការរង់ចាំ AI (បើអ្នកមាន AI ពិត ត្រូវកែត្រង់នេះ)
        with st.spinner(f'⏳ (សាកល្បង) កំពុងឌឹបសំឡេង AI: "{voice_option}"... សូមរង់ចាំ ៣ វិនាទី'):
            time.sleep(3) # ក្លែងធ្វើការធ្វើការងារ ៣ វិនាទី
            
            # រក្សាទុកទិន្នន័យវីដេអូដើម ដើម្បីយកទៅបង្ហាញជាលទ្ធផលសាកល្បង
            uploaded_video.seek(0)
            st.session_state.trial_video_data = uploaded_video.read()
            st.session_state.trial_done = True
            st.rerun() # ធ្វើឲ្យទំព័រផ្ទុកឡើងវិញ ដើម្បីបង្ហាញវីដេអូ

if st.session_state.trial_done:
    st.success("✅ សាកល្បង Dubbing បានបញ្ចប់ដោយជោគជ័យ! ឆែកមើលលទ្ធផលខាងក្រោម៖")
    if st.session_state.trial_video_data:
        st.video(st.session_state.trial_video_data)
        st.download_button(
            label="📥 ទាញយកវីដេអូសាកល្បង (Download)",
            data=st.session_state.trial_video_data,
            file_name="trial_dubbed_result.mp4",
            mime="video/mp4"
        )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =======================================================
# 6. ផ្នែក Activate VIP សម្រាប់ការប្រើប្រាស់ពេញ
# =======================================================
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

# =======================================================
# 7. ផ្នែក START (Full Version) តម្រូវឲ្យ Activate
# =======================================================
st.markdown("### 🚀 ដំណើរការពេញ (Full Process)")
st.markdown('<div class="green-btn">', unsafe_allow_html=True)

if st.button("🚀 START (Full Version)", use_container_width=True):
    if not st.session_state.is_activated:
        st.warning("សូម Activate VIP ជាមុនសិន ទើបអាចប្រើប្រាស់មុខងារ START នេះបាន!")
    elif uploaded_video is None:
        st.warning("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
    else:
        # នៅទីនេះអ្នកអាចដាក់ AI Logic ពិតរបស់អ្នកសម្រាប់ VIP
        # ឧទាហរណ៍៖ st.session_state.vip_video_data = run_real_ai_dubbing(uploaded_video, voice_option)
        st.success(f"✅ ចុច START (Full Version) ដោយជោគជ័យ! (សម្លេង: {voice_option})")
        st.info("⏳ (ចំណាំសម្រាប់អ្នកអភិវឌ្ឍន៍)៖ នៅទីនេះអ្នកអាចដាក់កូដ AI Dubbing ពិតរបស់អ្នក។ ពេលដំណើរការចប់ សូម Save ជាទម្រង់ Bytes និងប្រើ st.video() ដើម្បីបង្ហាញវីដេអូ។")
        
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.button("📂 OPEN FOLDER", type="secondary", use_container_width=True)
