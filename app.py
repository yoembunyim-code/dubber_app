import streamlit as st
import json
import os
import time

# ==========================================
# CONFIGURATION
# ==========================================
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

# ==========================================
# LICENSE MANAGER
# ==========================================
def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("video_processed", 0)
    return 0

def save_license(count):
    with open(LICENSE_FILE, 'w') as f:
        json.dump({"video_processed": count}, f)

def check_license():
    usage = load_license()
    if usage >= TRIAL_VIDEO_LIMIT:
        return False, usage
    return True, usage

# ==========================================
# STREAMLIT UI DESIGN
# ==========================================
st.set_page_config(page_title="AI Khmer Dubbing PRO", page_icon="🎬", layout="wide")

# Header
st.title("🎬 AI Khmer Dubbing PRO")
st.markdown("---")

# ===== បង្កើតជួរឈរ 2 (Col1: ឆ្វេង, Col2: ស្តាំ) ដើម្បីកុំឱ្យមាន Error NameError =====
col1, col2 = st.columns([2, 1])

# ------------------- RIGHT COLUMN: CONTROLS -------------------
with col2:
    st.subheader("🕹️ CONTROLS")
    
    # File Uploader
    video_file = st.file_uploader("BROWSE VIDEO", type=["mp4", "avi", "mov", "mkv"])
    srt_file = st.file_uploader("BROWSE SRT (Optional)", type=["srt"])
    
    # Options
    lang_option = st.selectbox("SOURCE LANG:", ["Auto-detect", "English", "Chinese"])
    keep_bg = st.checkbox("Keep background music", value=True)
    
    # START BUTTON
    if st.button("START DUBBING", type="primary", use_container_width=True):
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            # CHECK LICENSE
            can_run, usage_count = check_license()
            if not can_run:
                st.error(f"❌ អ្នកបានប្រើប្រាស់ដោយឥតគិតថ្លៃ {TRIAL_VIDEO_LIMIT} វីដេអូហើយ!\n\n👉 សូមទិញកូដពេញលេញសម្រាប់ប្រើប្រាស់គ្មានដែនកំណត់។\n📞 ទាក់ទងទិញតាម Telegram: **{CONTACT_TELEGRAM}**")
                st.stop()
            
            # Increment License
            save_license(usage_count + 1)
            st.session_state['process_start'] = True
            st.success(f"កំពុងដំណើរការលើកទី {usage_count + 1}/{TRIAL_VIDEO_LIMIT}")

    # STOP BUTTON
    if st.button("STOP", type="secondary", use_container_width=True):
        st.warning("កម្មវិធីបានឈប់ដំណើរការដោយអ្នកប្រើប្រាស់។")
        if 'process_start' in st.session_state:
            st.session_state['process_start'] = False

    # Show Telegram contact
    st.markdown("---")
    st.caption(f"👨‍💻 Developer: **{CONTACT_TELEGRAM}**")

# ------------------- LEFT COLUMN: LOGS & VIDEO OUTPUT -------------------
with col1:
    st.subheader("📄 Processing Logs")
    log_area = st.empty()
    progress_bar = st.progress(0)

    # ========== LOGIC TO SIMULATE AI DUBBING ==========
    if 'process_start' in st.session_state and st.session_state['process_start']:
        log_text = ""
        
        # កំណត់ឈ្មោះឯកសារលទ្ធផល
        final_output_filename = "output_dubbed_video.mp4"
        
        # ----------------------------------------------------------------
        # ធ្វើការក្លែងធ្វើ (Simulation) ជំហាន AI 
        # (នៅទីនេះអ្នកអាចយកកូដ AI ពិតៗរបស់អ្នកមកដាក់ជំនួសបាន)
        # ----------------------------------------------------------------
        
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
            log_text += "[81%] Translating... / កំពុងបកប្រែ...\n"
            log_area.code(log_text)
            progress_bar.progress(0.85)
            time.sleep(1.5)

        if st.session_state['process_start']:
            log_text += "[92%] Mixing audio into video... / កំពុងផ្សំសំឡេង...\n"
            log_area.code(log_text)
            progress_bar.progress(0.92)
            time.sleep(2)

        if st.session_state['process_start']:
            log_text += "[96%] Rendering final video... / កំពុង Render...\n"
            log_area.code(log_text)
            progress_bar.progress(0.96)
            
            # ===== Save Video File ទៅក្នុង Server =====
            # (នៅក្នុងគម្រោងពិត កូដ AI នឹងបង្កើតឯកសារនេះ)
            # នៅទីនេះខ្ញុំសរសេរកូដសម្រាប់ Save វីដេអូដើមទៅជាឯកសារលទ្ធផល ដើម្បីសាកល្បងឃើញវីដេអូចេញមក
            with open(final_output_filename, "wb") as f:
                f.write(video_file.getbuffer()) 
            time.sleep(1)

        if st.session_state['process_start']:
            log_text += "[100%] Dubbing Completed Successfully! / បានបញ្ចប់ដោយជោគជ័យ!\n"
            log_area.code(log_text)
            progress_bar.progress(1.0)
            
            # ===== បង្ហាញវីដេអូដល់អ្នកប្រើ =====
            if os.path.exists(final_output_filename):
                st.success("ដំណើរការបញ្ចប់! នេះជាវីដេអូលទ្ធផលរបស់អ្នក៖")
                st.video(final_output_filename) # បង្ហាញវីដេអូ
            else:
                st.warning("រកមិនឃើញឯកសារវីដេអូទេ។")

        st.session_state['process_start'] = False
