import streamlit as st

# 1. កំណត់រចនាសម្ព័ន្ធទំព័រ (Page Config)
st.set_page_config(page_title="VIP Activation System", layout="wide", page_icon="🔑")

# 2. បន្ថែម CSS ដើម្បីធ្វើឲ្យ UI ឡូយដូចរូបទី៣ (Desktop style)
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa; /* ពណ៌ផ្ទៃខាងក្រោយស្រាល */
    }
    /* តុបតែងប៊ូតុងទូទៅ */
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
        height: 3.2em;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    /* តុបតែង SideBar ឲ្យងងឹតឡូយ */
    section[data-testid="stSidebar"] {
        background-color: #1e2129;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff;
    }
    /* ពណ៌ប៊ូតុង START (ប្ដូរទៅជាពណ៌បៃតងដូចរូបទី៣) */
    .stButton.green-btn > button {
        background-color: #28a745 !important;
        color: white !important;
        height: 4em;
        font-size: 18px;
        border: none;
    }
    /* តុបតែងប្រអប់បញ្ចូល Activation Code */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ced4da;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. ផ្នែក SIDEBAR (កែច្នៃពីរូបទី 1)
# ==========================================
with st.sidebar:
    st.markdown("## ℹ️ **ព័ត៌មានអាជ្ញាប័ណ្ណ**")
    st.markdown("---")
    
    # លេខសម្គាល់ម៉ាស៊ីន
    st.markdown("**លេខសម្គាល់ឧបករណ៍ (Machine ID):**")
    st.code("58611610212922", language="text") # លាក់ License Key ចោល បង្ហាញតែ Machine ID
    
    # ស្ថានភាព និងកាលបរិច្ឆេទ
    st.markdown("**ស្ថានភាពប្រើប្រាស់:** `មិនទាន់បើកសកម្ម`")
    st.markdown("**កាលបរិច្ឆេទផុតកំណត់:** `None`")
    st.markdown("**ចំនួនវីដេអូដែលបានប្រើ:** `3/3`")
    
    st.markdown("---")
    # ប៊ូតុង Reset License (Debug)
    if st.button("🔄 Reset License (Debug)", use_container_width=True):
        st.success("បានធ្វើការ Reset License ដោយជោគជ័យ (សម្រាប់សាកល្បង)")


# ==========================================
# 4. ផ្នែក MAIN UI (កែរូបទី 2 ឲ្យដូចរូបទី 3)
# ==========================================
st.markdown("<h1 style='text-align: center;'>🔑 VIP Activation System</h1>", unsafe_allow_html=True)
st.markdown("---")

# 4.1 ប្រអប់បញ្ចូល Activation Code និងប៊ូតុង Activate
col_input, col_btn = st.columns([4, 1])
with col_input:
    act_code = st.text_input("បញ្ចូល Activation Code នៅទីនេះ", placeholder="ឧទាហរណ៍: XXXX-XXXX-XXXX", label_visibility="collapsed")
with col_btn:
    if st.button("✅ Activate VIP", type="primary", use_container_width=True):
        if not act_code or act_code.strip() == "N/A":
            st.error("❌ Invalid Code! សូមពិនិត្យមើលកូដរបស់អ្នកឡើងវិញ!")
        else:
            st.success("🎉 Activate ជោគជ័យ!") # នៅចំណុចនេះ អ្នកអាចបន្ថែម Logic Activate ពិតៗរបស់អ្នក

st.markdown("<br>", unsafe_allow_html=True)

# 4.2 បង្កើតប្លង់ប៊ូតុងតាមជួរស្រដៀងរូបទី 3
st.markdown("### 📂 ប្រអប់ឧបករណ៍គ្រប់គ្រង (Control Panel)")
st.markdown("<hr style='border: 0;'>", unsafe_allow_html=True)

# ជួរទី 1: Browse Video, Browse SRT
c1, c2 = st.columns(2)
with c1:
    st.button("📂 BROWSE VIDEO", type="primary", use_container_width=True)
with c2:
    st.button("📄 BROWSE SRT", type="primary", use_container_width=True)

# ជួរទី 2: Auto, SREY MOM, PIDETH
c1, c2, c3 = st.columns(3)
with c1:
    st.button("🤖 AUTO", use_container_width=True)
with c2:
    st.button("👩 SREY MOM", use_container_width=True)
with c3:
    st.button("🧑 PIDETH", use_container_width=True)

# ជួរទី 3: DUB AS-IS
st.button("🗣️ DUB AS-IS (no translate)", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ជួរទី 4: START (ប៊ូតុងធំពណ៌បៃតង)
# យើងរុំក្នុង HTML div class="green-btn" ដើម្បីឲ្យ CSS ខាងលើចាប់យកពណ៌បានត្រឹមត្រូវ
st.markdown('<div class="green-btn">', unsafe_allow_html=True)
if st.button("🚀 START", use_container_width=True):
    st.success("កំពុងដំណើរការ Dubbing និង Translation... សូមរង់ចាំ!")
st.markdown('</div>', unsafe_allow_html=True)

# ជួរទី 5: OPEN FOLDER
st.button("📂 OPEN FOLDER", type="secondary", use_container_width=True)
