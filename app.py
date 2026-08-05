import streamlit as st
import os
import tempfile
import subprocess
import shutil
from deep_translator import GoogleTranslator
from gtts import gTTS

# ==================== កំណត់ទំព័រ ====================
st.set_page_config(
    page_title="AI Auto Dubbing Khmer Pro",
    page_icon="🎬",
    layout="centered"
)

# ==================== CSS Styling (UI ដូចរូបភាព) ====================
st.markdown("""
<.start-btn > button { background-color: #4caf50 !important; color: white !important; font-size: 20px; height: 60px; width: 100%; border-radius: 10px; font-weight: bold; }>
    .main-title { font-size: 32px; font-weight: 800; color: #FF4B4B; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #666666; text-align: center; margin-bottom: 20px; }
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: bold; height: 50px; border: none;
    }
    /* Buttons Color Style */
    .blue-btn > button { background-color: #2b7fff; color: white; }
    .green-btn > button { background-color: #2d9c5c; color: white; }
    .purple-btn > button { background-color: #7e57c2; color: white; }
    .gray-btn > button { background-color: #bdbdbd; color: black; }
    .start-btn > button { background-color: #4caf50; color: white; font-size: 20px; height: 60px; }
    .folder-btn > button { background-color: #673ab7; color: white; }
    
    .notice-box {
        background: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 15px;
        border-left: 5px solid #FF4B4B;
    }
    .vip-box {
        background: #fffbe6; padding: 15px; border-radius: 10px; border: 2px solid #faad14; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Telegram Config ====================
TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

# ==================== Secrets & Valid Keys ====================
try:
    VALID_KEYS = st.secrets.get("VALID_KEYS", {
        "BUNYIM-VIP-001": "សកម្ម",
        "KHMER-VIP-002": "សកម្ម",
        "VIP-2026-TEST": "សកម្ម"  # សម្រាប់សាកល្បង
    })
except Exception:
    VALID_KEYS = {"BUNYIM-VIP-001": "សកម្ម", "KHMER-VIP-002": "សកម្ម", "VIP-2026-TEST": "សកម្ម"}

# ==================== Session State ====================
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False
if "trial_count" not in st.session_state:
    st.session_state.trial_count = 0
if "vip_key_entered" not in st.session_state:
    st.session_state.vip_key_entered = ""
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "auto"
if "last_video_result" not in st.session_state:
    st.session_state.last_video_result = None

# ==================== រកផ្លូវ FFmpeg ====================
def get_ffmpeg_paths():
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    
    if not ffmpeg_path or not ffprobe_path:
        try:
            import imageio_ffmpeg
            ffmpeg_from_imageio = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_from_imageio:
                ffmpeg_dir = os.path.dirname(ffmpeg_from_imageio)
                ffmpeg_path = ffmpeg_from_imageio
                possible_ffprobe = os.path.join(ffmpeg_dir, "ffprobe")
                if os.path.exists(possible_ffprobe):
                    ffprobe_path = possible_ffprobe
                elif os.path.exists(possible_ffprobe + ".exe"):
                    ffprobe_path = possible_ffprobe + ".exe"
                if ffmpeg_dir not in os.environ["PATH"]:
                    os.environ["PATH"] += os.pathsep + ffmpeg_dir
        except Exception as e:
            st.warning(f"⚠️ imageio_ffmpeg error: {e}")
            
    return ffmpeg_path, ffprobe_path

# ==================== មុខងារបង្កើតសំឡេងខ្មែរ (Fixed TTS) ====================
def generate_khmer_audio(text_to_speak):
    """ប្រើ gTTS ដើម្បីបង្កើតអូឌីយ៉ូភាសាខ្មែរ"""
    try:
        tts = gTTS(text=text_to_speak, lang='km')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"កំហុសក្នុងការបង្កើត TTS: {e}")
        return None

# ==================== មុខងារកែច្នៃវីដេអូ (Dummy Processing) ====================
def process_video_with_dubbing(video_path, srt_path):
    """ដំណើរការពិតប្រាកដនឹងផ្សំសំឡេងនៅទីនេះ (ខ្ញុំបង្ហាញ Flow គំរូ)"""
    try:
        # ១. អាន SRT និងបកប្រែជាខ្មែរ
        with open(srt_path, 'r', encoding='utf-8') as f:
            khmer_text = f.read()
            # គំរូ៖ បកប្រែជាខ្មែរ (អ្នកអាចប្រើ deep_translator នៅទីនេះ)
            # translator = GoogleTranslator(source='auto', target='km')
            # khmer_text = translator.translate(khmer_text)
            
        # ២. បង្កើតសំឡេងពីអត្ថបទខ្មែរ
        audio_file = generate_khmer_audio(khmer_text[:500]) # សាកល្បង 500 តួអង្គដំបូង
        
        if not audio_file:
            return None
            
        # ៣. បញ្ចូលសំឡេងទៅក្នុងវីដេអូ (ដោយប្រើ FFmpeg)
        ffmpeg, _ = get_ffmpeg_paths()
        output_video = os.path.join(tempfile.gettempdir(), "output_dubbed_video.mp4")
        
        cmd = [
            ffmpeg, "-i", video_path, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", "-y", output_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"FFmpeg Error: {result.stderr}")
            return None
            
        return output_video
        
    except Exception as e:
        st.error(f"កំហុសក្នុងដំណើរការវីដេអូ៖ {e}")
        return None

# ==================== UI & Logic Main ====================
st.markdown('<div class="main-title">🎬 AI Dubbing Khmer PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ប្រព័ន្ធបកប្រែសំឡេងវីដេអូជាភាសាខ្មែរស្វ័យប្រវត្តិ</div>', unsafe_allow_html=True)

# --- ផ្នែកគ្រប់គ្រង Trial & VIP ---
usage_info = st.container()
with usage_info:
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        if st.session_state.is_vip:
            st.success("👑 អ្នកកំពុងប្រើប្រាស់កំណែ VIP គ្មានដែនកំណត់!")
        else:
            remaining = max(0, 3 - st.session_state.trial_count)
            st.warning(f"📊 អ្នកនៅសល់ *{remaining}* លើកក្នុងការសាកល្បងដោយឥតគិតថ្លៃ។")
            if remaining == 0:
                st.error("⛔ អស់កូតាសាកល្បងហើយ! សូមបញ្ចូលកូដ VIP ដើម្បីបន្ត។")
                
    with col_btn:
        st.markdown(f"[![Telegram](https://img.shields.io/badge/Telegram-@{TELEGRAM_USERNAME}-blue)]({TELEGRAM_LINK})", unsafe_allow_html=True)

# --- បញ្ចូលលេខកូដ VIP ---
with st.expander("🔑 បញ្ចូលលេខកូដ VIP នៅទីនេះ", expanded=not st.session_state.is_vip):
    vip_input = st.text_input("បញ្ចូល Key ដែលបានទិញពី Telegram:", type="password", placeholder="ឧទាហរណ៍: BUNYIM-VIP-001")
    if st.button("ពិនិត្យកូដ VIP"):
        if vip_input.strip() in VALID_KEYS:
            st.session_state.is_vip = True
            st.session_state.trial_count = 0 # កុំបារម្ភពីកូតា
            st.success("✅ កូដ VIP ត្រឹមត្រូវហើយ! អ្នកអាចប្រើប្រាស់ប្រព័ន្ធបានគ្មានដែនកំណត់។")
            st.rerun()
        else:
            st.error("❌ កូដ VIP មិនត្រឹមត្រូវ។ សូមផ្ទៀងផ្ទាត់ ឬទាក់ទង Telegram ដើម្បីទិញ។")

# --- ចាប់ផ្ដើមដំណើរការប្រសិនបើមានសិទ្ធិ ---
if st.session_state.is_vip or st.session_state.trial_count < 3:
    st.markdown("---")
    
    # Browse Video / SRT
    cols_upload = st.columns(2)
    with cols_upload[0]:
        uploaded_video = st.file_uploader("📂 BROWSE VIDEO", type=["mp4", "mov", "avi", "mkv"])
    with cols_upload[1]:
        uploaded_srt = st.file_uploader("📄 BROWSE SRT", type=["srt"])

    # Voice Selection Row
    st.markdown("### 🎤 ជ្រើសរើសសំឡេង")
    cols_voice = st.columns(4)
    with cols_voice[0]:
        if st.button("AUTO", key="auto_btn"):
            st.session_state.selected_voice = "auto"
    with cols_voice[1]:
        if st.button("SREY MOM", key="srey_btn"):
            st.session_state.selected_voice = "srey_mom"
    with cols_voice[2]:
        if st.button("PISETH", key="piseth_btn"):
            st.session_state.selected_voice = "piseth"
    with cols_voice[3]:
        if st.button("DUB AS-IS", key="asis_btn"):
            st.session_state.selected_voice = "as_is"
            
    st.write(f"👉 *សំឡេងដែលបានជ្រើសរើស:* {st.session_state.selected_voice}")
    st.markdown("---")

    # Main Action Buttons: START & OPEN FOLDER
    col_start, col_open = st.columns([3, 1])
    
    with col_start:
        if st.button("🚀 START", key="start_process"):
            if uploaded_video is None or uploaded_srt is None:
                st.warning("⚠️ សូមបង្ហោះទាំងវីដេអូ និងឯកសារ SRT ជាមុនសិន!")
            else:
                # Save uploads temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                    tmp_video.write(uploaded_video.getvalue())
                    video_path = tmp_video.name
                with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as tmp_srt:
                    tmp_srt.write(uploaded_srt.getvalue())
                    srt_path = tmp_srt.name
                
                # Processing
                with st.spinner("⏳ កំពុងដំណើរការ... សូមរង់ចាំមួយភ្លេត!"):
                    output_path = process_video_with_dubbing(video_path, srt_path)
                
                if output_path:
                    # បង្កើនកូតាប្រើប្រាស់ (លុះត្រាតែមិនមែន VIP)
                    if not st.session_state.is_vip:
                        st.session_state.trial_count += 1
                    
                    st.session_state.last_video_result = output_path
                    st.session_state.processing_complete = True
                    st.success("✅ ដំណើរការជោគជ័យ! អ្នកអាចទាញយកវីដេអូបានខាងក្រោម។")
                    st.rerun()
                else:
                    st.error("❌ មានបញ្ហាក្នុងដំណើរការវីដេអូ។ សូមពិនិត្យមើលកំហុសខាងលើ។")

    with col_open:
        st.markdown('<div class="folder-btn">', unsafe_allow_html=True)
        if st.button("📂 OPEN FOLDER", key="open_folder"):
            if st.session_state.last_video_result and os.path.exists(st.session_state.last_video_result):
                folder_path = os.path.dirname(st.session_state.last_video_result)
                try:
                    if os.name == 'nt': # Windows
                        os.startfile(folder_path)
                    else: # Mac / Linux
                        subprocess.run(['open', folder_path] if os.name == 'posix' else ['xdg-open', folder_path])
                except:
                    st.info(f"ឯកសារលទ្ធផលស្ថិតនៅក្នុង Folder៖ {folder_path}")
            else:
                st.info("សូមដំណើរការ START ជាមុនសិន ដើម្បីបង្កើតឯកសារលទ្ធផល។")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- បង្ហាញលទ្ធផលក្រោយ Process ---
    if st.session_state.processing_complete and st.session_state.last_video_result:
        st.markdown("---")
        with open(st.session_state.last_video_result, "rb") as file:
            st.download_button(
                label="⬇️ ទាញយកវីដេអូដែលបានបកប្រែ",
                data=file,
                file_name="output_dubbed_video.mp4",
                mime="video/mp4"
            )
        st.video(st.session_state.last_video_result)

else:
    # នៅពេលអស់កូតា និងមិនមែន VIP
    st.error("⛔ អ្នកបានប្រើប្រាស់សាកល្បងទាំង ៣ ដងហើយ។ សូមបញ្ចូលលេខកូដ VIP ខាងលើដើម្បីបន្ត។")
    st.markdown(f"💬 សម្រាប់ការទិញកូដ VIP សូមទាក់ទងតាម Telegram៖ *[{TELEGRAM_USERNAME}]({TELEGRAM_LINK})*")
