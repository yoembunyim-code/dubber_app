import streamlit as st

# =======================================================
# 🔑 ផ្នែកទី 1៖ កំណត់ទម្រង់ដែលងាយស្រួលកែប្រែ (Config)
# =======================================================

# 1.1 ដាក់ឈ្មោះ Telegram របស់អ្នកនៅទីនេះ (អ្នកគ្រាន់តែប្តូរតែត្រង់នេះម្តងគត់)
OWNER_TELEGRAM = "t.me/bunyimyoem" # ឧ. "@SereyMom_Ai"

# 1.2 លេខ Machine ID របស់កុំព្យូទ័រអ្នកបច្ចុប្បន្ន
CURRENT_MACHINE_ID = "58611610212922"

# 1.3 បញ្ជីលេខកូដសម្រាប់ភ្ញៀវ (ដាក់បន្ថែមបានច្រើនដោយគ្រាន់តែបន្ថែមបន្ទាត់ចុះក្រោម)
# ទម្រង់៖ "លេខកូដរបស់ភ្ញៀវ": "លេខ Machine ID របស់ភ្ញៀវ"
LICENSE_DATABASE = {
    # លេខសម្រាប់អ្នកប្រើប្រាស់របស់អ្នក
    "BUNYIM-VIP-001": "58611610212922",
    
    # សម្រាប់សាកល្បងការទប់ស្កាត់
    "ADMIN-9999": "58221133882211",
    
    # (ឧទាហរណ៍: បន្ថែមភ្ញៀវថ្មីនៅទីនេះ)
    # "ជាឧទាហរណ៍-8888": "59001122334455",
}


# =======================================================
# 2. កំណត់រចនាសម្ព័ន្ធទំព័រ Streamlit
# =======================================================
st.set_page_config(page_title="VIP Activation System", layout="wide", page_icon="🔑")

# =======================================================
# 3. កំណត់ Session State (ចងចាំថាបាន Activate ឬអត់)
# =======================================================
if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False

# =======================================================
# 4. CSS តុបតែង UI ឲ្យឡូយៗ (អ្នកមិនចាំបាច់កែផ្នែកនេះទេ)
# =======================================================
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
# 5. ផ្នែក SIDEBAR (ខាងឆ្វេង)
# =======================================================
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    st.markdown("---")
    st.markdown("**លេខសម្គាល់ឧបករណ៍ (Machine ID):**")
    st.code(CURRENT_MACHINE_ID, language="text")
    
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាពប្រើប្រាស់:** `{status_text}`")
    
    st.markdown("---")
    # ផ្នែក Telegram ត្រូវបានចាប់យក OWNER_TELEGRAM ពីផ្នែក Config ដោយស្វ័យប្រវត្តិ
    st.markdown("#### 📞 ត្រូវការជំនួយ?")
    st.markdown(f"[![Telegram](https://img.shields.io/badge/Telegram-{OWNER_TELEGRAM}-blue?style=for-the-badge&logo=telegram)](https://t.me/{OWNER_TELEGRAM.replace('@', '')})")
    
    st.markdown("---")
    if st.button("🔄 Reset License (Debug)", use_container_width=True):
        st.session_state.is_activated = False
        st.success("បាន Reset ស្ថានភាពវិញ!")

# =======================================================
# 6. ផ្នែក MAIN UI
# =======================================================
st.markdown("<h1 style='text-align: center;'>🔑 VIP Activation System</h1>", unsafe_allow_html=True)
st.markdown("---")

# 6.1 ផ្នែកបញ្ចូល Activation Code និង Activate
if st.session_state.is_activated:
    st.success("🎉 ប្រព័ន្ធត្រូវបាន Activate រួចរាល់ហើយ! អ្នកអាចប្រើប្រាស់មុខងារខាងក្រោមបានពេញលេញ។")
else:
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        act_code_input = st.text_input("បញ្ចូល Activation Code ដើម្បីបើកសិទ្ធិ", placeholder="ឧ. VIP-2026-ABCD", label_visibility="collapsed")
    with c_btn:
        if st.button("✅ Activate VIP", type="primary", use_container_width=True):
            if not act_code_input or act_code_input.strip() == "":
                st.error("❌ សូមបញ្ចូលលេខកូដជាមុនសិន។")
            else:
                if act_code_input in LICENSE_DATABASE:
                    expected_machine = LICENSE_DATABASE[act_code_input]
                    if expected_machine == CURRENT_MACHINE_ID:
                        st.session_state.is_activated = True
                        st.success("🎉 ធ្វើការ Activate ជោគជ័យ! សូមរីករាយប្រើប្រាស់។")
                        st.rerun()
                    else:
                        st.error("❌ លេខកូដនេះត្រូវបានប្រើប្រាស់ដោយឧបករណ៍ (Machine) ផ្សេងហើយ! លេខកូដ ១ អាចប្រើបានតែ ១ ឧបករណ៍ប៉ុណ្ណោះ។")
                else:
                    st.error("❌ លេខកូដមិនត្រឹមត្រូវ! សូមទាក់ទង Telegram របស់យើងដើម្បីទិញ License។")

# 6.2 ផ្នែកឧបករណ៍គ្រប់គ្រងរូបទី៣
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

c1, c2, c3 = st.columns(3)
with c1:
    st.button("🤖 AUTO", use_container_width=True)
with c2:
    st.button("👩 SREY MOM", use_container_width=True)
with c3:
    st.button("🧑 PIDETH", use_container_width=True)

st.button("🗣️ DUB AS-IS (no translate)", use_container_width=True)

st.markdown('<div class="green-btn">', unsafe_allow_html=True)
if st.button("🚀 START", use_container_width=True):
    if not st.session_state.is_activated:
        st.warning("សូម Activate VIP ជាមុនសិន!")
    elif uploaded_video is None:
        st.warning("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
    else:
        # ពីទីនេះទៅ គឺជាចំណុចដែលអ្នកត្រូវសរសេរកូដ AI Dubbing របស់អ្នក
        # ឧទាហរណ៍៖ output_video_path = process_ai_dubbing(uploaded_video)
        
        # យើងក្លែងធ្វើជាកន្លែងរក្សាទុកវីដេអូលទ្ធផល
        result_video_path = "output_video.mp4" # ជាឈ្មោះឯកសារលទ្ធផលក្រោយ AI ដំណើរការរួច
        
        st.success("✅ ដំណើរការ Dubbing ចប់ហើយ! អ្នកអាចឆែកមើល ឬទាញយកវីដេអូបាននៅខាងក្រោម៖")
        
        # បង្ហាញវីដេអូដោយផ្ទាល់ក្នុង App ដើម្បីឆែកមើល
        # ចំណាំ៖ ប្រសិនបើអ្នកចង់បង្ហាញវីដេអូដែលទើបតែដំណើរការចប់ ត្រូវប្រាកដថាផ្លូវ (Path) ឯកសារត្រឹមត្រូវ។
        with open(result_video_path, "rb") as f:
            video_bytes = f.read()
            st.video(video_bytes) # បង្ហាញក្នុង App

        # ផ្តល់ប៊ូតុង Download ឱ្យអ្នកប្រើប្រាស់អាចយកទៅ Save នៅលើម៉ាស៊ីនរបស់ខ្លួន
        st.download_button(
            label="📥 ទាញយកវីដេអូដែលបាន Dubbing (Download)",
            data=video_bytes,
            file_name="dubbed_result_video.mp4",
            mime="video/mp4"
        )

st.markdown('</div>', unsafe_allow_html=True)
st.button("📂 OPEN FOLDER", type="secondary", use_container_width=True)
