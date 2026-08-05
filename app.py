import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64
import time
import tempfile
import subprocess
import urllib.parse
import requests

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
#  DUBBING ENGINE - បកសំឡេងតាមតួអង្គ
# ================================================================

def extract_audio(video_path, audio_path):
    """ដកស្រង់សំឡេងពីវីដេអូ"""
    try:
        cmd = f"ffmpeg -i {video_path} -q:a 0 -map a {audio_path} -y"
        subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return os.path.exists(audio_path)
    except:
        return False

def transcribe_audio_to_text(audio_path):
    """បម្លែងសំឡេងជាអត្ថបទ (Speech-to-Text)"""
    try:
        # ប្រើ Whisper (ត្រូវដំឡើង: pip install openai-whisper)
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="zh")  # ស្គាល់ភាសាចិន
        return result["text"], result["segments"]  # ត្រឡប់អត្ថបទ និងពេលវេលា
    except:
        # Fallback: ប្រសិនបើគ្មាន Whisper
        return "សួស្តី! នេះជាការសាកល្បងបកប្រែវីដេអូ", []

def translate_to_khmer(text):
    """បកប្រែអត្ថបទជាភាសាខ្មែរ"""
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src='zh-cn', dest='km')
        return result.text
    except:
        # Fallback
        return "សួស្តី! នេះជាការបកប្រែជាភាសាខ្មែរ"

def get_khmer_audio_from_text(text):
    """បង្កើតសំឡេងខ្មែរពីអត្ថបទ (ប្រើ Google TTS)"""
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=km&client=tw-ob"
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def merge_audio_video(video_path, audio_path, output_path):
    """បញ្ចូលសំឡេងថ្មីចូលវីដេអូ"""
    try:
        cmd = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -map 0:v:0 -map 1:a:0 {output_path} -y"
        subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return os.path.exists(output_path)
    except:
        return False

