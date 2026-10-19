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

# បញ្ជី VIP Codes សារថ្មី (អ្នកអាចបន្ថែម ឬកែប្រែត្រង់នេះបាន)
DEFAULT_VIP_CODES = ["VIP2026", "KHMER_DUB_VIP", "BUNYIM_PRO", "VIP8888", "KHMER2026"]

try:
    VALID_VIP_CODES = st.secrets.get("VIP_CODES", DEFAULT_VIP_CODES)
except Exception:
    VALID_VIP_CODES = DEFAULT_VIP_CODES


# ==========================================
# LICENSE & VIP MANAGEMENT
# ==========================================
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
        st.error(f"មិនអាចរក្សាទុកព័ត៌មានអាជ្ញាបណ្ណបានទេ: {e}")

license_data = load_license()


# ==========================================
# TEXT-TO-SPEECH (EDGE TTS) ENGINE
# ==========================================
async def generate_khmer_audio(text, output_file, voice="km-KH-SreymomNeural"):
    """
    បង្កើតសំឡេងនិយាយភាសាខ្មែរចេញពីអត្ថបទ ដោយមានការពិនិត្យការពារកុំឱ្យមាន error ប្រសិនបើអត្ថបទទទេ
    """
    clean_text = text.strip() if text else ""
    if not clean_text:
        st.warning("⚠️ មិនមានអត្ថបទសម្រាប់បកប្រែបង្កើតជាសំឡេងទេ។")
        return False

    try:
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        st.error(f"⚠️ មានបញ្ហាក្នុងការបង្កើតសំឡេង (Edge TTS): {e}")
        return False

def text_to_speech_khmer(text, output_file, voice="km-KH-SreymomNeural"):
    return asyncio.run(generate_khmer_audio(text, output_file, voice))


# ==========================================
# STREAMLIT UI LAYOUT
# ==========================================
st.set_page_config(page_title="AI Khmer Auto Dubber Pro", page_icon="🎬", layout="wide")

st.title("🎬 AI Khmer Auto Dubber Pro")
st.caption("កម្មវិធីស្វ័យប្រវត្តិបកប្រែ និងបញ្ចូលសំឡេងវីដេអូជាភាសាខ្មែរ")

# --- SIDEBAR: VIP & SETTINGS ---
st.sidebar.header("🔑 ប្រព័ន្ធអាជ្ញាបណ្ណ & VIP")

vip_input = st.sidebar.text_input("បញ្ចូលលេខកូដ VIP៖", value=license_data.get("vip_code", ""))
if st.sidebar.button("ផ្ទៀងផ្ទាត់ VIP"):
    if vip_input.strip() in VALID_VIP_CODES:
        license_data["is_vip"] = True
        license_data["vip_code"] = vip_input.strip()
        save_license(license_data)
        st.sidebar.success("🎉 អ្នកបានបើកប្រើប្រាស់មុខងារ VIP ជោគជ័យ!")
    else:
        st.sidebar.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវទេ!")

if license_data.get("is_vip"):
    st.sidebar.info("🌟 ស្ថានភាព៖ **VIP Account** (មិនមានដែនកំណត់)")
else:
    remaining = max(0, TRIAL_VIDEO_LIMIT - license_data.get("usage_count", 0))
    st.sidebar.warning(f"⏳ ស្ថានភាព៖ **Free Trial** (សល់ {remaining}/{TRIAL_VIDEO_LIMIT} វីដេអូ)")
    st.sidebar.markdown(f"📩 ទាក់ទងទិញកូដ VIP: [{CONTACT_TELEGRAM}]({TELEGRAM_LINK})")

st.sidebar.hr()
st.sidebar.header("⚙️ ការកំណត់សំឡេង និង Model")
whisper_model_type = st.sidebar.selectbox("ជ្រើសរើស Whisper Model:", ["tiny", "base", "small", "medium"], index=1)
khmer_voice = st.sidebar.selectbox("ជ្រើសរើសសំឡេងខ្មែរ:", ["km-KH-SreymomNeural", "km-KH-PisethNeural"])


# ==========================================
# MAIN DUBBING PROCESS
# ==========================================
uploaded_file = st.file_uploader("បញ្ចូលវីដេអូរបស់អ្នក (.mp4, .mov, .avi):", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # ពិនិត្យលក្ខខណ្ឌប្រើប្រាស់ Trial
    if not license_data.get("is_vip") and license_data.get("usage_count", 0) >= TRIAL_VIDEO_LIMIT:
        st.error("⚠️ អ្នកបានប្រើប្រាស់អស់ចំនួនដង Free Trial ហើយ! សូមបញ្ចូលលេខកូដ VIP ដើម្បីបន្តប្រើប្រាស់។")
    else:
        st.video(uploaded_file)
        
        if st.button("🚀 ចាប់ផ្តើមបញ្ចូលសំឡេងខ្មែរ"):
            with st.spinner("កំពុងដំណើរការទាញយក និងបកប្រែសំឡេង..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # ១. រក្សាទុកវីដេអូជាបណ្តោះអាសន្ន
                    input_video_path = os.path.join(temp_dir, "input_video.mp4")
                    with open(input_video_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # ២. ដំណើរការ Whisper រកមើលអត្ថបទនិយាយ
                    st.info("🎙️ កំពុងទាញយកអត្ថបទនិយាយចេញពីវីដេអូ (Speech-to-Text)...")
                    model = whisper.load_model(whisper_model_type)
                    result = model.transcribe(input_video_path)
                    
                    full_text = result.get("text", "").strip()

                    if not full_text:
                        st.error("⚠️ បរាជ័យ៖ មិនអាចចាប់យកសំឡេងនិយាយក្នុងវីដេអូបានទេ។ សូមពិនិត្យមើលថាតើវីដេអូនោះមានសំឡេងនិយាយច្បាស់លាស់ដែរឬទេ។")
                    else:
                        st.write("**អត្ថបទដើមដែលចាប់បាន៖**", full_text)

                        # ៣. បកប្រែជាភាសាខ្មែរ
                        st.info("🌐 កំពុងបកប្រែជាភាសាខ្មែរ...")
                        translator = GoogleTranslator(source='auto', target='km')
                        translated_text = translator.translate(full_text)
                        st.write("**អត្ថបទបកប្រែជាភាសាខ្មែរ៖**", translated_text)

                        # ៤. បង្កើតសំឡេងនិយាយភាសាខ្មែរ (TTS)
                        output_audio_path = os.path.join(temp_dir, "khmer_audio.mp3")
                        st.info("🔊 កំពុងបង្កើតសំឡេងនិយាយភាសាខ្មែរ...")
                        
                        tts_success = text_to_speech_khmer(translated_text, output_audio_path, voice=khmer_voice)

                        if tts_success and os.path.exists(output_audio_path):
                            st.audio(output_audio_path)
                            st.success("✅ បង្កើតសំឡេងបញ្ចូលជាភាសាខ្មែរបានជោគជ័យ!")

                            # កើនចំនួនប្រើប្រាស់ប្រសិនបើជា Free User
                            if not license_data.get("is_vip"):
                                license_data["usage_count"] = license_data.get("usage_count", 0) + 1
                                save_license(license_data)
                        else:
                            st.error("⚠️ មិនអាចបង្កើតសំឡេងបានទេ។ No audio was received. Please verify that your parameters are correct.")
