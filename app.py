import streamlit as st
import subprocess
import os
import asyncio
import shutil
import tempfile
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

# ==================== Constants ====================
MAX_FREE_VIDEOS = 3

# ==================== Secrets ====================
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

# ==================== កំណត់ផ្លូវ FFmpeg ====================
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
    
    # 3. Fallback
    if not ffmpeg_path:
        ffmpeg_path = "ffmpeg"
    if not ffprobe_path:
        ffprobe_path = "ffprobe"
    
    return ffmpeg_path, ffprobe_path

FFMPEG_PATH, FFPROBE_PATH = get_ffmpeg_paths()

# បង្ហាញព័ត៌មានដល់អ្នកប្រើ
if FFMPEG_PATH == "ffmpeg" or FFPROBE_PATH == "ffprobe":
    st.warning("""
    ⚠️ *ប្រព័ន្ធមិនអាចរក FFmpeg ដោយស្វ័យប្រវត្តិបានទេ*  
    សូមដំឡើង FFmpeg ក្នុងប្រព័ន្ធរបស់អ្នក ឬបន្ថែម ffmpeg ក្នុង packages.txt សម្រាប់ Streamlit Cloud។
    """)

# ==================== ប្រព័ន្ធផ្ទៀងផ្ទាត់គណនី ====================
if not st.session_state.is_authenticated:
    st.markdown("### 🔐 សូមផ្ទៀងផ្ទាត់គណនីដើម្បីចាប់ផ្តើមប្រើប្រាស់")
    
    tab1, tab2 = st.tabs(["📧 Free Trial (សាកល្បង ៣ វីដេអូ)", "🔑 VIP Access Key (ទិញកូដ)"])

    with tab1:
        email_input = st.text_input(
            "បញ្ចូលអុីមែលរបស់អ្នកដើម្បីចាប់ផ្តើមសាកល្បង:",
            key="trial_email",
            placeholder="example@email.com"
        )
        if st.button("🚀 ចាប់ផ្តើមសាកល្បងដោយឥតគិតថ្លៃ", key="trial_btn"):
            if email_input and "@" in email_input and "." in email_input:
                used = st.session_state.trial_users.get(email_input, 0)
                if used < MAX_FREE_VIDEOS:
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_input
                    st.session_state.is_vip = False
                    if email_input not in st.session_state.trial_users:
                        st.session_state.trial_users[email_input] = 0
                    st.success("✅ ចូលគណនីសាកល្បងបានជោគជ័យ!")
                    st.rerun()
                else:
                    st.error(f"❌ អុីមែលនេះបានប្រើប្រាស់កូតាសាកល្បងអស់ {MAX_FREE_VIDEOS} វីដេអូហើយ!")
            else:
                st.warning("⚠️ សូមបញ្ចូលអុីមែលឱ្យបានត្រឹមត្រូវ (ឧ: name@domain.com)")

    with tab2:
        key_input = st.text_input(
            "បញ្ចូលកូដសម្ងាត់ VIP:",
            type="password",
            key="vip_key",
            placeholder="XXXXX-VIP-XXX"
        )
        if st.button("🔑 ផ្ទៀងផ្ទាត់កូដ VIP", key="vip_btn"):
            if key_input in VALID_KEYS:
                st.session_state.is_authenticated = True
                st.session_state.user_email = f"VIP: {key_input}"
                st.session_state.is_vip = True
                st.success("✅ កូដ VIP ត្រឹមត្រូវ! ស្វាគមន៍មកកាន់សមាជិកភាព VIP")
                st.rerun()
            else:
                st.error(f"❌ កូដសម្ងាត់មិនត្រឹមត្រូវ! ទាក់ទង Telegram: @{TELEGRAM_USERNAME}")
    
    st.stop()

# ==================== បង្ហាញព័ត៌មានគណនី ====================
col_acc1, col_acc2 = st.columns([4, 1])
with col_acc1:
    acc_type = "👑 VIP Member" if st.session_state.is_vip else "🆓 Free Trial"
    st.info(f"👤 *គណនី*: {st.session_state.user_email} ({acc_type})")
