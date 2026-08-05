import streamlit as st
import os
import tempfile
import subprocess
import shutil
from gtts import gTTS
import speech_recognition as sr

st.set_page_config(page_title="AI Dubbing Khmer PRO", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@400;700&display=swap');
    
    * { font-family: 'Kanit', sans-serif; }
    
    .main-title {
        font-size: 50px;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B6B, #FF8C42, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-title {
        font-size: 18px;
        color: #666;
        text-align: center;
        margin-bottom: 40px;
        letter-spacing: 1px;
    }
    
    .upload-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .upload-box h2 {
        font-size: 32px;
        margin: 0;
    }
    
    .stButton > button {
        border-radius: 15px;
        font-weight: 700;
        font-size: 18px;
        padding: 15px 40px;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .process-btn > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        width: 100%;
        height: 70px;
        font-size: 22px;
    }
    
    .process-btn > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(56, 239, 125, 0.5);
    }
    
    .vip-btn > button {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: #222;
        width: 100%;
        height: 60px;
        font-size: 18px;
    }
    
    .vip-btn > button:hover {
        transform: translateY(-3px);
    }
    
    .success-box {
        background: #d4edda;
        border: 2px solid #28a745;
        border-radius: 15px;
        padding: 20px;
        color: #155724;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin: 20px 0;
    }
    
    .error-box {
        background: #f8d7da;
        border: 2px solid #f5c6cb;
        border-radius: 15px;
        padding: 20px;
        color: #721c24;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin: 20px 0;
    }
    
    .processing-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 30px;
        color: white;
        text-align: center;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .vip-box {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        color: #222;
        font-weight: bold;
        font-size: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(247, 151, 30, 0.3);
    }
    
    .info-box {
        background: #e7f3ff;
        border-left: 5px solid #2196F3;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        color: #1565c0;
        font-weight: 500;
    }
    
    .download-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(56, 239, 125, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        padding: 12px 30px;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B6B, #FF8C42);
        color: white;
    }
    
    .telegram-link {
        background: #0088cc;
        color: white;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
        transition: all 0.3s;
    }
    
    .telegram-link:hover {
        background: #0077b5;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

try:
    VALID_KEYS = st.secrets.get("VALID_KEYS", {
        "BUNYIM-VIP-001": "សកម្ម",
        "KHMER-VIP-002": "សកម្ម",
        "VIP-2026-TEST": "សកម្ម"
    })
except:
    VALID_KEYS = {
        "BUNYIM-VIP-001": "សកម្ម",
        "KHMER-VIP-002": "សកម្ម",
        "VIP-2026-TEST": "សកម្ម"
    }

if "is_vip" not in st.session_state:
    st.session_state.is_vip = False
if "trial_count" not in st.session_state:
    st.session_state.trial_count = 0
if "processing" not in st.session_state:
    st.session_state.processing = False

def get_ffmpeg_paths():
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    
    if not ffmpeg or not ffprobe:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_exe:
                ffmpeg_dir = os.path.dirname(ffmpeg_exe)
                ffmpeg = ffmpeg_exe
                ffprobe = os.path.join(ffmpeg_dir, "ffprobe")
                if not os.path.exists(ffprobe):
                    ffprobe = os.path.join(ffmpeg_dir, "ffprobe.exe")
                if ffmpeg_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] += os.pathsep + ffmpeg_dir
        except:
            pass
    
    return ffmpeg, ffprobe

def extract_audio_from_video(video_path):
    try:
        ffmpeg, _ = get_ffmpeg_paths()
        if not ffmpeg:
            return None
        
        audio_path = os.path.join(tempfile.gettempdir(), "extracted_audio.wav")
        cmd = [ffmpeg, "-i", video_path, "-q:a", "9", "-n", audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(audio_path):
            return audio_path
        return None
    except Exception as e:
        st.error(f"❌ មិនបានស្រង់សម្លេង: {str(e)}")
        return None

def transcribe_audio(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='km-KH')
            return text
    except Exception as e:
        st.warning(f"⚠️ មិនបានស្គាល់ពាក្យ: {str(e)}")
        return ""

def generate_khmer_audio(text_to_speak):
    try:
        if not text_to_speak or len(text_to_speak.strip()) == 0:
            return None
        
        tts = gTTS(text=text_to_speak, lang='km', slow=False)
        audio_path = os.path.join(tempfile.gettempdir(), "khmer_dubbing.mp3")
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"❌ មិនបានបង្កើតសម្លេង: {str(e)}")
        return None

