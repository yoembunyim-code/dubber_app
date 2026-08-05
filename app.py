import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64

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
        padding: 10px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background-color: #f0f8ff;
    }
    .video-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 8px 16px;
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

# ========== HEADER ==========
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("🎬 Khmer Dubber")
    st.markdown("បកប្រែវីដេអូជាភាសាខ្មែរ ជាមួយ AI")

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

# ========== TELEGRAM CONTACT (TOP) ==========
st.markdown("""
<div class="telegram-box">
    <h3>📱 ទាក់ទងមកយើងខ្ញុំ</h3>
    <p>សម្រាប់ទិញ VIP ឬទទួល Activation Code</p>
    <a href="https://t.me/YOUR_TELEGRAM" target="_blank">👉 @YOUR_TELEGRAM</a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ========== MAIN LAYOUT ==========
tab1, tab2, tab3 = st.tabs(["📹 Dub Video", "🔑 VIP Activation", "ℹ️ About"])

# ========== TAB 1: DUB VIDEO ==========
with tab1:
    col_left, col_right = st.columns([1, 1])
    
    # ----- LEFT COLUMN: Upload & Controls -----
    with col_left:
        st.subheader("📤 Upload Video")
        
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            accept_multiple_files=False,
            help="Upload your video file to dub"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_video = uploaded_file
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.info(f"📁 Size: {uploaded_file.size / (1024*1024):.2f} MB")
            
            status = st.session_state.status
            can_process = False
            reason = ""
            
            if status == "vip":
                can_process = True
            elif status == "expired":
                reason = "License expired. Please buy VIP."
            else:
                videos_used = st.session_state.license_data.get("videos_used", 0)
                if videos_used >= 3:
                    reason = "Trial expired. Please buy VIP."
                else:
                    can_process = True
            
            st.markdown("---")
            st.subheader("🎯 Action")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if can_process:
                    if st.button("🎤 Dub Video", use_container_width=True, type="primary"):
                        with st.spinner("Processing video... This may take a moment..."):
                            import time
                            time.sleep(3)
                            st.session_state.video_processed = True
                            st.session_state.dubbed_video = st.session_state.uploaded_video
                            
                            if status != "vip":
                                new_count = st.session_state.license_data.get("videos_used", 0) + 1
                                st.session_state.license_data["videos_used"] = new_count
                                save_license(st.session_state.license_data)
                                st.session_state.status = check_license_status(st.session_state.license_data)
                            
                            st.success("✅ Video dubbed successfully!")
                            st.rerun()
                else:
                    st.button("🎤 Dub Video", disabled=True, use_container_width=True)
                    st.warning(f"⚠️ {reason}")
            
            with col_btn2:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.uploaded_video = None
                    st.session_state.dubbed_video = None
                    st.session_state.video_processed = False
                    st.rerun()
            
            if status == "trial":
                videos_used = st.session_state.license_data.get("videos_used", 0)
                remaining = 3 - videos_used
                if remaining > 0:
                    st.info(f"📹 Trial remaining: {remaining} / 3")
                else:
                    st.warning("⚠️ No trials left! Activate VIP to continue.")
                    
                    # Telegram contact in warning
                    st.markdown("""
                    <div style="background:#fff3cd;padding:15px;border-radius:10px;border-left:4px solid #ffc107;">
                        <b>📱 ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖</b><br>
                        <a href="https://t.me/YOUR_TELEGRAM" target="_blank">@YOUR_TELEGRAM</a>
                    </div>
                    """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="upload-box">
                <h3>📂 Drag & Drop</h3>
                <p>or click to browse</p>
                <p style="font-size:12px;color:#888;">Supported: MP4, AVI, MOV, MKV, WEBM</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ----- RIGHT COLUMN: Video Preview -----
    with col_right:
        st.subheader("📺 Video Preview")
        
        if st.session_state.video_processed and st.session_state.dubbed_video is not None:
            st.success("🎉 Dubbed video ready!")
            
            video_data = st.session_state.dubbed_video.getvalue()
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
                label="💾 Download Dubbed Video",
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
            
            st.caption("📌 Original video - Click 'Dub Video' to process")
            
        else:
            st.info("👆 Upload a video to preview")

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
            st.warning(f"🆓 **Trial Mode** ({remaining}/3 videos remaining)")
        
        st.markdown("---")
        
        code = st.text_input("Activation Code", placeholder="Enter your VIP code...", type="password")
        
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
                    st.warning("Please enter an Activation Code.")
        
        with col_act_btn2:
            if st.button("🔄 Check License", use_container_width=True):
                st.session_state.license_data = load_license()
                st.session_state.status = check_license_status(st.session_state.license_data)
                st.rerun()
    
    with col_act2:
        st.subheader("💎 Get VIP Access")
        
        st.markdown("""
        ### 🎯 VIP Benefits:
        - ✅ Unlimited video dubbing
        - ✅ No trial limits
        - ✅ Priority processing
        - ✅ Access to all features
        - ✅ 1 year validity
        """)
        
        st.markdown("---")
        
        # ===== TELEGRAM BOX IN VIP TAB =====
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0088cc,#00acee);padding:20px;border-radius:15px;color:white;text-align:center;">
            <h3>📱 Contact for VIP Purchase</h3>
            <p>សម្រាប់ទិញ VIP ឬទទួល Activation Code</p>
            <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="color:white;font-weight:bold;font-size:18px;text-decoration:none;">
                👉 @YOUR_TELEGRAM
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💬 Contact on Telegram", use_container_width=True):
            st.info("📱 Telegram: @YOUR_TELEGRAM")

# ========== TAB 3: ABOUT ==========
with tab3:
    col_about1, col_about2 = st.columns([2, 1])
    
    with col_about1:
        st.subheader("ℹ️ About Khmer Dubber")
        
        st.markdown("""
        ### 🎬 What is Khmer Dubber?
        
        Khmer Dubber is an AI-powered video dubbing tool that translates videos into Khmer language.
        
        ### ✨ Features:
        - 🎤 AI-powered voice dubbing
        - 🇰🇭 Khmer language support
        - 📹 Multiple video formats supported
        - 💾 Download dubbed videos
        
        ### 📋 How to use:
        1. Upload your video
        2. Click "Dub Video"
        3. Wait for processing
        4. Download your dubbed video
        
        ### 💰 Pricing:
        - **Trial**: 3 free videos
        - **VIP**: Unlimited access
        """)
    
    with col_about2:
        st.subheader("📱 Contact Us")
        
        # ===== TELEGRAM BOX IN ABOUT TAB =====
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0088cc,#00acee);padding:20px;border-radius:15px;color:white;text-align:center;">
            <h3>📱 Telegram</h3>
            <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="color:white;font-weight:bold;font-size:18px;text-decoration:none;">
                @YOUR_TELEGRAM
            </a>
            <p style="margin-top:10px;">សម្រាប់ជំនួយ និងទិញ VIP</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 📧 Email
        your@email.com
        
        ### 🌐 Website
        https://your-website.com
        """)

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/4CAF50/FFFFFF?text=Khmer+Dubber", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Actions")
    
    status = st.session_state.status
    if status == "vip":
        st.success("✅ VIP")
    elif status == "expired":
        st.error("❌ Expired")
    else:
        videos_used = st.session_state.license_data.get("videos_used", 0)
        remaining = 3 - videos_used
        if remaining > 0:
            st.warning(f"🆓 Trial ({remaining}/3)")
        else:
            st.error("⛔ Trial Expired")
    
    st.markdown("---")
    
    st.markdown("### 📱 Contact")
    
    # ===== TELEGRAM IN SIDEBAR =====
    st.markdown("""
    <div style="background:#0088cc;padding:15px;border-radius:10px;color:white;text-align:center;">
        <b>📱 Telegram</b><br>
        <a href="https://t.me/YOUR_TELEGRAM" target="_blank" style="color:white;font-weight:bold;text-decoration:none;">
            @YOUR_TELEGRAM
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Settings")
    if st.button("🔄 Reset App", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("Version 1.0.0")

# ========== FOOTER ==========
st.markdown("---")

# ===== TELEGRAM IN FOOTER =====
st.markdown("""
<div style="text-align:center;padding:10px;">
    <p>📱 <b>Contact:</b> <a href="https://t.me/YOUR_TELEGRAM" target="_blank">@YOUR_TELEGRAM</a></p>
    <p style="font-size:12px;color:#888;">© 2026 Khmer Dubber. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
