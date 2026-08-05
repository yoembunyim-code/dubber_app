import streamlit as st

# =====================================================================
# 1. ផ្នែកក្លែងធ្វើ Backend Database (សម្រាប់ចាក់សោលេខកូដ ១ ប្រើ ១ ឧបករណ៍)
# =====================================================================
# ក្នុងជីវិតពិត អ្នកគួររក្សាទុកព័ត៌មាននេះនៅក្នុង Database (ដូចជា SQLite ឬ API)។
# នៅទីនេះយើងក្លែងធ្វើ Data តាម Dictionary ដើម្បីឲ្យអ្នកសាកល្បងបានភ្លាមៗ។

# ឧទាហរណ៍៖ License_Key: Machine_ID ដែលបានចងភ្ជាប់
LICENSE_DATABASE = {
    # លេខកូដត្រឹមត្រូវសម្រាប់ម៉ាស៊ីននេះ (សាកល្បងដាក់កូដនេះទៅ!)
    "VIP-2026-ABCD": "58611610212922",
    # លេខកូដដែលចងភ្ជាប់ជាមួយម៉ាស៊ីនផ្សេង (ដើម្បីសាកល្បងថាទប់ស្កាត់បាន)
    "ADMIN-9999": "58221133882211"
    LICENSE_DATABASE = { "LICENSE_KEY_1": "BUNYIM_ID_1",
                        "LICENSE_KEY_2": "BUNYIM_ID_2" }

# សន្មតថាកុំព្យូទ័ររបស់អ្នកបច្ចុប្បន្នមាន Machine ID នេះ (អ្នកអាចប្តូរវាសាកល្បងបាន)
CURRENT_MACHINE_ID = "58611610212922"

# =====================================================================
# 2. កំណត់រចនាសម្ព័ន្ធទំព័រ
# =====================================================================
st.set_page_config(page_title="VIP Activation System", layout="wide", page_icon="🔑")

# 3. ការកំណត់ Session State (ដើម្បីឲ្យកម្មវិធីចងចាំថាបាន Activate ហើយ)
if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'machine_id' not in st.session_state:
    st.session_state.machine_id = CURRENT_MACHINE_ID

# =====================================================================
# 4. CSS ធ្វើឲ្យ UI ឡូយដូច Desktop App
# =====================================================================
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; font-family: 'Segoe UI', sans-serif; }
    /* Sidebar ពណ៌ងងឹត ឡូយ */
    section[data-testid="stSidebar"] { background-color: #1e293b; color: #ffffff; }
    section[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }
    
    /* តុបតែងប៊ូតុងទូទៅ */
    .stButton > button {
        border-radius: 10px; font-weight: 600; border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out; width: 100%; height: 3.2em;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

    /* ប៊ូតុង START ពណ៌បៃតងទំហំធំ */
    .stButton.green-btn > button { background-color: #10b981 !important; color: white !important; height: 4.5em; font-size: 20px; }
    
    /* តុបតែងកន្លែងផ្ទុកវីដេអូ (File Uploader) ឲ្យក្លែងជាប៊ូតុងពណ៌ខៀវ */
    div[data-testid="stFileUploader"] { width: 100%; }
    div[data-testid="stFileUploader"] section { padding: 0; border: none; background: transparent; }
    div[data-testid="stFileUploader"] button {
        background-color: #3b82f6 !important; color: white !important; border-radius: 10px;
        width: 100%; height: 3.2em; font-weight: bold; border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s;
    }
    div[data-testid="stFileUploader"] button:hover { background-color: #2563eb !important; transform: translateY(-2px); }

    /* តុបតែងប្រអប់បញ្ចូល */
    .stTextInput > div > div > input { border-radius: 10px; border: 1px solid #cbd5e1; padding: 12px; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 5. ផ្នែក SIDEBAR (ព័ត៌មាន និង Telegram)
# =====================================================================
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    st.markdown("---")
    st.markdown("**លេខសម្គាល់ឧបករណ៍ (Machine ID):**")
    st.code(CURRENT_MACHINE_ID, language="text") # បង្ហាញ ID ប៉ុន្តែមិនបង្ហាញ Key
    
    # ពិនិត្យស្ថានភាព
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាពប្រើប្រាស់:** `{status_text}`")
    st.markdown("**កាលបរិច្ឆេទផុតកំណត់:** `គ្មានកំណត់`")
    
    st.markdown("---")
    
    # ----- កន្លែងឈ្មោះ Telegram -----
    st.markdown("#### 📞 ត្រូវការជំនួយ?")
    st.markdown("សម្រាប់ការគាំទ្រ ឬទិញ License:")
    # ប្តូរ YOUR_TELEGRAM ទៅជាឈ្មោះពិតរបស់អ្នក
    st.markdown("[![Telegram](https://img.shields.io/badge/Telegram-@YOUR_TELEGRAM-blue?style=for-the-badge&logo=telegram)](https://t.me/bunyimyoem)")
    
    st.markdown("---")
    if st.button("🔄 Reset License (Debug)", use_container_width=True):
        st.session_state.is_activated = False
        st.success("បាន Reset ស្ថានភាពទៅដើមវិញដោយជោគជ័យ!")

# =====================================================================
# 6. ផ្នែក MAIN UI (ការ Activate និង Control Panel)
# =====================================================================
st.markdown("<h1 style='text-align: center;'>🔑 VIP Activation System</h1>", unsafe_allow_html=True)
st.markdown("---")

if st.session_state.is_activated:
    st.success("🎉 ប្រព័ន្ធត្រូវបាន Activate រួចរាល់ហើយ! អ្នកអាចប្រើប្រាស់មុខងារខាងក្រោមបានពេញលេញ។")
else:
    # 6.1 ប្រអប់បញ្ចូល Activation Code តែម្ដង
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        act_code_input = st.text_input("បញ្ចូល Activation Code ដើម្បីបើកសិទ្ធិ", placeholder="ឧ. VIP-2026-ABCD", label_visibility="collapsed")
    with c_btn:
        if st.button("✅ Activate VIP", type="primary", use_container_width=True):
            if not act_code_input or act_code_input.strip() == "":
                st.error("❌ សូមបញ្ចូលលេខកូដជាមុនសិន។")
            else:
                # Logic ពិនិត្យលេខកូដ ១ ប្រើ ១ ឧបករណ៍
                if act_code_input in LICENSE_DATABASE:
                    expected_machine = LICENSE_DATABASE[act_code_input]
                    if expected_machine == CURRENT_MACHINE_ID:
                        st.session_state.is_activated = True
                        st.success("🎉 ធ្វើការ Activate ជោគជ័យ! សូមរីករាយប្រើប្រាស់។")
                        st.rerun() # Refresh ទំព័រឲ្យបង្ហាញ Control Panel ភ្លាមៗ
                    else:
                        st.error("❌ លេខកូដនេះត្រូវបានប្រើប្រាស់ដោយឧបករណ៍ (Machine) ផ្សេងហើយ! លេខកូដ ១ អាចប្រើបានតែ ១ ឧបករណ៍ប៉ុណ្ណោះ។")
                else:
                    st.error("❌ លេខកូដមិនត្រឹមត្រូវ! សូមពិនិត្យឡើងវិញ (ឬទាក់ទង Telegram ដើម្បីទិញ)។")

# =====================================================================
# 7. ប្លង់ Control Panel ស្រដៀងរូបទី៣
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📂 ប្រអប់ឧបករណ៍គ្រប់គ្រង")
st.markdown("<hr style='border: 0;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    # ជំនួសឲ្យប៊ូតុង យើងប្រើ file_uploader ឲ្យដាក់វីដេអូបានពិត
    uploaded_video = st.file_uploader("Browse Video", type=['mp4', 'avi', 'mov', 'mkv'], label_visibility="collapsed")
    if uploaded_video is not None:
        st.caption(f"ឯកសារ៖ `{uploaded_video.name}` ទំហំ៖ {round(len(uploaded_video.getvalue()) / 1024 / 1024, 2)} MB")
        # នៅចំណុចនេះ អ្នកអាចបញ្ចូលកូដដំណើរការ AI Dubbing របស់អ្នកបានដោយប្រើ uploaded_video.read()
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

st.markdown("<br>", unsafe_allow_html=True)

# ប៊ូតុង START ពណ៌បៃតងធំ
st.markdown('<div class="green-btn">', unsafe_allow_html=True)
if st.button("🚀 START", use_container_width=True):
    if not st.session_state.is_activated:
        st.warning("សូម Activate VIP ជាមុនសិន ទើបអាចប្រើ START បាន!")
    elif uploaded_video is None:
        st.warning("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
    else:
        st.success("ចាប់ផ្ដើមដំណើរការ Dubbing និង Translation ដោយជោគជ័យ!")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.button("📂 OPEN FOLDER", type="secondary", use_container_width=True)