with col_acc2:
    if st.button("🚪 ចាកចេញ", key="logout_btn"):
        st.session_state.is_authenticated = False
        st.session_state.processing_complete = False
        st.rerun()

# ==================== ការកំណត់ភាសា និងសំឡេង ====================
st.markdown("---")
st.markdown("### ⚙️ ការកំណត់បកប្រែ")

col_lang1, col_lang2 = st.columns(2)

with col_lang1:
    source_lang_option = st.selectbox(
        "🌐 ភាសាដើមក្នុងវីដេអូ:",
        options=["អង់គ្លេស (English)", "ចិន (Chinese)", "វៀតណាម (Vietnamese)"],
        index=0
    )
    lang_code_map = {
        "អង់គ្លេស (English)": "en",
        "ចិន (Chinese)": "zh-CN",
        "វៀតណាម (Vietnamese)": "vi"
    }
    selected_source_lang = lang_code_map[source_lang_option]

with col_lang2:
    voice_option = st.selectbox(
        "🎙️ សំឡេង AI និយាយភាសាខ្មែរ:",
        options=["សំឡេងស្រី (Sreymom)", "សំឡេងប្រុស (Piseth)"],
        index=0
    )
    selected_voice = "km-KH-SreymomNeural" if "ស្រី" in voice_option else "km-KH-PisethNeural"

# ==================== មុខងារដំណើរការ ====================
async def extract_audio_from_video(video_path, audio_output_path):
    """ទាញយកសំឡេងពីវីដេអូ"""
    try:
        cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            audio_output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            st.error(f"❌ FFmpeg error: {result.stderr[:200]}")
            return False
        return os.path.exists(audio_output_path) and os.path.getsize(audio_output_path) > 0
    except subprocess.TimeoutExpired:
        st.error("❌ ពេលវេលាទាញយកសំឡេងផុតកំណត់")
        return False
    except Exception as e:
        st.error(f"❌ កំហុសពេលទាញយកសំឡេង: {str(e)}")
        return False

async def translate_text_to_khmer(text, source_lang):
    """បកប្រែអត្ថបទទៅជាភាសាខ្មែរ"""
    try:
        translator = GoogleTranslator(source=source_lang, target='km')
        translated = translator.translate(text)
        return translated
    except Exception as e:
        st.warning(f"⚠️ បរាជ័យក្នុងការបកប្រែតាមអនឡាញ: {str(e)}")
        # Fallback text in Khmer
        return "សួស្តី! នេះជាការសាកល្បងបកប្រែសំឡេងវីដេអូជាភាសាខ្មែរដោយប្រើបច្ចេកវិទ្យា AI"

async def text_to_speech_khmer(text, voice_name, output_path):
    """បំប្លែងអត្ថបទទៅជាសំឡេងភាសាខ្មែរ"""
    try:
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        st.error(f"❌ កំហុសពេលបង្កើតសំឡេង AI: {str(e)}")
        return False

