import streamlit as st
import os
import json
import asyncio
import tempfile
import shutil
import whisper
import subprocess
import re
from deep_translator import GoogleTranslator
import edge_tts

# ==========================================
# CONFIGURATION & DATABASE
# ==========================================
CONTACT_TELEGRAM = "@yoem bunyim"
TELEGRAM_LINK = "https://t.me/bunyimyoem"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"
VALID_VIP_CODES = st.secrets.get("VIP_CODES", [])

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("video_processed", 0), data.get("is_vip", False)
        except Exception:
            return 0, False
    return 0, False

def save_license(count, is_vip=False):
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump({"video_processed": count, "is_vip": is_vip}, f)
    except Exception:
        pass

def check_license(is_vip):
    if is_vip:
        return True, "VIP Unlimited"
    usage, _ = load_license()
    if usage >= TRIAL_VIDEO_LIMIT:
        return False, usage
    return True, usage

def clean_khmer_text(text):
    if not text:
        return ""
    text = re.sub(r'[\"\’\‘\“\”]', '', text)
    text = text.replace("...", "។ ").replace(";", " ")
    return text.strip()

# ==========================================
# STREAMLIT UI DESIGN
# ==========================================
st.set_page_config(page_title="AI Khmer Dubbing PRO (Clean Multi-Voice)", page_icon="🎬", layout="wide")

usage, is_vip = load_license()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    st.title("⚙️ Settings & VIP")
    
    st.subheader("🔑 Enter VIP Code")
    vip_input = st.text_input("VIP Code", placeholder="បញ្ចូលលេខកូដនៅទីនេះ")
    if st.button("Activate VIP"):
        if vip_input in VALID_VIP_CODES:
            save_license(usage, is_vip=True)
            st.success("✅ បានធ្វើឱ្យសកម្ម VIP ដោយជោគជ័យ!")
            st.rerun()
        else:
            st.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវ។")

    st.markdown("---")
    st.subheader("🎙️ ការកំណត់សំឡេងតួអង្គ (Multi-Voice)")
    
    male_voice = st.selectbox(
        "👨 សំឡេងតួអង្គប្រុស:", 
        ["km-KH-PisethNeural", "km-KH-ChhornNeural"],
        index=0
    )
    
    female_voice = st.selectbox(
        "👩 សំឡេងតួអង្គស្រី:", 
        ["km-KH-SreymomNeural"],
        index=0
    )

    voice_mode = st.radio(
        "🎭 ទម្រង់ប្រើប្រាស់សំឡេង៖",
        ["ឆ្លាស់គ្នា (Auto Alternate Male/Female)", "ប្រើសំឡេងប្រុសទាំងអស់", "ប្រើសំឡេងស្រីទាំងអស់"]
    )
    
    whisper_model_type = st.selectbox(
        "🎯 ភាពសុក្រឹតនៃការចាប់ចង្វាក់និយាយ:",
        ["small", "base"],
        index=0
    )
    
    add_breathing = st.checkbox("🎭 បញ្ចូលការផ្អាកដកដង្ហើមតាមតួអង្គ", value=True)
    st.markdown("---")
    st.markdown(f"💎 ទិញកូដ VIP: <a href='{TELEGRAM_LINK}' target='_blank'><b>{CONTACT_TELEGRAM}</b></a>", unsafe_allow_html=True)

