import streamlit as st
import whisper
import subprocess
import os
import asyncio
import shutil
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import edge_tts

st.title("Video Dubbing (English -> Khmer)")

TRIAL_DAYS = 3

VALID_KEYS = {
    "BUNYIM-VIP-001": "សកម្ម",
    "BUNYIM-VIP-002": "សកម្ម",
    "TEST-KEY-123": "សកម្ម"
}

telegram_link = "https://t.me/bunyimyoem"  # ប្តូរជា Telegram Username របស់អ្នក

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def check_access():
    if st.session_state.is_authenticated:
        return True

    st.markdown("### 🔐 បញ្ចូលគណនី ឬកូដសម្ងាត់")
    st.info(f"សាកល្បងប្រើប្រាស់ដោយឥតគិតថ្លៃចំនួន {TRIAL_DAYS} ថ្ងៃ។")
    
    tab1, tab2 = st.tabs(["📧 Free Trial", "🔑 Access Key"])

    with tab1:
        st.markdown("#### ចុះឈ្មោះដោយប្រើ Email")
        email_input = st.text_input("អុីមែលរបស់អ្នក:", key="trial_email_input")
        
        if "trial_users" not in st.session_state:
            st.session_state.trial_users = {}

        if st.button("ចាប់ផ្តើម"):
            if email_input and "@" in email_input:
                now = datetime.now()
                if email_input not in st.session_state.trial_users:
                    st.session_state.trial_users[email_input] = now
                
                start_date = st.session_state.trial_users[email_input]
                expiry_date = start_date + timedelta(days=TRIAL_DAYS)

                if now < expiry_date:
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = email_input
                    st.success(f"ជោគជ័យ! ប្រើបានដល់ថ្ងៃ៖ {expiry_date.strftime('%Y-%m-%d %H:%M')}")
                    st.rerun()
                else:
                    st.error("រយៈពេលសាកល្បងបានផុតកំណត់ហើយ! សូមទិញកូដ។")
            else:
                st.warning("សូមបញ្ចូលអុីមែលឱ្យបានត្រឹមត្រូវ។")

    with tab2:
        st.markdown("#### វាយបញ្ចូលកូដ")
        key_input = st.text_input("កូដសម្ងាត់:", type="password", key="access_key_input")
        if st.button("ផ្ទៀងផ្ទាត់"):
            if key_input in VALID_KEYS:
                st.session_state.is_authenticated = True
                st.success("កូដត្រឹមត្រូវ!")
                st.rerun()
            else:
                st.error("កូដមិនត្រឹមត្រូវ។")

    st.markdown(f"ទិញកូដ Telegram: [ចុចទីនេះ]({telegram_link})")
    return False

if not check_access():
    st.stop()

st.success(f"គណនី៖ {st.session_state.get('user_email', 'Access Key VIP')}")

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
    
    model = whisper.load_model("tiny")
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
        
        try: kh_text = translator.translate(text)
        except: kh_text = text
        
        kh_text_ready = add_breathing_pauses(kh_text)
        audio_path = f"{temp_dir}/s_{count}.mp3"
        
        await edge_tts.Communicate(kh_text_ready, voice_name, rate="-10%", pitch="-2Hz").save(audio_path)
        
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
    
    if st.button("ចាប់ផ្តើមបកប្រែសំឡេង"):
        with st.spinner("កំពុងដំណើរការ..."):
            success = asyncio.run(process_video(input_filename, output_filename, selected_voice))
            
            if success and os.path.exists(output_filename):
                st.success("ជោគជ័យ!")
                st.video(output_filename)
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="ទាញយកវីដេអូ",
                        data=file,
                        file_name="dubbed_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.warning("មានបញ្ហាក្នុងការដំណើរការ!")