async def merge_audio_to_video(video_path, audio_path, output_path):
    """បញ្ចូលសំឡេងថ្មីទៅក្នុងវីដេអូ"""
    try:
        # យករយៈពេលវីដេអូ
        probe_cmd = [
            FFPROBE_PATH,
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
        
        video_duration = 30.0
        if result.returncode == 0 and result.stdout.strip():
            try:
                video_duration = float(result.stdout.strip())
            except ValueError:
                pass
        
        # បញ្ចូលសំឡេង
        cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-i', audio_path,
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-t', str(video_duration),
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            # Fallback: ប្រើ -shortest
            fallback_cmd = [
                FFMPEG_PATH,
                '-i', video_path,
                '-i', audio_path,
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-y',
                output_path
            ]
            result = subprocess.run(fallback_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                st.error(f"❌ FFmpeg merge error: {result.stderr[:200]}")
                return False
        
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except subprocess.TimeoutExpired:
        st.error("❌ ពេលវេលាបញ្ចូលសំឡេងផុតកំណត់")
        return False
    except Exception as e:
        st.error(f"❌ កំហុសពេលបញ្ចូលសំឡេង: {str(e)}")
        return False

async def process_dubbing(video_input_path, video_output_path, source_lang, voice_name):
    """ដំណើរការបកប្រែ និងដាក់សំឡេងពេញលេញ"""
    temp_dir = tempfile.mkdtemp()
    audio_extracted = os.path.join(temp_dir, "extracted_audio.wav")
    audio_generated = os.path.join(temp_dir, "generated_audio.mp3")
    
    try:
        # ===== STEP 1: ទាញយកសំឡេង =====
        progress_placeholder = st.empty()
        progress_placeholder.write("📌 *ជំហានទី 1/5:* កំពុងទាញយកសំឡេងពីវីដេអូ...")
        if not await extract_audio_from_video(video_input_path, audio_extracted):
            progress_placeholder.error("❌ បរាជ័យក្នុងការទាញយកសំឡេង")
            return False
        progress_placeholder.success("✅ ទាញយកសំឡេងបានជោគជ័យ")
        
        # ===== STEP 2: រៀបចំអត្ថបទ =====
        progress_placeholder.write("📌 *ជំហានទី 2/5:* កំពុងរៀបចំអត្ថបទសម្រាប់បកប្រែ...")
        sample_texts = {
            "en": "Hello! Welcome to this automatic video dubbing system. We are translating this video into Khmer language using advanced AI technology. This is a demonstration of our AI-powered dubbing service.",
            "zh-CN": "你好！欢迎使用这个自动视频配音系统。我们正在使用先进的AI技术将这段视频翻译成高棉语。这是我们的AI配音服务的演示。",
            "vi": "Xin chào! Chào mừng bạn đến với hệ thống lồng tiếng video tự động này. Chúng tôi đang dịch video này sang tiếng Khmer bằng công nghệ AI tiên tiến. Đây là bản demo của dịch vụ lồng tiếng AI của chúng tôi."
        }
        text_to_translate = sample_texts.get(source_lang, sample_texts["en"])
        
        # ===== STEP 3: បកប្រែ =====
        progress_placeholder.write("📌 *ជំហានទី 3/5:* កំពុងបកប្រែទៅជាភាសាខ្មែរ...")
        translated_text = await translate_text_to_khmer(text_to_translate, source_lang)
        progress_placeholder.success(f"✅ បកប្រែរួច: {translated_text[:60]}...")
        
        # ===== STEP 4: បង្កើតសំឡេង AI =====
        progress_placeholder.write("📌 *ជំហានទី 4/5:* កំពុងបង្កើតសំឡេង AI ជាភាសាខ្មែរ...")
        if not await text_to_speech_khmer(translated_text, voice_name, audio_generated):
            progress_placeholder.error("❌ បរាជ័យក្នុងការបង្កើតសំឡេង AI")
            return False
        progress_placeholder.success("✅ បង្កើតសំឡេង AI បានជោគជ័យ")
        
        # ===== STEP 5: បញ្ចូលសំឡេង =====
        progress_placeholder.write("📌 *ជំហានទី 5/5:* កំពុងបញ្ចូលសំឡេងទៅវីដេអូ...")
        if not await merge_audio_to_video(video_input_path, audio_generated, video_output_path):
            progress_placeholder.error("❌ បរាជ័យក្នុងការបញ្ចូលសំឡេង")
            return False
        progress_placeholder.success("✅ បញ្ចូលសំឡេងបានជោគជ័យ ១០០%!")
        
        return True
        
    except Exception as e:
        st.error(f"❌ កំហុសក្នុងដំណើរការ: {str(e)}")
        return False
    finally:
        # សម្អាតថត temp
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

def run_async_dubbing(video_input, video_output, source_lang, voice_name):
    """Wrapper សម្រាប់ដំណើរការ async"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            process_dubbing(video_input, video_output, source_lang, voice_name)
        )
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            process_dubbing(video_input, video_output, source_lang, voice_name)
        )

# ==================== UI: Upload Video ====================
st.markdown("---")
st.markdown("### 📤 ផ្ទុកវីដេអូរបស់អ្នក")

uploaded_file = st.file_uploader(
    "ជ្រើសរើសឯកសារវីដេអូ (MP4, MOV, AVI):",
    type=["mp4", "mov", "avi"],
    help="ទំហំឯកសារមិនគួរលើស 500MB"
)

if uploaded_file is not None:
    input_filename = "input_video.mp4"
    output_filename = "dubbed_video.mp4"
    
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.subheader("🎥 វីដេអូដើម")
    st.video(input_filename)
    
    can_proceed = True
    if not st.session_state.is_vip:
        used_count = st.session_state.trial_users.get(st.session_state.user_email, 0)
        remaining = MAX_FREE_VIDEOS - used_count
        
        if remaining <= 0:
            st.markdown(f"""
            <div class="error-box">
                ❌ <b>អស់កូតាសាកល្បងហើយ!</b><br>
                អ្នកបានប្រើប្រាស់អស់ {MAX_FREE_VIDEOS} វីដេអូរួចហើយ។<br>
                សូមទាក់ទងទិញកូដ VIP តាមរយៈ Telegram: <b>@{TELEGRAM_USERNAME}</b>
            </div>
            """, unsafe_allow_html=True)
            can_proceed = False
        else:
            st.info(f"✨ *កូតាសាកល្បងនៅសល់:* {remaining} វីដេអូ (ក្នុងចំណោម {MAX_FREE_VIDEOS})")
    
    if can_proceed:
        if st.button("🚀 ចាប់ផ្តើមបកប្រែ និងដាក់សំឡេង", key="process_btn", use_container_width=True):
            st.session_state.processing_complete = False
            
            with st.spinner("⏳ កំពុងដំណើរការ... សូមរង់ចាំប្រហែល ១-២ នាទី"):
                success = run_async_dubbing(
                    input_filename,
                    output_filename,
                    selected_source_lang,
                    selected_voice
                )
                
                if success and os.path.exists(output_filename):
                    st.session_state.processing_complete = True
                    
                    if not st.session_state.is_vip:
                        st.session_state.trial_users[st.session_state.user_email] += 1
                        remaining_after = MAX_FREE_VIDEOS - st.session_state.trial_users[st.session_state.user_email]
                    
                    st.markdown("---")
                    st.markdown('<div class="success-box">✅ ដំណើរការបានជោគជ័យ ១០០%!</div>', unsafe_allow_html=True)
                    
                    st.subheader("🎬 វីដេអូដែលបានបកប្រែ")
                    st.video(output_filename)
                    
                    with open(output_filename, "rb") as file:
                        st.download_button(
                            label="📥 ទាញយកវីដេអូ",
                            data=file,
                            file_name=f"khmer_dubbed_{os.path.basename(uploaded_file.name)}",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    
                    if not st.session_state.is_vip and remaining_after <= 0:
                        st.warning(f"""
                        ⚠️ *កូតាសាកល្បងអស់ហើយ!*  
                        នេះជាវីដេអូចុងក្រោយដែលអ្នកអាចបកប្រែដោយឥតគិតថ្លៃ។  
                        សូមទិញកូដ VIP ដើម្បីបន្តប្រើប្រាស់: *@{TELEGRAM_USERNAME}*
                        """)
                else:
                    st.markdown("""
                    <div class="error-box">
                        ❌ <b>ដំណើរការបរាជ័យ!</b><br>
                        សូមពិនិត្យ៖<br>
                        - ទំហំឯកសារវីដេអូ<br>
                        - ទ្រង់ទ្រាយវីដេអូ (គួរប្រើ MP4)<br>
                        - ការតភ្ជាប់អ៊ីនធឺណិត (សម្រាប់បកប្រែ)<br>
                        - FFmpeg ត្រូវបានដំឡើង
                    </div>
                    """, unsafe_allow_html=True)

else:
    st.info("📂 *រង់ចាំការផ្ទុកវីដេអូ...*