st.title("🎬 AI Khmer Video Dubbing PRO (Anti-Duplicate & Clean)")
st.markdown("បកប្រែវីដេអូរឿងជាភាសាខ្មែរ ជាមួយសំឡេងប្រុស-ស្រីឆ្លើយឆ្លងគ្នា និងលុបបំបាត់ការនិយាយជាន់គ្នាច្រើនដង។")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🕹️ Controls")
    video_file = st.file_uploader("1. BROWSE VIDEO (MP4, MKV, AVI)", type=["mp4", "avi", "mov", "mkv"])
    
    if is_vip:
        st.success("🔓 VIP Mode Active (Unlimited)")
    else:
        st.warning(f"📊 Trial Usage: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    start_dubbing = st.button("🚀 START CLEAN DUBBING", type="primary", use_container_width=True)

with col1:
    st.subheader("📄 Processing Logs & Output")
    log_area = st.empty()
    progress_bar = st.progress(0)

    if start_dubbing:
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            can_run, status_msg = check_license(is_vip)
            if not can_run:
                st.error(f"❌ អ្នកបានប្រើប្រាស់អស់កូតាឥតគិតថ្លៃ! សូមទាក់ទងមកកាន់ Telegram {CONTACT_TELEGRAM} ដើម្បីទិញកូដ VIP បន្ត។")
                st.stop()
            
            if not is_vip:
                save_license(usage + 1, is_vip=False)

            try:
                log_area.code("[10%] កំពុងផ្ទុកទិន្នន័យវីដេអូ...")
                progress_bar.progress(0.10)

                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                vid_in = tfile.name
                
                vid_out = vid_in.replace(".mp4", "_dubbed.mp4")
                temp_dir = tempfile.mkdtemp()

                log_area.code(f"[30%] កំពុងទាញសំឡេង និងវិភាគ Timing ជាមួយ Whisper ({whisper_model_type})...")
                progress_bar.progress(0.30)
                
                temp_audio = os.path.join(temp_dir, "temp.mp3")
                subprocess.run(['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', temp_audio, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                model = whisper.load_model(whisper_model_type)
                segments = model.transcribe(temp_audio)["segments"]

                translator = GoogleTranslator(source='auto', target='km')

                def add_breathing_pauses(text):
                    if not add_breathing:
                        return text
                    words_to_pause = ["និង", "ហើយ", "ប៉ុន្តែ", "ដែល", "ព្រោះ", "ដូច្នេះ", "ម្យ៉ាងទៀត"]
                    for word in words_to_pause:
                        text = text.replace(word, f", {word}")
                    text = text.replace("។", "។ ").replace(",,", ",").replace(", ,", ",")
                    return text

                log_area.code("[60%] កំពុងបកប្រែ  lọcប្រយោគស្ទួន និងបែងចែកសំឡេងប្រុស-ស្រី...")
                progress_bar.progress(0.60)

                async def generate_tts(text, voice, output_path):
                    for attempt in range(3):
                        try:
                            communicate = edge_tts.Communicate(text, voice)
                            await communicate.save(output_path)
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                                return True
                        except Exception:
                            await asyncio.sleep(0.5)
                        return False

                async def process_audio():
                    audio_segments = []
                    local_count = 0
                    seen_texts = set()  # ប្រើសម្រាប់ទប់ស្កាត់មិនឱ្យប្រយោគដដែលៗនិយាយជាន់គ្នា
                    
                    for idx, seg in enumerate(segments):
                        text = seg["text"].strip()
                        start_time = seg["start"]
                        end_time = seg["end"]
                        target_duration = end_time - start_time
                        
                        if not text or target_duration <= 0.3:
                            continue
                        
                        # បើប្រយោគស្រដៀងគ្នា ឬជាន់គ្នាខ្លាំង មិនបាច់យកទេ
                        if text.lower() in seen_texts:
                            continue
                        seen_texts.add(text.lower())
                        
                        try:
                            kh_text = translator.translate(text)
                        except Exception:
                            kh_text = text
                        
                        kh_text = clean_khmer_text(kh_text)
                        if not kh_text:
                            continue

                        # ជ្រើសរើសសំឡេងប្រុស ឬស្រី
                        if voice_mode == "ឆ្លាស់គ្នា (Auto Alternate Male/Female)":
                            chosen_voice = male_voice if local_count % 2 == 0 else female_voice
                        elif voice_mode == "ប្រើសំឡេងប្រុសទាំងអស់":
                            chosen_voice = male_voice
                        else:
                            chosen_voice = female_voice

                        kh_text_ready = add_breathing_pauses(kh_text)
                        raw_audio = os.path.join(temp_dir, f"raw_{local_count}.mp3")
                        fitted_audio = os.path.join(temp_dir, f"fitted_{local_count}.wav")
                        
                        success = await generate_tts(kh_text_ready, chosen_voice, raw_audio)
                        if not success:
                            continue

                        probe_cmd = [
                            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1', raw_audio
                        ]
                        res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        try:
                            generated_duration = float(res.stdout.strip())
                        except Exception:
                            generated_duration = target_duration

                        speed_ratio = generated_duration / target_duration
                        speed_ratio = max(0.7, min(speed_ratio, 1.8))
                        
                        stretch_cmd = [
                            'ffmpeg', '-i', raw_audio,
                            '-filter:a', f'atempo={speed_ratio}',
                            '-ar', '44100', '-ac', '2', fitted_audio, '-y'
                        ]
                        subprocess.run(stretch_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        audio_segments.append((start_time, fitted_audio))
                        local_count += 1

                    return audio_segments

                audio_segments = asyncio.run(process_audio())

                if len(audio_segments) > 0:
                    log_area.code("[85%] កំពុងផ្គុំសំឡេង AI ឱ្យត្រូវ Timing វីដេអូដើម...")
                    progress_bar.progress(0.85)

                    inputs = []
                    filter_parts = []
                    
                    for idx, (start_time, audio_path) in enumerate(audio_segments):
                        inputs.extend(["-i", audio_path])
                        delay_ms = int(start_time * 1000)
                        filter_parts.append(f"[{idx+1}:a]adelay={delay_ms}|{delay_ms},volume=2.0[a{idx}]")
                    
                    mix_inputs = "".join([f"[a{i}]" for i in range(len(audio_segments))])
                    filter_str = ";".join(filter_parts) + f";{mix_inputs}amix=inputs={len(audio_segments)}:normalize=0[outa]"
                    
                    cmd = ["ffmpeg", "-i", vid_in] + inputs + [
                        "-filter_complex", filter_str,
                        "-map", "0:v:0", "-map", "[outa]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-y", vid_out
                    ]
                    
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    log_area.code("[100%] ជោគជ័យ ១០០%!")
                    progress_bar.progress(1.0)
                    st.balloons()
                    
                    st.success("✅ វីដេអូបកប្រែ និងសំឡេងស្អាតគ្មានការនិយាយជាន់គ្នាស្ទួនៗរួចរាល់!")
                    st.video(vid_out)
                else:
                    st.warning("មិនអាចបង្កើតសំឡេង AI ខ្មែរបានទេ! សូមព្យាយាមម្តងទៀត។")

                shutil.rmtree(temp_dir, ignore_errors=True)

            except Exception as e:
                st.error(f"មានបញ្ហាក្នុងការដំណើរការ: {e}")
