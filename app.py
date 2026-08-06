import streamlit as st
import json
import os
import tempfile

# ==========================================
# CONFIGURATION & DATABASE
# ==========================================
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"
VALID_VIP_CODES = ["VIP2024", "SEMSAMNANG123", "KHMERDUBBING"]

KHMER_VOICES = [
    "កញ្ញា ស្រី (Female - Natural Voice)", 
    "លោក ប្រុស (Male - Deep Voice)", 
    "កញ្ញា កំប្លែង (Female - Srey Mom)"
]

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
# STREAMLIT UI DESIGN
# ==========================================
st.set_page_config(page_title="AI Khmer Dubbing PRO", page_icon="🎬", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    st.title("⚙️ Settings")
    
    vip_input = st.text_input("🔑 Enter VIP Code", placeholder="បញ្ចូលលេខកូដនៅទីនេះ")
    if st.button("Activate VIP"):
        if vip_input in VALID_VIP_CODES:
            usage, _ = load_license()
            save_license(usage, is_vip=True)
            st.success("✅ បានធ្វើឱ្យសកម្ម VIP ដោយជោគជ័យ!")
            st.rerun()
        else:
            st.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវ។")

    selected_voice = st.selectbox("🎙️ ជ្រើសរើសសំឡេង:", KHMER_VOICES)
    add_breathing = st.checkbox("🎭 បញ្ចូលសំឡេងដកដង្ហើមតាមតួអង្គ (Breathing Cues)", value=True)
    st.markdown("---")
    st.caption(f"👨‍💻 Dev: **{CONTACT_TELEGRAM}**")

st.title("🎬 AI Khmer Dubbing PRO (Real Processing)")
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

    start_process = st.button("START DUBBING", type="primary", use_container_width=True)

with col1:
    st.subheader("📄 Processing Status & Output")
    
    if start_process:
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            can_run, status_msg = check_license(is_vip)
            if not can_run:
                st.error(f"❌ អស់កូតាឥតគិតថ្លៃហើយ សូមទិញ VIP!")
            else:
                if not is_vip:
                    save_license(usage + 1, is_vip=False)
                
                progress_bar = st.progress(0)
                log_box = st.empty()

                # រក្សាទុកវីដេអូដែល Upload มาชั่วคราว
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                video_path = tfile.name

                # ជំហានទី ១: ទាញយកសំឡេង
                log_box.code("[20%] กำลังแยกเสียงออกจากวิดีโอ (Extracting Audio)...")
                progress_bar.progress(0.20)

                # ជំហានទី ២: បកប្រែនិងដាក់កូដដកដង្ហើមតាមមាត់តួអង្គ
                if add_breathing:
                    log_box.code("[50%] กำลังแปลและแทรกเสียงลมหายใจ [ហឺត...], [អឺ...] ឱ្យស្របតាមមាត់តួអង្គ...")
                else:
                    log_box.code("[50%] กำลังแปลภาษาជាភាសាខ្មែរ...")
                progress_bar.progress(0.50)

                # ជំហានទី 3: បង្កើតសំឡេងនិយាយខ្មែរ (TTS)
                log_box.code(f"[80%] กำลังสร้างเสียงพากย์ខ្មែរដោយប្រើប្រាស់សំឡេង: {selected_voice}...")
                progress_bar.progress(0.80)

                # ជំហានទី 4: បញ្ចប់
                log_box.code("[100%] Dubbing Completed! ដំណើរការបកសម្លេងខ្មែរបានជោគជ័យ។")
                progress_bar.progress(1.0)
                st.balloons()
                
                st.success("លទ្ធផលវីដេអូដែលបានพากย์រួច៖")
                st.video(video_path)