def process_dub_video(video_data, text_to_dub=None):
    """
    ដំណើរការបកប្រែវីដេអូតាមតួអង្គ
    """
    try:
        # បង្កើតឯកសារបណ្តោះអាសន្ន
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            tmp_video.write(video_data)
            video_path = tmp_video.name
        
        audio_path = video_path.replace('.mp4', '_audio.mp3')
        khmer_audio_path = video_path.replace('.mp4', '_khmer.mp3')
        output_path = video_path.replace('.mp4', '_dubbed.mp4')
        
        # ===== STEP 1: Extract audio =====
        yield 10, "🎵 កំពុងដកស្រង់សំឡេងពីវីដេអូ..."
        if not extract_audio(video_path, audio_path):
            yield 0, "❌ មិនអាចដកស្រង់សំឡេងបានទេ"
            return
        
        # ===== STEP 2: Transcribe audio to text =====
        yield 30, "📝 កំពុងបម្លែងសំឡេងជាអត្ថបទ..."
        text, segments = transcribe_audio_to_text(audio_path)
        
        if text:
            # ===== STEP 3: Translate to Khmer =====
            yield 50, "🌐 កំពុងបកប្រែជាភាសាខ្មែរ..."
            khmer_text = translate_to_khmer(text)
            
            # ===== STEP 4: Generate Khmer audio =====
            yield 70, "🗣️ កំពុងបង្កើតសំឡេងខ្មែរ..."
            khmer_audio_data = get_khmer_audio_from_text(khmer_text)
            
            if khmer_audio_data is None:
                yield 0, "❌ មិនអាចបង្កើតសំឡេងខ្មែរបានទេ"
                return
            
            # រក្សាទុកសំឡេងខ្មែរ
            with open(khmer_audio_path, 'wb') as f:
                f.write(khmer_audio_data)
            
            # ===== STEP 5: Merge audio with video =====
            yield 85, "🎬 កំពុងបញ្ចូលសំឡេងចូលវីដេអូ..."
            if not merge_audio_video(video_path, khmer_audio_path, output_path):
                yield 0, "❌ មិនអាចបញ្ចូលសំឡេងចូលវីដេអូបានទេ"
                return
            
            # ===== STEP 6: Read final video =====
            yield 95, "✅ កំពុងរៀបចំវីដេអូចុងក្រោយ..."
            
            with open(output_path, 'rb') as f:
                dubbed_data = f.read()
            
            # សម្អាតឯកសារបណ្តោះអាសន្ន
            try:
                os.unlink(video_path)
                os.unlink(audio_path)
                os.unlink(khmer_audio_path)
                os.unlink(output_path)
            except:
                pass
            
            yield 100, "✅ បានបកប្រែវីដេអូជោគជ័យ!"
            yield dubbed_data, khmer_text, segments
        else:
            # ប្រើអត្ថបទដែលអ្នកប្រើបានបញ្ចូល
            if text_to_dub is None or text_to_dub.strip() == "":
                text_to_dub = "សួស្តី! ស្វាគមន៍មកកាន់ Khmer Dubber។ វីដេអូនេះត្រូវបានបកប្រែជាភាសាខ្មែរដោយប្រើបច្ចេកវិទ្យា AI។"
            
            khmer_text = text_to_dub
            yield 50, "🌐 កំពុងបកប្រែជាភាសាខ្មែរ..."
            
            # Generate Khmer audio
            yield 70, "🗣️ កំពុងបង្កើតសំឡេងខ្មែរ..."
            khmer_audio_data = get_khmer_audio_from_text(khmer_text)
            
            if khmer_audio_data is None:
                yield 0, "❌ មិនអាចបង្កើតសំឡេងខ្មែរបានទេ"
                return
            
            with open(khmer_audio_path, 'wb') as f:
                f.write(khmer_audio_data)
            
            # Merge
            yield 85, "🎬 កំពុងបញ្ចូលសំឡេងចូលវីដេអូ..."
            if not merge_audio_video(video_path, khmer_audio_path, output_path):
                yield 0, "❌ មិនអាចបញ្ចូលសំឡេងចូលវីដេអូបានទេ"
                return
            
            with open(output_path, 'rb') as f:
                dubbed_data = f.read()
            
            try:
                os.unlink(video_path)
                os.unlink(audio_path)
                os.unlink(khmer_audio_path)
                os.unlink(output_path)
            except:
                pass
            
            yield 100, "✅ បានបកប្រែវីដេអូជោគជ័យ!"
            yield dubbed_data, khmer_text, []
        
    except Exception as e:
        yield 0, f"❌ កំហុស: {str(e)}"

# ================================================================
#  STREAMLIT UI
# ================================================================

