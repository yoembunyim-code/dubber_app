import json
import os
import time
import asyncio
import tempfile
import streamlit as st

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
except Exception:
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

import edge_tts
from deep_translator import GoogleTranslator
import whisper

# ==============================================================================
# ⚙️ CONFIGURATION & VIP SYSTEM
# ==============================================================================
TELEGRAM_USERNAME = "bunyim"  # ✍️ ដូរទៅជា Username Telegram របស់អ្នក
VALID_VIP_CODES = [
    "VIP-SECRET-2026",
    "VIP-PASS-8888",
    "VIP-PRO-9999",
    "CAM-VIP-1234"
]

TRIAL_LIMIT = 3
LICENSE_FILE = "license.json"

clean_telegram = TELEGRAM_USERNAME.replace("@", "").strip()
TELEGRAM_LINK = f"https://t.me/{clean_telegram}"


# ==============================================================================
# 🛡️ LICENSE MANAGER
# ==============================================================================
def load_license():
    default = {"license_key": "", "activated": False, "expiry_date": "", "trial_used": 0}
    if not os.path.exists(LICENSE_FILE):
        return default
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_license(data):
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def activate_vip(code):
    if code.strip() in VALID_VIP_CODES:
        data = load_license()
        data["license_key"] = code
        data["activated"] = True
        save_license(data)
        return True, "🎉 បើកប្រើប្រាស់ VIP ជោគជ័យ! អ្នកអាចប្រើបានគ្មានដែនកំណត់។"
    return False, "⚠️ VIP Code មិនត្រឹមត្រូវទេ! សូមទាក់ទង Admin តាម Telegram។"


# ==============================================================================
# 🎙️ WHISPER AI TRANSCRIPTION & TRANSLATION
# ==============================================================================
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")


def transcribe_video_segments(video_path):
    """ស្តាប់សំឡេងតួអង្គ និងទាញយក Timecode យ៉ាងជាក់លាក់"""
    audio_wav_path = video_path.replace(".mp4", "_temp.wav")
    try:
        video = VideoFileClip(video_path)
        if video.audio is None:
            video.close()
            return None, "⚠️ វីដេអូនេះគ្មានសំឡេងដើមទេ!"

        # ទាញយកសំឡេងជា WAV ធម្មតា بۆ Whisper စစ်ဆေး
        video.audio.write_audiofile(
            audio_wav_path,
            codec='pcm_s16le',
            fps=16000,
            ffmpeg_params=["-ac", "1"],
            logger=None
        )
        video.close()

        model = load_whisper_model()
        result = model.transcribe(audio_wav_path, verbose=False)
        segments = result.get("segments", [])

        if os.path.exists(audio_wav_path):
            os.remove(audio_wav_path)

        if not segments:
            return None, "⚠️ មិនអាចចាប់យល់សំឡេងនិយាយក្នុងវីដេអូបានទេ!"

        synced_segments = []
        for seg in segments:
            text = seg["text"].strip()
            start_time = seg["start"]
            end_time = seg["end"]
            
            if text:
                try:
                    khmer_text = GoogleTranslator(source='auto', target='km').translate(text)
                except Exception:
                    khmer_text = text

                if "Error 500" not in khmer_text and "Server Error" not in khmer_text:
                    synced_segments.append({
                        "start": start_time,
                        "end": end_time,
                        "text": khmer_text
                    })

        return synced_segments, None

    except Exception as e:
        if os.path.exists(audio_wav_path):
            os.remove(audio_wav_path)
        return None, f"⚠️ មានបញ្ហាក្នុងការទាញយកសំឡេង៖ {e}"


def generate_tts_audio(text, voice_code, output_path):
    """បង្កើតសំឡេង AI ខ្មែរស្អាតគ្មានសំឡេងរំខាន"""
    communicate = edge_tts.Communicate(text, voice_code)
    asyncio.run(communicate.save(output_path))


