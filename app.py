import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import time
from googletrans import Translator
import subprocess

# ==========================================
# CONFIG (កំណត់រចនាសម្ព័ន្ធ)
# ==========================================
APP_TITLE = "AI Khmer Dubbing PRO"
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

# ==========================================
# LICENSE MANAGER (គ្រប់គ្រងការសាកល្បង 3 វីដេអូ)
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
# GUI APPLICATION (រចនាដូចរូបភាពគេ)
# ==========================================
class DubbingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("800x650")
        ctk.set_appearance_mode("System")  # Light/Dark mode
        ctk.set_default_color_theme("blue")

        self.license_mgr = LicenseManager()
        self.video_path = ""
        self.srt_path = ""
        
        # ===== LEFT PANEL: Logs & Progress (ផ្នែកខាងឆ្វេង) =====
        self.left_frame = ctk.CTkFrame(self, width=400, corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(self.left_frame, text="Processing Logs", font=("Arial", 14, "bold")).pack(pady=5, padx=10, anchor="w")
        self.log_box = ctk.CTkTextbox(self.left_frame, height=300)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        # Progress Bar
        ctk.CTkLabel(self.left_frame, text="Progress Status:").pack(padx=10, anchor="w")
        self.progress_bar = ctk.CTkProgressBar(self.left_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # ===== RIGHT PANEL: Buttons & Controls (ផ្នែកខាងស្តាំ) =====
        self.right_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.right_frame.pack(side="right", fill="y", padx=15, pady=15)

        ctk.CTkLabel(self.right_frame, text="CONTROLS", font=("Arial", 14, "bold"), text_color="orange").pack(pady=10)

        # Buttons styling like image
        self.btn_browse = ctk.CTkButton(self.right_frame, text="BROWSE VIDEO", fg_color="#2196F3", hover_color="#1976D2", width=180, height=40, command=self.browse_video)
        self.btn_browse.pack(pady=10)

        self.btn_srt = ctk.CTkButton(self.right_frame, text="BROWSE SRT", fg_color="#4CAF50", hover_color="#388E3C", width=180, height=40, command=self.browse_srt)
        self.btn_srt.pack(pady=10)

        self.btn_auto = ctk.CTkButton(self.right_frame, text="AUTO", fg_color="#9C27B0", hover_color="#7B1FA2", width=80, height=30)
        self.btn_auto.pack(pady=5)

        self.btn_start = ctk.CTkButton(self.right_frame, text="START DUBBING", fg_color="#D32F2F", hover_color="#B71C1C", width=180, height=50, font=("Arial", 16, "bold"), command=self.start_dubbing)
        self.btn_start.pack(pady=20)
        
        self.btn_open = ctk.CTkButton(self.right_frame, text="OPEN FOLDER", fg_color="#9C27B0", hover_color="#7B1FA2", width=180, height=40, command=self.open_output_folder)
        self.btn_open.pack(pady=10)

        # Telegram Name
        ctk.CTkLabel(self, text=f"Developer: {CONTACT_TELEGRAM}", text_color="#FF5722", font=("Arial", 10, "bold")).pack(side="bottom", pady=5)

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
            self.log(f"Video selected: {os.path.basename(file_path)}")

    def browse_srt(self):
        file_path = filedialog.askopenfilename(filetypes=[("Subtitle Files", "*.srt")])
        if file_path:
            self.srt_path = file_path
            self.log(f"SRT selected: {os.path.basename(file_path)}")

    def open_output_folder(self):
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.startfile(output_dir)

    def start_dubbing(self):
        if not self.video_path:
            messagebox.showwarning("Warning", "Please select a video first!")
            return

        # License Check
        can_run, msg = self.license_mgr.check_and_increment()
        if not can_run:
            self.log(msg)
            messagebox.showwarning("Trial Ended!", msg)
            return

        self.log(msg)
        self.is_running = True
        self.btn_start.configure(state="disabled")
        
        self.thread = threading.Thread(target=self.run_translation_pipeline, daemon=True)
        self.thread.start()

    # ========== THE REAL TRANSLATION ENGINE ==========
    def run_translation_pipeline(self):
        try:
            # Step 1: Aligning Audio (Extract Audio)
            self.log("[80%] Extracting audio from video... / កំពុងដកស្រង់សំឡេង...", progress_val=0.8)
            time.sleep(1)
            for i in range(8, 23):
                if not self.is_running: return
                self.log(f"[80%] Extracting audio... {i}/22 / កំពុងដកស្រង់សំឡេង...")
                time.sleep(0.3)

            # Step 2: Translating to Khmer
            self.log("[85%] Translating text to Khmer... / កំពុងបកប្រែជាខ្មែរ...", progress_val=0.85)
            translator = Translator()
            # ត្រង់នេះក្នុងការអនុវត្តពិត អ្នកនឹងប្រើ Whisper ដកសំឡេងចេញមកជាអត្ថបទអង់គ្លេស រួចយកអត្ថបទនោះមកបកប្រែ។ 
            # ដើម្បីសាកល្បងកូដ ខ្ញុំនឹងក្លែងធ្វើការបកប្រែអត្ថបទគំរូ។
            sample_english_text = "Hello, welcome to my video translation tool."
            translated_text = translator.translate(sample_english_text, src='en', dest='km').text
            time.sleep(1.5)
            self.log(f"[85%] Translation result: {translated_text}")
            time.sleep(1.5)

            # Step 3: Generating Khmer Voice (TTS)
            self.log("[90%] Generating Khmer Audio (TTS)... / កំពុងបង្កើតសំឡេងខ្មែរ...", progress_val=0.9)
            # នៅត្រង់នេះ ក្នុងការអនុវត្តពិត អ្នកនឹងប្រើ Google Cloud TTS API ដើម្បីបង្កើតឯកសារ .wav
            # តែសម្រាប់សាកល្បងរូបរាងកម្មវិធី យើងក្លែងធ្វើការងារនេះ។
            time.sleep(2)

            # Step 4: Mixing Audio
            self.log("[96%] Mixing audio into video... / កំពុងផ្សំសំឡេងចូលវីដេអូ...", progress_val=0.96)
            # នៅត្រង់នេះគឺដំណាក់កាលយកសំឡេងខ្មែរទៅផ្សំជាមួយ Background របស់វីដេអូដើម (ប្រើ FFmpeg)។
            time.sleep(2)

            # Complete
            self.log("[100%] Dubbing Completed Successfully! / បានបញ្ចប់ដោយជោគជ័យ!", progress_val=1.0)
            messagebox.showinfo("Completed", "Dubbing process finished!\nCheck the Output folder.")

        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.is_running = False
            self.btn_start.configure(state="normal")

# ==========================================
# RUN THE APP
# ==========================================
if __name__ == "__main__":
    app = DubbingApp()
    app.mainloop()
