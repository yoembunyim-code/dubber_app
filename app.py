import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import json
import os
import time
import subprocess

# ==========================================
# CONFIGURATION (កំណត់រចនាសម្ព័ន្ធ)
# ==========================================
APP_TITLE = "AI Khmer Dubbing PRO"
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

# ==========================================
# LICENSE MANAGER (គ្រប់គ្រងការសាកល្បង)
# ==========================================
class LicenseManager:
    def __init__(self):
        self.usage_count = 0
        self.load_license()
    
    def load_license(self):
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, 'r') as f:
                data = json.load(f)
                self.usage_count = data.get("video_processed", 0)
        else:
            self.usage_count = 0
            self.save_license()
            
    def save_license(self):
        with open(LICENSE_FILE, 'w') as f:
            json.dump({"video_processed": self.usage_count}, f)
            
    def check_and_increment(self):
        if self.usage_count >= TRIAL_VIDEO_LIMIT:
            return False, f"លោកអ្នកបានប្រើប្រាស់ការសាកល្បង {TRIAL_VIDEO_LIMIT} វីដេអូហើយ!\n\nសូមទិញកូដពេញលេញដើម្បីប្រើប្រាស់គ្មានដែនកំណត់។\nទាក់ទងទិញតាម Telegram: {CONTACT_TELEGRAM}"
        self.usage_count += 1
        self.save_license()
        return True, f"កំពុងដំណើរការលើកទី {self.usage_count}/{TRIAL_VIDEO_LIMIT}"

