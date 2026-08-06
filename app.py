import streamlit as st
import json
import os
from datetime import datetime, timedelta
import uuid
import platform
import base64
from pathlib import Path

# ================================================================
#  LICENSE MANAGER
# ================================================================

LICENSE_FILE = "license.json"
VALID_KEY = "DEEPSEEK-VIP-2026"

def get_machine_id():
    return str(uuid.getnode()) + "_" + platform.node()

def load_license():
    default_data = {
        "license_key": "",
        "activated": False,
        "activation_date": "",
        "expiry_date": "",
        "machine_id": get_machine_id(),
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
    except (json.JSONDecodeError, IOError):
        return default_data

def save_license(data):
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def check_license_status(data):
    if data.get("activated", False):
        expiry = data.get("expiry_date", "")
        if expiry:
            try:
                exp_date = datetime.strptime(expiry, "%Y-%m-%d")
                if datetime.now() > exp_date:
                    return "expired"
            except ValueError:
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
        data["machine_id"] = get_machine_id()
        data["videos_used"] = 0
        
        if save_license(data):
            return True, "VIP Activated Successfully! ✅", data
        else:
            return False, "Failed to save license file.", data
    else:
        return False, "Invalid Activation Code. ❌", data

# ================================================================
#  STREAMLIT UI - MODERN DESIGN
# ================================================================

st.set_page_config(
    page_title="🎬 AI Video Dubber",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- Custom CSS for Beautiful Design -----
st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main Container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 20px;
    }
    
    /* Card Style */
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    /* Gradient Button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Success/Info Boxes */
    .stAlert {
        border-radius: 12px !important;
        border-left: 5px solid #667eea !important;
    }
    
    /* Upload Box */
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    .upload-box:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #764ba2;
    }
    
    /* Title Animation */
    .title-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: 800;
        text-align: center;
    }
    
    /* Voice Selection Styling */
    .voice-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .voice-card:hover {
        border-color: #667eea;
        transform: scale(1.05);
    }
    .voice-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
    }
    
    /* Status Badge */
    .badge-vip {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-trial {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-expired {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6b7280;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
#  INITIALIZE SESSION STATE
# ================================================================

if 'license_data' not in st.session_state:
    st.session_state.license_data = load_license()
    st.session_state.current_status = check_license_status(st.session_state.license_data)
    st.session_state.video_file = None
    st.session_state.selected_voice = "Male Voice 1"
    st.session_state.is_playing = False
    st.session_state.script_text = ""

# ================================================================
#  SIDEBAR - VIP Activation
# ================================================================

with st.sidebar:
    st.markdown("## 🔑 VIP Control Panel")
    st.markdown("---")
    
    # Status Display
    status = st.session_state.current_status
    if status == "vip":
        st.markdown('<div class="badge-vip">✅ VIP Activated</div>', unsafe_allow_html=True)
        st.success("🎉 Unlimited Access")
    elif status == "expired":
        st.markdown('<div class="badge-expired">❌ License Expired</div>', unsafe_allow_html=True)
        st.error("Please renew your license")
    else:
        remaining = 3 - st.session_state.license_data.get("videos_used", 0)
        if remaining < 0:
            remaining = 0
        if remaining > 0:
            st.markdown(f'<div class="badge-trial">🆓 Trial: {remaining} left</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-expired">⛔ Trial Expired</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Activation
    st.markdown("### 🔐 Activate VIP")
    code = st.text_input("Activation Code:", placeholder="Enter your code", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Activate", use_container_width=True):
            success, message, updated_data = activate_license(code)
            if success:
                st.session_state.license_data = updated_data
                st.session_state.current_status = check_license_status(updated_data)
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        if st.button("🔍 Check", use_container_width=True):
            st.session_state.license_data = load_license()
            st.session_state.current_status = check_license_status(st.session_state.license_data)
            st.rerun()
    
    st.markdown("---")
    
    # Telegram Contact
    st.markdown("### 📱 Contact")
    st.info("💎 For VIP Purchase\n📱 @YOUR_TELEGRAM")

# ================================================================
#  MAIN CONTENT
# ================================================================

st.markdown('<h1 class="title-gradient">🎬 AI Video Dubber</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280;'>Convert your videos with AI voiceovers in multiple languages</p>", unsafe_allow_html=True)

# ----- Main Container -----
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # ========== TWO COLUMN LAYOUT ==========
    col_video, col_control = st.columns([2, 1])
    
    # ----- LEFT COLUMN: Video Upload & Player -----
    with col_video:
        st.markdown("### 📹 Video Upload & Player")
        
        # Video Upload
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            help="Supported formats: MP4, AVI, MOV, MKV, WEBM"
        )
        
        if uploaded_file is not None:
            st.session_state.video_file = uploaded_file
            
            # Save and display video
            video_bytes = uploaded_file.read()
            video_base64 = base64.b64encode(video_bytes).decode()
            
            st.markdown(f"""
            <div class="card">
                <video width="100%" controls>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """, unsafe_allow_html=True)
            
            # Video Info
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("File Size", f"{len(video_bytes)//1024} KB")
            with col_info2:
                st.metric("Format", uploaded_file.type.split('/')[-1].upper())
            with col_info3:
                st.metric("Status", "✅ Loaded")
        else:
            st.markdown("""
            <div class="upload-box">
                <h3>📤 Drop your video here</h3>
                <p style="color: #6b7280;">or click to browse files</p>
                <p style="font-size: 0.8em; color: #9ca3af;">Supported: MP4, AVI, MOV, MKV, WEBM</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Script Display Area
        st.markdown("### 📝 Script / Subtitle")
        script_area = st.text_area(
            "Enter script or subtitles",
            placeholder="Type your script here or upload SRT file...",
            height=150,
            key="script_input"
        )
        if script_area:
            st.session_state.script_text = script_area
    
    # ----- RIGHT COLUMN: Voice Selection & Controls -----
    with col_control:
        st.markdown("### 🎤 Voice Selection")
        
        # Voice options
        voices = {
            "Male Voice 1": "🎙️ Deep Male",
            "Male Voice 2": "🎙️ Warm Male", 
            "Female Voice 1": "🎙️ Bright Female",
            "Female Voice 2": "🎙️ Soft Female",
            "Khmer Voice": "🇰🇭 សំឡេងខ្មែរ",
            "English Voice": "🇬🇧 English Voice"
        }
        
        # Voice selection grid
        voice_cols = st.columns(2)
        for idx, (voice_key, voice_label) in enumerate(voices.items()):
            col_idx = idx % 2
            with voice_cols[col_idx]:
                is_selected = st.session_state.selected_voice == voice_key
                border_style = "2px solid #667eea" if is_selected else "2px solid transparent"
                bg_style = "linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)" if is_selected else "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
                
                if st.button(
                    voice_label,
                    key=f"voice_{voice_key}",
                    use_container_width=True,
                    help=f"Select {voice_key}"
                ):
                    st.session_state.selected_voice = voice_key
                    st.rerun()
        
        st.markdown("---")
        
        # ====== Control Buttons ======
        st.markdown("### 🎮 Controls")
        
        # Check if video is uploaded
        has_video = st.session_state.video_file is not None
        
        # Status checks
        status = st.session_state.current_status
        can_play = False
        status_msg = ""
        
        if status == "vip":
            can_play = True
            status_msg = "VIP Mode - Unlimited"
        elif status == "expired":
            can_play = False
            status_msg = "❌ License Expired"
        else:  # trial
            remaining = 3 - st.session_state.license_data.get("videos_used", 0)
            if remaining > 0:
                can_play = True
                status_msg = f"Trial - {remaining} left"
            else:
                can_play = False
                status_msg = "⛔ Trial Expired"
        
        # Start Button
        col_start, col_stop = st.columns(2)
        with col_start:
            if st.button("▶ Start", use_container_width=True, disabled=not (can_play and has_video)):
                if not has_video:
                    st.warning("Please upload a video first!")
                else:
                    status = st.session_state.current_status
                    
                    if status == "trial":
                        videos_used = st.session_state.license_data.get("videos_used", 0)
                        if videos_used >= 3:
                            st.error("Trial expired! Please activate VIP.")
                        else:
                            st.session_state.license_data["videos_used"] = videos_used + 1
                            save_license(st.session_state.license_data)
                            st.session_state.current_status = check_license_status(st.session_state.license_data)
                            st.session_state.is_playing = True
                            st.success(f"🎬 Playing with {st.session_state.selected_voice}!")
                            st.rerun()
                    else:
                        st.session_state.is_playing = True
                        st.success(f"🎬 Playing with {st.session_state.selected_voice}!")
        
        with col_stop:
            if st.button("⏹ Stop", use_container_width=True):
                st.session_state.is_playing = False
                st.info("⏹ Stopped")
                st.rerun()
        
        # Status display
        if st.session_state.is_playing:
            st.info(f"🎬 Now playing with {st.session_state.selected_voice}")
            st.progress(100, text="Processing...")
        else:
            if has_video:
                st.info("⏸ Ready to play")
            else:
                st.warning("📤 Upload a video to start")
        
        st.markdown("---")
        
        # ====== Buy VIP Button ======
        st.markdown("### 💎 Unlock VIP")
        if st.button("💎 Buy VIP Now", use_container_width=True):
            st.info("💎 សម្រាប់ទិញ VIP ឬទទួល Activation Code សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")
        
        # ====== Current Status Summary ======
        st.markdown("---")
        st.markdown("### 📊 Status")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("License", "VIP" if status == "vip" else "Trial" if status == "trial" else "Expired")
        with col_s2:
            st.metric("Voice", st.session_state.selected_voice.split(" ")[0])
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================================================================
#  FOOTER
# ================================================================

st.markdown("""
<div class="footer">
    <p>🎬 AI Video Dubber v2.0 | Powered by DeepSeek AI</p>
    <p style="font-size: 0.8em; color: #9ca3af;">Contact Telegram: @YOUR_TELEGRAM</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
#  REQUIREMENTS.TXT
# ================================================================

# streamlit
# openai-whisper (optional for speech-to-text)
# moviepy (optional for video processing)
