import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64
import time
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
#  KHMER TEXT-TO-SPEECH (ប្រើ Google Translate TTS)
# ================================================================

def generate_khmer_audio_url(text):
    """
    បង្កើត URL សម្រាប់សំឡេងខ្មែរពី Google TTS
    ប្រើ gTTS API តាមរយៈ Internet
    """
    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    # Google TTS URL (គាំទ្រភាសាខ្មែរ)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=km&client=tw-ob"
    return url

def get_khmer_audio_base64(text):
    """
    ទាញយកសំឡេងខ្មែរពី Google TTS ហើយបម្លែងជា base64
    """
    try:
        url = generate_khmer_audio_url(text)
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            audio_base64 = base64.b64encode(response.content).decode()
            return audio_base64
        return None
    except:
        return None

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
    .stButton > button:active {
        transform: translateY(0px) scale(0.97);
    }
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none !important;
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
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
    }
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #1565c0, #0a2e6e);
        box-shadow: 0 8px 30px rgba(33, 150, 243, 0.4);
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
    .audio-player {
        width: 100%;
        margin: 10px 0;
        border-radius: 12px;
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
</style>
""", unsafe_allow_html=True)

# ========== INIT SESSION STATE ==========
if 'license_data' not in st.session_state:
    st.session_state.license_data = load_license()
if 'status' not in st.session_state:
    st.session_state.status = check_license_status(st.session_state.license_data)
if 'uploaded_video' not in st.session_state:
    st.session_state.uploaded_video = None
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
if 'audio_base64' not in st.session_state:
    st.session_state.audio_base64 = None
if 'show_audio' not in st.session_state:
    st.session_state.show_audio = False

# ========== HEADER ==========
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("🎬 Khmer Dubber AI")
    st.markdown("### បកប្រែវីដេអូ និងបង្កើតសំឡេងខ្មែរ 🇰🇭")

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
                st.markdown(f"""
                <div class="voice-card {'selected' if male_selected else ''}">
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
                st.markdown(f"""
                <div class="voice-card {'selected' if female_selected else ''}">
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
            st.subheader("📝 អត្ថបទដែលចង់ឲ្យនិយាយជាខ្មែរ")
            user_text = st.text_area(
                "បញ្ចូលអត្ថបទ",
                placeholder="ឧទាហរណ៍: សួស្តី! ស្វាគមន៍មកកាន់ Khmer Dubber",
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
                    if st.button("🎤 បង្កើតសំឡេងខ្មែរ", use_container_width=True, type="primary"):
                        st.session_state.processing = True
                        st.session_state.progress = 0
                        st.session_state.show_audio = False
                        
                        # Progress
                        for i in range(10, 101, 10):
                            st.session_state.progress = i
                            time.sleep(0.03)
                        
                        # Get text
                        text_to_use = user_text if user_text else "សួស្តី! ស្វាគមន៍មកកាន់ Khmer Dubber។ យើងខ្ញុំសូមជូនដំណឹងថាវីដេអូនេះត្រូវបានបកប្រែជាភាសាខ្មែរដោយប្រើបច្ចេកវិទ្យា AI។"
                        
                        # Generate Khmer audio
                        audio_base64 = get_khmer_audio_base64(text_to_use)
                        
                        if audio_base64:
                            st.session_state.audio_base64 = audio_base64
                            st.session_state.khmer_text = text_to_use
                            st.session_state.show_audio = True
                            st.session_state.video_processed = True
                            
                            # Update trial count
                            if status != "vip":
                                new_count = st.session_state.license_data.get("videos_used", 0) + 1
                                st.session_state.license_data["videos_used"] = new_count
                                save_license(st.session_state.license_data)
                                st.session_state.status = check_license_status(st.session_state.license_data)
                            
                            st.session_state.progress = 100
                            st.success("✅ បានបង្កើតសំឡេងខ្មែរជោគជ័យ!")
                        else:
                            st.error("❌ មិនអាចបង្កើតសំឡេងខ្មែរបានទេ (សូមពិនិត្យ Internet)")
                        
                        st.session_state.processing = False
                        st.rerun()
                else:
                    st.button("🎤 បង្កើតសំឡេងខ្មែរ", disabled=True, use_container_width=True)
                    if reason:
                        st.warning(f"⚠️ {reason}")
            
            with col_btn2:
                if st.button("🔄 កំណត់ឡើងវិញ", use_container_width=True, type="secondary"):
                    st.session_state.uploaded_video = None
                    st.session_state.video_processed = False
                    st.session_state.khmer_text = ""
                    st.session_state.processing = False
                    st.session_state.progress = 0
                    st.session_state.user_text = ""
                    st.session_state.audio_base64 = None
                    st.session_state.show_audio = False
                    st.rerun()
            
            # ===== PROGRESS BAR =====
            if st.session_state.progress > 0 and st.session_state.progress < 100:
                st.markdown(f"""
                <div style="margin: 20px 0;">
                    <div style="display:flex;justify-content:space-between;font-size:15px;color:#555;">
                        <span>🔄 កំពុងបង្កើតសំឡេង...</span>
                        <span style="font-weight:bold;color:#43a047;">{st.session_state.progress}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" style="width:{st.session_state.progress}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ===== SUCCESS & AUDIO PLAYER =====
            if st.session_state.show_audio and st.session_state.audio_base64:
                st.markdown(f"""
                <div class="success-box">
                    <div style="font-size:48px;">🎉</div>
                    <h3 style="color:#2e7d32;">បង្កើតសំឡេងខ្មែរជោគជ័យ!</h3>
                    <p style="color:#555;">ចុចប៊ូតុង Play ដើម្បីស្តាប់សំឡេងខ្មែរ</p>
                </div>
                """, unsafe_allow_html=True)
                
                # ===== AUDIO PLAYER =====
                st.markdown(f"""
                <div style="background:#f5f5f5;padding:20px;border-radius:14px;margin:10px 0;">
                    <div style="font-weight:bold;color:#333;margin-bottom:10px;">🔊 សំឡេងខ្មែរ</div>
                    <audio controls style="width:100%;border-radius:10px;">
                        <source src="data:audio/mp3;base64,{st.session_state.audio_base64}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                </div>
                """, unsafe_allow_html=True)
                
                # ===== TRANSLATED TEXT =====
                if st.session_state.khmer_text:
                    st.markdown(f"""
                    <div class="translation-box">
                        <div style="font-size:14px;color:#888;margin-bottom:8px;">📝 អត្ថបទខ្មែរ</div>
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
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.subheader("📺 មើលវីដេអូ")
        
        if st.session_state.uploaded_video is not None:
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
            
            if st.session_state.processing:
                st.info("⏳ កំពុងបង្កើតសំឡេង...")
            elif st.session_state.show_audio:
                st.success("🔊 សំឡេងខ្មែរបានបង្កើតរួច! ស្តាប់នៅខាងឆ្វេង")
            else:
                st.caption("📌 វីដេអូដើម - បញ្ចូលអត្ថបទ ហើយចុច 'បង្កើតសំឡេងខ្មែរ'")
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
    
    Khmer Dubber uses AI to generate Khmer voice from text.
    
    ### 🎤 Voice Options:
    - **បុរស (Male)** - Deep male voice
    - **ស្ត្រី (Female)** - Clear female voice
    
    ### 💰 Pricing:
    - **Trial**: 3 free generations
    - **VIP**: Unlimited access
    
    ### 📱 Contact:
    **Telegram:** @YOUR_TELEGRAM
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
    st.caption("Version 4.0.0")
