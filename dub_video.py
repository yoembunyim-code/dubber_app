import streamlit as st
import whisper
import subprocess
import os
import asyncio
import shutil
from deep_translator import GoogleTranslator
import edge_tts

st.title("Video Dubbing (Any Language ➔ Khmer) 🇰🇭")

# កំណត់ចំនួនវីដេអូរយៈពេលសាកល្បង (Free Trial)
MAX_FREE_VIDEOS = 3
telegram_link = "https://t.me/bunyimyoem" # ប្តូរដាក់តំណ Telegram របស់អ្នក

# ទាញយកកូដសម្ងាត់ពី Streamlit Secrets
VALID_KEYS = st.secrets.get("VALID_KEYS", {
    "BUNYIM-VIP-001": "សកម្ម",
    "BUNYIM-VIP-002": "សកម្ម"
})

# រៀបចំ Session State សម្រាប់ចងចាំការប្រើប្រាស់
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False
if "trial_users" not in st.session_state:
    st.session_state.trial_users = {} 

def check_access():
    if st.session_state.is_authenticated:
        return True

    st.markdown("### 🔐 បញ្ចូលគណនី ឬកូដសម្ងាត់")
    st.info(f"សាកល្បងប្រើប្រាស់ដោយឥតគិតថ្លៃចំនួន {MAX_FREE_VIDEOS} វីដេអូ។")
    
    tab1, tab2 = st.tabs(["📧 Free Trial", "🔑 Access Key"])

    with tab1:
        st.markdown("#### ចុះឈ្មោះដោយប្រើ Email")
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
                        
                    st.success(f"ជោគជ័យ! អ្នកអាចប្រើប្រាស់បាន {MAX_FREE_VIDEOS - used_count} វីដេអូទៀត។")
                    st.rerun()
                else:
                    st.error("អុីមែលនេះបានប្រើប្រាស់អស់ចំនួន ៣ វីដេអូហើយ! សូមទិញកូដ VIP។")
            else:
                st.warning("សូមបញ្ចូលអុីមែលឱ្យបានត្រឹមត្រូវ។")

    with tab2:
        st.markdown("#### វាយបញ្ចូលកូដ VIP")
        key_input = st.text_input("កូដសម្ងាត់:", type="password", key="access_key_input")
        if st.button("ផ្ទៀងផ្ទាត់"):
            if key_input in VALID_KEYS:
                st.session_state.is_authenticated = True
                st.session_state.user_email = f"VIP Key: {key_input}"
                st.session_state.is_vip = True
                st.success("កូដត្រឹមត្រូវ! អ្នកអាចប្រើបានដោយគ្មានដែនកំណត់។")
                st.rerun()
            else:
                st.error("កូដមិនត្រឹមត្រូវ។")

    st.markdown(f"ទិញកូដ Telegram: [ចុចទីនេះ]({telegram_link})")
    return False

if not check_access():
    st.stop()

col1, col2 = st.columns([4, 1])
with col1:
    account_type = "👑 VIP" if st.session_state.is_vip else "🆓 Free Trial"
    st.success(f"គណនី ({account_type})៖ {st.session_state.user_email}")
with col2:
    if st.button("ចាកចេញ (Logout)"):
        st.session_state.is_authenticated = False
        st.session_state.user_email = ""
        st.session_state.is_vip = False
        st.rerun()

voice_option = st.selectbox(
    "ជ្រើសរើសសំឡេង:",
    ("សំឡេងស្រី (Sreymom)", "សំឡេងប្រុស (Piseth)")
)

if voice_option == "សំឡេងប្រុស (Piseth)":
    selected_voice = "km-KH-PisethNeural"
else:
    selected_voice = "km-KH-SreymomNeural"

def add_breathing_pauses(text):
    words_to_pause = ["និង", "ហើយ", "ប៉ុន្តែ", "ដែល", "ព្រោះ", "ដូច្នេះ", "ម្យ៉ាងទៀត"]
    for word in words_to_pause:
        text = text.replace(word, f", {word}")
    text = text.replace("។", "។ ") 
    text = text.replace(",,", ",").replace(", ,", ",")
    return text

