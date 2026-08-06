import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import uuid
import platform
import speech_recognition as sr
import threading
import time

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
    """ពិនិត្យស្ថានភាព License: 'vip', 'expired', 'trial'"""
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
    """ដំណើរការ Activate VIP"""
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
#  SPEECH-TO-TEXT (បកការនិយាយជាខ្មែរ)
# ================================================================

class SpeechToText:
    def __init__(self, callback):
        self.callback = callback
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.thread = None
        
    def start_listening(self):
        """ចាប់ផ្តើមស្តាប់សំឡេង"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
    def stop_listening(self):
        """បញ្ឈប់ការស្តាប់"""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=1)
            
    def _listen_loop(self):
        """ដំណើរការស្តាប់សំឡេងជាបន្តបន្ទាប់"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while self.is_listening:
                try:
                    # ស្តាប់សំឡេង
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # បកស្គ្រីបជាភាសាខ្មែរ
                    text = self.recognizer.recognize_google(audio, language="km-KH")
                    
                    # បញ្ជូនអត្ថបទទៅ callback
                    if text and self.callback:
                        self.callback(text)
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    # មិនអាចបកស្គ្រីបបាន
                    if self.callback:
                        self.callback("(មិនអាចស្គាល់សំឡេងបានទេ)")
                except sr.RequestError:
                    if self.callback:
                        self.callback("(កំហុសក្នុងការភ្ជាប់ Google API)")
                except Exception as e:
                    if self.callback:
                        self.callback(f"(កំហុស: {str(e)})")
                
                time.sleep(0.5)


# ================================================================
#  MAIN APPLICATION - GUI
# ================================================================

class VIPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VIP Activation System - Video Tool with Khmer Speech")
        self.geometry("850x650")
        self.resizable(False, False)
        
        # ដំណើរការផ្ទុក License
        self.license_data = load_license()
        self.current_status = check_license_status(self.license_data)
        self.remaining_videos = 3 - self.license_data.get("videos_used", 0)
        if self.remaining_videos < 0:
            self.remaining_videos = 0
            
        # Speech-to-Text
        self.stt = SpeechToText(self.on_speech_recognized)
        self.is_playing = False
        
        self.setup_ui()
        self.update_ui_state()

    def setup_ui(self):
        # Container មេ
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ========== 1. ផ្នែកខាងលើ: Activation System ==========
        activation_frame = ttk.LabelFrame(main_frame, text="🔑 VIP Activation System", padding="15")
        activation_frame.pack(fill=tk.X, pady=(0, 15))

        activation_frame.columnconfigure(0, weight=1)
        activation_frame.columnconfigure(1, weight=1)

        # ផ្នែកឆ្វេង: Entry + Buttons
        left_act = ttk.Frame(activation_frame)
        left_act.grid(row=0, column=0, sticky="w", padx=5)

        ttk.Label(left_act, text="Activation Code:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 8))
        
        self.code_entry = ttk.Entry(left_act, width=30, font=("Arial", 10))
        self.code_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.activate_btn = ttk.Button(left_act, text="✅ Activate VIP", command=self.activate_vip)
        self.activate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.check_btn = ttk.Button(left_act, text="🔍 Check License", command=self.check_license)
        self.check_btn.pack(side=tk.LEFT)

        # ផ្នែកខាងស្តាំ: Status Label
        right_act = ttk.Frame(activation_frame)
        right_act.grid(row=0, column=1, sticky="e", padx=5)

        self.status_label = ttk.Label(right_act, text="Status: Checking...", font=("Arial", 11, "bold"))
        self.status_label.pack(side=tk.RIGHT)

        # ========== 2. ផ្នែកកណ្តាល: Video Player ==========
        video_frame = ttk.LabelFrame(main_frame, text="▶️ Video Player with Khmer Speech-to-Text", padding="15")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Label បង្ហាញចំនួនវីដេអូនៅសល់
        self.remaining_label = ttk.Label(video_frame, text="Videos Remaining (Trial): 3", font=("Arial", 11))
        self.remaining_label.pack(pady=(0, 10))

        # បង្អួចសម្រាប់បង្ហាញវីដេអូ និងអត្ថបទបកស្គ្រីប
        self.video_display = tk.Text(video_frame, height=10, state=tk.DISABLED, bg="#f4f4f4", font=("Khmer OS", 12))
        self.video_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.update_video_display("🎬 ចុច '▶ Start Video' ដើម្បីចាប់ផ្តើមស្តាប់សំឡេង\n\nអត្ថបទដែលបកប្រែនឹងបង្ហាញនៅទីនេះ")

        # ----- Control Buttons -----
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(control_frame, text="▶ Start Video", command=self.start_video, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop Video", command=self.stop_video, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.buy_vip_btn = ttk.Button(control_frame, text="💎 Buy VIP", command=self.show_telegram, width=15)
        self.buy_vip_btn.pack(side=tk.LEFT)

        # ========== 3. ផ្នែកខាងក្រោម: Telegram Contact ==========
        tele_frame = ttk.Frame(main_frame)
        tele_frame.pack(fill=tk.X)
        
        self.tele_label = ttk.Label(tele_frame, text="📱 Contact Telegram: @YOUR_TELEGRAM", foreground="#1a73e8", font=("Arial", 10, "bold"))
        self.tele_label.pack(side=tk.RIGHT)

    # ============================================================
    #  METHODS
    # ============================================================

    def update_video_display(self, text):
        """ធ្វើបច្ចុប្បន្នភាពអត្ថបទក្នុងបង្អួច Video"""
        self.video_display.config(state=tk.NORMAL)
        self.video_display.delete(1.0, tk.END)
        self.video_display.insert(tk.END, text)
        self.video_display.see(tk.END)
        self.video_display.config(state=tk.DISABLED)

    def append_to_video_display(self, text):
        """បន្ថែមអត្ថបទទៅក្នុងបង្អួច Video (សម្រាប់ Speech-to-Text)"""
        self.video_display.config(state=tk.NORMAL)
        self.video_display.insert(tk.END, f"\n🎤 {text}")
        self.video_display.see(tk.END)
        self.video_display.config(state=tk.DISABLED)

    def on_speech_recognized(self, text):
        """Callback ពេលបកស្គ្រីបសំឡេងបាន"""
        if self.is_playing:
            self.append_to_video_display(text)

    def update_ui_state(self):
        """ធ្វើបច្ចុប្បន្នភាព UI តាមស្ថានភាពបច្ចុប្បន្ន"""
        status = check_license_status(self.license_data)
        self.current_status = status

        if status == "vip":
            self.status_label.config(text="✅ VIP Activated", foreground="green")
            self.remaining_label.config(text="🎉 VIP Mode - Unlimited Videos")
            self.start_btn.config(state=tk.NORMAL)

        elif status == "expired":
            self.status_label.config(text="❌ License Expired", foreground="red")
            self.remaining_label.config(text="⛔ License Expired. Please buy VIP.")
            self.start_btn.config(state=tk.DISABLED)

        else:  # Trial
            remaining = 3 - self.license_data.get("videos_used", 0)
            if remaining < 0:
                remaining = 0
            self.remaining_videos = remaining

            if remaining > 0:
                self.status_label.config(text="🆓 Trial Version", foreground="orange")
                self.remaining_label.config(text=f"📹 Videos Remaining (Trial): {remaining}")
                self.start_btn.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="⛔ Trial Expired", foreground="red")
                self.remaining_label.config(text="🚫 No trials left.")
                self.start_btn.config(state=tk.DISABLED)
                self.update_video_display(
                    "⛔ អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\n"
                    "ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM"
                )

    def activate_vip(self):
        """ដំណើរការចុច Activate VIP"""
        code = self.code_entry.get()
        success, message, updated_data = activate_license(code)
        
        if success:
            self.license_data = updated_data
            self.update_ui_state()
            self.update_video_display("✅ VIP Activated Successfully! All features unlocked. 🎉")
            self.code_entry.delete(0, tk.END)
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Activation Failed", message)

    def check_license(self):
        """ពិនិត្យ License ឡើងវិញ"""
        self.license_data = load_license()
        self.update_ui_state()
        
        status = self.current_status
        if status == "vip":
            msg = "✅ VIP Activated and valid."
        elif status == "expired":
            msg = "❌ License expired."
        else:
            remaining = 3 - self.license_data.get("videos_used", 0)
            if remaining < 0:
                remaining = 0
            msg = f"🆓 Trial mode. {remaining} videos remaining."
        
        messagebox.showinfo("License Status", msg)

    def start_video(self):
        """ដំណើរការចុច Start Video"""
        status = check_license_status(self.license_data)
        
        # ករណី Expired
        if status == "expired":
            messagebox.showerror("Access Denied", "License expired. Please buy VIP.")
            return

        # ករណី Trial - ពិនិត្យចំនួនវីដេអូ
        if status == "trial":
            videos_used = self.license_data.get("videos_used", 0)
            if videos_used >= 3:
                self.start_btn.config(state=tk.DISABLED)
                self.update_ui_state()
                messagebox.showwarning(
                    "Trial Expired",
                    "អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\n"
                    "ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM"
                )
                return
            
            # រាប់ចំនួនវីដេអូ
            self.license_data["videos_used"] = videos_used + 1
            save_license(self.license_data)
            self.update_ui_state()

        # ====== ចាប់ផ្តើម Speech-to-Text ======
        self.is_playing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # សម្អាតបង្អួច និងបង្ហាញសារចាប់ផ្តើម
        self.update_video_display(
            f"🎬 កំពុងចាក់វីដេអូ...\n"
            f"{'🎉 VIP Mode' if status == 'vip' else f'📹 សល់ {self.remaining_videos} ដង'}\n"
            f"{'─' * 50}\n"
            f"🎤 កំពុងស្តាប់សំឡេងជាភាសាខ្មែរ...\n\n"
            f"(សូមនិយាយជាភាសាខ្មែរ)"
        )
        
        # ចាប់ផ្តើមស្តាប់
        self.stt.start_listening()

    def stop_video(self):
        """បញ្ឈប់ Video និង Speech-to-Text"""
        self.is_playing = False
        self.stt.stop_listening()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.append_to_video_display("\n⏹ បានបញ្ឈប់ការស្តាប់")

    def show_telegram(self):
        """បង្ហាញព័ត៌មានទំនាក់ទំនង Telegram"""
        messagebox.showinfo(
            "Contact for VIP",
            "សម្រាប់ទិញ VIP ឬទទួល Activation Code សូមទាក់ទង Telegram៖\n\n"
            "📱 @YOUR_TELEGRAM"
        )

    def on_closing(self):
        """បិទកម្មវិធីឲ្យបានត្រឹមត្រូវ"""
        self.is_playing = False
        self.stt.stop_listening()
        self.destroy()


# ================================================================
#  MAIN ENTRY POINT
# ================================================================

if __name__ == "__main__":
    app = VIPApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