def merge_audio_to_video(video_path, audio_path):
    try:
        ffmpeg, _ = get_ffmpeg_paths()
        if not ffmpeg:
            st.error("❌ FFmpeg មិនរកឃើញ")
            return None
        
        output_path = os.path.join(tempfile.gettempdir(), "dubbed_video_final.mp4")
        cmd = [ffmpeg, "-i", video_path, "-i", audio_path, "-c:v", "copy", 
               "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", 
               "-shortest", "-y", output_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        return None
    except Exception as e:
        st.error(f"❌ មិនបានផ្សំវីដេអូ: {str(e)}")
        return None

st.markdown('<h1 class="main-title">🎬 AI Dubbing Khmer PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">✨ បង្កើតសម្លេងខ្មែរចូលវីដេអូរបស់អ្នក ដោយ AI ⚡</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 ដាក់វីដេអូបង្ហាញដោះស្រាយ", "📝 កែលម្អសម្លេង", "🔐 VIP"])

with tab1:
    st.markdown('<div class="upload-box"><h2>📹 ជ្រើសយកវីដេអូរបស់អ្នក</h2><p>MP4 • AVI • MOV • MKV</p></div>', unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader("", type=["mp4", "avi", "mov", "mkv", "flv", "webm"], label_visibility="collapsed")
    
    if uploaded_video:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="info-box">✅ វីដេអូ បានផ្ទុក</div>', unsafe_allow_html=True)
            st.video(uploaded_video)
        
        with col2:
            st.markdown('<div class="info-box">📊ព័ត៌មាន</div>', unsafe_allow_html=True)
            st.write(f"📄 ឈ្មោះ: `{uploaded_video.name}`")
            st.write(f"📦 ទំហំ: `{uploaded_video.size / (1024*1024):.2f} MB`")
            
            if not st.session_state.is_vip and st.session_state.trial_count >= 3:
                st.error("❌ លោកអ្នកបានប្រើប្រាស់ដល់ដែនកំណត់សាកល្បង។ សូមលើក VIP!")
            else:
                if st.session_state.trial_count > 0 and not st.session_state.is_vip:
                    st.info(f"⚠️ សល់ {3 - st.session_state.trial_count} ដងសាកល្បង")
                
                st.markdown('<div class="process-btn">', unsafe_allow_html=True)
                if st.button("▶️ ចាប់ផ្តើមបង្កើត Dubbing ឬឹង!", use_container_width=True, key="start_dubbing"):
                    st.session_state.processing = True
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.processing:
            video_path = os.path.join(tempfile.gettempdir(), f"input_{uploaded_video.name}")
            with open(video_path, "wb") as f:
                f.write(uploaded_video.getbuffer())
            
            with st.container():
                st.markdown('<div class="processing-box"><h3>⏳ កំពុងដាច់ស្រង់សម្លេងពីវីដេអូ...</h3></div>', unsafe_allow_html=True)
                progress = st.progress(0)
                
                audio_path = extract_audio_from_video(video_path)
                progress.progress(25)
                
                if audio_path:
                    st.markdown('<div class="processing-box"><h3>🎤 កំពុងស្គាល់ពាក្យឡើង...</h3></div>', unsafe_allow_html=True)
                    progress.progress(50)
                    
                    original_text = transcribe_audio(audio_path)
                    progress.progress(65)
                    
                    st.markdown('<div class="processing-box"><h3>🎙️ កំពុងបង្កើតសម្លេងខ្មែរ...</h3></div>', unsafe_allow_html=True)
                    progress.progress(80)
                    
                    if original_text:
                        khmer_audio = generate_khmer_audio(original_text)
                    else:
                        khmer_audio = generate_khmer_audio("សូមស្វាគមន៍ មក AI Dubbing Khmer")
                    
                    progress.progress(90)
                    
                    if khmer_audio:
                        st.markdown('<div class="processing-box"><h3>🎬 កំពុងផ្សំវីដេអូ...</h3></div>', unsafe_allow_html=True)
                        progress.progress(95)
                        
                        final_video = merge_audio_to_video(video_path, khmer_audio)
                        progress.progress(100)
                        
                        if final_video and os.path.exists(final_video):
                            st.markdown('<div class="success-box">✅ បានរៀងរាល់ដោយជោគជ័យ!</div>', unsafe_allow_html=True)
                            
                            with open(final_video, "rb") as f:
                                video_data = f.read()
                            
                            st.markdown('<div class="download-box"><h3>📥 ទាញយកវីដេអូដែលបានដាច់ស្រង់</h3></div>', unsafe_allow_html=True)
                            st.download_button(
                                label="⬇️ ទាញយក Dubbed Video",
                                data=video_data,
                                file_name=f"dubbed_{uploaded_video.name}",
                                mime="video/mp4",
                                use_container_width=True
                            )
                            
                            st.markdown(f'<div class="info-box">📱 ចែករំលែក: <a href="{TELEGRAM_LINK}" class="telegram-link">Telegram</a></div>', unsafe_allow_html=True)
                            
                            if not st.session_state.is_vip:
                                st.session_state.trial_count += 1
                        else:
                            st.markdown('<div class="error-box">❌ មិនបានផ្សំវីដេអូ សូមព្យាយាមម្តងទៀត</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">❌ មិនបានបង្កើតសម្លេង</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">❌ មិនបានស្រង់សម្លេងពីវីដេអូ</div>', unsafe_allow_html=True)
            
            st.session_state.processing = False

with tab2:
    st.markdown('<div class="info-box">📝 កែលម្អ ឬលើកលម្ងាង់សម្លេងខ្មែររបស់អ្នក</div>', unsafe_allow_html=True)
    
    custom_text = st.text_area("🎤 ដាក់សម្លេងខ្មែរលម្អិត", height=200, placeholder="ឧទាហរណ៍: សូមស្វាគមន៍ក្នុងវីដេអូរបស់ខ្ញុំ...")
    
    if custom_text.strip():
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔊 ស្តាប់សម្លេងឡើង", use_container_width=True):
                audio_file = generate_khmer_audio(custom_text)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
        
        with col2:
            if st.button("💾 រក្សាឯកសារ MP3", use_container_width=True):
                audio_file = generate_khmer_audio(custom_text)
                if audio_file:
                    with open(audio_file, "rb") as f:
                        st.download_button(
                            label="⬇️ ទាញយក MP3",
                            data=f,
                            file_name="khmer_audio.mp3",
                            mime="audio/mpeg",
                            use_container_width=True
                        )

with tab3:
    st.markdown('<div class="vip-box">🔑 វាលីដ VIP - ប្រើប្រាស់គ្មានដែនកំណត់</div>', unsafe_allow_html=True)
    
    if st.session_state.is_vip:
        st.markdown('<div class="success-box">👑 អ្នក VIP ហើយ! ប្រើប្រាស់គ្មានដែនកំណត់</div>', unsafe_allow_html=True)
    else:
        vip_key = st.text_input("🔐 ដាក់លេខកូដ VIP របស់អ្នក", type="password", placeholder="ឧទាហរណ៍: BUNYIM-VIP-001")
        
        if st.button("✓ ពិនិត្យលេខកូដ", use_container_width=True, key="check_vip"):
            if vip_key in VALID_KEYS and VALID_KEYS[vip_key] == "សកម្ម":
                st.session_state.is_vip = True
                st.markdown('<div class="success-box">✅ លេខកូដត្រឹមត្រូវ! អ្នក VIP ឡើងហើយ 👑</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown('<div class="error-box">❌ លេខកូដមិនត្រឹមត្រូវ</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">📱 មិនមានលេខកូដ? <a href="{}" class="telegram-link">ទាក់ទងទេលេក្រាម</a></div>'.format(TELEGRAM_LINK), unsafe_allow_html=True)
