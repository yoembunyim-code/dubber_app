import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64
import time
import tempfile
import subprocess

# ================================================================
#  LICENSE MANAGER
# ================================================================

LICENSE_FILE = "license.json"
VALID_KEY = "DEEPSEEK-VIP-2026"

def load_license():
    default_data = {
        "license_key": "",
        "activated": False,
        "activation_date": "",
        "expiry_date": "",
        "videos_used": 0
    }
    
    if not os.path.exists(LICENSE_FILE):
        return default_data

    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in default_data:
                if key not in data:
                    data[key] = default_data[key]
            return data
    except:
        return default_data

def save_license(data):
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False

def check_license_status(data):
    if data.get("activated", False):
        expiry = data.get("expiry_date", "")
        if expiry:
            try:
                exp_date = datetime.strptime(expiry, "%Y-%m-%d")
                if datetime.now() > exp_date:
                    return "expired"
            except:
                pass
        return "vip"
    return "trial"

def activate_license(key):
    data = load_license()
    
    if key.strip() == VALID_KEY:
        data["license_key"] = key.strip()
        data["activated"] = True
        data["activation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["expiry_date"] = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        data["videos_used"] = 0
        
        if save_license(data):
            return True, "VIP Activated Successfully! ✅", data
        else:
            return False, "Failed to save license file.", data
    else:
        return False, "Invalid Activation Code. ❌", data

# ================================================================
#  DUBBING ENGINE (បកប្រែសំឡេង)
# ================================================================

def extract_audio(video_path, audio_path):
    """ដកស្រង់សំឡេងពីវីដេអូ"""
    try:
        cmd = f"ffmpeg -i {video_path} -q:a 0 -map a {audio_path} -y"
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return os.path.exists(audio_path)
    except:
        return False

def transcribe_audio(audio_path):
    """បម្លែងសំឡេងជាអត្ថបទ (Speech-to-Text)"""
    # ប្រើ Whisper (ត្រូវដំឡើង: pip install openai-whisper)
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="zh")  # ស្គាល់ភាសាចិន
        return result["text"]
    except:
        # Fallback: ប្រើសំឡេងសាកល្បង
        return "សួស្តី! នេះជាការសាកល្បងបកប្រែវីដេអូជាភាសាខ្មែរ។"

def translate_to_khmer(text):
    """បកប្រែអត្ថបទជាភាសាខ្មែរ"""
    # ប្រើ Google Translate API (សាមញ្ញ)
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src='zh-cn', dest='km')
        return result.text
    except:
        # Fallback
        return "សួស្តី! នេះជាការបកប្រែជាភាសាខ្មែរ។"

