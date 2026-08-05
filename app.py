import streamlit as st
import os
import tempfile
import subprocess
import shutil
from deep_translator import GoogleTranslator
from gtts import gTTS

# ==================== កំណត់ទំព័រ ====================
st.set_page_config(page_title="AI Dubbing Khmer PRO", page_icon="🎬", layout="centered")

# ==================== CSS Styling ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@700&display=swap');
    .main-title { font-family: 'Kanit', sans-serif; font-size: 38px; background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-shadow: 0 2px 10px rgba(255, 65, 108, 0.2); }
    .sub-title { font-size: 17px; color: #a0a0a0; text-align: center; margin-bottom: 25px; letter-spacing: 0.5px; }
    .stButton > button { width: 100%; border-radius: 12px; font-weight: bold; height: 50px; border: none; transition: all 0.3s ease; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
    .start-btn > button { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; font-size: 22px; height: 65px; box-shadow: 0 6px 15px rgba(56, 239, 125, 0.4); }
    .start-btn > button:hover { background: linear-gradient(135deg, #0d887e 0%, #2ce06b 100%); box-shadow: 0 8px 20px rgba(56, 239, 125, 0.6); }
    .folder-btn > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; height: 65px; }
    .vip-box { background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); padding: 10px; border-radius: 12px; text-align: center; color: #222; font-weight: bold; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab-list"] button { font-weight: bold; font-size: 14px; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { background-color: #FF4B4B; color: white; }
</style>
""", unsafe_allow_html=True)

# ==================== Config & Secrets ====================
TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"
try:
    VALID_KEYS = st.secrets.get("VALID_KEYS", {"BUNYIM-VIP-001": "សកម្ម", "KHMER-VIP-002": "សកម្ម", "VIP-2026-TEST": "សកម្ម" })
except Exception:
    VALID_KEYS = {"BUNYIM-VIP-001": "សកម្ម", "KHMER-VIP-002": "សកម្ម", "VIP-2026-TEST": "សកម្ម"}

# ==================== Session State ====================
if "is_vip" not in st.session_state: st.session_state.is_vip = False
if "trial_count" not in st.session_state: st.session_state.trial_count = 0
if "selected_voice" not in st.session_state: st.session_state.selected_voice = "auto"
if "processing_complete" not in st.session_state: st.session_state.processing_complete = False
if "last_video_result" not in st.session_state: st.session_state.last_video_result = None

# ==================== FFmpeg Helper ====================
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
                if os.path.exists(possible_ffprobe): ffprobe_path = possible_ffprobe
                elif os.path.exists(possible_ffprobe + ".exe"): ffprobe_path = possible_ffprobe + ".exe"
                if ffmpeg_dir not in os.environ["PATH"]: os.environ["PATH"] += os.pathsep + ffmpeg_dir
        except Exception as e: pass
    return ffmpeg_path, ffprobe_path

# ==================== មុខងារបង្កើតសំឡេងខ្មែរ ====================
def generate_khmer_audio(text_to_speak):
    try:
        tts = gTTS(text=text_to_speak, lang='km')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
    except Exception as e:
        st.error(f"កំហុស TTS: {e}")
        return None

# ==================== មុខងារកែច្នៃវីដេអូ ====================
def process_video_dubbing(video_path, srt_path, voice_style):
    try:
        # ១. អានអត្ថបទពី SRT 
        with open(srt_path, 'r', encoding='utf-8') as f:
            khmer_text = f.read()
            
        # ២. បង្កើតសំឡេងខ្មែរ
        audio_file = generate_khmer_audio(khmer_text[:1000]) 
        if not audio_file: return None

        # ៣. ផ្សំជាមួយវីដេអូ
        ffmpeg, _ = get_ffmpeg_paths()
        output_video = os.path.join(tempfile.gettempdir(), "final_dubbed_video.mp4")
        cmd = [ffmpeg, "-i", video_path, "-i", audio_file, "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "-y", output_video]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0: return None
        return output_video
    except Exception as e: return None

# ==================== MAIN UI FLOW ====================
st.markdown('<div class="main-title">🎬 Dubbing Khmer PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🚀 បកប្រែសំឡេងវីដេអូរបស់អ្នកទៅជាភាសាខ្មែរយ៉ាងរហ័ស!</div>', unsafe_allow_html=True)

# --- VIP & Trial ---
if st.session_state.is_vip: st.success("👑 *គណនី VIP កំពុងដំណើរការ!*")
else:
    remaining = max(0, 3 - st.session_state.trial_count)
    st.warning(f"📊 អ្នកនៅសល់ *{remaining}* លើកសាកល្បង។") if remaining > 0 else st.error("⛔ អស់កូតាហើយ!")

with st.expander("🔑 បញ្ចូលកូដ VIP", expanded=(not st.session_state.is_vip)):
    st.markdown(f'<div class="vip-box">💎 ទិញកូដ VIP តាម Telegram៖ <a href="{TELEGRAM_LINK}" target="_blank" style="color:#000; text-decoration:underline;">@{TELEGRAM_USERNAME}</a></div>', unsafe_allow_html=True)
    vip_input = st.text_input("បញ្ចូលលេខកូដ VIP", type="password")
    if st.button("🛡️ ផ្ទៀងផ្ទាត់", use_container_width=True):
        if vip_input.strip() in VALID_KEYS:
            st.session_state.is_vip = True; st.session_state.trial_count = 0
            st.success("✅ ជោគជ័យ!"); st.rerun()
        else: st.error("❌ កូដមិនត្រឹមត្រូវ")

if st.session_state.is_vip or st.session_state.trial_count < 3:
    tab1, tab2, tab3 = st.tabs(["📁 បង្ហោះឯកសារ", "🎤 ជ្រើសសំឡេង", "🚀 ចាប់ផ្ដើម"])
    
    with tab1:
        st.subheader("📂 ជ្រើសរើសឯកសារ")
        uploaded_video = st.file_uploader("BROWSE VIDEO (MP4, MOV, AVI)", type=["mp4", "mov", "avi", "mkv"])
        uploaded_srt = st.file_uploader("BROWSE SRT (ឯកសារអក្សររត់)", type=["srt"])
        
        if uploaded_video: st.success("✅ បានបង្ហោះវីដេអូ!")
        if uploaded_srt: st.success("✅ បានបង្ហោះ SRT!")

    with tab2:
        st.subheader("🎤 ជ្រើសរើសគំរូសំឡេង")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 AUTO", key="auto", use_container_width=True): st.session_state.selected_voice = "auto"
            if st.button("👩 SREY MOM", key="srey", use_container_width=True): st.session_state.selected_voice = "srey_mom"
        with col2:
            if st.button("👨 PISETH", key="piseth", use_container_width=True): st.session_state.selected_voice = "piseth"
            if st.button("📢 DUB AS-IS", key="asis", use_container_width=True): st.session_state.selected_voice = "as_is"

    with tab3:
        st.markdown("---")
        col_start, col_folder = st.columns([3, 1])
        with col_start:
            st.markdown('<div class="start-btn">', unsafe_allow_html=True)
            if st.button("🚀 START បង្កើតវីដេអូ", key="start_btn", use_container_width=True):
                if uploaded_video is None:
                    st.warning("⚠️ សូមត្រឡប់ទៅផ្ទាំង 'Upload' ហើយបង្ហោះវីដេអូជាមុនសិន!")
                elif uploaded_srt is None:
                    st.warning("⚠️ សូមត្រឡប់ទៅផ្ទាំង 'Upload' ហើយបង្ហោះឯកសារ SRT ជាមុនសិន!")
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as v_tmp:
                        v_tmp.write(uploaded_video.getvalue())
                        video_path = v_tmp.name
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as s_tmp:
                        s_tmp.write(uploaded_srt.getvalue())
                        srt_path = s_tmp.name
                    
                    with st.spinner("⏳ កំពុងបង្កើតសំឡេងខ្មែរ និងផ្សំជាមួយវីដេអូ..."):
                        result = process_video_dubbing(video_path, srt_path, st.session_state.selected_voice)
                    
                    if result:
                        if not st.session_state.is_vip: st.session_state.trial_count += 1
                        st.session_state.last_video_result = result
                        st.session_state.processing_complete = True
                        st.success("🎉 បង្កើតវីដេអូជោគជ័យ!"); st.rerun()
                    else: st.error("❌ មានបញ្ហាពេលកែច្នៃវីដេអូ")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_folder:
            st.markdown('<div class="folder-btn">', unsafe_allow_html=True)
            if st.button("📂 FOLDER", key="folder_btn", use_container_width=True):
                if st.session_state.last_video_result and os.path.exists(st.session_state.last_video_result):
                    folder = os.path.dirname(st.session_state.last_video_result)
                    try:
                        if os.name == 'nt': os.startfile(folder)
                        else: subprocess.run(['open', folder] if os.name == 'posix' else ['xdg-open', folder])
                    except: pass
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.processing_complete and st.session_state.last_video_result:
        st.markdown("---")
        st.subheader("📥 ទាញយកវីដេអូលទ្ធផល")
        with open(st.session_state.last_video_result, "rb") as f:
            st.download_button(label="⬇️ ទាញយកវីដេអូ MP4", data=f, file_name="dubbed_video.mp4", mime="video/mp4", use_container_width=True)
        st.video(st.session_state.last_video_result)

st.markdown("---")
st.caption(f"🤝 Telegram: [@{TELEGRAM_USERNAME}]({TELEGRAM_LINK}) | Made with ❤️")
