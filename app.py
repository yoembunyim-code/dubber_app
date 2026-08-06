import streamlit as st
import json
import os
from datetime import datetime, timedelta
import uuid
import platform

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
#  STREAMLIT UI
# ================================================================

st.set_page_config(page_title="VIP Activation System", layout="wide")

# Initialize session state
if 'license_data' not in st.session_state:
    st.session_state.license_data = load_license()
    st.session_state.current_status = check_license_status(st.session_state.license_data)

# ========== HEADER ==========
st.title("🔑 VIP Activation System - Video Tool")
st.markdown("---")

# ========== COLUMN LAYOUT ==========
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📹 Video Player")
    
    # Video display area
    video_placeholder = st.empty()
    with video_placeholder.container():
        st.info("🎬 Press '▶ Start Video' to play.\n\n(Simulation for demonstration)")
    
    # Control buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        start_btn = st.button("▶ Start Video", use_container_width=True)
    with col_btn2:
        stop_btn = st.button("⏹ Stop Video", use_container_width=True)
    with col_btn3:
        buy_btn = st.button("💎 Buy VIP", use_container_width=True)

with col2:
    st.subheader("🔑 VIP Activation")
    
    # Activation Code input
    code = st.text_input("Activation Code:", placeholder="Enter your code here", type="password")
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("✅ Activate VIP", use_container_width=True):
            success, message, updated_data = activate_license(code)
            if success:
                st.session_state.license_data = updated_data
                st.session_state.current_status = check_license_status(updated_data)
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with col_act2:
        if st.button("🔍 Check License", use_container_width=True):
            st.session_state.license_data = load_license()
            st.session_state.current_status = check_license_status(st.session_state.license_data)
            st.rerun()
    
    st.markdown("---")
    
    # Status display
    status = st.session_state.current_status
    if status == "vip":
        st.success("✅ VIP Activated")
        st.info("🎉 VIP Mode - Unlimited Videos")
    elif status == "expired":
        st.error("❌ License Expired")
        st.warning("⛔ License Expired. Please buy VIP.")
    else:
        remaining = 3 - st.session_state.license_data.get("videos_used", 0)
        if remaining < 0:
            remaining = 0
        if remaining > 0:
            st.warning(f"🆓 Trial Version - {remaining} videos remaining")
        else:
            st.error("⛔ Trial Expired")
            st.warning("អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។ ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("📱 Contact Telegram: **@YOUR_TELEGRAM**", help="Click to copy")

# ========== HANDLE VIDEO START ==========
if start_btn:
    status = st.session_state.current_status
    
    if status == "expired":
        st.error("License expired. Please buy VIP.")
    elif status == "trial":
        videos_used = st.session_state.license_data.get("videos_used", 0)
        if videos_used >= 3:
            st.error("អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។ ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")
        else:
            st.session_state.license_data["videos_used"] = videos_used + 1
            save_license(st.session_state.license_data)
            st.session_state.current_status = check_license_status(st.session_state.license_data)
            
            remaining = 3 - st.session_state.license_data["videos_used"]
            with video_placeholder.container():
                st.success(f"▶ Playing video... ({videos_used + 1}/3 used)")
                if remaining == 0:
                    st.warning("⛔ អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។ ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")
            st.rerun()
    else:  # VIP
        with video_placeholder.container():
            st.success("🎬 Playing video... (VIP - Unlimited)\n\nEnjoy full access!")

if stop_btn:
    with video_placeholder.container():
        st.info("⏹ Video stopped. Press 'Start Video' to play again.")

if buy_btn:
    st.info("💎 សម្រាប់ទិញ VIP ឬទទួល Activation Code សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")

# ================================================================
#  REQUIREMENTS.TXT
# ================================================================

# បង្កើតឯកសារ requirements.txt ដោយមាន៖
# streamlit
