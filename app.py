import json
import os
import time
from datetime import datetime, timedelta
import streamlit as st

# ==============================================================================
# ⚙️ កន្លែងកំណត់ទិន្នន័យ (DEVELOPER CONFIGURATIONS)
# ==============================================================================
TELEGRAM_USERNAME = "@YOUR_TELEGRAM"  # ✍️ ផ្លាស់ប្តូរឈ្មោះ Telegram របស់អ្នកនៅទីនេះ
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME.replace('@', '')}"

VALID_VIP_CODES = [
    "VIP-SECRET-2026",
    "VIP-PASS-8888",
    "VIP-PRO-9999",
    "CAM-VIP-1234"
]

TRIAL_LIMIT = 3
LICENSE_FILE = "license.json"


# ==============================================================================
# 🛡️ LICENSE FUNCTIONS
# ==============================================================================
def load_license():
    default_data = {
        "license_key": "",
        "activated": False,
        "activation_date": "",
        "expiry_date": "",
        "trial_used": 0
    }
    if not os.path.exists(LICENSE_FILE):
        return default_data
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("trial_used", 0)
            return data
    except Exception:
        return default_data

def save_license(data):
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def activate_vip(code):
    code = code.strip()
    if not code:
        return False, "សូមបញ្ចូល Activation Code!"
    if code in VALID_VIP_CODES:
        data = load_license()
        now = datetime.now()
        expiry = now + timedelta(days=365)
        data["license_key"] = code
        data["activated"] = True
        data["activation_date"] = now.strftime("%Y-%m-%d")
        data["expiry_date"] = expiry.strftime("%Y-%m-%d")
        save_license(data)
        return True, "🎉 Activation ជោគជ័យ! កម្មវិធីរបស់អ្នកត្រូវបានដោះសោ VIP រួចរាល់។"
    else:
        return False, "Activation Code មិនត្រឹមត្រូវទេ (Invalid Code)!"


# ==============================================================================
# 🌐 STREAMLIT GUI INTERFACE
# ==============================================================================
st.set_page_config(page_title="VIP Activation System", page_icon="🎬", layout="centered")

if "license_data" not in st.session_state:
    st.session_state.license_data = load_license()

lic_data = st.session_state.license_data

st.title("🎬 VIDEO PROCESSING SOFTWARE")
st.markdown("---")

# 🔑 Activation Section
st.subheader("🔑 VIP Activation Panel")

col_input, col_btn = st.columns([3, 1])
with col_input:
    user_code = st.text_input("Activation Code:", placeholder="បញ្ចូលលេខកូដ VIP...", key="vip_code_input")
with col_btn:
    st.write("##")
    if st.button("Activate VIP", type="primary", use_container_width=True):
        success, msg = activate_vip(user_code)
        if success:
            st.session_state.license_data = load_license()
            st.success(msg)
            time.sleep(1)
            st.rerun()
        else:
            st.error(msg)

# Status & Info
is_vip = lic_data.get("activated", False)
used_trials = lic_data.get("trial_used", 0)
remaining_trials = max(0, TRIAL_LIMIT - used_trials)

c1, c2, c3 = st.columns([2, 1.5, 1.5])

with c1:
    if is_vip:
        st.success("ស្ថានភាព៖ VIP Activated ✅")
    elif remaining_trials > 0:
        st.warning(f"ស្ថានភាព៖ Trial Version ⏳")
    else:
        st.error("ស្ថានភាព៖ Trial Expired 🚫")

with c2:
    if st.button("📋 Check License", use_container_width=True):
        if is_vip:
            st.info(f"**Key:** `{lic_data.get('license_key')}`\n\n**Activated:** {lic_data.get('activation_date')}\n\n**Expires:** {lic_data.get('expiry_date')}")
        else:
            st.warning(f"ចំនួនវីដេអូសាកល្បងដែលបានប្រើ៖ {used_trials}/{TRIAL_LIMIT}")

with c3:
    st.link_button("🛒 ទិញ VIP Code", TELEGRAM_LINK, use_container_width=True)

st.markdown("---")

# 🎬 Video Processing Section
st.subheader("▶ ដំណើរការវីដេអូ")

if is_vip:
    st.success("🎉 អ្នកកំពុងប្រើប្រាស់ VIP Mode! អាចដំណើរការវីដេអូបានគ្មានដែនកំណត់។")
elif remaining_trials > 0:
    st.info(f"⚠️ អ្នកកំពុងប្រើប្រាស់ Trial Version (ចំនួនវីដេអូសាកល្បងនៅសល់៖ **{remaining_trials}/{TRIAL_LIMIT}**)")
else:
    st.error(f"🚫 អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ ({TRIAL_LIMIT}/{TRIAL_LIMIT} វីដេអូ)!\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ **{TELEGRAM_USERNAME}**")

start_disabled = (not is_vip) and (remaining_trials <= 0)

if st.button("▶ ចាប់ផ្តើមដំណើរការវីដេអូ (Start Video)", disabled=start_disabled, type="primary"):
    if is_vip:
        st.write("🔄 [VIP] កំពុងដំណើរការវីដេអូ...")
        time.sleep(1.5)
        st.success("✅ ដំណើរការវីដេអូរួចរាល់ដោយជោគជ័យ!")
    else:
        lic_data["trial_used"] += 1
        save_license(lic_data)
        st.session_state.license_data = lic_data
        st.write(f"🔄 [Trial] កំពុងដំណើរការវីដេអូ... (នៅសល់ {max(0, TRIAL_LIMIT - lic_data['trial_used'])} វីដេអូទៀត)")
        time.sleep(1.5)
        st.success("✅ ដំណើរការវីដេអូរួចរាល់!")
        st.rerun()