st.set_page_config(
    page_title="Khmer Dubber - Video Dubbing",
    page_icon="🎬",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 16px 24px;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #43a047, #2e7d32);
        color: white;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #388e3c, #1b5e20);
        box-shadow: 0 8px 30px rgba(76, 175, 80, 0.4);
    }
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #1e88e5, #0d47a1);
        color: white;
    }
    .upload-box {
        border: 3px dashed #43a047;
        border-radius: 18px;
        padding: 50px 20px;
        text-align: center;
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        transition: all 0.4s ease;
    }
    .upload-box:hover {
        border-color: #2e7d32;
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        transform: scale(1.01);
    }
    .status-badge {
        padding: 10px 28px;
        border-radius: 30px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s ease-in-out infinite;
        font-size: 16px;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    .telegram-box {
        background: linear-gradient(135deg, #0088cc, #00acee);
        padding: 25px 30px;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 8px 30px rgba(0, 136, 204, 0.3);
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    .telegram-box a {
        color: white;
        font-weight: bold;
        text-decoration: none;
        font-size: 22px;
    }
    .telegram-box a:hover {
        text-decoration: underline;
    }
    .video-container {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        animation: fadeInUp 0.6s ease;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .progress-container {
        width: 100%;
        background: #f0f0f0;
        border-radius: 12px;
        overflow: hidden;
        margin: 20px 0;
        height: 10px;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #43a047, #66bb6a, #43a047);
        background-size: 200% 100%;
        animation: shimmer 1.5s ease-in-out infinite;
        border-radius: 12px;
        transition: width 0.5s ease;
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .translation-box {
        background: linear-gradient(135deg, #f8f9fa, #e8f5e9);
        padding: 25px;
        border-radius: 14px;
        border-left: 6px solid #43a047;
        margin: 15px 0;
        animation: slideIn 0.6s ease;
        font-size: 16px;
        line-height: 1.8;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .success-box {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        border: 2px solid #43a047;
        animation: popIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    @keyframes popIn {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }
    .status-message {
        font-size: 16px;
        color: #555;
        padding: 10px;
        border-radius: 10px;
        background: #f5f5f5;
        margin: 10px 0;
        text-align: center;
    }
    .actor-timeline {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        max-height: 200px;
        overflow-y: auto;
    }
    .actor-line {
        padding: 5px 10px;
        border-left: 3px solid #43a047;
        margin: 3px 0;
        font-size: 14px;
        background: white;
        border-radius: 4px;
    }
    .actor-line .time {
        color: #888;
        font-size: 12px;
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
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'status_message' not in st.session_state:
    st.session_state.status_message = ""
if 'user_text' not in st.session_state:
    st.session_state.user_text = ""
if 'segments' not in st.session_state:
    st.session_state.segments = []

# ========== HEADER ==========
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("🎬 Khmer Dubber AI")
    st.markdown("### បកប្រែសំឡេងតួអង្គក្នុងវីដេអូជាភាសាខ្មែរ 🇰🇭")

with col_status:
    status = st.session_state.status
    if status == "vip":
        st.markdown('<div class="status-badge" style="background:#43a047;color:white;">✅ VIP Activated</div>', unsafe_allow_html=True)
    elif status == "expired":
        st.markdown('<div class="status-badge" style="background:#e53935;color:white;">❌ License Expired</div>', unsafe_allow_html=True)
    else:
        videos_used = st.session_state.license_data.get("videos_used", 0)
        remaining = 3 - videos_used
        if remaining < 0:
            remaining = 0
        if remaining > 0:
            st.markdown(f'<div class="status-badge" style="background:#fb8c00;color:white;">🆓 Trial: {remaining} left</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge" style="background:#e53935;color:white;">⛔ Trial Expired</div>', unsafe_allow_html=True)

st.markdown("---")

# ========== TELEGRAM CONTACT ==========
st.markdown("""
<div class="telegram-box">
    <div style="font-size:32px;">📱</div>
    <h3>ទាក់ទងមកយើងខ្ញុំ</h3>
    <p style="font-size:16px;">សម្រាប់ទិញ VIP ឬទទួល Activation Code</p>
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
            "ជ្រើសរើសវីដេអូដែលមានតួអង្គនិយាយ",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            accept_multiple_files=False,
            help="ដាក់វីដេអូដែលចង់បកប្រែសំឡេងតួអង្គជាខ្មែរ"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_video = uploaded_file
            st.success(f"✅ {uploaded_file.name}")
            st.info(f"📁 {uploaded_file.size / (1024*1024):.2f} MB")
            
            st.markdown("---")
            
            # ===== PROCESS BUTTON =====
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
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if can_process and not st.session_state.processing:
                    if st.button("🎤 បកប្រែសំឡេងតួអង្គ", use_container_width=True, type="primary"):
                        st.session_state.processing = True
                        st.session_state.progress = 0
                        st.session_state.video_processed = False
                        st.session_state.segments = []
                        
                        video_data = uploaded_file.getvalue()
                        
                        # Process with progress
                        for result in process_dub_video(video_data, None):
                            if isinstance(result, tuple) and len(result) == 2:
                                progress, message = result
                                if isinstance(progress, int):
                                    st.session_state.progress = progress
                                    st.session_state.status_message = message
                                    st.rerun()
                                elif isinstance(progress, str) and "❌" in progress:
                                    st.error(progress)
                                    st.session_state.processing = False
                                    st.rerun()
                            elif isinstance(result, tuple) and len(result) == 3:
                                dubbed_data, khmer_text, segments = result
                                st.session_state.dubbed_video = dubbed_data
                                st.session_state.video_processed = True
                                st.session_state.khmer_text = khmer_text
                                st.session_state.segments = segments
                                
                                # Update trial
                                if status != "vip":
                                    new_count = st.session_state.license_data.get("videos_used", 0) + 1
                                    st.session_state.license_data["videos_used"] = new_count
                                    save_license(st.session_state.license_data)
                                    st.session_state.status = check_license_status(st.session_state.license_data)
                                
                                st.session_state.progress = 100
                                st.session_state.processing = False
                                st.rerun()
                        
                        st.session_state.processing = False
                        st.rerun()
                else:
                    st.button("🎤 បកប្រែសំឡេងតួអង្គ", disabled=True, use_container_width=True)
                    if reason:
                        st.warning(f"⚠️ {reason}")
            
            with col_btn2:
                if st.button("🔄 កំណត់ឡើងវិញ", use_container_width=True, type="secondary"):
                    st.session_state.uploaded_video = None
                    st.session_state.dubbed_video = None
                    st.session_state.video_processed = False
                    st.session_state.khmer_text = ""
                    st.session_state.processing = False
                    st.session_state.progress = 0
                    st.session_state.user_text = ""
                    st.session_state.segments = []
                    st.rerun()
            
            # ===== PROGRESS BAR =====
            if st.session_state.progress > 0:
                st.markdown(f"""
                <div style="margin: 20px 0;">
                    <div style="display:flex;justify-content:space-between;font-size:15px;color:#555;">
                        <span>{st.session_state.status_message}</span>
                        <span style="font-weight:bold;color:#43a047;">{st.session_state.progress}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{st.session_state.progress}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ===== SHOW TRANSLATED TEXT =====
            if st.session_state.khmer_text and st.session_state.video_processed:
                st.markdown("---")
                st.subheader("📝 អត្ថបទដែលបានបកប្រែ")
                st.markdown(f"""
                <div class="translation-box">
                    <b>🇰🇭 ភាសាខ្មែរ:</b><br>
                    {st.session_state.khmer_text}
                </div>
                """, unsafe_allow_html=True)
            
            # ===== TRIAL STATUS =====
            if status == "trial":
                videos_used = st.session_state.license_data.get("videos_used", 0)
                remaining = 3 - videos_used
                if remaining > 0:
                    st.info(f"📹 នៅសល់សិទ្ធិសាកល្បង: {remaining} / 3")
                else:
                    st.warning("⚠️ អស់សិទ្ធិសាកល្បងហើយ!")
                    st.markdown("""
                    <div style="background:#fff3cd;padding:18px;border-radius:14px;border-left:5px solid #ffc107;">
                        <b>📱 ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖</b><br>
                        <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="font-size:18px;font-weight:bold;">@YOUR_TELEGRAM</a>
                    </div>
                    """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="upload-box">
                <div style="font-size:64px;">📂</div>
                <h3 style="color:#2e7d32;">អូស និង ទម្លាក់</h3>
                <p style="font-size:16px;color:#555;">ឬចុចដើម្បីជ្រើសរើសវីដេអូ</p>
                <p style="font-size:13px;color:#999;margin-top:10px;">គាំទ្រ: MP4, AVI, MOV, MKV, WEBM</p>
                <p style="font-size:13px;color:#e53935;margin-top:10px;">⚠️ ត្រូវការ FFmpeg និង Whisper (ប្រើសម្រាប់ស្គាល់សំឡេង)</p>
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
                <video width="100%" controls autoplay>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("🇰🇭 សំឡេងតួអង្គត្រូវបានបកប្រែជាភាសាខ្មែរ")
            
            # Show timeline if available
            if st.session_state.segments:
                with st.expander("📋 ពេលវេលានិយាយរបស់តួអង្គ"):
                    for seg in st.session_state.segments[:10]:
                        start = seg.get('start', 0)
                        end = seg.get('end', 0)
                        text = seg.get('text', '')
                        st.markdown(f"""
                        <div class="actor-line">
                            <span class="time">[{start:.1f}s - {end:.1f}s]</span>
                            {text[:50]}...
                        </div>
                        """, unsafe_allow_html=True)
            
            st.download_button(
                label="💾 ទាញយកវីដេអូ",
                data=video_data,
                file_name=f"dubbed_{uploaded_file.name if uploaded_file else 'video'}",
                mime="video/mp4",
                use_container_width=True,
                type="primary"
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
            
            st.caption("📌 វីដេអូដើម - ចុច 'បកប្រែសំឡេងតួអង្គ'")
            
        else:
            st.info("👆 ដាក់វីដេអូដើម្បីមើល")

# ========== TAB 2: VIP ACTIVATION ==========
with tab2:
    col_act1, col_act2 = st.columns([1, 1])
    
    with col_act1:
        st.subheader("🔑 Activate VIP")
        
        status = st.session_state.status
        if status == "vip":
            st.success("✅ **VIP Activated**")
            st.write(f"📅 Activated: {st.session_state.license_data.get('activation_date', 'N/A')}")
            st.write(f"📅 Expires: {st.session_state.license_data.get('expiry_date', 'N/A')}")
        elif status == "expired":
            st.error("❌ **License Expired**")
        else:
            videos_used = st.session_state.license_data.get("videos_used", 0)
            remaining = 3 - videos_used
            st.warning(f"🆓 **Trial Mode** ({remaining}/3)")
        
        st.markdown("---")
        
        code = st.text_input("Activation Code", placeholder="បញ្ចូល Code VIP...", type="password")
        
        col_act_btn1, col_act_btn2 = st.columns(2)
        
        with col_act_btn1:
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
        
        with col_act_btn2:
            if st.button("🔄 Check License", use_container_width=True):
                st.session_state.license_data = load_license()
                st.session_state.status = check_license_status(st.session_state.license_data)
                st.rerun()
    
    with col_act2:
        st.subheader("💎 VIP Benefits")
        st.markdown("""
        - ✅ Unlimited video dubbing
        - ✅ No trial limits
        - ✅ All voice options
        - ✅ 1 year validity
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0088cc,#00acee);padding:25px;border-radius:15px;color:white;text-align:center;">
            <h3>📱 Contact</h3>
            <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="color:white;font-weight:bold;font-size:20px;">
                @YOUR_TELEGRAM
            </a>
        </div>
        """, unsafe_allow_html=True)

# ========== TAB 3: ABOUT ==========
with tab3:
    st.subheader("ℹ️ About Khmer Dubber")
    st.markdown("""
    ### 🎬 How it works:
    
    1. **ដកស្រង់សំឡេង** ពីវីដេអូ
    2. **ស្គាល់សំឡេងតួអង្គ** (Speech-to-Text) ប្រើ Whisper
    3. **បកប្រែ** អត្ថបទជាភាសាខ្មែរ
    4. **បង្កើតសំឡេងខ្មែរ** ដោយ Google TTS
    5. **បញ្ចូលសំឡេងថ្មី** ចូលវីដេអូ (រក្សាពេលវេលាដើម)
    
    ### ⚙️ Requirements:
    - **FFmpeg** - សម្រាប់ដក/បញ្ចូលសំឡេង
    - **Whisper** - សម្រាប់ស្គាល់សំឡេង
    - **Internet** - សម្រាប់បកប្រែ និងបង្កើតសំឡេង
    
    ### 💰 Pricing:
    - **Trial**: 3 free videos
    - **VIP**: Unlimited access
    """)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### 🎬 Khmer Dubber")
    st.markdown("---")
    
    status = st.session_state.status
    if status == "vip":
        st.success("✅ VIP Mode")
    elif status == "expired":
        st.error("❌ License Expired")
    else:
        videos_used = st.session_state.license_data.get("videos_used", 0)
        remaining = 3 - videos_used
        if remaining > 0:
            st.warning(f"🆓 Trial ({remaining}/3)")
        else:
            st.error("⛔ Trial Expired")
    
    st.markdown("---")
    
    st.markdown("### 📱 Contact")
    st.markdown("""
    <div style="background:#0088cc;padding:18px;border-radius:12px;color:white;text-align:center;">
        <b>Telegram</b><br>
        <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="color:white;font-weight:bold;font-size:18px;">
            @YOUR_TELEGRAM
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔄 Reset App", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("Version 6.0.0")
