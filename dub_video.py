import streamlit as st
import whisper
import subprocess
import os
import asyncio
import shutil
from deep_translator import GoogleTranslator
import edge_tts

st.title("Video Dubbing (English -> Khmer)")

# --- បញ្ជីកូដសម្ងាត់សម្រាប់អតិថិជន (Access Keys) ---
VALID_KEYS = {
    "BUNYIM-VIP-001": "សកម្ម (Active)",
    "BUNYIM-VIP-002": "សកម្ម (Active)",
    "TEST-KEY-123": "សកម្ម (Active)"
}

st.markdown("### 🔐 សូមបញ្ចូលកូដសម្ងាត់របស់អ្នកដើម្បីប្រើប្រាស់")
st.info("💡 ទំនាក់ទំនងមកកាន់ Telegram របស់អ្នកដើម្បីទិញកូដសម្ងាត់ផ្ទាល់ខ្លួន។")

user_key = st.text_input("បញ្ចូល Access Key:", type="password")

if user_key not in VALID_KEYS:
    if user_key != "":
        st.error("❌ កូដសម្ងាត់មិនត្រឹមត្រូវ ឬមិនមានក្នុងប្រព័ន្ធទេ!")
    st.stop()

st.success("✅ កូដត្រឹមត្រូវ! សូមរីករាយជាមួយការប្រើប្រាស់កម្មវិធី។")

voice_option = st.selectbox(
    "សូមជ្រើសរើសប្រភេទសំឡេងដែលអ្នកចង់បាន (Choose Voice):",
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
        status_text.text(f"កំពុងបកប្រែ និងបង្កើតសំឡេង៖ {idx+1}/{total_segs}")

    if count > 0:
        status_text.text(">>> កំពុងចាក់បញ្ចូលសំឡេងថ្មីចូលវីដេអូ...")
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
        status_text.text("រួចរាល់ជាស្រេច!")
    
    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    shutil.rmtree(temp_dir, ignore_errors=True)
    return count > 0

uploaded_file = st.file_uploader("សូមជ្រើសរើស ឬទម្លាក់ឯកសារវីដេអូ (MP4)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    input_filename = "input_test.mp4"
    output_filename = "final_dubbed_video.mp4"
    
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.video(input_filename)
    
    if st.button("ចាប់ផ្តើមបកប្រែសំឡេង (Start Dubbing)"):
        with st.spinner("ប្រព័ន្ធកំពុងដំណើរการ សូមរង់ចាំបន្តិច..."):
            success = asyncio.run(process_video(input_filename, output_filename, selected_voice))
            
            if success and os.path.exists(output_filename):
                st.success("ជោគជ័យ ១០០%! វីដេអូបកប្រែរបស់អ្នករួចរាល់ហើយ៖")
                st.video(output_filename)
                
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="ទាញយកវីដេអូដែលបានបកប្រែ (Download)",
                        data=file,
                        file_name="dubbed_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.warning("គ្មានសំឡេងត្រូវបកប្រែ ឬមានបញ្ហាក្នុងការដំណើរការ!")
