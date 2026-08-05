import streamlit as st
import os
import tempfile
import subprocess
import shutil
import re
from gtts import gTTS

# ==================== កំណត់ទំព័រ ====================
st.set_page_config(page_title="AI Dubbing Khmer PRO", page_icon="🎬", layout="centered")

# ==================== CSS Styling ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@700&display=swap');
    .main-title {
        font-family: 'Kanit', sans-serif;
        font-size: 42px;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: 1px;
    }
    .sub-title {
        font-size: 18px;
        color: #b0b0b0;
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 1px solid #333;
        padding-bottom: 15px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        height: 50px;
        border: none;
        transition: all 0.3s ease;
        font-size: 16px;
    }
    .start-btn > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        font-size: 22px;
        height: 65px;
        box-shadow: 0 6px 20px rgba(56, 239, 125, 0.3);
    }
    .start-btn > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(56, 239, 125, 0.5);
    }
    .folder-btn > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        height: 65px;
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.3);
    }
    .folder-btn > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(118, 75, 162, 0.5);
    }
    .voice-selector {
        background: #1e1e2f;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid #333;
    }
    .stSlider > div > div > div {
        background: #667eea;
    }
    .result-box {
        background: #1a1a2e;
        padding: 20px;
        border-radius: 20px;
        margin-top: 25px;
        border-left: 6px solid #38ef7d;
    }
    .footer {
        margin-top: 40px;
        text-align: center;
        color: #888;
        font-size: 14px;
        border-top: 1px solid #2a2a3e;
        padding-top: 20px;
    }
    .footer a {
        color: #667eea;
        text-decoration: none;
        font-weight: bold;
    }
    .footer a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Config & Secrets ====================
TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

try:
    VALID_KEYS = st.secrets.get("VALID_KEYS", {"BUNYIM-VIP-001": "សកម្ម", "KHMER-VIP-002": "សកម្ម", "VIP-2026-TEST": "សកម្ម"})
except:
    VALID_KEYS = {"BUNYIM-VIP-001": "សកម្ម", "KHMER-VIP-002": "សកម្ម", "VIP-2026-TEST": "សកម្ម"}

# ==================== Session State ====================
if "is_vip" not in st.session_state: st.session_state.is_vip = False
if "trial_count" not in st.session_state: st.session_state.trial_count = 0
if "selected_voice" not in st.session_state: st.session_state.selected_voice = "female"
if "processing_result" not in st.session_state: st.session_state.processing_result = None

