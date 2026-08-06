import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import os

# ==========================================
# កូដថ្មីនេះ ត្រូវបានរៀបចំឡើងដើម្បីកែវីដេអូឱ្យមាត់តួអង្គនិយាយខ្មែរ
# (ត្រូវការតំឡើង Wav2Lip នៅលើកុំព្យូទ័ររបស់អ្នកសិន ទើបដំណើរការ)
# ==========================================

class DubbingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Khmer Dubbing Pro (Lip-Sync Edition)")
        self.root.geometry("500x500")
        
        # ផ្ទាំងព័ត៌មាន
        tk.Label(root, text="ធ្វើវីដេអូនិយាយខ្មែរតាមមាត់តួអង្គ", font=("Arial", 16, "bold")).pack(pady=20)

        # Button ជ្រើសវីដេអូ
        self.btn_video = tk.Button(root, text="1. ជ្រើសវីដេអូដើម", command=self.browse_video)
        self.btn_video.pack(pady=5)
        self.lbl_video = tk.Label(root, text="មិនទាន់ជ្រើស")
        self.lbl_video.pack()

        # Button ជ្រើសអូឌីយ៉ូសំឡេងខ្មែរ (ដែលបានបកប្រែរួច)
        self.btn_audio = tk.Button(root, text="2. ជ្រើសសំឡេងខ្មែរ (WAV)", command=self.browse_audio)
        self.btn_audio.pack(pady=5)
        self.lbl_audio = tk.Label(root, text="មិនទាន់ជ្រើស")
        self.lbl_audio.pack()

        # កន្លែងបង្ហាញ Status
        self.lbl_status = tk.Label(root, text="ត្រៀមដំណើរការ", fg="blue")
        self.lbl_status.pack(pady=20)

        # Button START
        self.btn_start = tk.Button(root, text="ចាប់ផ្តើម Lip-Sync (និយាយតាមមាត់)", bg="green", fg="white", font=("Arial", 12), command=self.start_dubbing)
        self.btn_start.pack(pady=20)

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4")])
        if path:
            self.video_path = path
            self.lbl_video.config(text=os.path.basename(path))

    def browse_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav")])
        if path:
            self.audio_path = path
            self.lbl_audio.config(text=os.path.basename(path))

    def start_dubbing(self):
        if not hasattr(self, 'video_path') or not hasattr(self, 'audio_path'):
            messagebox.showwarning("ព្រមាន", "សូមជ្រើសរើសវីដេអូ និង សំឡេងជាមុនសិន!")
            return
        
        self.lbl_status.config(text="កំពុងដំណើរការ... អាចចំណាយពេលបន្តិច (អាស្រ័យលើ GPU)", fg="red")
        self.btn_start.config(state="disabled")
        
        # ដំណើរការក្នុង Background កុំឱ្យ GUI បង្កក
        thread = threading.Thread(target=self.run_wav2lip)
        thread.start()

    def run_wav2lip(self):
        try:
            # ============================================================
            # នេះគឺជាកូដស្នូលដែលធ្វើឱ្យមាត់និយាយតាមសំឡេងខ្មែរ
            # អ្នកត្រូវយក Wav2Lip មកតំឡើង និងកែផ្លូវ file path ឱ្យត្រូវ
            # ============================================================
            
            # ឧទាហរណ៍ពាក្យបញ្ជាសម្រាប់ Wav2Lip
            # ទាមទារឱ្យមានឯកសារ wav2lip_gan.pth នៅក្នុង Folder models
            cmd = [
                "python", "wav2lip/inference.py", 
                "--checkpoint_path", "models/wav2lip_gan.pth",
                "--face", self.video_path,
                "--audio", self.audio_path,
                "--outfile", "output_final_dubbed.mp4"
            ]
            
            # រត់ពាក្យបញ្ជា (វានឹងប្រើ GPU ដើម្បីធ្វើ Lip-Sync)
            subprocess.run(cmd, check=True)
            
            self.lbl_status.config(text="ដំណើរការបានបញ្ចប់! ពិនិត្យវីដេអូ output_final_dubbed.mp4", fg="green")
            messagebox.showinfo("បានបញ្ចប់", "Lip-Sync បានជោគជ័យ! តួអង្គនឹងនិយាយខ្មែរហើយ។")
            
        except Exception as e:
            self.lbl_status.config(text=f"មានបញ្ហា: {str(e)}", fg="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_start.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = DubbingApp(root)
    root.mainloop()
