# app.py (សម្រាប់ Streamlit Cloud)
import streamlit as st
import json
import os
import uuid
import datetime
import platform

# ================================================================
#  ផ្នែក LICENSE MANAGER (ដូចគ្នានឹងមុន ប៉ុន្តែបន្ថែមការ​ប្រើ session_state)
# ================================================================

LICENSE_FILE = "license.json"

def get_machine_id():
    """បង្កើត Machine ID តែមួយគត់"""
    try:
        # ប្រើ MAC address
        return str(uuid.getnode())
    except:
        # បើមិនបាន ប្រើ hostname
        return platform.node()

def default_license():
    return {
        "license_key": "",
        "activated": False,
        "activation_date": None,
        "expiry_date": None,
        "machine_id": get_machine_id(),
        "videos_used": 0
    }

def load_license():
    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            required = ["license_key","activated","activation_date","expiry_date","machine_id","videos_used"]
            for field in required:
                if field not in data:
                    return default_license()
            return data
    except:
        return default_license()

def save_license(data):
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False

def check_license(data):
    if not data.get("activated", False):
        return False, "Trial"
    if data.get("machine_id") != get_machine_id():
        return False, "Invalid Machine"
    expiry = data.get("expiry_date")
    if expiry:
        try:
            exp_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
            if exp_date < datetime.datetime.now().date():
                return False, "Expired"
        except:
            pass
    return True, "VIP"

def activate_license(key):
    valid_keys = ["VIP-2024-ABCD", "SUPER-VIP-2026", "TEAM-8888"]
    if key not in valid_keys:
        return False, "Invalid Code"
    data = load_license()
    data["license_key"] = key
    data["activated"] = True
    data["activation_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    exp = datetime.datetime.now() + datetime.timedelta(days=365)
    data["expiry_date"] = exp.strftime("%Y-%m-%d")
    data["machine_id"] = get_machine_id()
    if save_license(data):
        return True, "Activated Successfully"
    return False, "Failed to save license"


# ================================================================
#  ផ្នែក STREAMLIT UI
# ================================================================

# កំណត់រចនាសម្ព័ន្ធទំព័រ
st.set_page_config(page_title="VIP Activation System", layout="centered")

# ផ្ទុក License ពីឯកសារ (នឹងរក្សាទុកក្នុង session_state ដើម្បីកុំឲ្យអានឯកសារញឹកញាប់)
if "license_data" not in st.session_state:
    st.session_state.license_data = load_license()
if "videos_used" not in st.session_state:
    st.session_state.videos_used = st.session_state.license_data.get("videos_used", 0)

# ========== HEADER ==========
st.title("🔑 VIP Activation System")
st.markdown("---")

# ========== TOP SECTION: Activation ==========
col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Activation Code")
    code_input = st.text_input("បញ្ចូល Activation Code:", placeholder="e.g. VIP-2024-ABCD", key="code_input")
with col2:
    st.write("")  # spacing
    st.write("")
    col_act, col_chk = st.columns(2)
    with col_act:
        if st.button("✅ Activate VIP", use_container_width=True):
            if code_input.strip() == "":
                st.error("សូមបញ្ចូល Code មុនពេល Activate")
            else:
                success, msg = activate_license(code_input.strip())
                if success:
                    st.session_state.license_data = load_license()
                    st.session_state.videos_used = st.session_state.license_data.get("videos_used", 0)
                    st.success("🎉 VIP Activated ដោយជោគជ័យ!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}\n\nសូមទាក់ទង Telegram: @YOUR_TELEGRAM")
    with col_chk:
        if st.button("🔍 Check License", use_container_width=True):
            st.session_state.license_data = load_license()
            st.session_state.videos_used = st.session_state.license_data.get("videos_used", 0)
            st.rerun()

# ========== STATUS DISPLAY ==========
st.markdown("---")
license_data = st.session_state.license_data
videos_used = st.session_state.videos_used
is_vip, reason = check_license(license_data)

if is_vip:
    st.success("✅ **VIP Activated** (គ្មានដែនកំណត់)")
    st.info(f"📅 ថ្ងៃផុតកំណត់: {license_data.get('expiry_date', 'N/A')}")
    status_color = "green"
    trial_msg = ""
    start_disabled = False
else:
    if reason == "Expired":
        st.error("⛔ **License Expired** - សូមទិញ VIP ថ្មី")
        trial_msg = "សូមទិញ VIP ដើម្បីបន្តប្រើប្រាស់"
        start_disabled = True
    elif reason == "Invalid Machine":
        st.error("⛔ **Invalid Device** - License មិនត្រូវគ្នានឹងឧបករណ៍នេះទេ")
        trial_msg = "សូមទាក់ទងអ្នកគ្រប់គ្រង"
        start_disabled = True
    else:
        remaining = 3 - videos_used
        if remaining > 0:
            st.warning(f"📌 **Trial Version** - នៅសល់ {remaining} ដង (ក្នុងចំណោម 3)")
            trial_msg = f"នៅសល់ {remaining} ដង"
            start_disabled = False
        else:
            st.error("⛔ **Trial Expired** - អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ")
            trial_msg = "អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ"
            start_disabled = True

# ========== VIDEO SIMULATION ==========
st.markdown("---")
st.subheader("🎬 Video Player Simulation")

# Button Start Video
if st.button("▶ Start Video", disabled=start_disabled, use_container_width=True):
    if is_vip:
        st.success("កំពុងចាក់វីដេអូ... (VIP - Unlimited)")
    else:
        if videos_used < 3:
            # បង្កើនចំនួន
            new_videos_used = videos_used + 1
            license_data["videos_used"] = new_videos_used
            if save_license(license_data):
                st.session_state.license_data = load_license()
                st.session_state.videos_used = st.session_state.license_data.get("videos_used", 0)
                remaining = 3 - new_videos_used
                st.success(f"ចាក់វីដេអូរួចរាល់! (នៅសល់ {remaining} ដង)")
                st.rerun()
            else:
                st.error("មានបញ្ហាក្នុងការរក្សាទុកទិន្នន័យ")
        else:
            st.warning("អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។ សូមទិញ VIP ដើម្បីបន្តប្រើប្រាស់")

# ========== BUY VIP BUTTON ==========
st.markdown("---")
if st.button("💬 Buy VIP", use_container_width=True):
    st.info("សម្រាប់ទិញ VIP ឬទទួល Activation Code\n\nសូមទាក់ទង Telegram: **@YOUR_TELEGRAM**\n\n(លុបពាក្យ YOUR_TELEGRAM ចេញ រួចដាក់ឈ្មោះអ្នកវិញ)")

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("ℹ️ License Info")
    st.write(f"**Machine ID:** {get_machine_id()}")
    st.write(f"**License Key:** {license_data.get('license_key', 'None')}")
    st.write(f"**Activated:** {license_data.get('activated', False)}")
    st.write(f"**Activation Date:** {license_data.get('activation_date', 'N/A')}")
    st.write(f"**Expiry Date:** {license_data.get('expiry_date', 'N/A')}")
    st.write(f"**Videos Used:** {videos_used}/3")
    st.write("---")
    if st.button("🔄 Reset License (Debug)"):
        # សម្រាប់សាកល្បងតែប៉ុណ្ណោះ
        if os.path.exists(LICENSE_FILE):
            os.remove(LICENSE_FILE)
        st.session_state.license_data = default_license()
        st.session_state.videos_used = 0
        st.success("បានកំណត់ License ឡើងវិញជា Trial")
        st.rerun()