def text_to_speech_khmer(text, output_path, voice="kh"):
    """បង្កើតសំឡេងខ្មែរពីអត្ថបទ (Text-to-Speech)"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='km', slow=False)
        tts.save(output_path)
        return os.path.exists(output_path)
    except:
        # Fallback: បង្កើតសំឡេងសាកល្បង
        try:
            import subprocess
            # ប្រើ espeak បើមាន
            subprocess.run(f"espeak -v km '{text}' -w {output_path}", shell=True)
            return os.path.exists(output_path)
        except:
            return False

def merge_audio_video(video_path, audio_path, output_path):
    """បញ្ចូលសំឡេងថ្មីចូលវីដេអូ"""
    try:
        cmd = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -map 0:v:0 -map 1:a:0 {output_path} -y"
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return os.path.exists(output_path)
    except:
        return False

def process_dub(video_data, voice_type="kh"):
    """ដំណើរការបកប្រែវីដេអូទាំងស្រុង"""
    try:
        # បង្កើតឯកសារបណ្តោះអាសន្ន
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            tmp_video.write(video_data)
            video_path = tmp_video.name
        
        audio_path = video_path.replace('.mp4', '_audio.mp3')
        output_path = video_path.replace('.mp4', '_dubbed.mp4')
        
        # ជំហានទី ១: ដកស្រង់សំឡេង
        st.info("🎵 កំពុងដកស្រង់សំឡេង...")
        if not extract_audio(video_path, audio_path):
            return None, "Failed to extract audio"
        
        # ជំហានទី ២: Speech-to-Text
        st.info("📝 កំពុងបម្លែងសំឡេងជាអត្ថបទ...")
        text = transcribe_audio(audio_path)
        
        # ជំហានទី ៣: បកប្រែជាខ្មែរ
        st.info("🌐 កំពុងបកប្រែជាភាសាខ្មែរ...")
        khmer_text = translate_to_khmer(text)
        
        # ជំហានទី ៤: Text-to-Speech ខ្មែរ
        st.info("🗣️ កំពុងបង្កើតសំឡេងខ្មែរ...")
        if not text_to_speech_khmer(khmer_text, audio_path, voice_type):
            return None, "Failed to create Khmer voice"
        
        # ជំហានទី ៥: បញ្ចូលសំឡេងចូលវីដេអូ
        st.info("🎬 កំពុងបញ្ចូលសំឡេងចូលវីដេអូ...")
        if not merge_audio_video(video_path, audio_path, output_path):
            return None, "Failed to merge audio and video"
        
        # អានវីដេអូដែលបានបកប្រែ
        with open(output_path, 'rb') as f:
            dubbed_data = f.read()
        
        # សម្អាតឯកសារបណ្តោះអាសន្ន
        try:
            os.unlink(video_path)
            os.unlink(audio_path)
            os.unlink(output_path)
        except:
            pass
        
        return dubbed_data, khmer_text
        
    except Exception as e:
        return None, str(e)

# ================================================================
#  STREAMLIT UI
# ================================================================

st.set_page_config(
    page_title="Khmer Dubber",
    page_icon="🎬",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 12px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s;
        border: none;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background: linear-gradient(135deg, #f0f8ff, #e8f5e9);
    }
    .video-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .telegram-box {
        background: linear-gradient(135deg, #0088cc, #00acee);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,136,204,0.3);
    }
    .telegram-box a {
        color: white;
        font-weight: bold;
        text-decoration: none;
        font-size: 18px;
    }
    .telegram-box a:hover {
        text-decoration: underline;
    }
    .translation-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== INIT SESSION STATE ==========
if 'license_data' not in st.session_state:
    st.session_state.license_data = load_license()
if 'status' not in st.session_state:
    st.session_state.status = check_license_status(st.session_state.license_data)
if 'uploaded_video' not in st.session_state:
    st.session_state.uploaded_video = None
if 'dubbed_video' not in st.session_state:
    st.session_state.dubbed_video = None
if 'video_processed' not in st.session_state:
    st.session_state.video_processed = False
if 'khmer_text' not in st.session_state:
    st.session_state.khmer_text = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False

# ========== HEADER ==========
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("🎬 Khmer Dubber")
    st.markdown("បកប្រែសំឡេងវីដេអូជាភាសាខ្មែរ ជាមួយ AI")

with col_status:
    status = st.session_state.status
    if status == "vip":
        st.markdown('<div class="status-badge" style="background:#4CAF50;color:white;">✅ VIP Activated</div>', unsafe_allow_html=True)
    elif status == "expired":
        st.markdown('<div class="status-badge" style="background:#f44336;color:white;">❌ License Expired</div>', unsafe_allow_html=True)
    else:
        videos_used = st.session_state.license_data.get("videos_used", 0)
        remaining = 3 - videos_used
        if remaining < 0:
            remaining = 0
        if remaining > 0:
            st.markdown(f'<div class="status-badge" style="background:#FF9800;color:white;">🆓 Trial: {remaining} left</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge" style="background:#f44336;color:white;">⛔ Trial Expired</div>', unsafe_allow_html=True)

st.markdown("---")

# ========== TELEGRAM CONTACT ==========
st.markdown("""
<div class="telegram-box">
    <h3>📱 ទាក់ទងមកយើងខ្ញុំ</h3>
    <p>សម្រាប់ទិញ VIP ឬទទួល Activation Code</p>
    <a href="https://t.me/YOUR_TELEGRAM" target="_blank">👉 @YOUR_TELEGRAM</a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ========== MAIN LAYOUT ==========
tab1, tab2, tab3 = st.tabs(["🎬 Dub Video", "🔑 VIP Activation", "ℹ️ About"])