# ==================== មុខងារបង្កើតសំឡេងដោយប្រើ FFmpeg (មិនប្រើ pydub) ====================
def generate_khmer_audio_with_pauses(text, speed=1.0, pitch=1.0, voice="female"):
    """
    បង្កើត audio ពីអត្ថបទ ដោយប្រើ gTTS + ffmpeg concat ដើម្បីបន្ថែមការផ្អាក
    """
    try:
        # ពិនិត្យមើល ffmpeg
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            try:
                import imageio_ffmpeg
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            except:
                st.error("⚠️ រក FFmpeg មិនឃើញ សូមដំឡើង FFmpeg")
                return None

        # បំបែកអត្ថបទតាមសញ្ញាផ្អាក
        sentences = re.split(r'(?<=[។.!?;:,\n])', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            st.warning("គ្មានអត្ថបទដើម្បីបង្កើតសំឡេង")
            return None

        # បង្កើតឯកសារ audio សម្រាប់ប្រយោគនីមួយៗ
        audio_files = []
        temp_dir = tempfile.mkdtemp()

        for idx, sent in enumerate(sentences):
            # បង្កើត MP3 ដោយ gTTS
            tts = gTTS(text=sent, lang='km', slow=False)
            mp3_path = os.path.join(temp_dir, f"part_{idx:03d}.mp3")
            tts.save(mp3_path)
            audio_files.append(mp3_path)

        # បង្កើតឯកសារ list.txt សម្រាប់ ffmpeg concat
        list_path = os.path.join(temp_dir, "list.txt")
        with open(list_path, "w", encoding="utf-8") as f:
            for i, mp3 in enumerate(audio_files):
                f.write(f"file '{mp3}'\n")
                # បន្ថែម silence រវាងប្រយោគ (លើកលែងប្រយោគចុងក្រោយ)
                if i < len(audio_files) - 1:
                    # ពិនិត្យថាតើប្រយោគបញ្ចប់ដោយសញ្ញាណាមួយ
                    last_char = sentences[i][-1] if sentences[i] else ''
                    if last_char in '។.!?':
                        pause_ms = 700   # ផ្អាកយូរ
                    elif last_char in ';:,':
                        pause_ms = 400   # ផ្អាកមធ្យម
                    else:
                        pause_ms = 250   # ផ្អាកខ្លី
                    # បង្កើត silence ដោយ ffmpeg
                    silence_file = os.path.join(temp_dir, f"silence_{i:03d}.mp3")
                    subprocess.run([
                        ffmpeg, "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                        "-t", f"{pause_ms/1000:.3f}", "-q:a", "9", "-y", silence_file
                    ], capture_output=True, check=True)
                    f.write(f"file '{silence_file}'\n")

        # បញ្ចូលគ្នាទាំងអស់ជា audio តែមួយ
        output_audio = os.path.join(temp_dir, "combined.mp3")
        subprocess.run([
            ffmpeg, "-f", "concat", "-safe", "0", "-i", list_path,
            "-c", "copy", "-y", output_audio
        ], capture_output=True, check=True)

        # ប្រសិនបើមានការកែប្រែ speed/pitch យើងអាចធ្វើបានដោយ ffmpeg filter
        if speed != 1.0 or pitch != 1.0:
            final_audio = os.path.join(temp_dir, "final.mp3")
            filter_str = ""
            if speed != 1.0:
                filter_str += f"atempo={speed}"
            if pitch != 1.0:
                # pitch អាចធ្វើបានដោយ asetrate + aresample
                if filter_str:
                    filter_str += ","
                filter_str += f"asetrate=44100*{pitch},aresample=44100"
            cmd = [
                ffmpeg, "-i", output_audio,
                "-filter:a", filter_str,
                "-y", final_audio
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            output_audio = final_audio

        return output_audio

    except Exception as e:
        st.error(f"កំហុសក្នុងការបង្កើតសំឡេង៖ {e}")
        return None

# ==================== មុខងារដំណើរការវីដេអូ ====================
def process_video_with_audio(video_path, audio_path):
    try:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            try:
                import imageio_ffmpeg
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            except:
                st.error("⚠️ រក FFmpeg មិនឃើញ សូមដំឡើង FFmpeg")
                return None

        output_video = os.path.join(tempfile.gettempdir(), "final_dubbed_video.mp4")
        cmd = [
            ffmpeg, "-i", video_path, "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y",
            output_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return output_video
        else:
            st.error(f"FFmpeg error: {result.stderr}")
            return None
    except Exception as e:
        st.error(f"កំហុសដំណើរការ៖ {e}")
        return None

# ==================== Main UI ====================
st.markdown('<div class="main-title">🎬 Dubbing Khmer PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🚀 បកប្រែសំឡេងវីដេអូរបស់អ្នកទៅជាភាសាខ្មែរយ៉ាងរហ័ស!</div>', unsafe_allow_html=True)

# VIP Logic
if not st.session_state.is_vip and st.session_state.trial_count >= 3:
    st.error("⛔ អស់កូតាសាកល្បងហើយ! សូមបញ្ចូលកូដ VIP ខាងក្រោម។")
    with st.expander("🔑 បញ្ចូលកូដ VIP"):
        vip_in = st.text_input("លេខកូដ", type="password")
        if st.button("ផ្ទៀងផ្ទាត់"):
            if vip_in.strip() in VALID_KEYS:
                st.session_state.is_vip = True
                st.session_state.trial_count = 0
                st.success("✅ ជោគជ័យ! សូមចុច F5 ដើម្បីចាប់ផ្ដើមឡើងវិញ")
            else:
                st.error("❌ កូដមិនត្រឹមត្រូវ")
    st.stop()

# ==================== Upload & Text Input ====================
col1, col2 = st.columns(2)
with col1:
    uploaded_video = st.file_uploader("📁 ផ្ទុកវីដេអូ", type=["mp4", "mov", "avi", "mkv"])
with col2:
    uploaded_srt = st.file_uploader("📄 ផ្ទុក SRT (ស្រេចចិត្ត)", type=["srt"])

# បញ្ចូលអត្ថបទដោយផ្ទាល់
st.markdown("### ✍️ អត្ថបទដែលចង់ឲ្យនិយាយ")
text_input = st.text_area(
    "បញ្ចូលអត្ថបទជាភាសាខ្មែរ (ប្រសិនបើមាន SRT អត្ថបទនឹងយកពី SRT)",
    height=150,
    placeholder="ឧទាហរណ៍៖ សួស្តីបងប្អូនទាំងអស់គ្នា! ថ្ងៃនេះយើងនឹងនិយាយអំពី...",
    key="text_input"
)

# ==================== Voice & Speed Controls ====================
st.markdown("### 🎛️ ការកំណត់សំឡេង")
with st.container():
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        voice_option = st.selectbox(
            "🗣️ សម្លេង",
            ["ស្រី (Female)", "ប្រុស (Male)"],
            index=0,
            key="voice_select"
        )
        st.session_state.selected_voice = "female" if "ស្រី" in voice_option else "male"

    with col_b:
        speed_value = st.slider(
            "⏱️ ល្បឿន",
            min_value=0.5, max_value=2.0, value=1.0, step=0.1,
            help="ល្បឿននិយាយ (1.0 = ធម្មតា)"
        )

    with col_c:
        pitch_value = st.slider(
            "🎵 កម្រិតសំឡេង",
            min_value=0.5, max_value=1.5, value=1.0, step=0.05,
            help="កម្រិតសំឡេងខ្ពស់/ទាប (1.0 = ធម្មតា)"
        )

# ==================== Start & Folder Buttons ====================
col_start, col_folder = st.columns([3, 1])
with col_start:
    start_btn = st.button("🚀 START", use_container_width=True, key="start_btn")
with col_folder:
    folder_btn = st.button("📂 Open Folder", use_container_width=True, key="folder_btn")

# ==================== ដំណើរការចម្បង ====================
if start_btn:
    # ពិនិត្យថាមានវីដេអូ និងអត្ថបទ
    if uploaded_video is None:
        st.error("សូមផ្ទុកវីដេអូជាមុនសិន!")
        st.stop()

    # យកអត្ថបទពី SRT បើមាន បើមិនមានយកពី Text Area
    text_to_speak = ""
    if uploaded_srt is not None:
        try:
            srt_content = uploaded_srt.read().decode("utf-8")
            # ដកស្រង់អត្ថបទចេញពី SRT (យកតែអត្ថបទ មិនយកលេខ និងពេលវេលា)
            lines = srt_content.splitlines()
            text_lines = []
            for line in lines:
                if not re.match(r'^\d+$', line) and not re.match(r'^\d{2}:\d{2}:\d{2},\d{3}', line) and line.strip():
                    text_lines.append(line.strip())
            text_to_speak = " ".join(text_lines)
        except:
            st.warning("មិនអាចអាន SRT បាន សូមបញ្ចូលអត្ថបទដោយផ្ទាល់")
            text_to_speak = text_input
    else:
        text_to_speak = text_input

    if not text_to_speak.strip():
        st.error("សូមបញ្ចូលអត្ថបទ ឬផ្ទុកឯកសារ SRT!")
        st.stop()

    # បង្កើតសំឡេង
    with st.spinner("⏳ កំពុងបង្កើតសំឡេងខ្មែរ..."):
        audio_file = generate_khmer_audio_with_pauses(
            text=text_to_speak,
            speed=speed_value,
            pitch=pitch_value,
            voice=st.session_state.selected_voice
        )

    if not audio_file or not os.path.exists(audio_file):
        st.error("បង្កើតសំឡេងមិនបាន សូមពិនិត្យអត្ថបទ")
        st.stop()

    # រក្សាទុកវីដេអូបណ្ដោះអាសន្ន
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        tmp_video.write(uploaded_video.read())
        video_path = tmp_video.name

    # ដំណើរការ dubbing
    with st.spinner("🎞️ កំពុងបញ្ចូលសំឡេងទៅក្នុងវីដេអូ..."):
        output_video = process_video_with_audio(video_path, audio_file)

    if output_video and os.path.exists(output_video):
        st.session_state.processing_result = output_video
        st.session_state.trial_count += 1
        st.success("✅ ដំណើរការរួចរាល់!")
    else:
        st.error("❌ មានបញ្ហាក្នុងការដំណើរការវីដេអូ")

# ==================== បង្ហាញលទ្ធផល ====================
if st.session_state.processing_result:
    result_path = st.session_state.processing_result
    if os.path.exists(result_path):
        st.markdown("---")
        st.markdown("### 🎥 វីដេអូលទ្ធផល")

        with open(result_path, "rb") as f:
            video_bytes = f.read()

        st.video(video_bytes)

        st.download_button(
            label="📥 ទាញយកវីដេអូ",
            data=video_bytes,
            file_name="dubbed_video.mp4",
            mime="video/mp4",
            use_container_width=True
        )

        if st.button("🗑️ សម្អាតលទ្ធផល"):
            try:
                os.remove(result_path)
                st.session_state.processing_result = None
                st.rerun()
            except:
                pass

# ==================== Footer ====================
st.markdown(f"""
<div class="footer">
    📌 សម្រាប់ជំនួយ ឬសំណួរ សូមទាក់ទងមកកាន់ <a href="{TELEGRAM_LINK}" target="_blank">@{TELEGRAM_USERNAME}</a><br>
    © 2026 AI Dubbing Khmer PRO — រក្សាសិទ្ធិគ្រប់យ៉ាង
</div>
""", unsafe_allow_html=True)
