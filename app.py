import streamlit as st
import whisper
import subprocess
import os
import asyncio
import shutil
from deep_translator import GoogleTranslator
import edge_tts

# ----------------- ការកំណត់ទំព័រ (Page Configuration) -----------------
st.set_page_config(
    page_title="AI Video Dubbing Khmer Pro",
    page_icon="🎬",
    layout="centered"
)

# ----------------- CSS Styling ឱ្យកាន់តែស្រស់ស្អាត -----------------
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #FF4B4B; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #FF4B4B; color: white; }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    .telegram-box { background-color: #e6f7ff; padding: 15px; border-radius: 8px; border-left: 5px solid #1890ff; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 AI Video Dubbing (Any Language ➔ Khmer)</div>', unsafe_allow_html=True)

# ----------------- កន្លែងដាក់តេលេក្រាមរបស់អ្នក -----------------
TELEGRAM_USERNAME = "bunyimyoem"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME}"

st.markdown(f"""
    <div class="telegram-box">
        💬 <b>ចង់បានកូដ VIP ឬមានបញ្ហាក្នុងការប្រើប្រាស់?</b><br>
        សូមទាក់ទងមកកាន់តេលេក្រាមរបស់យើងខ្ញុំ៖ <a href="{TELEGRAM_LINK}" target="_blank"><b>@{TELEGRAM_USERNAME}</b></a>
    </div>
""", unsafe_allow_html=True)

# ----------------- ការគ្រប់គ្រងគណនី និងកូដ VIP -----------------
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
                    st.error(f"អុីមែលនេះបានប្រើប្រាស់អស់ចំនួន {MAX_FREE_VIDEOS} វីដេអូនាពេលកន្លងមកហើយ! សូមទិញកូដ VIP តាម Telegram ខាងលើ។")
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

# ----------------- របារបង្ហាញព័ត៌មានអ្នកប្រើប្រាស់ -----------------
col_acc1, col_acc2 = st.columns([4, 1])
with col_acc1:
    acc_type = "👑 VIP Member" if st.session_state.is_vip else "🆓 Free Tier"
    st.info(f"👤 គណនី៖ *{st.session_state.user_email}* ({acc_type})")
with col_acc2:
    if st.button("ចាកចេញ"):
        st.session_state.is_authenticated = False
        st.rerun()

# ----------------- ការជ្រើសរើសសំឡេង AI -----------------
voice_option = st.selectbox(
    "🎙️ ជ្រើសរើសសំឡេង AI សម្រាប់បកប្រែ៖",
    ("សំឡេងស្រីធម្មជាតិ (Sreymom)", "សំឡេងប្រុសធម្មជាតិ (Piseth)")
)
selected_voice = "km-KH-PisethNeural" if "ប្រុស" in voice_option else "km-KH-SreymomNeural"

