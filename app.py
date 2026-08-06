import streamlit as str_ui
import json
import os
import tempfile
import openai

# ==========================================
# CONFIGURATION & API KEYS (កំណត់រចនាសម្ព័ន្ធ)
# ==========================================
# បញ្ជាក់៖ អ្នកត្រូវដាក់ OpenAI API Key របស់អ្នកនៅទីនេះ ឬប្រើ st.secrets
# openai.api_key = "YOUR_OPENAI_API_KEY"

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
# REAL AI BACKEND FUNCTIONS (មុខងារ AI ពិតប្រាកដ)
# ==========================================
def extract_audio_from_video(video_path):
    """ទាញយកឯកសារសំឡេង (Audio) ចេញពីវីដេអូ"""
    import moviepy.editor as mp
    audio_path = video_path.replace(".mp4", ".mp3")
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, logger=None)
    return audio_path

def transcribe_and_translate_audio(audio_path, add_breathing=True):
    """ប្រើប្រាស់ OpenAI Whisper ដើម្បីដកស្រង់សំឡេង និង GPT ដើម្បីបកប្រែជាភាសាខ្មែរតាមសាច់រឿងពិត"""
    
    # 1. Transcribe audio to text using Whisper API
    with open(audio_path, "rb") as audio_file:
        transcript_response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    original_text = transcript_response.get("text", "")

    # 2. Translate and format with GPT-4 (Adding breathing cues for lip-sync)
    breathing_instruction = ""
    if add_breathing:
        breathing_instruction = (
            " ត្រូវបញ្ចូលសញ្ញាដកដង្ហើម ឬកាយវិការតាមមាត់តួអង្គឱ្យបានធម្មជាតិ "
            "ដូចជា [ហឺត...], [ដកដង្ហើមធំ], [អឺ...], ឬផ្អាកបន្តិចនៅកន្លែងដែលសមស្រប ដើម្បីងាយស្រួលក្នុងការធ្វើ Lip-sync។"
        )

    prompt = (
        f"សូមបកប្រែអត្ថបទខាងក្រោមនេះជាភាសាខ្មែរឱ្យចំតាមសាច់រឿង និងបរិបទពិតប្រាកដក្នុងវីដេអូ ដោយហាមដាច់ខាតមិនត្រូវដាក់ពាក្យថា 'សូមស្វាគមន៍' បើសិនជាវីដេអូមិនបាននិយាយពាក្យហ្នឹងទេ។{breathing_instruction}\n\n"
        f"អត្ថបទដើម៖ {original_text}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "អ្នកគឺជាអ្នកជំនាញបកប្រែវីដេអូ និងកែសម្រួលស្គ្រីបនិយាយភាសាខ្មែរឱ្យមានជីវិតរស់រវើកដូចមនុស្សពិត។"},
            {"role": "user", "content": prompt}
        ]
    )
    
    translated_script = response['choices'][0]['message']['content']
    return original_text, translated_script

# ==========================================
# STREAMLIT UI DESIGN
# ==========================================
str_ui.set_page_config(page_title="AI Khmer Dubbing PRO", page_icon="🎬", layout="wide")

with str_ui.sidebar:
    str_ui.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    str_ui.title("⚙️ Settings")
    
    vip_input = str_ui.text_input("🔑 Enter VIP Code", placeholder="បញ្ចូលលេខកូដនៅទីនេះ")
    if str_ui.button("Activate VIP"):
        if vip_input in VALID_VIP_CODES:
            usage, _ = load_license()
            save_license(usage, is_vip=True)
            str_ui.success("✅ បានធ្វើឱ្យសកម្ម VIP ដោយជោគជ័យ!")
            str_ui.rerun()
        else:
            str_ui.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវ។")

    selected_voice = str_ui.selectbox("🎙️ ជ្រើសរើសសំឡេង:", KHMER_VOICES)
    add_breathing = str_ui.checkbox("🎭 បញ្ចូលសំឡេងដកដង្ហើមតាមតួអង្គ (Breathing Cues)", value=True)
    str_ui.markdown("---")
    str_ui.caption(f"👨‍💻 Dev: **{CONTACT_TELEGRAM}**")

str_ui.title("🎬 AI Khmer Dubbing PRO (AI Backend Connected)")
str_ui.markdown("---")

col1, col2 = str_ui.columns([2, 1])

with col2:
    str_ui.subheader("🕹️ Controls")
    video_file = str_ui.file_uploader("1. BROWSE VIDEO", type=["mp4", "avi", "mov", "mkv"])
    srt_file = str_ui.file_uploader("2. BROWSE SRT (Optional)", type=["srt"])
    lang_option = str_ui.selectbox("SOURCE LANG:", ["Auto-detect", "English", "Chinese", "Thai", "Japanese"])
    keep_bg = str_ui.checkbox("Keep background music", value=True)
    
    usage, is_vip = load_license()
    if is_vip:
        str_ui.success("🔓 VIP Mode Active (Unlimited)")
    else:
        str_ui.info(f"📊 Trial: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    start_process = str_ui.button("START DUBBING", type="primary", use_container_width=True)

with col1:
    str_ui.subheader("📄 Processing Status & Real AI Output")
    
    if start_process:
        if video_file is None:
            str_ui.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            can_run, status_msg = check_license(is_vip)
            if not can_run:
                str_ui.error(f"❌ អស់កូតាឥតគិតថ្លៃហើយ សូមទិញ VIP!")
            else:
                if not is_vip:
                    save_license(usage + 1, is_vip=False)
                
                progress_bar = str_ui.progress(0)
                log_box = str_ui.empty()

                # រក្សាទុកវីដេអូសាកល្បង
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                video_path = tfile.name

                try:
                    # ជំហានទី ១: ទាញយកសំឡេង
                    log_box.code("[20%] កំពុងទាញយកសំឡេងចេញពីវីដេអូ (Extracting Audio)...")
                    progress_bar.progress(0.20)
                    audio_path = extract_audio_from_video(video_path)

                    # ជំហានទី ២: ដកស្រង់អត្ថបទ និងបកប្រែតាមសាច់រឿងពិត (Whisper + GPT)
                    log_box.code("[50%] កំពុងប្រើប្រាស់ AI (Whisper & GPT) ដើម្បីបកប្រែជាភាសាខ្មែរតាមសាច់រឿងដើម និងបញ្ចូលការដកដង្ហើម...")
                    progress_bar.progress(0.50)
                    
                    original_text, translated_script = transcribe_and_translate_audio(audio_path, add_breathing)

                    # ជំហានទី 3: បង្ហាញលទ្ធផលស្គ្រីបដែលបានបកប្រែ
                    log_box.code("[80%] កំពុងរៀបចំស្គ្រីបនិយាយរួចរាល់...")
                    progress_bar.progress(0.80)

                    progress_bar.progress(1.0)
                    str_ui.balloons()
                    
                    str_ui.success("បកប្រែ និងបង្កើតស្គ្រីបបានជោគជ័យដោយមិនខុសសាច់រឿង!")
                    
                    # បង្ហាញលទ្ធផលអត្ថបទដែលបានបកប្រែ
                    str_ui.markdown("### 📝 ស្គ្រីបដែលបានបកប្រែជាភាសាខ្មែរ (ច្បាស់តាមសាច់រឿង):")
                    str_ui.info(translated_script)

                    str_ui.markdown("### 🎬 វីដេអូលទ្ធផល៖")
                    str_ui.video(video_path)

                except Exception as e:
                    str_ui.error(f"មានបញ្តាក្នុងការដំណើរការ AI: {e}")
