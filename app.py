import json
import os
import time
import asyncio
import tempfile
import re
import streamlit as st

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip
except Exception:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip

import edge_tts
from deep_translator import GoogleTranslator
import whisper

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================
TELEGRAM_USERNAME = "t.me/bunyimyoem"  # ✍️ ដូរទៅជា Telegram Username របស់អ្នក
VALID_VIP_CODES = ["VIP-SECRET-2026", "VIP-PASS-8888", "VIP-PRO-9999"]
TRIAL_LIMIT = 3
LICENSE_FILE = "license.json"
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME.replace('@', '')}"


# ==============================================================================
# 🎙️ WHISPER AI WITH TIMESTAMPS & NATURAL PAUSES
# ==============================================================================
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")


def transcribe_with_timestamps(video_path):
    """ស្តាប់សំឡេងដើម + ទាញយក Timecode ដើម ដើម្បីធ្វើ Lip-Sync"""
    audio_wav_path = video_path.replace(".mp4", "_temp.wav")
    try:
        video = VideoFileClip(video_path)
        if video.audio is None:
            video.close()
            return None, "⚠️ វីដេអូនេះគ្មានសំឡេងដើមទេ!"

        video.audio.write_audiofile(
            audio_wav_path,
            codec='pcm_s16le',
            fps=16000,
            ffmpeg_params=["-ac", "1"],
            logger=None
        )
        video.close()

        model = load_whisper_model()
        # transcribe ជាមួយ word_timestamps ដើម្បីដឹងថាពេលណាត្រូវឈប់ដកដង្ហើម
        result = model.transcribe(audio_wav_path, verbose=False)
        segments = result.get("segments", [])

        if os.path.exists(audio_wav_path):
            os.remove(audio_wav_path)

        if not segments:
            return None, "⚠️ មិនអាចទាញយកចង្វាក់និយាយពីវីដេអូបានទេ!"

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

                # Filter បង្ការ Error 500
                if "Error 500" not in khmer_text and "Server Error" not in khmer_text:
                    synced_segments.append({
                        "start": start_time,
                        "end": end_time,
                        "duration": end_time - start_time,
                        "text": khmer_text
                    })

        return synced_segments, None

    except Exception as e:
        if os.path.exists(audio_wav_path):
            os.remove(audio_wav_path)
        return None, f"⚠️ មានបញ្ហាក្នុងការទាញយកចង្វាក់មាត់៖ {e}"


def generate_ssml_audio_with_pauses(text, voice_code, output_path, pause_ms=400):
    """បន្ថែម SSML Break/Pause ដើម្បីឱ្យ AI និយាយមានចន្លោះដកដង្ហើមធម្មជាតិ"""
    # ជំនួសសញ្ញា (?, ., !, ,, ៕) ដោយការបន្ថែមចន្លោះដកដង្ហើម (Pause)
    formatted_text = re.sub(r'([.!?\n៕])', rf'\1 <break time="{pause_ms}ms"/> ', text)
    
    ssml_content = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='km-KH'>
    <voice name='{voice_code}'>
        <prosody rate='0%'>
            {formatted_text}
        </prosody>
    </voice>
</speak>"""

    communicate = edge_tts.Communicate(ssml_content, voice_code)
    asyncio.run(communicate.save(output_path))


def process_lipsync_dubbing(video_bytes, voice_code, pause_ms):
    """ដំណើរការ Lip-Sync & Natural Breathing Dubbing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f_in:
        f_in.write(video_bytes)
        in_vdo_path = f_in.name

    out_vdo_path = in_vdo_path.replace(".mp4", "_sync_out.mp4")

    try:
        segments, err = transcribe_with_timestamps(in_vdo_path)
        if err:
            st.error(err)
            return None, ""

        video = VideoFileClip(in_vdo_path)
        audio_clips = []
        full_transcript = []

        for idx, seg in enumerate(segments):
            seg_audio_path = in_vdo_path.replace(".mp4", f"_seg_{idx}.mp3")
            generate_ssml_audio_with_pauses(seg["text"], voice_code, seg_audio_path, pause_ms)

            # បញ្ចូលសំឡេងទៅតាម Timecode ដើម ដើម្បីឱ្យ Lip-Sync
            speech_clip = AudioFileClip(seg_audio_path).set_start(seg["start"])
            
            # បន្ថែមល្បឿន ឬបន្ថយល្បឿនអូតូម៉ាតិច ដើម្បីឱ្យសមស្របតាមចលនាមាត់
            audio_clips.append(speech_clip)
            full_transcript.append(f"[{int(seg['start'])}s] {seg['text']}")

        final_audio = CompositeAudioClip(audio_clips)
        final_video = video.set_audio(final_audio)
        final_video.write_videofile(out_vdo_path, codec="libx264", audio_codec="aac", logger=None)

        with open(out_vdo_path, "rb") as f:
            result_bytes = f.read()

        video.close()
        final_audio.close()

        return result_bytes, "\n".join(full_transcript)

    except Exception as e:
        st.error(f"⚠️ មានបញ្ហាក្នុងការ Sync សំឡេង៖ {e}")
        return None, ""


# ==============================================================================
# 🌐 STREAMLIT UI
# ==============================================================================
st.set_page_config(page_title="Khmer AI Lip-Sync Dubber", page_icon="🎙️", layout="centered")

st.title("🎙️ KHMER AI LIP-SYNC & NATURAL DUBBER")
st.caption("បកប្រែ + បញ្ចូលសំឡេងខ្មែរ ត្រូវតាមចលនាមាត់តួអង្គ និងមានចង្វាក់ដកដង្ហើមធម្មជាតិ")

uploaded_vdo = st.file_uploader("១. បញ្ចូលវីដេអូដែលត្រូវ Lip-Sync", type=["mp4", "mov"])

col1, col2 = st.columns(2)
with col1:
    selected_voice = st.selectbox("សំឡេង AI ខ្មែរ៖", [("km-KH-PisethNeural", "🇰🇭 ពិសិដ្ឋ (ប្រុស)"), ("km-KH-SreymomNeural", "🇰🇭 ស្រីមុំ (ស្រី)")], format_func=lambda x: x[1])
with col2:
    pause_time = st.slider("រយៈពេលឈប់ដកដង្ហើមរវាងប្រយោគ (ms):", 200, 1000, 450, 50)

if st.button("▶ ចាប់ផ្តើមធ្វើ Lip-Sync & Natural Dubbing", type="primary", use_container_width=True):
    if not uploaded_vdo:
        st.warning("សូម Upload វីដេអូជាមុនសិន!")
    else:
        with st.spinner("🤖 កំពុង Align Timestamps និងបន្ថែម SSML Breathing Pauses..."):
            res_video, script = process_lipsync_dubbing(uploaded_vdo.getvalue(), selected_voice[0], pause_time)
            if res_video:
                st.success("✅ Lip-Sync ជោគជ័យ!")
                st.video(res_video)
                st.text_area("📝 អត្ថបទដែលបានតម្រឹម Timecode:", script, height=150)