def process_clean_dubbing(video_bytes, voice_code):
    """កាត់សំឡេងដើម និងសំឡេងរំខានចេញទាំងស្រុង ដាក់បញ្ចូលតែសំឡេង AI សុទ្ធ"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f_in:
        f_in.write(video_bytes)
        in_vdo_path = f_in.name

    out_vdo_path = in_vdo_path.replace(".mp4", "_clean_out.mp4")

    try:
        segments, err = transcribe_video_segments(in_vdo_path)
        if err:
            st.error(err)
            return None, ""

        # បើកវីដេអូដើម ប៉ុន្តែដកសំឡេងដើមចេញទាំងស្រុង (remove_audio())
        video = VideoFileClip(in_vdo_path).remove_audio()
        audio_clips = []
        full_transcript = []

        for idx, seg in enumerate(segments):
            seg_audio_path = in_vdo_path.replace(".mp4", f"_seg_{idx}.mp3")
            
            # បង្កើតសំឡេង AI សម្រាប់ប្រយោគនីមួយៗ
            generate_tts_audio(seg["text"], voice_code, seg_audio_path)

            # កំណត់ទីតាំងសំឡេង AI ឱ្យចេញចំពេលតួអង្គនិយាយ
            speech_clip = AudioFileClip(seg_audio_path).set_start(seg["start"])
            audio_clips.append(speech_clip)
            
            full_transcript.append(f"[{int(seg['start'])}s] {seg['text']}")

        # ដាក់បញ្ចូលតែសំឡេង AI សុទ្ធចូលទៅក្នុងវីដេអូ
        final_audio = CompositeAudioClip(audio_clips)
        final_video = video.set_audio(final_audio)
        
        final_video.write_videofile(out_vdo_path, codec="libx264", audio_codec="aac", logger=None)

        with open(out_vdo_path, "rb") as f:
            result_bytes = f.read()

        video.close()
        final_audio.close()

        return result_bytes, "\n".join(full_transcript)

    except Exception as e:
        st.error(f"⚠️ មានបញ្ហាក្នុងការបង្កើតវីដេអូ៖ {e}")
        return None, ""


# ==============================================================================
# 🌐 STREAMLIT UI INTERFACE
# ==============================================================================
st.set_page_config(page_title="Khmer AI Pure Dubber", page_icon="🎙️", layout="centered")

if "lic" not in st.session_state:
    st.session_state.lic = load_license()
if "vdo" not in st.session_state:
    st.session_state.vdo = None
if "txt" not in st.session_state:
    st.session_state.txt = ""

lic = st.session_state.lic
is_vip = lic.get("activated", False)
rem_trials = max(0, TRIAL_LIMIT - lic.get("trial_used", 0))

st.title("🎙️ KHMER AI PURE DUBBER (NO NOISE)")
st.caption("កាត់សំឡេងដើម និងសំឡេងរំខានចេញទាំងស្រុង យកតែសំឡេង AI ខ្មែរនិយាយតាមតួអង្គសុទ្ធៗ")

# 📲 Telegram Contact
st.link_button("💬 ទាក់ទង Admin តាម Telegram (ដើម្បីទិញ VIP Code)", TELEGRAM_LINK, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 🔑 VIP Activation
with st.expander("🔑 ផ្ទាំងបញ្ចូល VIP Code ចូលប្រើប្រាស់", expanded=not is_vip):
    col1, col2 = st.columns([3, 1])
    code_in = col1.text_input("VIP Code", placeholder="បញ្ចូលលេខកូដ VIP...", label_visibility="collapsed")
    if col2.button("Activate", type="primary", use_container_width=True):
        ok, msg = activate_vip(code_in)
        if ok:
            st.session_state.lic = load_license()
            st.success(msg)
            time.sleep(1)
            st.rerun()
        else:
            st.error(msg)

if is_vip:
    st.success("ស្ថានភាព៖ VIP Member ✅ (ប្រើប្រាស់បានរហូត គ្មានដែនកំណត់)")
elif rem_trials > 0:
    st.warning(f"ស្ថានភាព៖ សាកល្បងឥតគិតថ្លៃ ⏳ (នៅសល់ {rem_trials}/{TRIAL_LIMIT} វីដេអូ)")
else:
    st.error("ស្ថានភាព៖ អស់សិទ្ធិសាកល្បងហើយ 🚫 (សូមទាក់ទង Admin តាម Telegram ដើម្បីទិញ VIP Code)")

st.markdown("---")

# 1. Video Upload
uploaded_vdo = st.file_uploader("១. បញ្ចូលវីដេអូ (MP4/MOV)", type=["mp4", "mov"])

# 2. Voice Selection
selected_voice = st.selectbox(
    "២. ជ្រើសរើសសំឡេង AI ខ្មែរ៖",
    options=[
        ("km-KH-PisethNeural", "🇰🇭 ពិសិដ្ឋ (សំឡេងប្រុស)"),
        ("km-KH-SreymomNeural", "🇰🇭 ស្រីមុំ (សំឡេងស្រី)")
    ],
    format_func=lambda x: x[1]
)

st.markdown("---")

# 3. Action Button
can_run = is_vip or (rem_trials > 0)

if st.button("▶ ចាប់ផ្តើមបកប្រែ (កាត់សំឡេងរំខានចេញ យកតែសំឡេង AI សុទ្ធ)", disabled=not can_run, type="primary", use_container_width=True):
    if not uploaded_vdo:
        st.warning("សូម Upload វីដេអូជាមុនសិន!")
    else:
        with st.spinner("🤖 កំពុងកាត់សំឡេងដើមនិងសំឡេងរំខានចេញ រួចបញ្ចូលសំឡេង AI ខ្មែរសុទ្ធ..."):
            res_video, script = process_clean_dubbing(uploaded_vdo.getvalue(), selected_voice[0])
            
            if res_video:
                st.session_state.vdo = res_video
                st.session_state.txt = script
                
                if not is_vip:
                    lic["trial_used"] += 1
                    save_license(lic)
                    st.session_state.lic = lic
                
                st.success("✅ បកប្រែរួចរាល់ លុបសំឡេងរំខាន ១០០%!")
                time.sleep(0.5)
                st.rerun()

# 4. Results
if st.session_state.vdo:
    st.markdown("---")
    st.subheader("🎉 លទ្ធផលវីដេអូដែលធ្វើរួច៖")
    st.video(st.session_state.vdo)
    st.text_area("📝 អត្ថបទដែលបានបកប្រែជាខ្មែរ៖", st.session_state.txt, height=150)
    st.download_button(
        label="📥 ទាញយកវីដេអូទុក (Download Video)",
        data=st.session_state.vdo,
        file_name="pure_dubbed_video.mp4",
        mime="video/mp4",
        use_container_width=True
    )

st.markdown("---")
st.link_button("💬 មានចម្ងល់ ឬចង់ទិញ VIP Code? ទាក់ទង Admin តាម Telegram", TELEGRAM_LINK, use_container_width=True)
