import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64
import time

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
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #2196F3, #1976D2);
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
    .voice-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .voice-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .voice-card.selected {
        border-color: #4CAF50;
        background: #e8f5e9;
    }
    .progress-bar {
        width: 100%;
        height: 6px;
        background: #e0e0e0;
        border-radius: 3px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-bar .fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 3px;
        transition: width 0.5s;
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
if 'selected_voice' not in st.session_state:
    st.session_state.selected_voice = "Male 1"
if 'dub_language' not in st.session_state:
    st.session_state.dub_language = "Khmer"
if 'translation_text' not in st.session_state:
    st.session_state.translation_text = ""
if 'processing_progress' not in st.session_state:
    st.session_state.processing_progress = 0

# ========== VOICE OPTIONS ==========
VOICE_OPTIONS = {
    "Male 1": {"emoji": "👨", "desc": "បុរស សំឡេងធម្មតា"},
    "Male 2": {"emoji": "👨‍🦰", "desc": "បុរស សំឡេងជ្រៅ"},
    "Female 1": {"emoji": "👩", "desc": "ស្ត្រី សំឡេងធម្មតា"},
    "Female 2": {"emoji": "👩‍🦳", "desc": "ស្ត្រី សំឡេងផ្អែម"},
    "Youth": {"emoji": "🧑", "desc": "ក្មេង សំឡេងស្រស់"},
    "Elder": {"emoji": "👴", "desc": "ចាស់ សំឡេងក្រៀម"},
}

# ========== HEADER ==========
col_title, col_status = st.columns([2, 1])

with col_title:
    st.title("🎬 Khmer Dubber")
    st.markdown("បកប្រែវីដេអូជាភាសាខ្មែរ ជាមួយ AI និងសម្លេងជ្រើសរើស")

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
tab1, tab2, tab3 = st.tabs(["🎬 Dub Video", "🔑 VIP Activation", "ℹ️ About"])

# ========== TAB 1: DUB VIDEO ==========
with tab1:
    col_left, col_right = st.columns([1, 1])
    
    # ----- LEFT COLUMN: Upload & Controls -----
    with col_left:
        st.subheader("📤 Upload Video")
        
        uploaded_file = st.file_uploader(
            "ជ្រើសរើសវីដេអូ",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm', 'm4v'],
            accept_multiple_files=False,
            help="ដាក់វីដេអូដែលអ្នកចង់បកប្រែ"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_video = uploaded_file
            st.success(f"✅ បានដាក់វីដេអូ: {uploaded_file.name}")
            st.info(f"📁 ទំហំ: {uploaded_file.size / (1024*1024):.2f} MB")
            
            # ===== LANGUAGE & VOICE SELECTION =====
            st.markdown("---")
            st.subheader("⚙️ ការកំណត់ការបកប្រែ")
            
            # Language selection
            col_lang1, col_lang2 = st.columns(2)
            with col_lang1:
                dub_language = st.selectbox(
                    "🌐 ភាសាគោលដៅ",
                    ["Khmer", "English", "Thai", "Vietnamese", "Chinese", "Japanese"],
                    index=0
                )
                st.session_state.dub_language = dub_language
            
            with col_lang2:
                st.markdown("**🎤 ជ្រើសរើសសម្លេង**")
                selected_voice = st.selectbox(
                    "សម្លេង",
                    list(VOICE_OPTIONS.keys()),
                    index=0,
                    format_func=lambda x: f"{VOICE_OPTIONS[x]['emoji']} {x} - {VOICE_OPTIONS[x]['desc']}"
                )
                st.session_state.selected_voice = selected_voice
            
            # ===== VOICE PREVIEW CARDS =====
            st.markdown("**សម្លេងដែលអាចជ្រើសរើសបាន៖**")
            cols = st.columns(3)
            for idx, (voice, info) in enumerate(VOICE_OPTIONS.items()):
                col_idx = idx % 3
                with cols[col_idx]:
                    is_selected = st.session_state.selected_voice == voice
                    border_color = "#4CAF50" if is_selected else "#e0e0e0"
                    bg_color = "#e8f5e9" if is_selected else "#f8f9fa"
                    st.markdown(f"""
                    <div style="background:{bg_color};padding:12px;border-radius:10px;border:2px solid {border_color};text-align:center;margin:5px 0;cursor:pointer;">
                        <div style="font-size:28px;">{info['emoji']}</div>
                        <div style="font-weight:bold;">{voice}</div>
                        <div style="font-size:12px;color:#666;">{info['desc']}</div>
                        {'' if not is_selected else '<div style="color:#4CAF50;">✅ Selected</div>'}
                    </div>
                    """, unsafe_allow_html=True)
            
            # ===== SUBTITLE OPTIONS =====
            st.markdown("---")
            st.subheader("📝 ចំណងជើងរង")
            
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                add_subtitles = st.checkbox("បន្ថែមចំណងជើងរងភាសាខ្មែរ", value=True)
            with col_sub2:
                subtitle_position = st.selectbox("ទីតាំង", ["បាត", "កណ្តាល", "លើ"])
            
            # ===== ACTION BUTTONS =====
            st.markdown("---")
            st.subheader("🎯 ចាប់ផ្តើមបកប្រែ")
            
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
                if can_process:
                    if st.button("🎤 បកប្រែវីដេអូ", use_container_width=True, type="primary"):
                        with st.spinner("កំពុងដំណើរការបកប្រែ... សូមរង់ចាំ..."):
                            # Simulate processing with progress
                            for i in range(101):
                                st.session_state.processing_progress = i
                                time.sleep(0.02)
                            
                            st.session_state.video_processed = True
                            st.session_state.dubbed_video = st.session_state.uploaded_video
                            
                            # Update trial count
                            if status != "vip":
                                new_count = st.session_state.license_data.get("videos_used", 0) + 1
                                st.session_state.license_data["videos_used"] = new_count
                                save_license(st.session_state.license_data)
                                st.session_state.status = check_license_status(st.session_state.license_data)
                            
                            # Set translation text
                            st.session_state.translation_text = f"✅ បានបកប្រែជោគជ័យ!\n\nសម្លេង: {st.session_state.selected_voice}\nភាសា: {st.session_state.dub_language}"
                            
                            st.success("✅ បានបកប្រែវីដេអូជោគជ័យ!")
                            st.rerun()
                else:
                    st.button("🎤 បកប្រែវីដេអូ", disabled=True, use_container_width=True)
                    st.warning(f"⚠️ {reason}")
            
            with col_btn2:
                if st.button("🔄 កំណត់ឡើងវិញ", use_container_width=True):
                    st.session_state.uploaded_video = None
                    st.session_state.dubbed_video = None
                    st.session_state.video_processed = False
                    st.session_state.translation_text = ""
                    st.session_state.processing_progress = 0
                    st.rerun()
            
            # ===== TRIAL STATUS =====
            if status == "trial":
                videos_used = st.session_state.license_data.get("videos_used", 0)
                remaining = 3 - videos_used
                if remaining > 0:
                    st.info(f"📹 នៅសល់សិទ្ធិសាកល្បង: {remaining} / 3")
                else:
                    st.warning("⚠️ អស់សិទ្ធិសាកល្បងហើយ! សូម Activate VIP ដើម្បីបន្តប្រើប្រាស់")
                    st.markdown("""
                    <div style="background:#fff3cd;padding:15px;border-radius:10px;border-left:4px solid #ffc107;">
                        <b>📱 ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖</b><br>
                        <a href="https://t.me/YOUR_TELEGRAM" target="_blank">@YOUR_TELEGRAM</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ===== PROGRESS BAR =====
            if st.session_state.processing_progress > 0 and st.session_state.processing_progress < 100:
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="fill" style="width:{st.session_state.processing_progress}%;"></div>
                </div>
                <p style="text-align:center;font-size:14px;">កំពុងដំណើរការ... {st.session_state.processing_progress}%</p>
                """, unsafe_allow_html=True)
            
        else:
            # Empty state
            st.markdown("""
            <div class="upload-box">
                <h3>📂 អូស និង ទម្លាក់</h3>
                <p>ឬចុចដើម្បីជ្រើសរើសវីដេអូ</p>
                <p style="font-size:12px;color:#888;">គាំទ្រ: MP4, AVI, MOV, MKV, WEBM</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ----- RIGHT COLUMN: Video Preview -----
    with col_right:
        st.subheader("📺 មើលវីដេអូ")
        
        if st.session_state.video_processed and st.session_state.dubbed_video is not None:
            st.success("🎉 វីដេអូដែលបានបកប្រែរួចរាល់!")
            
            # Show translation info
            if st.session_state.translation_text:
                st.info(st.session_state.translation_text)
            
            # Show video
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
            
            # Download button
            st.download_button(
                label="💾 ទាញយកវីដេអូដែលបានបកប្រែ",
                data=video_data,
                file_name=f"dubbed_{st.session_state.uploaded_video.name if st.session_state.uploaded_video else 'video'}",
                mime="video/mp4",
                use_container_width=True
            )
            
        elif st.session_state.uploaded_video is not None:
            # Show original video
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
            
            st.caption("📌 វីដេអូដើម - ចុច 'បកប្រែវីដេអូ' ដើម្បីដំណើរការ")
            
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
            st.warning(f"🆓 **Trial Mode** ({remaining}/3 videos remaining)")
        
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
        st.subheader("💎 Get VIP Access")
        
        st.markdown("""
        ### 🎯 អត្ថប្រយោជន៍ VIP:
        - ✅ បកប្រែវីដេអូគ្មានដែនកំណត់
        - ✅ មិនមានកំណត់ Trial
        - ✅ ដំណើរការលឿនជាងមុន
        - ✅ ប្រើប្រាស់មុខងារទាំងអស់
        - ✅ សុពលភាព ១ ឆ្នាំ
        """)
        
        st.markdown("---")
        
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
        st.subheader("ℹ️ អំពី Khmer Dubber")
        
        st.markdown("""
        ### 🎬 តើ Khmer Dubber ជាអ្វី?
        
        Khmer Dubber គឺជាឧបករណ៍បកប្រែវីដេអូដោយប្រើ AI ដែលអាចបកប្រែវីដេអូជាភាសាខ្មែរ។
        
        ### ✨ មុខងារ:
        - 🎤 បកប្រែសំឡេងដោយ AI
        - 🇰🇭 គាំទ្រភាសាខ្មែរ
        - 📹 គាំទ្រវីដេអូច្រើនប្រភេទ
        - 💾 ទាញយកវីដេអូដែលបានបកប្រែ
        - 🎤 ជ្រើសរើសសម្លេងបានច្រើនប្រភេទ
        
        ### 📋 របៀបប្រើប្រាស់:
        1. ដាក់វីដេអូរបស់អ្នក
        2. ជ្រើសរើសសម្លេងដែលចូលចិត្ត
        3. ចុច "បកប្រែវីដេអូ"
        4. រង់ចាំដំណើរការ
        5. ទាញយកវីដេអូដែលបានបកប្រែ
        
        ### 💰 តម្លៃ:
        - **Trial**: ៣ វីដេអូឥតគិតថ្លៃ
        - **VIP**: ប្រើប្រាស់គ្មានដែនកំណត់
        """)
    
    with col_about2:
        st.subheader("📱 Contact Us")
        
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
    
    st.markdown("### 🎤 សម្លេងបច្ចុប្បន្ន")
    if st.session_state.selected_voice:
        voice_info = VOICE_OPTIONS.get(st.session_state.selected_voice, {})
        st.markdown(f"""
        <div style="background:#f0f0f0;padding:15px;border-radius:10px;text-align:center;">
            <div style="font-size:40px;">{voice_info.get('emoji', '🎤')}</div>
            <div style="font-weight:bold;">{st.session_state.selected_voice}</div>
            <div style="font-size:12px;color:#666;">{voice_info.get('desc', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📱 Contact")
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
    st.caption("Version 2.0.0")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:10px;">
    <p>📱 <b>Contact:</b> <a href="https://t.me/YOUR_TELEGRAM" target="_blank">@YOUR_TELEGRAM</a></p>
    <p style="font-size:12px;color:#888;">© 2026 Khmer Dubber. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
