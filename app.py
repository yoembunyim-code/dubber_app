import streamlit as st
import subprocess
import os
import asyncio
import shutil
import tempfile
import time
from deep_translator import GoogleTranslator
import edge_tts

# ==================== កំណត់ទំព័រ ====================
st.set_page_config(
    page_title="AI Auto Video Dubbing Khmer Pro",
    page_icon="🎬",
    layout="centered"
)

# ==================== CSS Styling ====================
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px;
        color: #666666;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF2222 100%);
        color: white;
        padding: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff3333, #e00000);
        color: white;
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(255,0,0,0.3);
    }
    .notice-box {
        background: linear-gradient(135deg, #fffbe6 0%, #fff1b8 100%);
        padding: 18px;
        border-radius: 12px;
        border-left: 6px solid #faad14;
        margin-bottom: 20px;
        color: #d46b08;
        font-size: 14px;
        line-height: 1.6;
    }
    .success-box {
        background: linear-gradient(135deg, #f6ffed 0%, #b7eb8f 100%);
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #52c41a;
        margin-bottom: 20px;
        color: #389e0d;
    }
    .error-box {
        background: linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%);
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #ff4d4f;
        margin-bottom: 20px;
        color: #cf1322;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== បង្ហាញចំណងជើង ====================
st.markdown('<div class="main-title">🎬 AI Auto Video Dubbing (Khmer)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ប្រព័ន្ធបកប្រែសំឡេងវីដេអូជាភាសាខ្មែរអូតូម៉ាតិក</div>', unsafe_allow_html=True)

# ==================== ការកំណត់ Telegram ====================
TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

st.markdown(f"""
    <div class="notice-box">
        🎁 <b>គោលការណ៍ប្រើប្រាស់ប្រព័ន្ធ៖</b><br>
        ✅ សាកល្បងបកប្រែវីដេអូដោយឥតគិតថ្លៃបាន <b>៣ វីដេអូដំបូង</b><br>
        🔑 បន្ទាប់ពីអស់កូតា ត្រូវ<b>ទិញកូដ VIP Access Key</b><br>
        💬 ទិញកូដ VIP តាមរយៈ Telegram: <a href="{TELEGRAM_LINK}" target="_blank"><b>@{TELEGRAM_USERNAME}</b></a>
    </div>
""", unsafe_allow_html=True)

# ==================== Constants & Secrets ====================
MAX_FREE_VIDEOS = 3

try:
    VALID_KEYS = st.secrets.get("VALID_KEYS", {
        "BUNYIM-VIP-001": "សកម្ម",
        "KHMER-VIP-002": "សកម្ម"
    })
except Exception:
    VALID_KEYS = {
        "BUNYIM-VIP-001": "សកម្ម",
        "KHMER-VIP-002": "សកម្ម"
    }

# ==================== Session State ====================
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False
if "trial_users" not in st.session_state:
    st.session_state.trial_users = {}
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# ==================== កំណត់ផ្លូវ FFmpeg (កែពេញលេញហើយ) ====================
def get_ffmpeg_paths():
    """រកផ្លូវ ffmpeg និង ffprobe ឲ្យបានត្រឹមត្រូវ"""
    ffmpeg_path = None
    ffprobe_path = None
    
    # 1. ព្យាយាមរកពី system PATH
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    
    # 2. បើមិនឃើញ សាកប្រើ imageio_ffmpeg
    if not ffmpeg_path or not ffprobe_path:
        try:
            import imageio_ffmpeg
            ffmpeg_from_imageio = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_from_imageio:
                ffmpeg_dir = os.path.dirname(ffmpeg_from_imageio)
                ffmpeg_path = ffmpeg_from_imageio
                # សាករក ffprobe ក្នុងថតដូចគ្នា
                possible_ffprobe = os.path.join(ffmpeg_dir, "ffprobe")
                if os.path.exists(possible_ffprobe):
                    ffprobe_path = possible_ffprobe
                elif os.path.exists(possible_ffprobe + ".exe"):
                    ffprobe_path = possible_ffprobe + ".exe"
                # បន្ថែមថតចូល PATH
                if ffmpeg_dir not in os.environ["PATH"]:
                    os.environ["PATH"] += os.pathsep + ffmpeg_dir
        except Exception as e:
            st.warning(f"⚠️ imageio_ffmpeg មិនអាចប្រើបាន: {e}")
    
    # 3. Fallback ចុងក្រោយ (កែឲ្យពេញលេញ)
    if not ffmpeg_path or not ffprobe_path:
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            ffprobe_path = imageio_ffmpeg.get_ffprobe_exe()
        except Exception:
            ffmpeg_path = "ffmpeg"
            ffprobe_path = "ffprobe"
    
    return ffmpeg_path, ffprobe_path

FFMPEG_PATH, FFPROBE_PATH = get_ffmpeg_paths()

# ==================== Functions ====================
async def generate_tts(text, output_file):
    """បង្កើតសំឡេងខ្មែរពីអត្ថបទដែលបានបកប្រែ"""
    voice = "km-KH-SreymomNeural"  # សំឡេងស្រីខ្មែរ
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_file)

def merge_audio_video(video_input_path, audio_input_path, output_path):
    """លាយសំឡេងថ្មីចូលទៅក្នុងវីដេអូដោយប្រើ FFmpeg"""
    cmd = [
        FFMPEG_PATH, "-i", video_input_path, "-i", audio_input_path,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", 
        "-map", "1:a:0", "-shortest", "-y", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg Error: {result.stderr}")

# ==================== UI ====================
# Sidebar តូចមួយសម្រាប់ពិនិត្យ VIP
with st.sidebar:
    st.header("🔑 បញ្ចូល Key")
    key_input = st.text_input("បញ្ចូល VIP Access Key")
    if st.button("ផ្ទៀងផ្ទាត់"):
        if key_input in VALID_KEYS:
            st.session_state.is_vip = True
            st.session_state.is_authenticated = True
            st.success("✅ អ្នកបានក្លាយជា VIP ហើយ!")
            st.rerun()
        else:
            st.error("❌ Key មិនត្រឹមត្រូវ")
    
    if st.session_state.is_vip:
        st.success("🌟 ស្ថានភាព៖ VIP")
    else:
        st.info("📢 ប្រើប្រាស់កំណែសាកល្បង (ឥតគិតថ្លៃ)")

# Main Content
uploaded_file = st.file_uploader("📁 ផ្ទុកឡើងឯកសារវីដេអូ (mp4, avi, mov)", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    # រក្សាទុកឯកសារក្នុង temporary folder
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "input_video.mp4")
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video(video_path)

    if st.button("🚀 ចាប់ផ្ដើមបកប្រែ និងបន្ថែមសំឡេង"):
        with st.spinner("កំពុងដំណើរការ (សូមរង់ចាំបន្តិច)..."):
            try:
                # -----------------------------------------------------------------
                # 1. ផ្នែកដកសម្តីពីវីដេអូ (Transcription) - អ្នកអាចប្តូរទៅ Whisper ត្រង់នេះ
                # សម្រាប់ពេលនេះ ខ្ញុំដាក់ពាក្យគំរូ និងនិយាយថាត្រូវកែត្រង់នេះ
                # -----------------------------------------------------------------
                st.info("📝 ចំណាំ៖ ត្រង់នេះ អ្នកត្រូវបិទភ្ជាប់កូដដកសម្តី (Speech to Text) ពីវីដេអូរបស់អ្នក ឧទាហរណ៍៖ ប្រើ Whisper")
                # ឧបមាថាយើងទាញអក្សរបានពីវីដេអូមកដាក់ក្នុងអថេរ extracted_text
                extracted_text = "Hello, this is a test video for automatic dubbing into Khmer language." # <--- កែត្រង់នេះ

                # 2. បកប្រែទៅជាភាសាខ្មែរ
                translator = GoogleTranslator(source='auto', target='km')
                khmer_text = translator.translate(extracted_text)
                
                # 3. បង្កើត Audio ថ្មី (ផ្នែកនេះធ្វើឲ្យសំឡេងដើរតាមអក្សរថ្មី)
                audio_path = os.path.join(temp_dir, "new_audio.mp3")
                asyncio.run(generate_tts(khmer_text, audio_path))
                
                # 4. លាយសំឡេង Audio ថ្មីចូលវីដេអូ
                output_path = os.path.join(temp_dir, "final_output.mp4")
                merge_audio_video(video_path, audio_path, output_path)
                
                # 5. ✅ បង្ហាញលទ្ធផល + កែបញ្ហាសំឡេងចាស់ឲ្យអស់!
                with open(output_path, "rb") as f:
                    video_bytes = f.read()
                
                st.success("🎉 បកប្រែ និងបន្ថែមសំឡេងបានជោគជ័យ!")
                # ត្រង់នេះសំខាន់ណាស់៖ ប្រើ ?t={int(time.time())} ដើម្បីបង្ខំឲ្យ Browser ទាញយកវីដេអូថ្មីជានិច្ច
                st.video(f"{output_path}?t={int(time.time())}") 

                # ប៊ូតុងទាញយក
                st.download_button(
                    label="📥 ទាញយកវីដេអូ",
                    data=video_bytes,
                    file_name="dubbed_video_khmer.mp4",
                    mime="video/mp4"
                )

            except Exception as e:
                st.error(f"❌ មានបញ្ហាកើតឡើង៖ {str(e)}")
            finally:
                # សម្អាតឯកសារបណ្ដោះអាសន្ន
                shutil.rmtree(temp_dir, ignore_errors=True)