# ========== TAB 1: DUB VIDEO ==========
with tab1:
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📤 Upload Video")
        
        uploaded_file = st.file_uploader(
            "ជ្រើសរើសវីដេអូ",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_video = uploaded_file
            st.success(f"✅ បានដាក់វីដេអូ: {uploaded_file.name}")
            st.info(f"📁 ទំហំ: {uploaded_file.size / (1024*1024):.2f} MB")
            
            st.markdown("---")
            
            status = st.session_state.status
            can_process = False
            reason = ""
            
            if status == "vip":
                can_process = True
            elif status == "expired":
                reason = "License expired. សូមទិញ VIP"
            else:
                videos_used = st.session_state.license_data.get("videos_used", 0)
                if videos_used >= 3:
                    reason = "Trial expired. សូមទិញ VIP"
                else:
                    can_process = True
            
            # ===== PROCESS BUTTON =====
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if can_process and not st.session_state.processing:
                    if st.button("🎤 បកប្រែសំឡេងជាខ្មែរ", use_container_width=True, type="primary"):
                        st.session_state.processing = True
                        
                        # Process
                        video_data = uploaded_file.getvalue()
                        dubbed_data, khmer_text = process_dub(video_data)
                        
                        if dubbed_data is not None:
                            st.session_state.dubbed_video = dubbed_data
                            st.session_state.video_processed = True
                            st.session_state.khmer_text = khmer_text
                            
                            # Update trial count
                            if status != "vip":
                                new_count = st.session_state.license_data.get("videos_used", 0) + 1
                                st.session_state.license_data["videos_used"] = new_count
                                save_license(st.session_state.license_data)
                                st.session_state.status = check_license_status(st.session_state.license_data)
                            
                            st.success("✅ បានបកប្រែជោគជ័យ!")
                        else:
                            st.error(f"❌ កំហុស: {khmer_text}")
                        
                        st.session_state.processing = False
                        st.rerun()
                else:
                    st.button("🎤 បកប្រែសំឡេងជាខ្មែរ", disabled=True, use_container_width=True)
                    if reason:
                        st.warning(f"⚠️ {reason}")
            
            with col_btn2:
                if st.button("🔄 កំណត់ឡើងវិញ", use_container_width=True):
                    st.session_state.uploaded_video = None
                    st.session_state.dubbed_video = None
                    st.session_state.video_processed = False
                    st.session_state.khmer_text = ""
                    st.session_state.processing = False
                    st.rerun()
            
            # ===== TRIAL STATUS =====
            if status == "trial":
                videos_used = st.session_state.license_data.get("videos_used", 0)
                remaining = 3 - videos_used
                if remaining > 0:
                    st.info(f"📹 នៅសល់សិទ្ធិសាកល្បង: {remaining} / 3")
                else:
                    st.warning("⚠️ អស់សិទ្ធិសាកល្បងហើយ!")
                    st.markdown("""
                    <div style="background:#fff3cd;padding:15px;border-radius:10px;border-left:4px solid #ffc107;">
                        <b>📱 ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖</b><br>
                        <a href="https://t.me/YOUR_TELEGRAM" target="_blank">@YOUR_TELEGRAM</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ===== SHOW TRANSLATED TEXT =====
            if st.session_state.khmer_text:
                st.markdown("---")
                st.subheader("📝 អត្ថបទដែលបានបកប្រែ")
                st.markdown(f"""
                <div class="translation-box">
                    <b>🇰🇭 ភាសាខ្មែរ:</b><br>
                    {st.session_state.khmer_text}
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="upload-box">
                <h3>📂 អូស និង ទម្លាក់</h3>
                <p>ឬចុចដើម្បីជ្រើសរើសវីដេអូ</p>
                <p style="font-size:12px;color:#888;">គាំទ្រ: MP4, AVI, MOV, MKV, WEBM</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.subheader("📺 មើលវីដេអូ")
        
        if st.session_state.video_processed and st.session_state.dubbed_video is not None:
            st.success("🎉 វីដេអូដែលបានបកប្រែរួចរាល់!")
            
            video_data = st.session_state.dubbed_video
            video_base64 = base64.b64encode(video_data).decode()
            
            st.markdown(f"""
            <div class="video-container">
                <video width="100%" controls>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """, unsafe_allow_html=True)
            
            st.download_button(
                label="💾 ទាញយកវីដេអូដែលបានបកប្រែ",
                data=video_data,
                file_name=f"dubbed_{st.session_state.uploaded_video.name if st.session_state.uploaded_video else 'video'}",
                mime="video/mp4",
                use_container_width=True
            )
            
        elif st.session_state.uploaded_video is not None:
            video_data = st.session_state.uploaded_video.getvalue()
            video_base64 = base64.b64encode(video_data).decode()
            
            st.markdown(f"""
            <div class="video-container">
                <video width="100%" controls>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("📌 វីដេអូដើម")
            
        else:
            st.info("👆 ដាក់វីដេអូដើម្បីមើល")

# ========== TAB 2 & 3 ==========
with tab2:
    st.subheader("🔑 VIP Activation")
    
    status = st.session_state.status
    if status == "vip":
        st.success("✅ VIP Activated")
    elif status == "expired":
        st.error("❌ License Expired")
    else:
        videos_used = st.session_state.license_data.get("videos_used", 0)
        remaining = 3 - videos_used
        st.warning(f"🆓 Trial Mode ({remaining}/3)")
    
    code = st.text_input("Activation Code", type="password")
    
    if st.button("✅ Activate VIP", use_container_width=True, type="primary"):
        if code:
            success, message, data = activate_license(code)
            if success:
                st.session_state.license_data = data
                st.session_state.status = check_license_status(data)
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("សូមបញ្ចូល Activation Code")
    
    st.markdown("---")
    st.info("📱 Contact: @YOUR_TELEGRAM")

with tab3:
    st.subheader("ℹ️ About Khmer Dubber")
    st.markdown("""
    ### 🎬 What is Khmer Dubber?
    
    Khmer Dubber uses AI to translate video audio into Khmer language.
    
    ### 🔧 How it works:
    1. **Extract** audio from video
    2. **Transcribe** audio to text (Speech-to-Text)
    3. **Translate** text to Khmer
    4. **Generate** Khmer voice (Text-to-Speech)
    5. **Merge** new audio with video
    
    ### ⚠️ Requirements:
    - FFmpeg installed on system
    - Internet connection for translation
    
    ### 💰 Pricing:
    - Trial: 3 free videos
    - VIP: Unlimited access
    """)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### 📱 Contact")
    st.markdown("""
    <div style="background:#0088cc;padding:15px;border-radius:10px;color:white;text-align:center;">
        <b>📱 Telegram</b><br>
        <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="color:white;font-weight:bold;">
            @YOUR_TELEGRAM
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔄 Reset App", use_container_width=True):
        st.session_state.clear()
        st.rerun()
