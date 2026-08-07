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
# CONFIGURATION & DATABASE (កំណត់រចនាសម្ព័ន្ធ)
# ==========================================
CONTACT_TELEGRAM = "@yoem bunyim"
TELEGRAM_LINK = "https://t.me/bunyimyoem"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

# ទាញយកកូដ VIP ពី Streamlit Secrets ដើម្បីសុវត្ថិភាព
VALID_VIP_CODES = st.secrets.get("VIP_CODES", [])

def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("video_processed", 0), data.get("is_vip", False)
    return 0, False

def save_license(count, is_vip=False):
    with open(LICENSE_FILE, 'w') as f:
        json.dump({"video_processed": count, "is_vip": is_vip}, f)

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
st.set_page_config(page_title="AI Khmer Dubbing PRO (VIP System)", page_icon="🎬", layout="wide")

# ពិនិត្យស្ថានភាព VIP ជាមុន
usage, is_vip = load_license()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    st.title("⚙️ Settings & VIP")
    
    if is_vip:
        st.success("🎉 អ្នកកំពុងប្រើប្រាស់កញ្ចប់ VIP Unlimited!")
        st.info("អរគុណសម្រាប់ការគាំទ្រប្រើប្រាស់សេវាកម្មរបស់យើង!")
    else:
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
    selected_voice = st.selectbox(
        "🎙️ ជ្រើសរើសសំឡេង AI:", 
        ["km-KH-SreymomNeural", "km-KH-PisethNeural"]
    )
    add_breathing = st.checkbox("🎭 បញ្ចូលការផ្អាកដកដង្ហើមតាមតួអង្គ", value=True)
    
    st.markdown("---")
    
    # បង្ហាញឈ្មោះ Telegram អក្សរធំៗជានិច្ច
    st.markdown(
        f"""
        <div style="background-color: #0e1117; border: 2px solid #0088cc; padding: 15px; border-radius: 10px; text-align: center;">
            <h3 style="color: #ffffff; margin-bottom: 5px;">💎 ទិញកូដ VIP តាមតេលេក្រាម</h3>
            <h1 style="color: #0088cc; font-size: 24px; font-weight: bold; margin-top: 5px; margin-bottom: 15px;">
                {CONTACT_TELEGRAM}
            </h1>
            <a href="{TELEGRAM_LINK}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #0088cc; color: white; border: none; padding: 12px 15px; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; width: 100%;">
                    💬 ឆាតទៅកាន់ Telegram
                </button>
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.title("🎬 AI Khmer Video Dubbing PRO (VIP Supported)")
st.markdown("បកប្រែសំឡេងវីដេអូជាភាសាខ្មែរតាមសាច់រឿងពិតប្រាកដ ព្រមទាំងដាក់បញ្ចូលសំឡេង AI ធម្មជាតិ (Edge-TTS)។")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🕹️ Controls")
    video_file = st.file_uploader("1. BROWSE VIDEO (Up to 1GB)", type=["mp4", "avi", "mov", "mkv"])
    
    if is_vip:
        st.success("🔓 VIP Mode Active (Unlimited)")
    else:
        st.warning(f"📊 Trial Usage: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    start_dubbing = st.button("🚀 START DUBBING", type="primary", use_container_width=True)

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
                st.error(f"❌ អ្នកបានប្រើប្រាស់អស់កូតាឥតគិតថ្លៃ (3 វីដេអូ) ហើយ! សូមទាក់ទងមកកាន់ Telegram {CONTACT_TELEGRAM} ដើម្បីទិញកូដ VIP បន្ត។")
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

                log_area.code("[30%] កំពុងទាញសំឡេង និងវិភាគម៉ោងជាមួយ Whisper AI...")
                progress_bar.progress(0.30)
                
                temp_audio = os.path.join(temp_dir, "temp.mp3")
                subprocess.run(['ffmpeg', '-i', vid_in, '-q:a', '0', '-map', 'a', temp_audio, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                model = whisper.load_model("base")
                segments = model.transcribe(temp_audio)["segments"]

                translator = GoogleTranslator(source='auto', target='km')
                inputs, filters = [], []

                def add_breathing_pauses(text):
                    if not add_breathing:
                        return text
                    words_to_pause = ["និង", "ហើយ", "ប៉ុន្តែ", "ដែល", "ព្រោះ", "ដូច្នេះ", "ម្យ៉ាងទៀត"]
                    for word in words_to_pause:
                        text = text.replace(word, f", {word}")
                    text = text.replace("។", "។ ").replace(",,", ",").replace(", ,", ",")
                    return text

                log_area.code("[60%] កំពុងបកប្រែ និងតម្រឹមសំឡេង AI ឱ្យស្មើ timing...")
                progress_bar.progress(0.60)

                async def process_audio():
                    local_count = 0
                    for seg in segments:
                        text = seg["text"].strip()
                        start_time = seg["start"]
                        end_time = seg["end"]
                        target_duration = end_time - start_time
                        
                        if not text or target_duration <= 0.3:
                            continue
                        
                        try:
                            kh_text = translator.translate(text)
                        except Exception:
                            kh_text = text
                        
                        if not kh_text or not kh_text.strip():
                            continue

                        kh_text_ready = add_breathing_pauses(kh_text.strip())
                        raw_audio_path = os.path.join(temp_dir, f"raw_{local_count}.mp3")
                        fitted_audio_path = os.path.join(temp_dir, f"fitted_{local_count}.wav")
                        
                        # ការពារ Error: No audio was received
                        try:
                            communicate = edge_tts.Communicate(kh_text_ready, selected_voice)
                            await communicate.save(raw_audio_path)
                        except Exception:
                            continue  # បើទាញសំឡេងមិនបាន ឱ្យរំលងប្រយោគនោះទៅប្រយោគបន្ទាប់

                        if not os.path.exists(raw_audio_path) or os.path.getsize(raw_audio_path) == 0:
                            continue

                        # គណនារយៈពេលនៃសំឡេង AI ដែលទើបបង្កើត
                        probe_cmd = [
                            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1', raw_audio_path
                        ]
                        res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        try:
                            generated_duration = float(res.stdout.strip())
                        except Exception:
                            generated_duration = target_duration

                        speed_ratio = generated_duration / target_duration
                        speed_ratio = max(0.7, min(speed_ratio, 1.5))
                        
                        stretch_cmd = [
                            'ffmpeg', '-i', raw_audio_path,
                            '-filter:a', f'atempo={speed_ratio}',
                            '-ar', '44100', fitted_audio_path, '-y'
                        ]
                        subprocess.run(stretch_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        delay_ms = int(start_time * 1000)
                        inputs.extend(["-i", fitted_audio_path])
                        filters.append(f"[{local_count+1}:a]adelay={delay_ms}|{delay_ms},apad[a{local_count}]")
                        local_count += 1

                    return local_count

                count = asyncio.run(process_audio())

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
                    
                    st.success("✅ វីដេអូបកប្រែ និងសំឡេងរួចរាល់ជាស្ថាពរ!")
                    st.video(vid_out)
                else:
                    st.warning("មិនអាចទាញយកសំឡេង AI ខ្មែរបានទេ! សូមព្យាយាមម្តងទៀត ឬប្តូរវីដេអូ។")

                shutil.rmtree(temp_dir, ignore_errors=True)

            except Exception as e:
                st.error(f"មានបញ្ហាក្នុងការដំណើរការ: {e}")
