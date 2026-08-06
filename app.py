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

# បញ្ជីលេខកូដ VIP ត្រឹមត្រូវ (អ្នកអាចបន្ថែមបានច្រើន)
VALID_VIP_CODES = ["VIP2024", "SEMSAMNANG123", "KHMERDUBBING"]

# បញ្ជីសំឡេងខ្មែរដែលអាចជ្រើសរើសបាន (នៅពេលភ្ជាប់ TTS ពិត អ្នកនឹងហៅ API តាមឈ្មោះនេះ)
KHMER_VOICES = [
    "កញ្ញា ស្រី (Female)", 
    "លោក ប្រុស (Male)", 
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

# Sidebar: កន្លែងដាក់លេខកូដ VIP និងជ្រើសសំឡេង
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80) # Logo គំរូ
    st.title("⚙️ Settings")
    
    # 1. កន្លែងបញ្ចូលលេខកូដ VIP
    st.subheader("🔑 Enter VIP Code")
    vip_input = st.text_input("VIP Code", placeholder="បញ្ចូលលេខកូដនៅទីនេះ")
    if st.button("Activate VIP"):
        if vip_input in VALID_VIP_CODES:
            usage, _ = load_license()
            save_license(usage, is_vip=True)
            st.success("✅ បានធ្វើឱ្យសកម្ម VIP ដោយជោគជ័យ! ឥឡូវអ្នកអាចប្រើបានគ្មានដែនកំណត់។")
            st.rerun()
        else:
            st.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវ។ សូមទាក់ទងទិញពីអ្នកអភិវឌ្ឍន៍។")

    # 2. ជ្រើសរើសសំឡេងខ្មែរ
    st.subheader("🎙️ Voice Selection")
    selected_voice = st.selectbox("ជ្រើសរើសសំឡេងដែលចង់បាន:", KHMER_VOICES)

    # Contact Info
    st.markdown("---")
    st.caption(f"👨‍💻 Dev: **{CONTACT_TELEGRAM}**")

# Main Area: ផ្នែកសំខាន់របស់កម្មវិធី
st.title("🎬 AI Khmer Dubbing PRO")
st.markdown("---")

col1, col2 = st.columns([2, 1])

# ------------------- RIGHT COLUMN: CONTROLS -------------------
with col2:
    st.subheader("🕹️ Controls")
    
    video_file = st.file_uploader("1. BROWSE VIDEO", type=["mp4", "avi", "mov", "mkv"])
    srt_file = st.file_uploader("2. BROWSE SRT (Optional)", type=["srt"])
    
    lang_option = st.selectbox("SOURCE LANG:", ["Auto-detect", "English", "Chinese", "Thai", "Japanese"])
    keep_bg = st.checkbox("Keep background music", value=True)
    
    # Check Current Status (VIP or Trial)
    usage, is_vip = load_license()
    if is_vip:
        st.success("🔓 VIP Mode Active (Unlimited)")
    else:
        st.info(f"📊 Trial: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    # START BUTTON
    if st.button("START DUBBING", type="primary", use_container_width=True):
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            # CHECK LICENSE
            can_run, status_msg = check_license(is_vip)
            if not can_run:
                st.error(f"❌ អ្នកបានប្រើប្រាស់ដោយឥតគិតថ្លៃ {TRIAL_VIDEO_LIMIT} វីដេអូហើយ!\n\n👉 សូមទិញកូដ VIP ដើម្បីប្រើប្រាស់គ្មានដែនកំណត់។")
                st.stop()
            
            if not is_vip:
                save_license(usage + 1, is_vip=False)
            
            st.session_state['process_start'] = True
            st.success(f"🚀 ចាប់ផ្តើមដំណើរការជាមួយសំឡេង: {selected_voice}")

    # STOP BUTTON
    if st.button("STOP", type="secondary", use_container_width=True):
        st.warning("កម្មវិធីបានឈប់ដំណើរការដោយអ្នកប្រើប្រាស់។")
        if 'process_start' in st.session_state:
            st.session_state['process_start'] = False

# ------------------- LEFT COLUMN: LOGS & OUTPUT -------------------
with col1:
    st.subheader("📄 Processing Logs")
    log_area = st.empty()
    progress_bar = st.progress(0)

    if 'process_start' in st.session_state and st.session_state['process_start']:
        log_text = ""
        
        # ក្លែងធ្វើដំណើរការ (អ្នកអាចបញ្ចូល AI ពិតៗនៅទីនេះ)
        log_text += "[80%] Aligning audio... / កំពុងដកស្រង់សំឡេង...\n"
        log_area.code(log_text)
        progress_bar.progress(0.80)
        time.sleep(0.5)

        for i in range(8, 23):
            if 'process_start' not in st.session_state or not st.session_state['process_start']: 
                break
            log_text += f"[80%] Aligning audio... {i}/22 / កំពុងដកស្រង់សំឡេង...\n"
            log_area.code(log_text)
            time.sleep(0.15) 

        if st.session_state['process_start']:
            log_text += "[85%] Translating to Khmer... / កំពុងបកប្រែជាខ្មែរ...\n"
            log_area.code(log_text)
            progress_bar.progress(0.85)
            time.sleep(1.5)

        if st.session_state['process_start']:
            log_text += f"[92%] Mixing audio into video with Voice: {selected_voice}... / កំពុងផ្សំសំឡេង...\n"
            log_area.code(log_text)
            progress_bar.progress(0.92)
            time.sleep(2)

        if st.session_state['process_start']:
            log_text += "[100%] Dubbing Completed Successfully! / បានបញ្ចប់ដោយជោគជ័យ!\n"
            log_area.code(log_text)
            progress_bar.progress(1.0)
            st.balloons()
            st.success("ដំណើរការបញ្ចប់! ពិនិត្យមើលវីដេអូលទ្ធផលខាងក្រោម។")
            
            # ក្លែងធ្វើការបង្ហាញវីដេអូលទ្ធផល
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")

        st.session_state['process_start'] = False
