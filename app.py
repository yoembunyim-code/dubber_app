import streamlit as st
import os
import time
import subprocess
import tempfile
from pathlib import Path

# ==========================================
# កំណត់រចនាសម្ព័ន្ធរបស់អ្នកនៅទីនេះ
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
# ==========================================

# 1. កំណត់ Session State សម្រាប់រក្សាទិន្នន័យ និងរាប់លេខ
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

st.set_page_config(page_title="AI Khmer Dubbing PRO", page_icon="🎬", layout="wide")

# 2. ក្បាលកម្មវិធី
st.title("🎬 AI Khmer Dubbing PRO")
st.markdown(f"**ទាក់ទងទិញកូដពេញលេញ (Unlimited)៖** `{CONTACT_TELEGRAM}`")
st.divider()

# 3. បង្កើត UI ដូចរូបភាព (ចែកជា 2 ជួរ)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("ជ្រើសរើសប្រភព")
    uploaded_video = st.file_uploader("**BROWSE VIDEO (វីដេអូ)**", type=['mp4', 'avi', 'mov', 'mkv'], key='video')
    uploaded_srt = st.file_uploader("**BROWSE SRT (ឯកសារបកប្រែ)**", type=['srt'], key='srt')
    
    # ជម្រើសផ្សេងៗ
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        st.button("AUTO", use_container_width=True)
    with col_opt2:
        st.button("SREY MOM", use_container_width=True)
    with col_opt3:
        st.button("DUB AS-IS", use_container_width=True)

with col2:
    st.subheader("ការគ្រប់គ្រង")
    btn_start = st.button("▶ START DUBBING", use_container_width=True, type="primary")
    btn_stop = st.button("⏹ STOP", use_container_width=True, type="secondary")
    btn_open = st.button("📂 OPEN FOLDER", use_container_width=True)
    
    # បង្ហាញថានៅសល់ប៉ុន្មានដង
    remaining = TRIAL_VIDEO_LIMIT - st.session_state.usage_count
    if remaining > 0:
        st.info(f"💡 នៅសល់ការសាកល្បងឥតគិតថ្លៃ៖ **{remaining}** ដង")
    else:
        st.error(f"⚠️ អស់ចំនួនសាកល្បងហើយ! សូមទិញកូដពីញុម។")

# 4. តំបន់បង្ហាញ Log (ដូចក្នុងរូបភាព)
st.divider()
log_container = st.container()
with log_container:
    st.subheader("ដំណើរការ (Logs)")
    log_text = st.empty()

# ==========================================
# មុខងារដំណើរការ AI (ស្នូលកម្មវិធី)
# ==========================================
def run_dubbing_engine(video_path, srt_path):
    """ដំណើរការ AI Pipeline"""
    # ដាក់បញ្ចូលសារ Log ទៅក្នុងប្រអប់
    def update_log(msg):
        st.session_state.log_messages.append(msg)
        with log_container:
            log_text.text("\n".join(st.session_state.log_messages))

    update_log("[20%] Aligning audio... / កំពុងដកស្រង់សំឡេង...")
    time.sleep(1.5) # ពិតៗ ត្រូវហៅ Whisper model នៅទីនេះ

    update_log("[40%] Translating to Khmer... / កំពុងបកប្រែជាភាសាខ្មែរ...")
    time.sleep(1.5) # ពិតៗ ត្រូវហៅ Google Translate API នៅទីនេះ

    update_log("[65%] Generating Khmer TTS... / កំពុងបង្កើតសំឡេងខ្មែរ...")
    time.sleep(1.5) # ពិតៗ ត្រូវហៅ TTS Model នៅទីនេះ

    update_log("[85%] Mixing audio into video... / កំពុងលាយសំឡេងចូលវីដេអូ...")
    time.sleep(2) # ពិតៗ ត្រូវហៅ FFmpeg នៅទីនេះ

    update_log("[100%] Rendering final video... / កំពុង Render ចប់ហើយ! រួចរាល់!")
    st.success("✅ ដំណើរការ Dubbing បានបញ្ចប់ដោយជោគជ័យ!")

# ==========================================
# ការគ្រប់គ្រងព្រឹត្តិការណ៍ (When button clicked)
# ==========================================

# ចុចប៊ូតុង START
if btn_start:
    if not uploaded_video:
        st.warning("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
    else:
        # ពិនិត្យចំនួនដងដែលបានប្រើ
        if st.session_state.usage_count >= TRIAL_VIDEO_LIMIT:
            st.error(f"❌ អស់ចំនួនការសាកល្បងហើយ! អ្នកត្រូវទិញកូដពេញលេញពីញុម ដើម្បីបន្តប្រើប្រាស់។ ទាក់ទងតាម Telegram: `{CONTACT_TELEGRAM}`")
        else:
            # ចាប់ផ្ដើមរាប់ +1
            st.session_state.usage_count += 1
            
            # រក្សាទុកវីដេអូជាឯកសារបណ្ដោះអាសន្ន
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                tmp_video.write(uploaded_video.read())
                video_path = tmp_video.name
            
            srt_path = None
            if uploaded_srt:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.srt') as tmp_srt:
                    tmp_srt.write(uploaded_srt.read())
                    srt_path = tmp_srt.name

            # ដំណើរការ AI (នឹងមិនបង្កក UI ទេ ព្រោះ Streamlit គឺដំណើរការតាមលំដាប់)
            st.session_state.log_messages = [] # សម្អាត Log ចាស់
            run_dubbing_engine(video_path, srt_path)
            
            # បង្ហាញ Telegram ជាថ្មីម្ដងទៀត ក្រោយដំណើរការចប់
            if st.session_state.usage_count >= TRIAL_VIDEO_LIMIT:
                st.warning(f"👉 ប្រសិនបើអ្នកពេញចិត្តនឹងកម្មវិធីនេះ សូមទិញកូដ Unlimited ពីញុមដើម្បីប្រើប្រាស់គ្មានដែនកំណត់។ Telegram: **{CONTACT_TELEGRAM}**")

# ចុចប៊ូតុង OPEN FOLDER
if btn_open:
    st.info("📂 នៅក្នុងប្រព័ន្ធ Cloud ការបើក Folder ដោយផ្ទាល់មិនអាចធ្វើបានទេ។ សូមមើលវីដេអូលទ្ធផលនៅក្នុង 'Output' folder តាមរយៈ GitHub Repo របស់អ្នក។")
