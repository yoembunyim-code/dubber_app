import streamlit as st
import os
import json
import asyncio
import tempfile
import shutil
import whisper
import subprocess
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

# ==========================================
# STREAMLIT UI DESIGN
# ==========================================
st.set_page_config(page_title="AI Khmer Auto Dubber Pro", page_icon="🎬", layout="wide")

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
    st.subheader("🎙️ ការកំណត់សំឡេង AI")
    male_voice = st.selectbox("👨 សំឡេងតួអង្គប្រុស:", ["km-KH-PisethNeural", "km-KH-ChhornNeural"], index=0)
    female_voice = st.selectbox("👩 សំឡេងតួអង្គស្រី:", ["km-KH-SreymomNeural"], index=0)
    
    voice_mode = st.radio(
        "🎭 ទម្រង់ប្រើប្រាស់សំឡេង៖",
        ["ឆ្លាស់គ្នាស្វ័យប្រវត្តិ (Auto Alternate)", "ប្រើសំឡេងប្រុសទាំងអស់", "ប្រើសំឡេងស្រីទាំងអស់"]
    )

    whisper_model = st.selectbox("🎯 កម្រិតចាប់សម្លេង Whisper:", ["base", "small"], index=0)

    st.markdown("---")
    st.markdown(f"💎 ទិញកូដ VIP: <a href='{TELEGRAM_LINK}' target='_blank'><b>{CONTACT_TELEGRAM}</b></a>", unsafe_allow_html=True)