# ----------------- កូដចម្បងក្នុងការដំណើរការវីដេអូ និងសំឡេង (Fixed Audio Processing) -----------------
async def process_video(vid_in, vid_out, voice_name):
    temp_dir = "temp_segments"
    if not os.path.exists(vid_in): 
        return False
    os.makedirs(temp_dir, exist_ok=True)

    # 1. យករយៈពេលវីដេអូសរុប (Duration)
    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', vid_in]
    probe_res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        video_duration = float(probe_res.stdout.strip())
    except:
        video_duration = 30.0

    # 2. ស្រង់សំឡេងចេញពីវីដេអូដើម
    orig_audio = "temp_orig.mp3"
    subprocess.run(['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', orig_audio, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    audio_to_transcribe = orig_audio if os.path.exists(orig_audio) and os.path.getsize(orig_audio) > 0 else vid_in

    # 3. ប្រើប្រាស់ Whisper AI ដើម្បីទាញយកកថាខណ្ឌ
    model = whisper.load_model("base")
    result = model.transcribe(audio_to_transcribe, word_timestamps=False)
    segments = result.get("segments", [])

    # ប្រសិនបើរកមិនឃើញ segments វានឹងយកទាំងមូលមកបកប្រែម្តងហ្មងដើម្បីការពារការអត់លឺសំឡេង
    if not segments and result.get("text"):
        segments = [{"start": 0.0, "end": video_duration, "text": result.get("text")}]

    translator = GoogleTranslator(source='auto', target='km')
    audio_segments = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    total_segs = len(segments)

    # 4. បកប្រែ និងបង្កើតសំឡេង MP3 នីមួយៗ
    for idx, seg in enumerate(segments):
        raw_text = seg.get("text", "").strip()
        if not raw_text: 
            continue
        
        try: 
            kh_text = translator.translate(raw_text)
        except: 
            kh_text = raw_text
        
        if not kh_text or kh_text.isspace():
            continue
            
        audio_path = f"{temp_dir}/seg_{idx}.mp3"
        try:
            communicate = edge_tts.Communicate(kh_text, voice_name)
            await communicate.save(audio_path)
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                start_time = float(seg.get("start", 0))
                audio_segments.append((start_time, audio_path))
        except:
            continue

        if total_segs > 0:
            progress_bar.progress(int(((idx + 1) / total_segs) * 70))
        status_text.text(f"កំពុងបង្កើតសំឡេង AI ខ្មែរ៖ {idx+1}/{total_segs}")

    # 5. វិធីសាស្ត្រថ្មីក្នុងការផ្គុំសំឡេងដោយប្រើ concat filter (លែងទើសបញ្ហា amix កាត់ផ្តាច់សំឡេង)
    if len(audio_segments) > 0:
        status_text.text("កំពុងផ្គុំសំឡេង AI ចូលក្នុងវីដេអូដោយសុវត្ថិភាព...")
        
        # រៀបចំបញ្ជី ፋይልសម្រាប់ FFmpeg Concat
        list_file_path = os.path.join(temp_dir, "file_list.txt")
        sorted_segs = sorted(audio_segments, key=lambda x: x[0])
        
        current_time = 0.0
        with open(list_file_path, "w", encoding="utf-8") as f_list:
            for start_t, path in sorted_segs:
                # បើមានគម្លាតស្ងាត់ ដាក់ silent audio បន្ថែម
                if start_t > current_time:
                    gap_duration = start_t - current_time
                    silence_path = os.path.join(temp_dir, f"silence_{current_time}.mp3")
                    subprocess.run([
                        'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo', 
                        '-t', str(gap_duration), '-q:a', '9', '-acodec', 'libmp3lame', silence_path, '-y'
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if os.path.exists(silence_path):
                        f_list.write(f"file '{os.path.abspath(silence_path)}'\n")
                
                f_list.write(f"file '{os.path.abspath(path)}'\n")
                # បង្ហាញរយៈពេលសំឡេងប៉ាន់ស្មាន (អាចប្រើ ffprobe រំលងដើម្បីលឿន)
                current_time = start_t + 3.0 

        combined_audio = os.path.join(temp_dir, "combined_dub.mp3")
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file_path, '-c', 'copy', combined_audio, '-y'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(combined_audio) and os.path.getsize(combined_audio) > 0:
            cmd = [
                'ffmpeg', '-i', vid_in, '-i', combined_audio,
                '-map', '0:v:0', '-map', '1:a:0',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-t', str(video_duration), '-y', vid_out
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            shutil.copy(vid_in, vid_out)

        progress_bar.progress(100)
        status_text.text("ការបកប្រែវីដេអូទទួលបានជោគជ័យរហូតដល់ចប់!")
    else:
        shutil.copy(vid_in, vid_out)

    if os.path.exists(orig_audio): 
        os.remove(orig_audio)
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return os.path.exists(vid_out) and os.path.getsize(vid_out) > 0

# ----------------- ចំណុចអាប់ឡូតវីដេអូ (File Uploader UI) -----------------
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
            st.error(f"🔒 គណនីសាកល្បងរបស់អ្នកបានអស់កូតាប្រើប្រាស់ហើយ។ សូមទាក់ទងមកកាន់ Telegram: @{TELEGRAM_USERNAME} ដើម្បីទិញកូដ VIP!")
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
