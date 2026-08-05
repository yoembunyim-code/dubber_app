import streamlit as st
import os
import time
from datetime import datetime

# =======================================================
# 1. ផ្នែក Config (សម្រាប់កែប្រែព័ត៌មានអ្នក)
# =======================================================
OWNER_TELEGRAM = "t.me/bunyimyoem" # <-- កែត្រង់នេះទៅជាឈ្មោះរបស់អ្នក

LICENSE_DATABASE = {
    "VIP-2026-ABCD": {"uses": 100, "expiry": "2026-12-31"}, 
    "ADMIN-9999":    {"uses": 999, "expiry": "2030-01-01"}, 
}

# =======================================================
# 2. កំណត់ទំព័រ និង CSS
# =======================================================
st.set_page_config(page_title="ប្រព័ន្ធឌឹបសំឡេង AI", layout="wide", page_icon="🎬")

if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'current_key' not in st.session_state:
    st.session_state.current_key = None
if 'trial_done' not in st.session_state:
    st.session_state.trial_done = False
if 'trial_video_data' not in st.session_state:
    st.session_state.trial_video_data = None

# តុបតែង UI ឲ្យមានរូបរាងដូចរូបទី៣
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; font-family: 'Khmer OS', 'Segoe UI', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #1e293b; color: #ffffff; }
    section[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }
    section[data-testid="stSidebar"] h3 { color: #ffffff; }

    .stButton > button { border-radius: 12px; font-weight: 600; border: none; transition: 0.2s; width: 100%; height: 3.5em; }
    .stButton > button:hover { transform: scale(1.02); }
    
    .stButton.green-btn > button { background-color: #10b981 !important; color: white !important; height: 4.5em; font-size: 20px; }
    .stButton.trial-btn > button { background-color: #f59e0b !important; color: white !important; height: 4em; font-size: 18px; }
    div[data-testid="stFileUploader"] button { background-color: #3b82f6 !important; color: white !important; border-radius: 12px; width: 100%; height: 3.5em; font-weight: bold; border: none; }
    .stTextInput > div > div > input { border-radius: 8px; border: 1px solid #ddd; padding: 12px; }
</style>
""", unsafe_allow_html=True)

# =======================================================
# 3. ផ្នែក SIDEBAR (បកប្រែជាខ្មែរទាំងស្រុង)
# =======================================================
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    st.markdown("---")
    
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាពប្រើប្រាស់:** `{status_text}`")
    if st.session_state.is_activated:
        st.caption(f"លេខកូដ៖ `{st.session_state.current_key}`")
    
    st.markdown("---")
    st.markdown("#### 📞 ត្រូវការជំនួយ?")
    st.markdown(f"ទាក់ទងមកយើងតាម Telegram៖")
    st.markdown(f"[![Telegram](https://img.shields.io/badge/Telegram-{OWNER_TELEGRAM}-blue?style=for-the-badge&logo=telegram)](https://t.me/{OWNER_TELEGRAM.replace('@', '')})")
    
    st.markdown("---")
    if st.button("🔄 កំណត់ឡើងវិញ (Debug)", use_container_width=True):
        st.session_state.is_activated = False
        st.session_state.current_key = None
        st.success("បានកំណត់ឡើងវិញដោយជោគជ័យ!")

# =======================================================
# 4. ផ្នែក MAIN UI
# =======================================================
st.markdown("<h1 style='text-align: center; color: #1e293b;'>🎬 ប្រព័ន្ធឌឹបសំឡេងវីដេអូ</h1>", unsafe_allow_html=True)
st.markdown("---")

# ផ្នែកផ្ទុកវីដេអូ
col1, col2 = st.columns(2)
with col1:
    uploaded_video = st.file_uploader("ផ្ទុកវីដេអូ", type=['mp4', 'avi', 'mov', 'mkv'], label_visibility="collapsed")
    if uploaded_video is not None:
        st.caption(f"ឯកសារ៖ `{uploaded_video.name}`")
with col2:
    st.button("📄 ផ្ទុកឯកសារ SRT", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ផ្នែកជ្រើសរើសសម្លេង
voice_option = st.selectbox("ជ្រើសរើសសម្លេង", ["ស្រី (Female)", "ប្រុស (Male)", "SREY MOM", "PIDETH"])
st.markdown("<br>", unsafe_allow_html=True)

# =======================================================
# 5. ផ្នែក FREE TRIAL
# =======================================================
st.markdown("### 🎁 សាកល្បងដោយឥតគិតថ្លៃ")
st.markdown('<div class="trial-btn">', unsafe_allow_html=True)
if st.button("🎬 សាកល្បងឌឹបវីដេអូ (Trial)", use_container_width=True):
    if uploaded_video is None:
        st.warning("សូមផ្ទុកវីដេអូជាមុនសិន!")
    else:
        st.session_state.trial_done = False
        with st.spinner('⏳ កំពុងដំណើរការឌឹប... សូមរង់ចាំបន្តិច'):
            time.sleep(3)
            uploaded_video.seek(0)
            st.session_state.trial_video_data = uploaded_video.read()
            st.session_state.trial_done = True
            st.rerun()

if st.session_state.trial_done:
    st.success("✅ ការសាកល្បងឌឹបសំឡេងបានបញ្ចប់! មើលលទ្ធផលខាងក្រោម៖")
    if st.session_state.trial_video_data:
        st.video(st.session_state.trial_video_data)
        st.download_button(
            label="📥 ទាញយកវីដេអូ",
            data=st.session_state.trial_video_data,
            file_name="trial_dubbed_result.mp4",
            mime="video/mp4"
        )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =======================================================
# 6. ផ្នែក Activate VIP
# =======================================================
st.markdown("### 🔑 បើកសិទ្ធិប្រើប្រាស់ពេញ")
if st.session_state.is_activated:
    st.success("🎉 ប្រព័ន្ធបាន Activate រួចរាល់! ចូលប្រើប្រាស់មុខងារពេញលេញខាងក្រោម។")
    
    # ===================================================
    # ផ្នែកនេះសំខាន់ណាស់! ខ្ញុំបានដាក់ Control Panel នៅទីនេះ
    # ===================================================
    st.markdown("### 📂 បន្ទះឧបករណ៍គ្រប់គ្រង")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("🤖 AUTO", use_container_width=True)
    with c2:
        st.button("👩 SREY MOM", use_container_width=True)
    with c3:
        st.button("🧑 PIDETH", use_container_width=True)

    st.button("🗣️ DUB AS-IS", use_container_width=True)
    
    st.markdown('<div class="green-btn">', unsafe_allow_html=True)
    if st.button("🚀 START (ពេញ)", use_container_width=True):
        if uploaded_video is None:
            st.warning("សូមផ្ទុកវីដេអូជាមុន!")
        else:
            st.success(f"✅ ចុច START ជោគជ័យ! សម្លេង: {voice_option}")
            st.info("នៅទីនេះអ្នកនឹងដាក់កូដ AI Dubbing ពិតរបស់អ្នក។")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ផ្នែក Activate Code
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        act_code_input = st.text_input("បញ្ចូលលេខកូដ VIP នៅទីនេះ", placeholder="ឧ. VIP-2026-ABCD", label_visibility="collapsed")
    with c_btn:
        if st.button("✅ Activate VIP", type="primary", use_container_width=True):
            if not act_code_input or act_code_input.strip() == "":
                st.error("❌ សូមបញ្ចូលលេខកូដ។")
            else:
                if act_code_input in LICENSE_DATABASE:
                    details = LICENSE_DATABASE[act_code_input]
                    try:
                        today = datetime.now().date()
                        expiry_date = datetime.strptime(details['expiry'], "%Y-%m-%d").date()
                        if today > expiry_date:
                            st.error("❌ កូដនេះផុតកំណត់ហើយ!")
                        elif details['uses'] <= 0:
                            st.error("❌ កូដនេះអស់ការប្រើប្រាស់ហើយ!")
                        else:
                            st.session_state.is_activated = True
                            st.session_state.current_key = act_code_input
                            LICENSE_DATABASE[act_code_input]['uses'] -= 1
                            st.success("🎉 Activate ជោគជ័យ!")
                            st.rerun()
                    except ValueError:
                        st.error("❌ កំហុសទិន្នន័យ។")
                else:
                    st.error("❌ លេខកូដមិនត្រឹមត្រូវ! ទាក់ទង Telegram ដើម្បីទិញ License។")
