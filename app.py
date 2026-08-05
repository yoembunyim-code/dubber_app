import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ========== LICENSE MANAGER ==========
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

# ========== STREAMLIT UI ==========
st.set_page_config(
    page_title="Khmer Dubber - VIP System",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'license_data' not in st.session_state:
    st.session_state.license_data = load_license()
if 'status' not in st.session_state:
    st.session_state.status = check_license_status(st.session_state.license_data)

# Header
st.title("🎬 Khmer Dubber - VIP Activation System")
st.markdown("---")

# Main Layout
col1, col2 = st.columns([2, 1])

# COLUMN 1: Video Player
with col1:
    st.subheader("▶️ Video Player")
    
    status = st.session_state.status
    
    # Show status
    if status == "vip":
        st.success("🎉 VIP Mode - Unlimited Videos")
        remaining_text = "∞"
    elif status == "expired":
        st.error("⛔ License Expired. Please buy VIP.")
        remaining_text = "0"
    else:
        videos_used = st.session_state.license_data.get("videos_used", 0)
        remaining = 3 - videos_used
        if remaining < 0:
            remaining = 0
        if remaining > 0:
            st.info(f"📹 Videos Remaining (Trial): {remaining}")
            remaining_text = str(remaining)
        else:
            st.warning("🚫 No trials left. Please buy VIP.")
            remaining_text = "0"
    
    # Video display
    video_placeholder = st.empty()
    if 'video_message' not in st.session_state:
        st.session_state.video_message = "🎬 Press '▶ Start Video' to play."
    
    st.text_area("Video Display", st.session_state.video_message, height=200, disabled=True)
    
    # Control buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        if status == "vip" or (status == "trial" and remaining > 0):
            if st.button("▶ Start Video", use_container_width=True):
                if status == "vip":
                    st.session_state.video_message = "🎬 Playing video... (VIP - Unlimited)"
                    st.success("Playing video...")
                else:
                    new_count = videos_used + 1
                    st.session_state.license_data["videos_used"] = new_count
                    save_license(st.session_state.license_data)
                    st.session_state.video_message = f"▶ Playing video... ({new_count}/3 used)"
                    st.info(f"Playing video {new_count}/3")
                    st.rerun()
        else:
            st.button("▶ Start Video", disabled=True, use_container_width=True)
    
    with col_btn2:
        if st.button("💎 Buy VIP", use_container_width=True):
            st.info("📱 Contact Telegram: @YOUR_TELEGRAM")
    
    with col_btn3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.license_data = load_license()
            st.session_state.status = check_license_status(st.session_state.license_data)
            st.rerun()

# COLUMN 2: Activation
with col2:
    st.subheader("🔑 VIP Activation")
    
    if status == "vip":
        st.success("✅ **VIP Activated**")
    elif status == "expired":
        st.error("❌ **License Expired**")
    else:
        st.warning("🆓 **Trial Version**")
    
    st.markdown("---")
    
    code = st.text_input("Activation Code:", placeholder="Enter your VIP code...")
    
    if st.button("✅ Activate VIP", use_container_width=True):
        if code:
            success, message, data = activate_license(code)
            if success:
                st.session_state.license_data = data
                st.session_state.status = check_license_status(data)
                st.session_state.video_message = "✅ VIP Activated Successfully!"
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Please enter an Activation Code.")
    
    st.markdown("---")
    
    st.info("📱 **Contact for VIP**")
    st.write("សម្រាប់ទិញ VIP សូមទាក់ទង Telegram៖")
    st.markdown("**@YOUR_TELEGRAM**")