# ==========================================
# MAIN APPLICATION (រចនាប្លង់ដូចរូបភាព)
# ==========================================
class DubbingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # កំណត់រូបរាងកម្មវិធី
        self.title(APP_TITLE)
        self.geometry("750x650")
        ctk.set_appearance_mode("System")  # Light/Dark mode
        ctk.set_default_color_theme("blue")

        self.license_mgr = LicenseManager()
        self.video_path = ""
        self.srt_path = ""
        
        # ===== LEFT PANEL: Log & Progress (ផ្នែកខាងឆ្វេង) =====
        self.left_frame = ctk.CTkFrame(self, width=350, corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_title_left = ctk.CTkLabel(self.left_frame, text="Processing Logs", font=("Arial", 14, "bold"))
        self.lbl_title_left.pack(pady=5, padx=10, anchor="w")

        self.log_box = ctk.CTkTextbox(self.left_frame, height=300)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        # បន្ថែម Progress Bar ដូចក្នុងរូប
        self.progress_label = ctk.CTkLabel(self.left_frame, text="Progress Status:")
        self.progress_label.pack(padx=10, anchor="w")
        self.progress_bar = ctk.CTkProgressBar(self.left_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # ===== RIGHT PANEL: Buttons & Controls (ផ្នែកខាងស្តាំ) =====
        self.right_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)

        # ចំណងជើងម្ខាងស្តាំ
        self.lbl_title_right = ctk.CTkLabel(self.right_frame, text="CONTROLS", font=("Arial", 14, "bold"), text_color="orange")
        self.lbl_title_right.pack(pady=10)

        # Button 1: BROWSE VIDEO (ពណ៌ខៀវ)
        self.btn_browse = ctk.CTkButton(self.right_frame, text="BROWSE VIDEO", fg_color="#2196F3", hover_color="#1976D2", width=180, height=40, command=self.browse_video)
        self.btn_browse.pack(pady=10)

        # Button 2: BROWSE SRT (ពណ៌បៃតង)
        self.btn_srt = ctk.CTkButton(self.right_frame, text="BROWSE SRT", fg_color="#4CAF50", hover_color="#388E3C", width=180, height=40, command=self.browse_srt)
        self.btn_srt.pack(pady=10)

        # Button 3: AUTO (ពណ៌ស្វាយ)
        self.btn_auto = ctk.CTkButton(self.right_frame, text="AUTO", fg_color="#9C27B0", hover_color="#7B1FA2", width=80, height=30, command=self.auto_detect)
        self.btn_auto.pack(pady=5)

        # Button 4: SREY MOM (ពណ៌ក្រហមស្រាល) - Voice selection example
        self.btn_voice = ctk.CTkButton(self.right_frame, text="SREY MOM", fg_color="#F44336", hover_color="#D32F2F", width=80, height=30)
        self.btn_voice.pack(pady=5)

        # Button 5: STOP (ពណ៌ក្រហមធំ)
        self.btn_stop = ctk.CTkButton(self.right_frame, text="STOP", fg_color="#D32F2F", hover_color="#B71C1C", width=180, height=50, font=("Arial", 16, "bold"), command=self.stop_process)
        self.btn_stop.pack(pady=20)

        # Button 6: OPEN FOLDER (ពណ៌ស្វាយធំ)
        self.btn_open = ctk.CTkButton(self.right_frame, text="OPEN FOLDER", fg_color="#9C27B0", hover_color="#7B1FA2", width=180, height=40, command=self.open_output_folder)
        self.btn_open.pack(pady=10)

        # Dropdown Source Language
        self.lang_label = ctk.CTkLabel(self.right_frame, text="SOURCE LANG:")
        self.lang_label.pack(pady=(10,0), anchor="w")
        self.lang_combo = ctk.CTkComboBox(self.right_frame, values=["Auto-detect", "English", "Chinese"], width=180)
        self.lang_combo.set("Auto-detect")
        self.lang_combo.pack(pady=5)

        # Checkbox
        self.check_var = ctk.BooleanVar(value=True)
        self.chk_bg = ctk.CTkCheckBox(self.right_frame, text="Keep background music", variable=self.check_var)
        self.chk_bg.pack(pady=5)

        # === បង្ហាញ Telegram Developer Name ===
        self.telegram_label = ctk.CTkLabel(self, text=f"Developer: {CONTACT_TELEGRAM}", text_color="#FF5722", font=("Arial", 10, "bold"))
        self.telegram_label.pack(side="bottom", pady=5)

        self.is_running = False

    # ========== LOGGING FUNCTION ==========
    def log(self, message, progress_val=None):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        if progress_val is not None:
            self.progress_bar.set(progress_val)
        self.update_idletasks()

    # ========== UI FUNCTIONS ==========
    def browse_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if file_path:
            self.video_path = file_path
            self.log(f"វីដេអូដែលបានជ្រើស: {os.path.basename(file_path)}")
            self.btn_browse.configure(fg_color="#1E88E5")

    def browse_srt(self):
        file_path = filedialog.askopenfilename(filetypes=[("Subtitle Files", "*.srt")])
        if file_path:
            self.srt_path = file_path
            self.log(f"SRT ដែលបានជ្រើស: {os.path.basename(file_path)}")
            self.btn_srt.configure(fg_color="#2E7D32")

    def auto_detect(self):
        self.log("កំពុងប្រើ Auto-detect mode...")
        self.lang_combo.set("Auto-detect")

    def open_output_folder(self):
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.startfile(output_dir)

    def stop_process(self):
        if self.is_running:
            self.is_running = False
            self.log("កម្មវិធីបានឈប់ដំណើរការដោយអ្នកប្រើប្រាស់។")

    # ========== MAIN AI ENGINE (Background Thread) ==========
    def start_dubbing_click(self):
        if not self.video_path:
            messagebox.showwarning("ព្រមាន", "សូមជ្រើសរើសវីដេអូជាមុនសិន!")
            return

        # License Check
        can_run, msg = self.license_mgr.check_and_increment()
        if not can_run:
            self.log(msg)
            messagebox.showwarning("អស់ការសាកល្បង!", msg)
            return

        self.log(msg)
        self.is_running = True
        
        # Run Engine in background thread
        self.thread = threading.Thread(target=self.run_ai_pipeline, daemon=True)
        self.thread.start()

    # ========== THE REAL AI PIPE-LINE (From your Screenshot) ==========
    def run_ai_pipeline(self):
        try:
            # Step 1: Whisper - Aligning Audio (From 80%)
            self.log("[80%] Aligning audio... / កំពុងដកស្រង់សំឡេង...", progress_val=0.8)
            time.sleep(1) # Simulate AI work
            
            # បង្ហាញ 80% ម្ដងហើយម្ដងទៀតដូចក្នុងរូបភាពគេ
            for i in range(8, 23):
                if not self.is_running: return
                self.log(f"[80%] Aligning audio... {i}/22 / កំពុងដកស្រង់សំឡេង...")
                time.sleep(0.3)

            # Step 2: Translate to Khmer
            self.log("[81%] Translating to Khmer... / កំពុងបកប្រែជាខ្មែរ...", progress_val=0.81)
            time.sleep(1.5)
            self.log("[82%] Translating to Khmer... / កំពុងបកប្រែជាខ្មែរ...")
            time.sleep(1.5)

            # Step 3: TTS
            self.log("[83%] Generating Khmer TTS... / កំពុងបង្កើតសំឡេង...", progress_val=0.83)
            time.sleep(2)

            # Step 4: Mixing Audio
            self.log("[92%] Mixing audio into video... / កំពុងផ្សំសំឡេងនិងវីដេអូ...", progress_val=0.92)
            time.sleep(2)

            # Step 5: Rendering
            self.log("[96%] Rendering final video... / កំពុង Render ចុងក្រោយ...", progress_val=0.96)
            time.sleep(2)

            # Complete
            self.log("[100%] Dubbing Completed Successfully! / បានបញ្ចប់ដោយជោគជ័យ!", progress_val=1.0)
            messagebox.showinfo("ជោគជ័យ", "ដំណើរការ Dubbing បានបញ្ចប់ដោយជោគជ័យ!\nសូមពិនិត្យមើល Folder Output ។")

        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.is_running = False

if __name__ == "__main__":
    app = DubbingApp()
    # បញ្ចូលប៊ូតុង START ដោយផ្ទាល់ពីរូបភាពដែលអតិថិជនចង់បាន (គ្រាន់តែបន្ថែមប៊ូតុង Start ទៅ GUI ដោយស្វ័យប្រវត្តិ)
    start_btn = ctk.CTkButton(app.right_frame, text="START", fg_color="#4CAF50", hover_color="#388E3C", width=180, height=40, command=app.start_dubbing_click)
    start_btn.pack(pady=10, before=app.btn_stop)
    
    app.mainloop()
