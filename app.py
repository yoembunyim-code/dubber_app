import streamlit as st
import os
import tempfile
import subprocess
import shutil
from gtts import gTTS

# ==================== កំណត់ទំព័រ ====================
st.set_page_config(page_title="AI Dubbing Khmer PRO", page_icon="🎬", layout="centered")

# ==================== CSS Styling ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@700&display=swap');
    .main-title { font-family: 'Kanit', sans-serif; font-size: 38px; background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 17px; color: #a0a0a0; text-align: center; margin-bottom: 25px; }
    .stButton > button { width: 100%; border-radius: 12px; font-weight: bold; height: 50px; border: none; transition: all 0.3s ease; }
    .start-btn > button { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; font-size: 20px; height: 65px; }
    .folder-btn > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; height: 65px; }
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
if "selected_voice" not in st.session_state: st.session_state.selected_voice = "auto"
if "processing_result" not in st.session_state: st.session_state.processing_result = None # រក្សាទុកលទ្ធផលវីដេអូ

# ==================== មុខងារបង្កើតសំឡេង ====================
def generate_khmer_audio(text_to_speak):
    try:
        tts = gTTS(text=text_to_speak, lang='km')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"កំហុស TTS: {e}")
        return None

def process_video_dubbing(video_path, srt_path):
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            khmer_text = f.read()
            
        audio_file = generate_khmer_audio(khmer_text[:1500])
        if not audio_file: return None

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            try:
                import imageio_ffmpeg
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            except:
                st.error("⚠️ រក FFmpeg មិនឃើញ")
                return None
                
        output_video = os.path.join(tempfile.gettempdir(), "final_dubbed_video.mp4")
        cmd = [ffmpeg, "-i", video_path, "-i", audio_file, "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "-y", output_video]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return output_video if result.returncode == 0 else None
    except Exception as e:
        st.error(f"កំហុសដំណើរការ: {e}")
        return None

# ==================== Main UI ====================
st.markdown('<div class="main-title">🎬 Dubbing Khmer PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🚀 បកប្រែសំឡេងវីដេអូរបស់អ្នកទៅជាភាសាខ្មែរយ៉ាងរហ័ស!</div>', unsafe_allow_html=True)

# VIP Logic (ដោយមិនប្រើ st.rerun ញឹកញាប់)
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
    st.stop() # បញ្ឈប់ដំណើរការត្រង់នេះ

# Upload UI
uploaded_video = st.file_uploader("📁 BROWSE VIDEO", type=["mp4", "mov", "avi", "mkv"])
uploaded_srt = st.file_uploader("📄 BROWSE SRT", type=["srt"])

# ផ្ទាំងជ្រើសសំឡេង
st.markdown("### 🎤 ជ្រើសរើសសំឡេង")
cols = st.columns(4)
voice_options = ["AUTO", "SREY MOM", "PISETH", "DUB AS-IS"]
for i, v in enumerate(voice_options):
    if cols[i].button(v, use_container_width=True):
        st.session_state.selected_voice = v.lower().replace(" ", "_")
st.caption(f"👉 សំឡេងដែលបានជ្រើស៖ {st.session_state.selected_voice}")

# Start & Folder
col1, col2 = st.columns([3,1])
with col1:
    if st.button("🚀 START", use_container_width=True):
        if uploaded_video is None or uploaded_srt is None:
            st.warning("⚠️ សូមបង្ហោះទាំងវីដេអូ និង SRT ជាមុនសិន!")
        else:
            with st.spinner("⏳ កំពុងដំណើរការ... សូមរង់ចាំបន្តិច"):
                # រក្សាទុកឯកសារបណ្ដោះអាសន្ន
                v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                v_tmp.write(uploaded_video.getvalue())
                v_tmp.close()
                
                s_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".srt")
                s_tmp.write(uploaded_srt.getvalue())
                s_tmp.close()
                
                result = process_video_dubbing(v_tmp.name, s_tmp.name)
                
                if result:
                    if not st.session_state.is_vip:
                        st.session_state.trial_count += 1
                    # រក្សាទុកផ្លូវឯកសារលទ្ធផល (ជៀសវាង Rerun)
                    st.session_state.processing_result = result
                else:
                    st.error("❌ មានបញ្ហាពេលកែច្នៃវីដេអូ")

with col2:
    if st.button("📂 FOLDER", use_container_width=True):
        if st.session_state.processing_result and os.path.exists(st.session_state.processing_result):
            folder = os.path.dirname(st.session_state.processing_result)
            try:
                if os.name == 'nt': os.startfile(folder)
                else: subprocess.run(['xdg-open', folder])
            except: pass

# បង្ហាញលទ្ធផលពី Session State
if st.session_state.processing_result and os.path.exists(st.session_state.processing_result):
    st.markdown("---")
    st.subheader("📥 លទ្ធផលវីដេអូ")
    with open(st.session_state.processing_result, "rb") as f:
        st.download_button(label="⬇️ ទាញយកវីដេអូ", data=f, file_name="dubbed_video.mp4", mime="video/mp4", use_container_width=True)
    st.video(st.session_state.processing_result)

st.markdown("---")
st.caption(f"🤝 Telegram: [@{TELEGRAM_USERNAME}]({TELEGRAM_LINK})")
