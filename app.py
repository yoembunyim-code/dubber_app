import streamlit as st
import json
import os
from datetime import datetime, timedelta
import uuid
import platform

LICENSE_FILE = "license.json"
VALID_KEY = "DEEPSEEK-VIP-2026"

def get_machine_id():
    return str(uuid.getnode()) + "_" + platform.node()

def load_license():
    default = {"license_key":"", "activated":False, "activation_date":"", "expiry_date":"", "machine_id":get_machine_id(), "videos_used":0}
    if not os.path.exists(LICENSE_FILE): return default
    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for k in default:
                if k not in data: data[k] = default[k]
            return data
    except: return default

def save_license(data):
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except: return False

def check_status(data):
    if data.get("activated", False):
        expiry = data.get("expiry_date", "")
        if expiry:
            try:
                if datetime.now() > datetime.strptime(expiry, "%Y-%m-%d"):
                    return "expired"
            except: pass
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
        if save_license(data): return True, "VIP Activated! ✅", data
        return False, "Save failed.", data
    return False, "Invalid Code. ❌", data

# ========== Streamlit UI ==========
st.set_page_config(page_title="VIP Activation System", page_icon="🔑", layout="wide")

st.title("🔑 VIP Activation System")

# Load license
license_data = load_license()
status = check_status(license_data)

# Sidebar for Activation
with st.sidebar:
    st.header("🔐 VIP Activation")
    code = st.text_input("Activation Code", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Activate VIP", use_container_width=True):
            success, msg, data = activate_license(code)
            if success:
                license_data = data
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with col2:
        if st.button("🔍 Check License", use_container_width=True):
            license_data = load_license()
            status = check_status(license_data)
            if status == "vip":
                st.success("✅ VIP Active")
            elif status == "expired":
                st.error("❌ License Expired")
            else:
                rem = 3 - license_data.get("videos_used", 0)
                st.info(f"🆓 Trial: {rem if rem > 0 else 0} videos left")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("▶️ Video Player")
    
    # Status display
    if status == "vip":
        st.success("✅ VIP Activated - Unlimited Access")
        st.balloons()
    elif status == "expired":
        st.error("❌ License Expired - Please Buy VIP")
    else:
        rem = 3 - license_data.get("videos_used", 0)
        if rem > 0:
            st.warning(f"🆓 Trial Mode - {rem} videos remaining")
        else:
            st.error("⛔ Trial Expired - Please Buy VIP")

    # Video display
    video_placeholder = st.empty()
    if status == "vip":
        video_placeholder.info("🎬 Playing video... (VIP - Unlimited)")
    elif status == "expired":
        video_placeholder.error("⛔ License expired. Please buy VIP.")
    else:
        rem = 3 - license_data.get("videos_used", 0)
        if rem > 0:
            video_placeholder.info(f"🎬 Playing video... ({3 - rem + 1}/3 used)")
        else:
            video_placeholder.error("⛔ អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")

    # Start button
    if st.button("▶ Start Video", use_container_width=True):
        if status == "expired":
            st.error("License expired. Buy VIP.")
        elif status == "vip":
            st.success("🎬 Playing... (VIP Unlimited)")
        else:
            used = license_data.get("videos_used", 0)
            if used >= 3:
                st.error("Trial expired. Contact Telegram: @YOUR_TELEGRAM")
            else:
                license_data["videos_used"] = used + 1
                save_license(license_data)
                st.success(f"▶ Playing ({used+1}/3)")
                st.rerun()

with col2:
    st.subheader("💎 Buy VIP")
    st.info("សម្រាប់ទិញ VIP សូមទាក់ទង Telegram៖")
    st.markdown("### 📱 @YOUR_TELEGRAM")
    
    if st.button("📩 Contact Telegram", use_container_width=True):
        st.success("ទាក់ទងមកកាន់ Telegram: @YOUR_TELEGRAM")

# Footer
st.divider()
st.caption("📱 Contact: @YOUR_TELEGRAM | Version 1.0")