st.title("🎬 AI Khmer Auto Dubber Pro (Full Automatic)")
st.markdown("ដាក់វីដេអូដែលមានសំឡេងចូល ប្រព័ន្ធនឹងបកប្រែជាភាសាខ្មែរ និងដាក់សំឡេង AI ឱ្យដោយស្វ័យប្រវត្តិ!")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. ដាក់វីដេអូរបស់អ្នក")
    video_file = st.file_uploader("ជ្រើសរើសវីដេអូ (MP4, MKV, AVI)", type=["mp4", "avi", "mov", "mkv"])
    
    if is_vip:
        st.success("🔓 VIP Mode Active (Unlimited)")
    else:
        st.warning(f"📊 Trial Usage: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    start_dubbing = st.button("🚀 ចាប់ផ្តើមបកប្រែ និងដាក់សំឡេងស្វ័យប្រវត្តិ", type="primary", use_container_width=True)

with col2:
    st.subheader("2. មើលវីដេអូ និងលទ្ធផល")
    if video_file:
        st.video(video_file)

if start_dubbing:
    if video_file is None:
        st.error("សូមដាក់បញ្ចូលវីដេអូជាមុនសិន!")
    else:
        can_run, status_msg = check_license(is_vip)
        if not can_run:
            st.error(f"❌ អ្នកបានប្រើប្រាស់អស់កូតាឥតគិតថ្លៃ! សូមទាក់ទងមក Telegram {CONTACT_TELEGRAM}")
            st.stop()
        
        if not is_vip:
            save_license(usage + 1, is_vip=False)

        try:
            with st.spinner("🤖 កំពុងដំណើរការស្តាប់ បកប្រែ និងបង្កើតសំឡេង AI..."):
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                vid_in = tfile.name
                vid_out = vid_in.replace(".mp4", "_auto_dubbed.mp4")
                temp_dir = tempfile.mkdtemp()

                # ១. ទាញសំឡេងចេញពីវីដេអូ
                temp_audio = os.path.join(temp_dir, "extracted_audio.mp3")
                extract_cmd = ['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', temp_audio, '-y']
                res_ext = subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # ឆែកមើលថាតើវីដេអូមានសំឡេងឬអត់
                if res_ext.returncode != 0 or not os.path.exists(temp_audio) or os.path.getsize(temp_audio) < 1000:
                    st.error("⚠️ វីដេអូនេះគ្មានសំឡេង (No Audio Track) ឬមិនអាចទាញយកសំឡេងបានទេ។ សូមព្យាយាមប្តូរវីដេអូផ្សេងដែលមានសំឡេងស្រាប់។")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    st.stop()

                # ២. ប្រើ Whisper ចាប់ Timing និង Text ពីសំឡេងដើម
                model = whisper.load_model(whisper_model)
                transcript = model.transcribe(temp_audio)
                segments = transcript.get("segments", [])

                translator = GoogleTranslator(source='auto', target='km')

                async def generate_tts(text, voice, output_path):
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(output_path)

                async def process_auto_segments():
                    audio_segments = []
                    seen_texts = set()
                    
                    for idx, seg in enumerate(segments):
                        text = seg["text"].strip()
                        start_t = seg["start"]
                        end_t = seg["end"]
                        target_duration = end_t - start_t

                        if not text or target_duration < 0.4:
                            continue

                        if text.lower() in seen_texts:
                            continue
                        seen_texts.add(text.lower())

                        try:
                            kh_text = translator.translate(text)
                        except Exception:
                            kh_text = text

                        if not kh_text:
                            continue

                        if voice_mode == "ឆ្លាស់គ្នាស្វ័យប្រវត្តិ (Auto Alternate)":
                            voice_code = male_voice if idx % 2 == 0 else female_voice
                        elif voice_mode == "ប្រើសំឡេងប្រុសទាំងអស់":
                            voice_code = male_voice
                        else:
                            voice_code = female_voice

                        raw_audio = os.path.join(temp_dir, f"raw_{idx}.mp3")
                        fitted_audio = os.path.join(temp_dir, f"fitted_{idx}.wav")

                        await generate_tts(kh_text, voice_code, raw_audio)

                        probe_cmd = [
                            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1', raw_audio
                        ]
                        res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        try:
                            gen_duration = float(res.stdout.strip())
                        except Exception:
                            gen_duration = target_duration

                        speed_ratio = gen_duration / target_duration
                        speed_ratio = max(0.5, min(speed_ratio, 2.0))

                        stretch_cmd = [
                            'ffmpeg', '-i', raw_audio,
                            '-filter:a', f'atempo={speed_ratio}',
                            '-ar', '44100', '-ac', '2', fitted_audio, '-y'
                        ]
                        subprocess.run(stretch_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        audio_segments.append((start_t, fitted_audio))

                    return audio_segments

                audio_segments = asyncio.run(process_auto_segments())

                if len(audio_segments) > 0:
                    inputs = []
                    filter_parts = []

                    for idx, (start_time, audio_path) in enumerate(audio_segments):
                        inputs.extend(["-i", audio_path])
                        delay_ms = int(start_time * 1000)
                        filter_parts.append(f"[{idx+1}:a]adelay={delay_ms}|{delay_ms},volume=3.0[a{idx}]")

                    mix_ai_inputs = "".join([f"[a{i}]" for i in range(len(audio_segments))])
                    
                    filter_str = ";".join(filter_parts) + f";{mix_ai_inputs}amix=inputs={len(audio_segments)}:duration=longest:dropout_transition=0[ai_mix];[0:a][ai_mix]amix=inputs=2:weights=0.2 1.0[outa]"

                    cmd = ["ffmpeg", "-i", vid_in] + inputs + [
                        "-filter_complex", filter_str,
                        "-map", "0:v:0", "-map", "[outa]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-y", vid_out
                    ]

                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    st.success("✅ បកប្រែ និងបង្កើតវីដេអូស្វ័យប្រវត្តិជោគជ័យ ១០០%!")
                    st.video(vid_out)

                    with open(vid_out, "rb") as f:
                        st.download_button("📥 ទាញយកវីដេអូ", data=f, file_name="auto_dubbed_story.mp4", mime="video/mp4", use_container_width=True)
                else:
                    st.warning("⚠️ Whisper រកមិនឃើញសម្លេង ឬប្រយោគដែលអាចបកប្រែបានក្នុងវីដេអូនេះទេ។")

                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            st.error(f"⚠️ មានបញ្ហាក្នុងការដំណើរការ៖ {e}")
