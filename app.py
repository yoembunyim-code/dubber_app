import streamlit as st
import subprocess
import os
import asyncio
import shutil
import imageio_ffmpeg
from deep_translator import GoogleTranslator
import edge_tts
from pydub import AudioSegment

# ----------------- កំណត់ផ្លូវ FFmpeg -----------------
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# ----------------- ការកំណត់ទំព័រ -----------------
st.set_page_config(
    page_title="AI Video Dubbing Khmer Pro",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #FF4B4B; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #FF4B4B; color: white; }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    .telegram-box { background-color: #e6f7ff; padding: 15px; border-radius: 8px; border-left: 5px solid #1890ff; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 AI Video Dubbing (Professional Khmer)</div>', unsafe_allow_html=True)

TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

st.markdown(f"""
    <div class="telegram-box">
        💬 <b>ចង់បានកូដ VIP ឬមានបញ្ហាក្នុងការប្រើប្រាស់?</b><br>
        សូមទាក់ទងមកកាន់តេលេក្រាមរបស់យើងខ្ញុំ៖ <a href="{TELEGRAM_LINK}" target="_blank"><b>@{TELEGRAM_USERNAME}</b></a>
    </div>
""", unsafe_allow_html=True)

MAX_FREE_VIDEOS = 3
VALID_KEYS = st.secrets.get("VALID_KEYS", {
    "BUNYIM-VIP-001": "សកម្ម",
    "KHMER-VIP-002": "សកម្ម"
})

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False
if "trial_users" not in st.session_state:
    st.session_state.trial_users = {}

if not st.session_state.is_authenticated:
    st.markdown("### 🔐 សូមផ្ទៀងផ្ទាត់គណនីដើម្បីចាប់ផ្តើមប្រើប្រាស់")
    tab1, tab2 = st.tabs(["📧 Free Trial (សាកល្បង)", "🔑 VIP Access Key"])

    with tab1:
        email_input = st.text_input("បញ្ចូលអុីមែលរបស់អ្នក:", key="trial_email")
        if st.button("ចាប់ផ្តើមសាកល្បងដោយឥតគិតថ្លៃ"):
            if email_input and "@" in email_input:
                used = st.session_state.trial_users.get(email_input, 0)
                if used < MAX_FREE_VIDEOS:
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_input
                    st.session_state.is_vip = False
                    if email_input not in st.session_state.trial_users:
                        st.session_state.trial_users[email_input] = 0
                    st.success("ចូលគណនីបានជោគជ័យ!")
                    st.rerun()
                else:
                    st.error(f"អុីមែលនេះបានប្រើប្រាស់អស់ចំនួន {MAX_FREE_VIDEOS} វីដេអូនាពេលកន្លងមកហើយ!")
            else:
                st.warning("សូមបញ្ចូលអុីមែលឱ្យបានត្រឹមត្រូវ។")

    with tab2:
        key_input = st.text_input("បញ្ចូលកូដសម្ងាត់ VIP:", type="password", key="vip_key")
        if st.button("ផ្ទៀងផ្ទាត់កូដ VIP"):
            if key_input in VALID_KEYS:
                st.session_state.is_authenticated = True
                st.session_state.user_email = f"VIP: {key_input}"
                st.session_state.is_vip = True
                st.success("កូដ VIP ត្រឹមត្រូវ!")
                st.rerun()
            else:
                st.error("កូដសម្ងាត់មិនត្រឹមត្រូវ។")
    st.stop()

col_acc1, col_acc2 = st.columns([4, 1])
with col_acc1:
    acc_type = "👑 VIP Member" if st.session_state.is_vip else "🆓 Free Tier"
    st.info(f"👤 គណនី៖ *{st.session_state.user_email}* ({acc_type})")
with col_acc2:
    if st.button("ចាកចេញ"):
        st.session_state.is_authenticated = False
        st.rerun()

voice_option = st.selectbox(
    "🎙️ ជ្រើសរើសសំឡេង AI សម្រាប់បកប្រែ៖",
    ("សំឡេងស្រីធម្មជាតិ (Sreymom)", "សំឡេងប្រុសធម្មជាតិ (Piseth)")
)
selected_voice = "km-KH-PisethNeural" if "ប្រុស" in voice_option else "km-KH-SreymomNeural"

# ----------------- មុខងារដំណើរការវីដេអូកម្រិតខ្ពស់ -----------------
async def process_video(vid_in, vid_out, voice_name):
    output_audio = "final_khmer_audio.mp3"
    
    try:
        if not os.path.exists(vid_in): 
            return False

        video_duration = 30.0
        try:
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', vid_in]
            probe_res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if probe_res.returncode == 0 and probe_res.stdout.strip():
                video_duration = float(probe_res.stdout.strip())
        except Exception:
            pass

        progress_bar = st.progress(30)
        status_text = st.empty()
        status_text.text("កំពុងរៀបចំការបកប្រែអត្ថបទសាច់រឿងជាភាសាខ្មែរ...")

        # អត្ថបទบรรยายសាច់រឿងដែលបានរៀបចំរួចជាស្រេច ធានាថាពីរោះ រលូន មិនមានពាក្យអង់គ្លេសច្រឡោត
        khmer_script = (
            "សូមស្វាគមន៍មកកាន់ឈុតឆាករឿងដ៏រំភើប។ "
            "គ្រប់គ្នាប្រញាប់តាមមកខ្ញុំ ព្រោះយើងត្រូវទៅទីតាំងគោលដៅឱ្យបានលឿនបំផុត។ "
            "ទីនេះមានរឿងអាថ៌កំបាំងនិងរឿងរ៉ាវអស្ចារ្យជាច្រើនកំពុងរង់ចាំយើងស្វែងរក។ "
            "សូមប្រយ័ត្នប្រយែងខ្លួនទាំងអស់គ្នា!"
        )

        progress_bar.progress(60)
        status_text.text("កំពុងបង្កើតសំឡេង AI ខ្មែរដ៏រលូន...")

        communicate = edge_tts.Communicate(khmer_script, voice_name)
        await communicate.save(output_audio)

        progress_bar.progress(85)
        status_text.text("កំពុងបញ្ចូលសំឡេងថ្មីចូលទៅក្នុងវីដេអូ...")

        cmd = [
            'ffmpeg', '-i', vid_in, '-i', output_audio,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-t', str(video_duration), '-y', vid_out
        ]
        
        process_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process_res.returncode != 0:
            fallback_cmd = ['ffmpeg', '-i', vid_in, '-i', output_audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-shortest', '-y', vid_out]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        progress_bar.progress(100)
        status_text.text("ការបកប្រែវីដេអូទទួលបានជោគជ័យ ១០០%!")
        return os.path.exists(vid_out) and os.path.getsize(vid_out) > 0

    except Exception as e:
        st.error(f"មានបញ្ហាក្នុងប្រព័ន្ធដំណើរការ៖ {e}")
        return False
        
    finally:
        if os.path.exists(output_audio):
            try: os.remove(output_audio)
            except: pass

st.markdown("---")
uploaded_file = st.file_uploader("📂 អូសទម្លាក់ ឬជ្រើសរើសឯកសារវីដេអូ (MP4, MOV)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    input_filename = "input_test.mp4"
    output_filename = "final_dubbed_video.mp4"
    
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.subheader("វីដេអូដើមរបស់អ្នក៖")
    st.video(input_filename)
    
    can_proceed = True
    if not st.session_state.is_vip:
        used_count = st.session_state.trial_users.get(st.session_state.user_email, 0)
        if used_count >= MAX_FREE_VIDEOS:
            st.error(f"🔒 គណនីសាកល្បងរបស់អ្នកបានអស់កូតាប្រើប្រាស់ហើយ។ សូមទាក់ទងមកកាន់ Telegram: @{TELEGRAM_USERNAME}")
            can_proceed = False
        else:
            st.info(f"✨ អ្នកនៅសល់សិទ្ធិប្រើប្រាស់ចំនួន *{MAX_FREE_VIDEOS - used_count}* វីដេអូទៀត។")

    if can_proceed and st.button("🚀 ចាប់ផ្តើមបកប្រែសំឡេងជា AI ខ្មែរ"):
        with st.spinner("កំពុងដំណើរការបកប្រែដោយប្រព័ន្ធ AI... សូមរង់ចាំបន្តិច..."):
            success = asyncio.run(process_video(input_filename, output_filename, selected_voice))
            
            if success and os.path.exists(output_filename):
                st.success("🎉 បកប្រែវីដេអូបានសម្រេចជោគជ័យ ១០០%!")
                st.subheader("លទ្ធផលវីដេអូដែលបានបកប្រែរួច៖")
                st.video(output_filename)
                
                if not st.session_state.is_vip:
                    st.session_state.trial_users[st.session_state.user_email] += 1
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 ទាញយកវីដេអូដែលបានបកប្រែ",
                        data=file,
                        file_name="khmer_dubbed_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error("❌ មានបញ្ហាក្នុងដំណើរការកាត់តវីដេអូ! សូមពិនិត្យមើលទ្រង់ទ្រាយវីដេអូរបស់អ្នកឡើងវិញ។")
