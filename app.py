import streamlit as st
import json
import os
from datetime import datetime, timedelta
import uuid
import platform

# ================================================================
#  LICENSE MANAGER (ផ្នែកគ្រប់គ្រងទិន្នន័យ License)
# ================================================================

LICENSE_FILE = "license.json"
VALID_KEY = "DEEPSEEK-VIP-2026"   # កូដសម្ងាត់សម្រាប់ Activate VIP

def get_machine_id():
    """បង្កើត Machine ID សម្រាប់ភ្ជាប់ជាមួយ License"""
    return str(uuid.getnode()) + "_" + platform.node()

def load_license():
    """អានទិន្នន័យពី license.json បើគ្មានឯកសារបង្កើតថ្មី"""
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
            # បញ្ចូល Key ដែលបាត់ (ករណីមានឯកសារចាស់)
            for key in default_data:
                if key not in data:
                    data[key] = default_data[key]
            return data
    except (json.JSONDecodeError, IOError):
        return default_data

def save_license(data):
    """រក្សាទុកទិន្នន័យទៅ license.json"""
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False

def check_license_status(data):
    """
    ពិនិត្យស្ថានភាព License
    Return: 'vip', 'expired', 'trial'
    """
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
    """
    ដំណើរការ Activate VIP
    Return: (success, message, updated_data)
    """
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

def init_session_state():
    """ដំឡើង Session State សម្រាប់ Streamlit"""
    if 'license_data' not in st.session_state:
        st.session_state.license_data = load_license()
    if 'status' not in st.session_state:
        st.session_state.status = check_license_status(st.session_state.license_data)
    if 'video_count' not in st.session_state:
        st.session_state.video_count = st.session_state.license_data.get("videos_used", 0)
    if 'remaining' not in st.session_state:
        remaining = 3 - st.session_state.video_count
        if remaining < 0:
            remaining = 0
        st.session_state.remaining = remaining

def update_license_data():
    """ធ្វើបច្ចុប្បន្នភាព Session State ពេលមានការផ្លាស់ប្តូរ"""
    st.session_state.license_data = load_license()
    st.session_state.status = check_license_status(st.session_state.license_data)
    st.session_state.video_count = st.session_state.license_data.get("videos_used", 0)
    remaining = 3 - st.session_state.video_count
    if remaining < 0:
        remaining = 0
    st.session_state.remaining = remaining

