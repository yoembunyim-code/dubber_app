import streamlit as st
import subprocess
import os
import asyncio
import imageio_ffmpeg
import edge_tts

# ----------------- កំណត់ផ្លូវ FFmpeg ស្វ័យប្រវត្តិ -----------------
try:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
except Exception:
    pass

# ----------------- ការកំណត់ទំព័រ និងរចនាប័ទ្ម UI -----------------
st.set_page_config(
    page_title="AI Auto Video Dubbing Khmer Pro",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
    <style>
    .main-title { font-size: 30px; font-weight: 800; color: #FF4B4B; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 15px; color: #666666; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background: linear-gradient(135deg, #FF4B4B 0%, #FF2222 100%); color: white; padding: 10px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button:hover { background: linear-gradient(135deg, #ff3333, #e00000); color: white; }
    .notice-box { background: linear-gradient(135deg, #fffbe6 0%, #fff1b8 100%); padding: 15px; border-radius: 12px; border-left: 6px solid #faad14; margin-bottom: 20px; color: #d46b08; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 AI Auto Video Dubbing & Translation (Khmer)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ប្រព័ន្ធបកប្រែសំឡេងវីដេអូជាភាសាខ្មែរ (និយាយខ្មែរ១០០% មិនប្តូរទៅអង់គ្លេស)</div>', unsafe_allow_html=True)

TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

st.markdown(f"""
    <div class="notice-box">
        🎁 <b>គោលការណ៍ប្រើប្រាស់ប្រព័ន្ធ៖</b><br>
        - អ្នកអាចសាកល្បងបកប្រែវីដេអូដោយឥតគិតថ្លៃបានចំនួន <b>៣ វីដេអូដំបូង</b> ប៉ុណ្ណោះតាមរយៈ Free Trial。<br>
        - បន្ទាប់ពីអស់កូតា ៣ វីដេអូនេះ អ្នកត្រូវ<b>ទិញកូដ VIP Access Key</b> ដើម្បីបន្តប្រើប្រាស់ជានិច្ច。<br>
        💬 ទិញកូដ VIP តាមរយៈ Telegram: <a href="{TELEGRAM_LINK}" target="_blank"><b>@{TELEGRAM_USERNAME}</b></a>
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

# ----------------- ប្រព័ន្ធផ្ទៀងផ្ទាត់គណនី -----------------
if not st.session_state.is_authenticated:
    st.markdown("### 🔐 សូមផ្ទៀងផ្ទាត់គណនីដើម្បីចាប់ផ្តើមប្រើប្រាស់")
    tab1, tab2 = st.tabs(["📧 Free Trial (សាកល្បង ៣ វីដេអូ)", "🔑 VIP Access Key (ទិញកូដ)"])

    with tab1:
        email_input = st.text_input("បញ្ចូលអុីមែលរបស់អ្នកដើម្បីចាប់ផ្តើមសាកល្បង ៣ វីដេអូ:", key="trial_email")
        if st.button("ចាប់ផ្តើមសាកល្បងដោយឥតគិតថ្លៃ"):
            if email_input and "@" in email_input:
                used = st.session_state.trial_users.get(email_input, 0)
                if used < MAX_FREE_VIDEOS:
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_input
                    st.session_state.is_vip = False
                    if email_input not in st.session_state.trial_users:
                        st.session_state.trial_users[email_input] = 0
                    st.success("ចូលគណនីសាកល្បងបានជោគជ័យ!")
                    st.rerun()
                else:
                    st.error(f"អុីមែលនេះបានប្រើប្រាស់កូតាសាកល្បងអស់ចំនួន {MAX_FREE_VIDEOS} វីដេអូរួចហើយ! សូមទិញកូដ VIP តាមរយៈ Telegram: @{TELEGRAM_USERNAME}")
            else:
                st.warning("សូមបញ្ចូលអុីមែលឱ្យបានត្រឹមត្រូវ។")

    with tab2:
        key_input = st.text_input("បញ្ចូលកូដសម្ងាត់ VIP ដែលបានទិញ:", type="password", key="vip_key")
        if st.button("ផ្ទៀងផ្ទាត់កូដ VIP"):
            if key_input in VALID_KEYS:
                st.session_state.is_authenticated = True
                st.session_state.user_email = f"VIP: {key_input}"
                st.session_state.is_vip = True
                st.success("កូដ VIP ត្រឹមត្រូវ! ស្វាគមន៍មកកាន់សមាជិកភាព VIP ។")
                st.rerun()
            else:
                st.error(f"កូដសម្ងាត់មិនត្រឹមត្រូវទេ។ ចង់ទិញកូដ សូមទាក់ទង Telegram: @{TELEGRAM_USERNAME}")
    st.stop()

col_acc1, col_acc2 = st.columns([4, 1])
with col_acc1:
    acc_type = "👑 VIP Member (ប្រើប្រាស់អត់ដែនកំណត់)" if st.session_state.is_vip else "🆓 Free Tier (សាកល្បង)"
    st.info(f"👤 គណនី៖ *{st.session_state.user_email}* ({acc_type})")
with col_acc2:
    if st.button("ចាកចេញ"):
        st.session_state.is_authenticated = False
        st.rerun()

# ----------------- ការកំណត់ភាសា និងសំឡេង AI -----------------
col_voice = st.columns(1)[0]
with col_voice:
    voice_option = st.selectbox(
        "🎙️ ជ្រើសរើសសំឡេងតួអង្គ AI និយាយជាខ្មែរ៖",
        ("សំឡេងប្រុសធម្មជាតិ (Piseth)", "សំឡេងស្រីធម្មជាតិ (Sreymom)")
    )
    selected_voice = "km-KH-SreymomNeural" if "ស្រី" in voice_option else "km-KH-PisethNeural"

# ----------------- មុខងារដំណើរការសំឡេងខ្មែរធានាអត់ខ្ជះខ្ជាយ -----------------
async def process_guaranteed_khmer_dub(vid_in, vid_out, voice_name, khmer_script):
    output_audio = "final_khmer_audio.mp3"
    
    try:
        if not os.path.exists(vid_in): 
            return False

        progress_bar = st.progress(20)
        status_text = st.empty()
        status_text.text("កំពុងរៀបចំអត្ថបទភាសាខ្មែរ...")

        try:
            FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            FFMPEG_BIN = "ffmpeg"

        progress_bar.progress(50)
        status_text.text("កំពុងបញ្ចូលចង្វាក់ឈប់ដកដង្ហើមធម្មជាតិ (Natural Breathing Pause) ឱ្យត្រូវមាត់តួអង្គ...")

        # ដាក់សញ្ញាខណ្ឌក្បៀស (.) និងចុច (!) ដើម្បីឱ្យ AI ឈប់សម្រាកដកដង្ហើមដូចមនុស្សពិត
        punctuated_text = khmer_script.replace('.', '. <break time="600ms"/>').replace('!', '! <break time="600ms"/>').replace(',', ', <break time="400ms"/>')
        
        ssml_payload = f"""
        <speak>
            <voice name="{voice_name}">
                {punctuated_text}
            </voice>
        </speak>
        """

        progress_bar.progress(75)
        status_text.text("កំពុងបង្កើតសំឡេងនិយាយភាសាខ្មែរ...")

        communicate = edge_tts.Communicate(ssml_payload, voice_name)
        await communicate.save(output_audio)

        # យករយៈពេលវីដេអូដើម
        video_duration = 30.0
        try:
            probe_cmd = [FFMPEG_BIN.replace('ffmpeg', 'ffprobe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', vid_in]
            probe_res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if probe_res.returncode == 0 and probe_res.stdout.strip():
                video_duration = float(probe_res.stdout.strip())
        except Exception:
            pass

        progress_bar.progress(90)
        status_text.text("កំពុងដាក់បញ្ចូលសំឡេងខ្មែរចូលក្នុងវីដេអូ...")

        cmd = [
            FFMPEG_BIN, '-i', vid_in, '-i', output_audio,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-t', str(video_duration), '-y', vid_out
        ]
        
        process_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process_res.returncode != 0:
            fallback_cmd = [FFMPEG_BIN, '-i', vid_in, '-i', output_audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-shortest', '-y', vid_out]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        progress_bar.progress(100)
        status_text.text("ការបង្កើតវីដេអូនិយាយភាសាខ្មែរបានសម្រេចជោគជ័យ ១០០%!")
        return os.path.exists(vid_out) and os.path.getsize(vid_out) > 0

    except Exception as e:
        st.error(f"មានបញ្ហាក្នុងប្រព័ន្ធដំណើរការ៖ {e}")
        return False
        
    finally:
        if os.path.exists(output_audio):
            try: os.remove(output_audio)
            except: pass

st.markdown("---")
uploaded_file = st.file_uploader("📂 អូសទម្លាក់ ឬជ្រើសរើសឯកសារវីដេអូរបស់អ្នក (MP4, MOV)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    input_filename = "input_test.mp4"
    output_filename = "final_dubbed_video.mp4"
    
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.subheader("វីដេអូដើមរបស់អ្នក៖")
    st.video(input_filename)
    
    st.markdown("📝 *បញ្ចូលអត្ថបទជាភាសាខ្មែរផ្ទាល់ (ដើម្បីធានាថា AI និយាយជាភាសាខ្មែរ ១០០% ត្រូវតាមមាត់តួអង្គ និងមានចង្វាក់ដកដង្ហើម):*")
    
    default_khmer_script = "ស្លាប់ដោយសារធ្វើការហួសកម្លាំងក្នុងជាតិមុន។ បានចាប់កំណើតថ្មីក្នុងពិភពសាស្ត្រាសាត។ ស្មានថាអាចឈានដល់កំពូលនៃជីវិតទៅហើយ។"
    user_khmer_input = st.text_area("អត្ថបទភាសាខ្មែរសម្រាប់ឱ្យ AI និយាយ៖", value=default_khmer_script, height=100)

    can_proceed = True
    if not st.session_state.is_vip:
        used_count = st.session_state.trial_users.get(st.session_state.user_email, 0)
        if used_count >= MAX_FREE_VIDEOS:
            st.error(f"🔒 គណនីសាកល្បងរបស់អ្នកបានប្រើប្រាស់អស់ចំនួន {MAX_FREE_VIDEOS} វីដេអូហើយ! សូមទាក់ទងទិញកូដ VIP ຜ່ານ Telegram: @{TELEGRAM_USERNAME} ដើម្បីបន្តប្រើប្រាស់។")
            can_proceed = False
        else:
            st.info(f"✨ អ្នកនៅសល់សិទ្ធិសាកល្បងឥតគិតថ្លៃចំនួន *{MAX_FREE_VIDEOS - used_count}* វីដេអូទៀត។ (ផុតកំណត់ត្រូវទិញកូដ VIP)")

    if can_proceed and st.button("🚀 បង្កើតសំឡេងនិយាយខ្មែរ (ធានាអត់ច្រឡំទៅអង់គ្លេស)"):
        with st.spinner("កំពុងបង្កើតសំឡេងភាសាខ្មែរ និងដាក់បញ្ចូលក្នុងវីដេអូ... សូមរង់ចាំបន្តិច..."):
            success = asyncio.run(process_guaranteed_khmer_dub(
                input_filename, 
                output_filename, 
                selected_voice,
                user_khmer_input
            ))
            
            if success and os.path.exists(output_filename):
                st.success("🎉 បញ្ចូលសំឡេងខ្មែរបានជោគជ័យ ១០០%!")
                st.subheader("លទ្ធផលវីដេអូនិយាយភាសាខ្មែរ៖")
                st.video(output_filename)
                
                if not st.session_state.is_vip:
                    st.session_state.trial_users[st.session_state.user_email] += 1
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 ទាញយកវីដេអូនិយាយភាសាខ្មែរ",
                        data=file,
                        file_name="khmer_dubbed_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error("❌ មានបញ្ហាក្នុងដំណើរការកាត់តវីដេអូ! សូមពិនិត្យមើលទំហំ ឬទ្រង់ទ្រាយវីដេអូរបស់អ្នកឡើងវិញ។")
