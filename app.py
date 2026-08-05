import streamlit as st
import os  # ត្រូវការបន្ថែមផ្នែកនេះ សម្រាប់ពិនិត្យឯកសារ

# =======================================================
# 1. ផ្នែក Config
# =======================================================
OWNER_TELEGRAM = "t.me/bunyimyoem" # កែត្រង់នេះ
CURRENT_MACHINE_ID = "58611610212922"

LICENSE_DATABASE = {
    "BUNYIM-VIP-001": "58611610212922",
    "ADMIN-9999": "58221133882211"
}

# កំណត់ឈ្មោះឯកសារលទ្ធផលពីដើម ដើម្បីកុំឲ្យវាឡើង NameError
OUTPUT_VIDEO_NAME = "output_video.mp4"

# =======================================================
# 2. កំណត់រចនាសម្ព័ន្ធទំព័រ & CSS
# =======================================================
st.set_page_config(page_title="VIP Activation System", layout="wide", page_icon="🔑")

if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False

st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #1e293b; color: #ffffff; }
    section[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }
    .stButton > button { border-radius: 10px; font-weight: 600; border: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s; width: 100%; height: 3.2em; }
    .stButton > button:hover { transform: translateY(-2px); }
    .stButton.green-btn > button { background-color: #10b981 !important; color: white !important; height: 4.5em; font-size: 20px; }
    div[data-testid="stFileUploader"] { width: 100%; }
    div[data-testid="stFileUploader"] section { padding: 0; border: none; background: transparent; }
    div[data-testid="stFileUploader"] button { background-color: #3b82f6 !important; color: white !important; border-radius: 10px; width: 100%; height: 3.2em; font-weight: bold; border: none; }
    .stTextInput > div > div > input { border-radius: 10px; border: 1px solid #cbd5e1; padding: 12px; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# =======================================================
# 3. ផ្នែក SIDEBAR
# =======================================================
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    st.markdown("---")
    st.markdown("**លេខសម្គាល់ឧបករណ៍ (Machine ID):**")
    st.code(CURRENT_MACHINE_ID, language="text")
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាពប្រើប្រាស់:** `{status_text}`")
    st.markdown("---")
    st.markdown("#### 📞 ត្រូវការជំនួយ?")
    st.markdown(f"[![Telegram](https://img.shields.io/badge/Telegram-{OWNER_TELEGRAM}-blue?style=for-the-badge&logo=telegram)](https://t.me/{OWNER_TELEGRAM.replace('@', '')})")
    st.markdown("---")
    if st.button("🔄 Reset License (Debug)", use_container_width=True):
        st.session_state.is_activated = False
        st.success("បាន Reset ស្ថានភាពវិញ!")

# =======================================================
# 4. ផ្នែក MAIN UI
# =======================================================
st.markdown("<h1 style='text-align: center;'>🔑 VIP Activation System</h1>", unsafe_allow_html=True)
st.markdown("---")

# 4.1 Activate
if st.session_state.is_activated:
    st.success("🎉 ប្រព័ន្ធត្រូវបាន Activate រួចរាល់ហើយ!")
else:
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        act_code_input = st.text_input("បញ្ចូល Activation Code", placeholder="ឧ. VIP-2026-ABCD", label_visibility="collapsed")
    with c_btn:
        if st.button("✅ Activate VIP", type="primary", use_container_width=True):
            if not act_code_input or act_code_input.strip() == "":
                st.error("❌ សូមបញ្ចូលលេខកូដជាមុនសិន។")
            else:
                if act_code_input in LICENSE_DATABASE:
                    expected_machine = LICENSE_DATABASE[act_code_input]
                    if expected_machine == CURRENT_MACHINE_ID:
                        st.session_state.is_activated = True
                        st.success("🎉 Activate ជោគជ័យ!")
                        st.rerun()
                    else:
                        st.error("❌ លេខកូដនេះត្រូវបានប្រើដោយឧបករណ៍ផ្សេងហើយ!")
                else:
                    st.error("❌ លេខកូដមិនត្រឹមត្រូវ!")

# 4.2 Control Panel
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📂 ប្រអប់ឧបករណ៍គ្រប់គ្រង")
st.markdown("<hr style='border: 0;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    uploaded_video = st.file_uploader("Browse Video", type=['mp4', 'avi', 'mov', 'mkv'], label_visibility="collapsed")
    if uploaded_video is not None:
        st.caption(f"ឯកសារ៖ `{uploaded_video.name}`")
with col2:
    st.button("📄 BROWSE SRT", type="primary", use_container_width=True)

# ចំណុចថ្មី៖ ដាក់ឲ្យមានអថេរ voice_option សម្រាប់រក្សាទុកជម្រើសសម្លេង
voice_option = st.selectbox("សម្លេង", ["ស្រី (Female)", "ប្រុស (Male)"])

c1, c2, c3 = st.columns(3)
with c1:
    st.button("🤖 AUTO", use_container_width=True)
with c2:
    st.button("👩 SREY MOM", use_container_width=True)
with c3:
    st.button("🧑 PIDETH", use_container_width=True)

st.button("🗣️ DUB AS-IS (no translate)", use_container_width=True)

# 4.3 ប៊ូតុង START (បានកែឲ្យដំណើរការពេលចុចរួច និងការពារ NameError)
st.markdown('<div class="green-btn">', unsafe_allow_html=True)
if st.button("🚀 START", use_container_width=True):
    if not st.session_state.is_activated:
        st.warning("សូម Activate VIP ជាមុនសិន!")
    elif uploaded_video is None:
        st.warning("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
    else:
        # ដំណើរការដោយជោគជ័យ
        st.success("✅ ចុច START ជោគជ័យ! (សម្លេងដែលអ្នកបានជ្រើសគឺ: " + voice_option + ")")

        # នៅផ្នែកនេះ អ្នកនឹងសរសេរកូដ AI របស់អ្នក ដែលទាញយក voice_option មកប្រើដើម្បីកំណត់សម្លេង។
        # ឧទាហរណ៍៖ run_ai_processing(uploaded_video, voice_option)

        # ពិនិត្យមើលថាវីដេអូលទ្ធផលត្រូវបាន AI បង្កើតជោគជ័យឬអត់ (ទប់ស្កាត់ NameError)
        if os.path.exists(OUTPUT_VIDEO_NAME):
            st.markdown("### 🎬 ឆែកមើលវីដេអូដែលបាន Dubbing")
            with open(OUTPUT_VIDEO_NAME, "rb") as f:
                video_bytes = f.read()
                st.video(video_bytes)
                st.download_button(
                    label="📥 ទាញយកវីដេអូ (Download)",
                    data=video_bytes,
                    file_name="dubbed_result.mp4",
                    mime="video/mp4"
                )
        else:
            st.info("⏳ រង់ចាំឲ្យ AI ដំណើរការបង្កើតវីដេអូរួចសិន ទើបបង្ហាញនៅទីនេះ (ឯកសារលទ្ធផលមិនទាន់មាន)។")
st.markdown('</div>', unsafe_allow_html=True)

st.button("📂 OPEN FOLDER", type="secondary", use_container_width=True)
