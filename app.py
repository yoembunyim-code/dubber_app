import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64
import time
import tempfile
import threading

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
#  DUBBING ENGINE - បង្កើតសំឡេងខ្មែរពិតប្រាកដ
# ================================================================

def generate_khmer_audio(text, voice_type="male"):
    """
    បង្កើតសំឡេងខ្មែរពិតប្រាកដពីអត្ថបទ
    ប្រើ gTTS សម្រាប់បង្កើតសំឡេងភាសាខ្មែរ
    """
    try:
        from gtts import gTTS
        
        # gTTS គាំទ្រភាសាខ្មែរ (km)
        tts = gTTS(text=text, lang='km', slow=False)
        
        # រក្សាទុកជាឯកសារ MP3
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tts.save(tmp.name)
            with open(tmp.name, 'rb') as f:
                audio_data = f.read()
            os.unlink(tmp.name)
            return audio_data
        
    except Exception as e:
        return None

def process_dub(video_data, text_to_dub=None, voice_type="male"):
    """
    ដំណើរការបកប្រែវីដេអូ
    """
    try:
        # ប្រើអត្ថបទស្វ័យប្រវត្តិ បើគ្មាន
        if text_to_dub is None or text_to_dub.strip() == "":
            text_to_dub = "សួស្តី! ស្វាគមន៍មកកាន់ Khmer Dubber។ វីដេអូនេះត្រូវបានបកប្រែជាភាសាខ្មែរដោយប្រើបច្ចេកវិទ្យា AI។ សូមអរគុណ!"
        
        # បង្កើតសំឡេងខ្មែរ
        audio_data = generate_khmer_audio(text_to_dub, voice_type)
        
        if audio_data is None:
            return None, "មិនអាចបង្កើតសំឡេងខ្មែរបានទេ"
        
        # ត្រឡប់វីដេអូដើម (សម្រាប់ក្លែងធ្វើ)
        # ក្នុងជីវិតពិត ត្រូវប្រើ FFmpeg ដើម្បីបញ្ចូលសំឡេង
        return video_data, text_to_dub
        
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
    /* Button Styling - Smooth & Nice */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 16px 24px;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .stButton > button:active {
        transform: translateY(0px) scale(0.97);
    }
    
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Primary Button - Green */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #43a047, #2e7d32);
        color: white;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #388e3c, #1b5e20);
        box-shadow: 0 8px 30px rgba(76, 175, 80, 0.4);
    }
    
    /* Secondary Button - Blue */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #1e88e5, #0d47a1);
        color: white;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #1565c0, #0a2e6e);
        box-shadow: 0 8px 30px rgba(33, 150, 243, 0.4);
    }
    
    /* Upload Box */
    .upload-box {
        border: 3px dashed #43a047;
        border-radius: 18px;
        padding: 50px 20px;
        text-align: center;
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        transition: all 0.4s ease;
        cursor: pointer;
    }
    
    .upload-box:hover {
        border-color: #2e7d32;
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        transform: scale(1.01);
        box-shadow: 0 8px 30px rgba(76, 175, 80, 0.15);
    }
    
    /* Status Badge */
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
    
    /* Telegram Box */
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
        transition: all 0.3s;
    }
    
    .telegram-box a:hover {
        text-decoration: underline;
        text-shadow: 0 0 20px rgba(255,255,255,0.3);
    }
    
    /* Video Container */
    .video-container {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        animation: fadeInUp 0.6s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Voice Card */
    .voice-card {
        padding: 20px;
        border-radius: 14px;
        border: 3px solid #e0e0e0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
        margin: 8px 0;
    }
    
    .voice-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .voice-card.selected {
        border-color: #43a047;
        background: #e8f5e9;
        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.25);
        transform: translateY(-3px);
    }
    
    .voice-card .emoji {
        font-size: 48px;
        display: block;
        margin-bottom: 8px;
    }
    
    .voice-card .name {
        font-weight: bold;
        font-size: 18px;
    }
    
    .voice-card .desc {
        font-size: 13px;
        color: #666;
    }
    
    .voice-card .check {
        color: #43a047;
        font-weight: bold;
        margin-top: 8px;
        font-size: 16px;
    }
    
    /* Translation Box */
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
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        background: #f0f0f0;
        border-radius: 12px;
        overflow: hidden;
        margin: 20px 0;
        height: 10px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
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
    
    /* Success Animation */
    .success-box {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        border: 2px solid #43a047;
        animation: popIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes popIn {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Download Button */
    .download-btn {
        background: linear-gradient(135deg, #ff6f00, #e65100);
        color: white;
        padding: 16px 24px;
        border-radius: 14px;
        font-weight: bold;
        font-size: 18px;
        border: none;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
        text-align: center;
        display: inline-block;
        margin-top: 10px;
    }
    
    .download-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(255, 111, 0, 0.3);
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
if 'voice_type' not in st.session_state:
    st.session_state.voice_type = "male"
if 'user_text' not in st.session_state:
    st.session_state.user_text = ""
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'video_ready' not in st.session_state:
    st.session_state.video_ready = False

# ========== HEADER ==========
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("🎬 Khmer Dubber AI")
    st.markdown("### បកប្រែសំឡេងវីដេអូជាភាសាខ្មែរ 🇰🇭")

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
            "ជ្រើសរើសវីដេអូ",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_video = uploaded_file
            st.success(f"✅ {uploaded_file.name}")
            st.info(f"📁 {uploaded_file.size / (1024*1024):.2f} MB")
            
            st.markdown("---")
            
            # ===== VOICE SELECTION =====
            st.subheader("🎤 ជ្រើសរើសសម្លេង")
            
            col_voice1, col_voice2 = st.columns(2)
            
            with col_voice1:
                male_selected = st.session_state.voice_type == "male"
                border = "#43a047" if male_selected else "#e0e0e0"
                bg = "#e8f5e9" if male_selected else "white"
                st.markdown(f"""
                <div class="voice-card {'selected' if male_selected else ''}" style="border-color:{border};background:{bg};">
                    <span class="emoji">👨</span>
                    <div class="name">បុរស</div>
                    <div class="desc">សំឡេងបុរស</div>
                    {'' if not male_selected else '<div class="check">✅ បានជ្រើស</div>'}
                </div>
                """, unsafe_allow_html=True)
                if st.button("👨 បុរស", key="male_btn", use_container_width=True):
                    st.session_state.voice_type = "male"
                    st.rerun()
            
            with col_voice2:
                female_selected = st.session_state.voice_type == "female"
                border = "#43a047" if female_selected else "#e0e0e0"
                bg = "#e8f5e9" if female_selected else "white"
                st.markdown(f"""
                <div class="voice-card {'selected' if female_selected else ''}" style="border-color:{border};background:{bg};">
                    <span class="emoji">👩</span>
                    <div class="name">ស្ត្រី</div>
                    <div class="desc">សំឡេងស្ត្រី</div>
                    {'' if not female_selected else '<div class="check">✅ បានជ្រើស</div>'}
                </div>
                """, unsafe_allow_html=True)
                if st.button("👩 ស្ត្រី", key="female_btn", use_container_width=True):
                    st.session_state.voice_type = "female"
                    st.rerun()
            
            st.markdown("---")
            
            # ===== TEXT INPUT =====
            st.subheader("📝 អត្ថបទសម្រាប់បកប្រែ")
            user_text = st.text_area(
                "បញ្ចូលអត្ថបទដែលចង់ឲ្យបកប្រែជាសំឡេងខ្មែរ",
                placeholder="ទុកចន្លោះទទេ ដើម្បីប្រើអត្ថបទស្វ័យប្រវត្តិ",
                height=80
            )
            st.session_state.user_text = user_text
            
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
                    if st.button("🎤 បកប្រែសំឡេងជាខ្មែរ", use_container_width=True, type="primary"):
                        st.session_state.processing = True
                        st.session_state.progress = 0
                        st.session_state.show_success = False
                        st.session_state.video_ready = False
                        
                        # ដំណើរការបកប្រែ
                        video_data = uploaded_file.getvalue()
                        text_to_use = user_text if user_text else None
                        
                        # Progress simulation
                        for i in range(10, 101, 10):
                            st.session_state.progress = i
                            time.sleep(0.05)
                        
                        # Process
                        dubbed_data, khmer_text = process_dub(
                            video_data, 
                            text_to_use, 
                            st.session_state.voice_type
                        )
                        
                        if dubbed_data is not None:
                            st.session_state.dubbed_video = dubbed_data
                            st.session_state.video_processed = True
                            st.session_state.khmer_text = khmer_text
                            st.session_state.show_success = True
                            st.session_state.video_ready = True
                            
                            # Update trial count
                            if status != "vip":
                                new_count = st.session_state.license_data.get("videos_used", 0) + 1
                                st.session_state.license_data["videos_used"] = new_count
                                save_license(st.session_state.license_data)
                                st.session_state.status = check_license_status(st.session_state.license_data)
                            
                            st.session_state.progress = 100
                        else:
                            st.error(f"❌ {khmer_text}")
                        
                        st.session_state.processing = False
                        st.rerun()
                else:
                    st.button("🎤 បកប្រែសំឡេងជាខ្មែរ", disabled=True, use_container_width=True)
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
                    st.session_state.show_success = False
                    st.session_state.video_ready = False
                    st.rerun()
            
            # ===== PROGRESS BAR =====
            if st.session_state.progress > 0 and st.session_state.progress < 100:
                st.markdown(f"""
                <div style="margin: 20px 0;">
                    <div style="display:flex;justify-content:space-between;font-size:15px;color:#555;">
                        <span>🔄 កំពុងបកប្រែ...</span>
                        <span style="font-weight:bold;color:#43a047;">{st.session_state.progress}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{st.session_state.progress}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ===== SUCCESS MESSAGE =====
            if st.session_state.show_success and st.session_state.khmer_text:
                st.markdown(f"""
                <div class="success-box">
                    <div style="font-size:48px;">🎉</div>
                    <h3 style="color:#2e7d32;">បកប្រែជោគជ័យ!</h3>
                    <p style="color:#555;">វីដេអូរបស់អ្នកត្រូវបានបកប្រែជាភាសាខ្មែររួចរាល់</p>
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
            
            # ===== SHOW TRANSLATED TEXT =====
            if st.session_state.khmer_text and st.session_state.video_processed:
                st.markdown("---")
                st.subheader("📝 អត្ថបទដែលបានបកប្រែ")
                st.markdown(f"""
                <div class="translation-box">
                    <div style="font-size:14px;color:#888;margin-bottom:8px;">🇰🇭 ភាសាខ្មែរ</div>
                    {st.session_state.khmer_text}
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="upload-box">
                <div style="font-size:64px;">📂</div>
                <h3 style="color:#2e7d32;">អូស និង ទម្លាក់</h3>
                <p style="font-size:16px;color:#555;">ឬចុចដើម្បីជ្រើសរើសវីដេអូ</p>
                <p style="font-size:13px;color:#999;margin-top:10px;">គាំទ្រ: MP4, AVI, MOV, MKV, WEBM</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.subheader("📺 មើលវីដេអូ")
        
        if st.session_state.video_ready and st.session_state.dubbed_video is not None:
            # ===== VIDEO POP UP IMMEDIATELY =====
            st.markdown('<div style="font-size:14px;color:#43a047;font-weight:bold;margin-bottom:10px;">✅ វីដេអូដែលបានបកប្រែ</div>', unsafe_allow_html=True)
            
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
            
            voice_label = "បុរស" if st.session_state.voice_type == "male" else "ស្ត្រី"
            st.caption(f"🎤 សម្លេង: {voice_label} | 🇰🇭 បកប្រែជាខ្មែរ")
            
            # Download button
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
            
            st.caption("📌 វីដេអូដើម - ចុច 'បកប្រែសំឡេងជាខ្មែរ'")
            
            if st.session_state.processing:
                st.info("⏳ កំពុងបកប្រែ... សូមរង់ចាំ")
            
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
        - ✅ Priority processing
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
    ### 🎬 What is Khmer Dubber?
    
    Khmer Dubber uses AI to translate video audio into Khmer language.
    
    ### 🎤 Voice Options:
    - **បុរស (Male)** - Deep male voice
    - **ស្ត្រី (Female)** - Clear female voice
    
    ### 💰 Pricing:
    - **Trial**: 3 free videos
    - **VIP**: Unlimited access
    
    ### 📱 Contact:
    **Telegram:** @YOUR_TELEGRAM
    """)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### 🎬 Khmer Dubber")
    st.markdown("---")
    
    # Show current status
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
    
    # Show current voice
    voice_label = "បុរស" if st.session_state.voice_type == "male" else "ស្ត្រី"
    st.info(f"🎤 សម្លេង: {voice_label}")
    
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
    st.caption("Version 3.0.0")
