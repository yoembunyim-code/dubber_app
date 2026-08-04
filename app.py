import streamlit as st
import whisper
import subprocess
import os
import asyncio
import shutil
from deep_translator import GoogleTranslator
import edge_tts

st.set_page_config(page_title="AI Video Dubbing Khmer", layout="centered")

st.title("AI Video Dubbing (Any Language ➔ Khmer) 🇰🇭")

MAX_FREE_VIDEOS = 3
telegram_link = "https://t.me/bunyimyoeme"

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

# ប្រព័ន្ធចូលគណនី (Authentication Check)
if not st.session_state.is_authenticated:
    st.markdown("### 🔐 សូមបញ្ចូលគណនី ឬកូដសម្ងាត់ដើម្បីបន្ត")
    st.info(f"សាកល្បងប្រើប្រាស់ដោយឥតគិតថ្លៃចំនួន {MAX_FREE_VIDEOS} វីដេអូ។")
    
    tab1, tab2 = st.tabs(["📧 Free Trial", "🔑 Access Key"])

    with tab1:
        email_input = st.text_input("អុីមែលរបស់អ្នក:", key="trial_email_input")
        if st.button("ចាប់ផ្តើមសាកល្បង"):
            if email_input and "@" in email_input:
                used_count = st.session_state.trial_users.get(email_input, 0)
                if used_count < MAX_FREE_VIDEOS:
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_input
                    st.session_state.is_vip = False
                    if email_input not in st.session_state.trial_users:
                        st.session_state.trial_users[email_input] = 0
                    st.success("ជោគជ័យ!")
                    st.rerun()
                else:
                    st.error("អុីមែលនេះបានប្រើប្រាស់អស់ចំនួន ៣ វីដេអូហើយ!")
            else:
                st.warning("សូមបញ្ចូលអុីមែលឱ្យបានត្រឹមត្រូវ។")

    with tab2:
        key_input = st.text_input("កូដសម្ងាត់ VIP:", type="password", key="access_key_input")
        if st.button("ផ្ទៀងផ្ទាត់កូដ"):
            if key_input in VALID_KEYS:
                st.session_state.is_authenticated = True
                st.session_state.user_email = f"VIP Key: {key_input}"
                st.session_state.is_vip = True
                st.success("កូដត្រឹមត្រូវ!")
                st.rerun()
            else:
                st.error("កូដមិនត្រឹមត្រូវ។")

    st.stop()

col1, col2 = st.columns([4, 1])
with col1:
    account_type = "👑 VIP" if st.session_state.is_vip else "🆓 Free Trial"
    st.success(f"គណនី ({account_type})៖ {st.session_state.user_email}")
with col2:
    if st.button("ចាកចេញ"):
        st.session_state.is_authenticated = False
        st.rerun()

voice_option = st.selectbox(
    "ជ្រើសរើសសំឡេង:",
    ("សំឡេងស្រី (Sreymom)", "សំឡេងប្រុស (Piseth)")
)

selected_voice = "km-KH-PisethNeural" if voice_option == "សំឡេងប្រុស (Piseth)" else "km-KH-SreymomNeural"

def clean_text_for_tts(text):
    for char in ['"', "'", '\\', '/', ':', '*', '?', '<', '>', '|', '[', ']', '{', '}']:
        text = text.replace(char, ' ')
    return text.strip()

async def process_video(vid_in, vid_out, voice_name):
    temp_dir = "temp_segments"
    if not os.path.exists(vid_in): 
        return False

    os.makedirs(temp_dir, exist_ok=True)

    subprocess.run(['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', 'temp_orig.mp3', '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    audio_to_transcribe = 'temp_orig.mp3' if os.path.exists('temp_orig.mp3') and os.path.getsize('temp_orig.mp3') > 0 else vid_in

    model = whisper.load_model("base")
    result = model.transcribe(audio_to_transcribe)
    segments = result.get("segments", [])

    translator = GoogleTranslator(source='auto', target='km')
    inputs, filters = [], []
    count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()
    total_segs = len(segments)

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
            
        kh_text_safe = clean_text_for_tts(kh_text)
        audio_path = f"{temp_dir}/s_{count}.mp3"
        
        try:
            communicate = edge_tts.Communicate(kh_text_safe, voice_name)
            await communicate.save(audio_path)
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                delay_ms = int(seg["start"] * 1000)
                inputs.extend(["-i", audio_path])
                filters.append(f"[{count+1}:a]adelay={delay_ms}|{delay_ms},volume=3.0[a{count}]")
                count += 1
        except Exception:
            continue

        if total_segs > 0:
            progress_bar.progress(int(((idx + 1) / total_segs) * 80))
        status_text.text(f"កំពុងបកប្រែ៖ {idx+1}/{total_segs}")

    if count > 0:
        status_text.text("កំពុងបញ្ចូលសំឡេងខ្មែរពេញលេញ...")
        mix = "".join([f"[a{i}]" for i in range(count)])
        
        # ប្រើប្រាស់ duration=longest ដើម្បីការពារកុំឱ្យវីដេអូត្រូវកាត់ផ្ដាច់ខ្លី
        filter_str = ";".join(filters) + f";{mix}amix=inputs={count}:duration=longest:dropout_transition=0[outa]"
        
        cmd = [
            "ffmpeg", "-i", vid_in
        ] + inputs + [
            "-filter_complex", filter_str,
            "-map", "0:v:0", "-map", "[outa]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-y", vid_out
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        progress_bar.progress(100)
        status_text.text("រួចរាល់!")
    else:
        shutil.copy(vid_in, vid_out)

    if os.path.exists("temp_orig.mp3"):
        os.remove("temp_orig.mp3")
    shutil.rmtree(temp_dir, ignore_errors=True)
    return os.path.exists(vid_out) and os.path.getsize(vid_out) > 0

# ----------------- កន្លែងអាប់ឡូតវីដេអូ -----------------
st.markdown("---")
uploaded_file = st.file_uploader("📂 ជ្រើសរើសឯកសារវីដេអូ (MP4, MOV)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    input_filename = "input_test.mp4"
    output_filename = "final_dubbed_video.mp4"
    
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.video(input_filename)
    
    can_generate = True
    if not st.session_state.is_vip:
        used = st.session_state.trial_users.get(st.session_state.user_email, 0)
        if used >= MAX_FREE_VIDEOS:
            st.error("🔒 គណនី Free របស់អ្នកបានប្រើប្រាស់អស់ ៣ វីដេអូហើយ! សូមទិញកូដ VIP។")
            can_generate = False
        else:
            st.info(f"អ្នកនៅសល់សិទ្ធិប្រើប្រាស់ចំនួន {MAX_FREE_VIDEOS - used} វីដេអូទៀត។")

    if can_generate and st.button("🚀 ចាប់ផ្តើមបកប្រែសំឡេង"):
        with st.spinner("កំពុងដំណើរការបកប្រែ និងបញ្ចូលសំឡេង AI ពេញលេញ..."):
            success = asyncio.run(process_video(input_filename, output_filename, selected_voice))
            
            if success and os.path.exists(output_filename):
                st.success("ជោគជ័យ!")
                st.video(output_filename)
                
                if not st.session_state.is_vip:
                    st.session_state.trial_users[st.session_state.user_email] += 1
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 ទាញយកវីដេអូ",
                        data=file,
                        file_name="dubbed_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.warning("មានបញ្ហាក្នុងការដំណើរការ! សូមសាកល្បងវីដេអូផ្សេងទៀត។")
