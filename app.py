import streamlit as st
import os
import json
import asyncio
import tempfile
import time
import re
import subprocess
import whisper
from deep_translator import GoogleTranslator
import edge_tts
from gtts import gTTS

# ==========================================
# PAGE CONFIGURATION & DARK STUDIO THEME CSS
# ==========================================
st.set_page_config(
    page_title="Movie Time - AI Khmer Dubbing Pro Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Professional Studio Styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Studio Header */
    .studio-header {
        background: linear-gradient(90deg, #161b22 0%, #21262d 100%);
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    .studio-title {
        color: #58a6ff;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Control Cards */
    .studio-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
    }
    
    /* Subtitle Table Header */
    .sub-table-header {
        background: #21262d;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        color: #f0f6fc;
    }
    
    /* Custom Status Badges */
    .badge-vip {
        background-color: #238636;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .badge-trial {
        background-color: #d29922;
        color: black;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# VIP & LICENSE SYSTEM
# ==========================================
LICENSE_FILE = "license_studio.json"
DEFAULT_VIP_CODES = ["VIP2026", "MOVIETIME_PRO", "BUNYIM_VIP", "VIP8888"]

try:
    VALID_VIP_CODES = st.secrets.get("VIP_CODES", DEFAULT_VIP_CODES)
except Exception:
    VALID_VIP_CODES = DEFAULT_VIP_CODES

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"usage_count": 0, "is_vip": False, "vip_code": ""}

def save_license(data):
    try:
        with open(LICENSE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        pass

license_data = load_license()


# ==========================================
# ASYNC EDGE-TTS KHMER AUDIO GENERATOR
# ==========================================
async def generate_single_audio(text, output_file, voice="km-KH-SreymomNeural", pitch="+0Hz", rate="+0%"):
    clean_text = text.strip() if text else ""
    if not clean_text:
        return False
    try:
        communicate = edge_tts.Communicate(clean_text, voice, pitch=pitch, rate=rate)
        await communicate.save(output_file)
        return os.path.exists(output_file) and os.path.getsize(output_file) > 0
    except Exception:
        pass
    
    # Fallback to gTTS if Edge-TTS fails
    try:
        tts = gTTS(text=clean_text, lang='km', slow=False)
        tts.save(output_file)
        return os.path.exists(output_file) and os.path.getsize(output_file) > 0
    except Exception:
        return False

def generate_khmer_tts(text, output_file, voice="km-KH-SreymomNeural", pitch="+0Hz", rate="+0%"):
    return asyncio.run(generate_single_audio(text, output_file, voice, pitch, rate))


# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/movie-studio.png", width=70)
    st.title("Movie Time Studio Pro")
    st.caption("AI Automatic Video Dubbing & Subtitle Suite")
    
    st.markdown("---")
    st.subheader("🔑 ប្រព័ន្ធសិទ្ធិប្រើប្រាស់ (License)")
    
    vip_code_input = st.text_input("បញ្ចូលលេខកូដ VIP Code:", value=license_data.get("vip_code", ""))
    if st.button("ផ្ទៀងផ្ទាត់កូដ (Verify Code)", use_container_width=True):
        if vip_code_input.strip() in VALID_VIP_CODES:
            license_data["is_vip"] = True
            license_data["vip_code"] = vip_code_input.strip()
            save_license(license_data)
            st.success("🎉 បើកសិទ្ធិ VIP Account រួចរាល់!")
            st.rerun()
        else:
            st.error("❌ កូដមិនត្រឹមត្រូវទេ!")
            
    if license_data.get("is_vip"):
        st.markdown('ស្ថានភាព៖ <span class="badge-vip">VIP UNLIMITED</span>', unsafe_allow_html=True)
    else:
        rem = max(0, 3 - license_data.get("usage_count", 0))
        st.markdown(f'ស្ថានភាព៖ <span class="badge-trial">FREE TRIAL (សល់ {rem} ដង)</span>', unsafe_allow_html=True)
        st.caption("📩 ទាក់ទង Telegram: @yoem bunyim ដើម្បីទិញកូដ")

    st.markdown("---")
    st.subheader("⚙️ ការកំណត់សំឡេង AI (Voice Engine)")
    
    whisper_size = st.selectbox("Whisper Model (STT):", ["base", "small", "medium"], index=0)
    
    voice_gender_mode = st.selectbox(
        "របៀបបែងចែកសំឡេងតួអង្គ:",
        [
            "🎭 ប្រុស-ស្រីឆ្លើយឆ្លងស្វ័យប្រវត្តិ (Multi-Speaker)",
            "👩 សំឡេងស្រីសុទ្ធ (Sreymom Neural)",
            "👨 សំឡេងប្រុសសុទ្ធ (Piseth Neural)"
        ]
    )
    
    speech_rate = st.slider("ល្បឿននិយាយ (Speed):", -20, 20, 0, format="%d%%")
    speech_pitch = st.slider("កម្រិតសំឡេង (Pitch):", -10, 10, 0, format="%dHz")


# ==========================================
# MAIN STUDIO INTERFACE
# ==========================================
st.markdown("""
<div class="studio-header">
    <div class="studio-title">
        🔥 Movie Time Studio Pro - AI Khmer Video Dubber
    </div>
    <div style="color: #8b949e; font-size: 14px; margin-top: 5px;">
        ប្រព័ន្ធបកប្រែ បញ្ចូលសំឡេងប្រុស-ស្រី និងបង្កើត Subtitle ស្វ័យប្រវត្តិ
    </div>
</div>
""", unsafe_allow_html=True)

# Top Bar Action Area
col_up, col_info = st.columns([2, 1])

with col_up:
    uploaded_video = st.file_uploader("📥 ទម្លាក់វីដេអូរឿងនៅទីនេះ (.mp4, .mov, .mkv):", type=["mp4", "mov", "mkv", "avi"])

with col_info:
    st.info("💡 **ណែនាំ៖** ជ្រើសរើសវីដេអូរឿងខ្លីៗ ឬ Trailer ដើម្បីទទួលបានលទ្ធផលលឿនបំផុត និងមានគុណភាពខ្ពស់។")

if uploaded_video is not None:
    
    # Grid Layout for Studio (Left: Preview & Controls | Right: Subtitle Table)
    left_panel, right_panel = st.columns([1, 1.2])
    
    with left_panel:
        st.markdown("<div class="studio-card">", unsafe_allow_html=True)
        st.subheader("📺 Video Preview")
        st.video(uploaded_video)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with right_panel:
        st.markdown("<div class="studio-card">", unsafe_allow_html=True)
        st.subheader("📝 ដំណើរការ និងកែសម្រួល Subtitles (SRT Editor)")
        
        start_process = st.button("⚡ ចាប់ផ្តើមវិភាគ និងបកប្រែ (Start AI Dubbing)", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Main Processing Engine
    if start_process:
        if not license_data.get("is_vip") and license_data.get("usage_count", 0) >= 3:
            st.error("⚠️ អស់ចំនួនដងប្រើប្រាស់ Free Trial ហើយ! សូមបញ្ចូលលេខកូដ VIP ក្នុង Sidebar។")
        else:
            status_box = st.status("🎬 កំពុងដំណើរការ AI Dubbing Studio...", expanded=True)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save Uploaded Video
                input_video_path = os.path.join(temp_dir, "input_media.mp4")
                with open(input_video_path, "wb") as f:
                    f.write(uploaded_video.read())
                    
                # 1. WHISPER SPEECH-TO-TEXT WITH TIMESTAMPS
                status_box.write("🎙️ 1. កំពុងទាញយកសំឡេង និង Timestamp ពីវីដេអូដើម (Whisper STT)...")
                try:
                    model = whisper.load_model(whisper_size)
                    transcribe_res = model.transcribe(input_video_path, verbose=False)
                    segments = transcribe_res.get("segments", [])
                except Exception as e:
                    st.error(f"Whisper Error: {e}")
                    segments = []
                
                if not segments:
                    st.error("⚠️ រកមិនឃើញសំឡេងនិយាយក្នុងវីដេអូនេះទេ។")
                else:
                    # 2. TRANSLATION TO KHMER
                    status_box.write("🌐 2. កំពុងបកប្រែអត្ថបទនីមួយៗជាភាសាខ្មែរ (Google Translation)...")
                    translator = GoogleTranslator(source='auto', target='km')
                    
                    subtitles_data = []
                    for idx, seg in enumerate(segments):
                        orig_text = seg.get("text", "").strip()
                        start_time = seg.get("start", 0)
                        end_time = seg.get("end", 0)
                        
                        if orig_text:
                            try:
                                khmer_text = translator.translate(orig_text)
                                time.sleep(0.1)
                            except Exception:
                                khmer_text = orig_text
                                
                            # Speaker Assignment
                            if "Multi-Speaker" in voice_gender_mode:
                                speaker = "👨 ស្រី (Sreymom)" if idx % 2 == 0 else "👨 ប្រុស (Piseth)"
                                voice_code = "km-KH-SreymomNeural" if idx % 2 == 0 else "km-KH-PisethNeural"
                            elif "ប្រុសសុទ្ធ" in voice_gender_mode:
                                speaker = "👨 ប្រុស (Piseth)"
                                voice_code = "km-KH-PisethNeural"
                            else:
                                speaker = "👩 ស្រី (Sreymom)"
                                voice_code = "km-KH-SreymomNeural"
                                
                            subtitles_data.append({
                                "id": idx + 1,
                                "start": round(start_time, 2),
                                "end": round(end_time, 2),
                                "original": orig_text,
                                "khmer": khmer_text,
                                "speaker": speaker,
                                "voice_code": voice_code
                            })
                    
                    status_box.write("✅ បកប្រែ និងបែងចែកតួអង្គបានជោគជ័យ!")
                    
                    # 3. GENERATE AUDIO TRACKS
                    status_box.write("🔊 3. កំពុងបង្កើតសំឡេងនិយាយខ្មែរតាម Segment (Edge-TTS)...")
                    
                    rate_str = f"{speech_rate:+d}%"
                    pitch_str = f"{speech_pitch:+d}Hz"
                    
                    audio_parts = []
                    for item in subtitles_data:
                        part_file = os.path.join(temp_dir, f"part_{item['id']}.mp3")
                        success = generate_khmer_tts(
                            text=item["khmer"],
                            output_file=part_file,
                            voice=item["voice_code"],
                            pitch=pitch_str,
                            rate=rate_str
                        )
                        if success:
                            audio_parts.append(part_file)
                            
                    # Merge Audio Files
                    full_khmer_audio = os.path.join(temp_dir, "khmer_full.mp3")
                    if audio_parts:
                        with open(full_khmer_audio, "wb") as outfile:
                            for p_file in audio_parts:
                                with open(p_file, "rb") as infile:
                                    outfile.write(infile.read())
                    
                    # 4. REMUX VIDEO WITH FFMPEG
                    status_box.write("🎬 4. កំពុងផ្គុំសំឡេងខ្មែរចូលទៅក្នុងវីដេអូដើម (FFmpeg Remuxing)...")
                    final_video_output = os.path.join(temp_dir, "dubbed_studio_output.mp4")
                    
                    ffmpeg_cmd = [
                        "ffmpeg", "-y",
                        "-i", input_video_path,
                        "-i", full_khmer_audio,
                        "-c:v", "copy",
                        "-map", "0:v:0",
                        "-map", "1:a:0",
                        "-c:a", "aac",
                        final_video_output
                    ]
                    
                    try:
                        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        status_box.update(label="🎉 ដំណើរការ Dubbing វីដេអូបានសម្រេចជោគជ័យ 100%!", state="complete")
                        
                        st.markdown("---")
                        st.subheader("🎉 លទ្ធផលវីដេអូដែលបានបញ្ចូលសំឡេងខ្មែររួចរាល់ (Final Result)")
                        
                        res_col1, res_col2 = st.columns([1.5, 1])
                        
                        with res_col1:
                            if os.path.exists(final_video_output):
                                with open(final_video_output, "rb") as vf:
                                    v_bytes = vf.read()
                                    st.video(v_bytes)
                                    st.download_button(
                                        label="📥 ទាញយកវីដេអូដែល Dub រួច (.mp4)",
                                        data=v_bytes,
                                        file_name="MovieTime_Khmer_Dubbed.mp4",
                                        mime="video/mp4",
                                        type="primary"
                                    )
                                    
                        with res_col2:
                            st.markdown("### 📊 ព័ត៌មាន Subtitle ដើម")
                            st.json(subtitles_data)
                            
                        # Update Usage License Count
                        if not license_data.get("is_vip"):
                            license_data["usage_count"] = license_data.get("usage_count", 0) + 1
                            save_license(license_data)
                            
                    except Exception as ffmpeg_err:
                        st.error(f"⚠️ កំហុសក្នុងដំណាក់កាល FFmpeg Remix: {ffmpeg_err}")
