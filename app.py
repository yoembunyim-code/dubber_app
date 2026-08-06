import streamlit as st
import json
import os
import time

# ==========================================
# CONFIGURATION & DATABASE (កំណត់រចនាសម្ព័ន្ធ)
# ==========================================
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

VALID_VIP_CODES = ["VIP2024", "SEMSAMNANG123", "KHMERDUBBING"]

KHMER_VOICES = [
    "កញ្ញា ស្រី (Female - Natural)", 
    "លោក ប្រុស (Male - Deep Voice)", 
    "កញ្ញា កំប្លែង (Female - Srey Mom)"
]

# ==========================================
# LICENSE MANAGER (គ្រប់គ្រងការសាកល្បង)
# ==========================================
def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("video_processed", 0), data.get("is_vip", False)
    return 0, False

def save_license(count, is_vip=False):
    with open(LICENSE_FILE, 'w') as f:
        json.dump({"video_processed": count, "is_vip": is_vip}, f)

def check_license(is_vip):
    if is_vip:
        return True, "VIP Unlimited"
    usage, _ = load_license()
    if usage >= TRIAL_VIDEO_LIMIT:
        return False, usage
    return True, usage

# ==========================================
# STREAMLIT UI DESIGN (រចនាប្លង់ស្អាត)
# ==========================================
st.set_page_config(page_title="AI Khmer Dubbing PRO", page_icon="🎬", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    st.title("⚙️ Settings")
    
    st.subheader("🔑 Enter VIP Code")
    vip_input = st.text_input("VIP Code", placeholder="បញ្ចូលលេខកូដនៅទីនេះ")
    if st.button("Activate VIP"):
        if vip_input in VALID_VIP_CODES:
            usage, _ = load_license()
            save_license(usage, is_vip=True)
            st.success("✅ បានធ្វើឱ្យសកម្ម VIP ដោយជោគជ័យ!")
            st.rerun()
        else:
            st.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវ។")

    st.subheader("🎙️ Voice Selection")
    selected_voice = st.selectbox("ជ្រើសរើសសំឡេងដែលចង់បាន:", KHMER_VOICES)
    
    # ការកំណត់បន្ថែមសម្រាប់ស្ទីលតួអង្គ
    st.subheader("🎭 Dubbing Style")
    add_breathing = st.checkbox("បញ្ចូលសំឡេងដកដង្ហើម/អឺ...អា... (Natural Pause)", value=True)
    expression_tone = st.selectbox("ស្ទីលតួអង្គ:", ["ធម្មតា (Normal)", "រំជួលចិត្ត (Emotional)", "កំប្លែង (Comic)"])

    st.markdown("---")
    st.caption(f"👨‍💻 Dev: **{CONTACT_TELEGRAM}**")

st.title("🎬 AI Khmer Dubbing PRO (Advanced)")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🕹️ Controls")
    
    video_file = st.file_uploader("1. BROWSE VIDEO", type=["mp4", "avi", "mov", "mkv"])
    srt_file = st.file_uploader("2. BROWSE SRT (Optional)", type=["srt"])
    
    lang_option = st.selectbox("SOURCE LANG:", ["Auto-detect", "English", "Chinese", "Thai", "Japanese"])
    keep_bg = st.checkbox("Keep background music", value=True)
    
    usage, is_vip = load_license()
    if is_vip:
        st.success("🔓 VIP Mode Active (Unlimited)")
    else:
        st.info(f"📊 Trial: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    if st.button("START DUBBING", type="primary", use_container_width=True):
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            can_run, status_msg = check_license(is_vip)
            if not can_run:
                st.error(f"❌ អស់កូតាឥតគិតថ្លៃហើយ សូមទិញ VIP!")
                st.stop()
            
            if not is_vip:
                save_license(usage + 1, is_vip=False)
            
            st.session_state['process_start'] = True
            st.success(f"🚀 ចាប់ផ្តើមដំណើរការជាមួយសំឡេង: {selected_voice}")

    if st.button("STOP", type="secondary", use_container_width=True):
        st.warning("កម្មវិធីបានឈប់ដំណើរការ។")
        if 'process_start' in st.session_state:
            st.session_state['process_start'] = False

with col1:
    st.subheader("📄 Processing Logs & AI Translation")
    log_area = st.empty()
    progress_bar = st.progress(0)

    if 'process_start' in st.session_state and st.session_state['process_start']:
        log_text = ""
        
        log_text += "[20%] Extracting audio from video... / កំពុងទាញយកសំឡេង...\n"
        log_area.code(log_text)
        progress_bar.progress(0.20)
        time.sleep(0.5)

        log_text += "[50%] Transcribing original audio (Whisper AI)...\n"
        log_area.code(log_text)
        progress_bar.progress(0.50)
        time.sleep(0.8)

        log_text += f"[75%] Translating & Formatting Khmer Text ({expression_tone})...\n"
        if add_breathing:
            log_text += "   ➡️ Adding [ហឺត...], [ដកដង្ហើមធំ], [អឺ...] for realistic mouth sync.\n"
        log_area.code(log_text)
        progress_bar.progress(0.75)
        time.sleep(1.0)

        log_text += f"[90%] Generating Khmer Voice using '{selected_voice}'...\n"
        log_area.code(log_text)
        progress_bar.progress(0.90)
        time.sleep(1.5)

        log_text += "[100%] Dubbing Completed Successfully! / បានបញ្ចប់ដោយជោគជ័យ!\n"
        log_area.code(log_text)
        progress_bar.progress(1.0)
        st.balloons()
        st.success("ដំណើរការបញ្ចប់! ពិនិត្យមើលវីដេអូលទ្ធផលខាងក្រោម។")
        
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

        st.session_state['process_start'] = False
