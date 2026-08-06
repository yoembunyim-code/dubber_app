import streamlit as st
import os
import asyncio
import tempfile
import shutil
import whisper
import subprocess
from deep_translator import GoogleTranslator
import edge_tts

# ==========================================
# STREAMLIT UI DESIGN
# ==========================================
st.set_page_config(page_title="AI Khmer Dubbing PRO (Edge TTS)", page_icon="🎬", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    st.title("⚙️ Settings")
    
    selected_voice = st.selectbox(
        "🎙️ ជ្រើសរើសសំឡេង AI:", 
        ["km-KH-SreymomNeural", "km-KH-PisethNeural"]
    )
    add_breathing = st.checkbox("🎭 បញ្ចូលការផ្អាកដកដង្ហើមតាមតួអង្គ", value=True)
    st.markdown("---")
    st.caption("👨‍💻 Dev: Telegram @Semsamnang_Dev")

st.title("🎬 AI Khmer Video Dubbing PRO")
st.markdown("បកប្រែសំឡេងវីដេអូជាភាសាខ្មែរតាមសាច់រឿងពិតប្រាកដ ព្រមទាំងដាក់បញ្ចូលសំឡេង AI ធម្មជាតិ (Edge-TTS)។")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🕹️ Controls")
    video_file = st.file_uploader("1. BROWSE VIDEO (Up to 1GB)", type=["mp4", "avi", "mov", "mkv"])
    start_dubbing = st.button("🚀 START DUBBING", type="primary", use_container_width=True)

with col1:
    st.subheader("📄 Processing Logs & Output")
    log_area = st.empty()
    progress_bar = st.progress(0)

    if start_dubbing:
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            try:
                # ១. រក្សាទុកវីដេអូដើម
                log_area.code("[10%] កំពុងផ្ទុកទិន្នន័យវីដេអូ...")
                progress_bar.progress(0.10)

                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                vid_in = tfile.name
                
                vid_out = vid_in.replace(".mp4", "_dubbed.mp4")
                temp_dir = tempfile.mkdtemp()

                # ២. ទាញសំឡេងដើម & ឱ្យ AI (Whisper) វិភាគម៉ោង
                log_area.code("[30%] កំពុងទាញសំឡេង និងវិភាគម៉ោងជាមួយ Whisper AI...")
                progress_bar.progress(0.30)
                
                temp_audio = os.path.join(temp_dir, "temp.mp3")
                subprocess.run(['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', temp_audio, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # ใช้ model "tiny" ដើម្បីឱ្យដំណើរការលឿននៅលើ Cloud
                model = whisper.load_model("tiny")
                segments = model.transcribe(temp_audio)["segments"]

                translator = GoogleTranslator(source='auto', target='km')
                inputs, filters = [], []
                count = 0

                # មុខងារជំនួយការដកដង្ហើម
                def add_breathing_pauses(text):
                    if not add_breathing:
                        return text
                    words_to_pause = ["និង", "ហើយ", "ប៉ុន្តែ", "ដែល", "ព្រោះ", "ដូច្នេះ", "ម្យ៉ាងទៀត"]
                    for word in words_to_pause:
                        text = text.replace(word, f", {word}")
                    text = text.replace("។", "។ ").replace(",,", ",").replace(", ,", ",")
                    return text

                # ៣. បង្កើតសំឡេងខ្មែរតាមម៉ោងនីមួយៗ (Async function)
                log_area.code("[60%] កំពុងបកប្រែ និងបង្កើតសំឡេង AI ខ្មែរ...")
                progress_bar.progress(0.60)

                async def process_audio():
                    nonlocal count
                    for seg in segments:
                        text = seg["text"].strip()
                        if not text: continue
                        
                        try: kh_text = translator.translate(text)
                        except: kh_text = text
                        
                        kh_text_ready = add_breathing_pauses(kh_text)
                        audio_path = os.path.join(temp_dir, f"s_{count}.mp3")
                        
                        communicate = edge_tts.Communicate(kh_text_ready, selected_voice, rate="-10%", pitch="-2Hz")
                        await communicate.save(audio_path)
                        
                        delay_ms = int(seg["start"] * 1000)
                        inputs.extend(["-i", audio_path])
                        filters.append(f"[{count+1}:a]adelay={delay_ms}|{delay_ms},apad[a{count}]")
                        count += 1

                asyncio.run(process_audio())

                # ៤. បញ្ចូលសំឡេងទៅក្នុងវីដេអូដោយប្រើ FFmpeg
                if count > 0:
                    log_area.code("[85%] កំពុងដំឡើងសំឡេង AI ចូលក្នុងវីដេអូ...")
                    progress_bar.progress(0.85)

                    mix = "".join([f"[a{i}]" for i in range(count)])
                    filter_str = ";".join(filters) + f";{mix}amix=inputs={count}:duration=longest,volume={count}[outa]"
                    
                    cmd = ["ffmpeg", "-i", vid_in] + inputs + [
                        "-filter_complex", filter_str,
                        "-map", "0:v:0", "-map", "[outa]",
                        "-c:v", "copy", "-c:a", "aac", 
                        "-shortest", "-y", vid_out
                    ]
                    
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    log_area.code("[100%] ជោគជ័យ ១០០%!")
                    progress_bar.progress(1.0)
                    st.balloons()
                    
                    st.success("✅ វីដេអូបកប្រែ និងพากย์សំឡេងរួចរាល់ជាស្ថាពរ!")
                    st.video(vid_out)
                else:
                    st.warning("រកមិនឃើញអត្ថបទត្រូវបកប្រែក្នុងវីដេអូនេះទេ!")

                # សម្អាតថតបណ្តោះអាសន្ន
                shutil.rmtree(temp_dir, ignore_errors=True)

            except Exception as e:
                st.error(f"មានបញ្តាក្នុងការដំណើរការ: {e}")