async def process_video(vid_in, vid_out, voice_name):
    temp_dir = "temp_segments"
    if not os.path.exists(vid_in): 
        st.error("រកមិនឃើញវីដេអូទេ!")
        return False

    os.makedirs(temp_dir, exist_ok=True)

    subprocess.run(['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', 'temp.mp3', '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    model = whisper.load_model("base")
    segments = model.transcribe("temp.mp3")["segments"]

    translator = GoogleTranslator(source='auto', target='km')
    inputs, filters = [], []
    count = 0
    total_segs = len(segments)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, seg in enumerate(segments):
        text = seg["text"].strip()
        if not text: 
            continue
        
        try: 
            kh_text = translator.translate(text)
        except: 
            kh_text = text
        
        if not kh_text or kh_text.isspace():
            continue
            
        kh_text_ready = add_breathing_pauses(kh_text)
        audio_path = f"{temp_dir}/s_{count}.mp3"
        
        try:
            await edge_tts.Communicate(kh_text_ready, voice_name).save(audio_path)
        except Exception:
            continue
        
        if os.path.exists(audio_path):
            delay_ms = int(seg["start"] * 1000)
            inputs.extend(["-i", audio_path])
            filters.append(f"[{count+1}:a]adelay={delay_ms}|{delay_ms},apad[a{count}]")
            count += 1

        progress_percentage = int(((idx + 1) / total_segs) * 90)
        progress_bar.progress(progress_percentage)
        status_text.text(f"កំពុងបកប្រែ៖ {idx+1}/{total_segs}")

    if count > 0:
        status_text.text("កំពុងចាក់បញ្ចូលសំឡេងចូលវីដេអូ...")
        mix = "".join([f"[a{i}]" for i in range(count)])
        filter_str = ";".join(filters) + f";{mix}amix=inputs={count}:duration=longest,volume={count}[outa]"
        
        cmd = [
            "ffmpeg", "-i", vid_in
        ] + inputs + [
            "-filter_complex", filter_str,
            "-map", "0:v:0", "-map", "[outa]",
            "-c:v", "copy", "-c:a", "aac", 
            "-shortest", "-y", vid_out
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        progress_bar.progress(100)
        status_text.text("រួចរាល់!")
    
    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    shutil.rmtree(temp_dir, ignore_errors=True)
    return count > 0

uploaded_file = st.file_uploader("ជ្រើសរើសឯកសារវីដេអូ (MP4)", type=["mp4", "mov", "avi"])

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
            st.error("🔒 គណនី Free របស់អ្នកបានប្រើប្រាស់អស់ ៣ វីដេអូហើយ! សូមទិញកូដ VIP ដើម្បីបន្តប្រើប្រាស់។")
            can_generate = False
        else:
            st.info(f"អ្នកនៅសល់សិទ្ធិប្រើប្រាស់ចំនួន {MAX_FREE_VIDEOS - used} វីដេអូទៀត។")

    if can_generate and st.button("ចាប់ផ្តើមបកប្រែសំឡេង"):
        with st.spinner("កំពុងដំណើរការ... អាចចំណាយពេលបន្តិច..."):
            success = asyncio.run(process_video(input_filename, output_filename, selected_voice))
            
            if success and os.path.exists(output_filename):
                st.success("ជោគជ័យ!")
                st.video(output_filename)
                
                if not st.session_state.is_vip:
                    st.session_state.trial_users[st.session_state.user_email] += 1
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="ទាញយកវីដេអូ",
                        data=file,
                        file_name="dubbed_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.warning("មានបញ្ហាក្នុងការដំណើរការ ឬគ្មានសំឡេងក្នុងវីដេអូ! សូមសាកល្បងវីដេអូផ្សេងម្ដងទៀត។")