def main():
    # កំណត់រចនាសម្ព័ន្ធ Page
    st.set_page_config(
        page_title="VIP Activation System - Dubber",
        page_icon="🎬",
        layout="wide"
    )
    
    # ដំឡើង Session State
    init_session_state()
    
    # ========== HEADER ==========
    st.title("🎬 Khmer Dubber - VIP Activation System")
    st.markdown("---")
    
    # ========== MAIN LAYOUT ==========
    col1, col2 = st.columns([2, 1])
    
    # ----- COLUMN 1: Video Player (មុខងារចម្បង) -----
    with col1:
        st.subheader("▶️ Video Player")
        
        # បង្ហាញចំនួនវីដេអូនៅសល់
        status = st.session_state.status
        if status == "vip":
            st.success("🎉 VIP Mode - Unlimited Videos")
            video_remaining = "∞"
        elif status == "expired":
            st.error("⛔ License Expired. Please buy VIP.")
            video_remaining = "0"
        else:
            remaining = st.session_state.remaining
            if remaining > 0:
                st.info(f"📹 Videos Remaining (Trial): {remaining}")
                video_remaining = str(remaining)
            else:
                st.warning("🚫 No trials left. Please buy VIP.")
                video_remaining = "0"
        
        # បង្អួចបង្ហាញវីដេអូ
        video_placeholder = st.empty()
        
        # កន្លែងសម្រាប់បង្ហាញស្ថានភាពវីដេអូ
        if 'video_message' not in st.session_state:
            st.session_state.video_message = "🎬 Press '▶ Start Video' to play.\n\n(Simulation for demonstration)"
        
        video_placeholder.text_area("Video Display", st.session_state.video_message, height=200, disabled=True)
        
        # Control Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            # ពិនិត្យថាតើប៊ូតុង Start អាចចុចបានឬទេ
            if status == "vip" or (status == "trial" and st.session_state.remaining > 0):
                if st.button("▶ Start Video", use_container_width=True):
                    start_video()
            else:
                st.button("▶ Start Video", disabled=True, use_container_width=True)
        
        with col_btn2:
            if st.button("💎 Buy VIP", use_container_width=True):
                show_telegram()
        
        with col_btn3:
            if st.button("🔄 Check License", use_container_width=True):
                update_license_data()
                st.rerun()
    
    # ----- COLUMN 2: Activation System (ផ្នែកខាងស្តាំ) -----
    with col2:
        st.subheader("🔑 VIP Activation")
        
        # បង្ហាញស្ថានភាពបច្ចុប្បន្ន
        if status == "vip":
            st.success("✅ **VIP Activated**")
        elif status == "expired":
            st.error("❌ **License Expired**")
        else:
            st.warning("🆓 **Trial Version**")
        
        st.markdown("---")
        
        # TextBox សម្រាប់បញ្ចូល Activation Code
        code = st.text_input("Activation Code:", placeholder="Enter your VIP code...")
        
        # Buttons
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            if st.button("✅ Activate VIP", use_container_width=True):
                if code:
                    success, message, data = activate_license(code)
                    if success:
                        st.session_state.license_data = data
                        update_license_data()
                        st.session_state.video_message = "✅ VIP Activated Successfully! All features unlocked. 🎉"
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter an Activation Code.")
        
        with col_act2:
            if st.button("🔍 Check License", use_container_width=True):
                update_license_data()
                st.rerun()
        
        st.markdown("---")
        
        # Telegram Contact
        st.info("📱 **Contact for VIP**")
        st.write("សម្រាប់ទិញ VIP ឬទទួល Activation Code សូមទាក់ទង Telegram៖")
        st.markdown("**@YOUR_TELEGRAM**")
        
        # ប៊ូតុង Buy VIP (ទី២)
        if st.button("💎 Buy VIP Now", use_container_width=True):
            show_telegram()

def start_video():
    """ដំណើរការចុច Start Video"""
    status = st.session_state.status
    
    # ករណី Expired
    if status == "expired":
        st.session_state.video_message = "⛔ License expired. Please buy VIP."
        st.error("Access Denied: License expired.")
        return
    
    # ករណី VIP
    if status == "vip":
        st.session_state.video_message = "🎬 Playing video... (VIP - Unlimited)\n\nEnjoy full access!"
        st.success("Playing video...")
        return
    
    # ----- ករណី Trial -----
    videos_used = st.session_state.video_count
    if videos_used >= 3:
        st.session_state.video_message = "⛔ អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM"
        st.warning("Trial expired. Please buy VIP.")
        return
    
    # ប្រើប្រាស់វីដេអូ ១ ដង
    new_count = videos_used + 1
    st.session_state.license_data["videos_used"] = new_count
    save_license(st.session_state.license_data)
    
    # ធ្វើបច្ចុប្បន្នភាព Session State
    st.session_state.video_count = new_count
    remaining = 3 - new_count
    if remaining < 0:
        remaining = 0
    st.session_state.remaining = remaining
    
    # បង្ហាញសារ
    st.session_state.video_message = f"▶ Playing video... ({new_count}/3 used)"
    st.info(f"Playing video {new_count}/3")
    
    # បើអស់ហើយ
    if remaining == 0:
        st.session_state.video_message = "⛔ អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM"
        st.warning("Trial expired. Please buy VIP.")
    
    st.rerun()

def show_telegram():
    """បង្ហាញព័ត៌មានទំនាក់ទំនង Telegram"""
    st.info(
        "📱 **Contact for VIP**\n\n"
        "សម្រាប់ទិញ VIP ឬទទួល Activation Code សូមទាក់ទង Telegram៖\n\n"
        "**@YOUR_TELEGRAM**"
    )

if __name__ == "__main__":
    main()
