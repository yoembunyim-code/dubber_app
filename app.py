import json
import os
import uuid
import webbrowser
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# ==============================================================================
# ⚙️ កន្លែងកំណត់ទិន្នន័យកម្មវិធី (DEVELOPER CONFIGURATIONS)
# ==============================================================================
TELEGRAM_USERNAME = "@YOUR_TELEGRAM"  # ✍️ ផ្លាស់ប្តូរឈ្មោះ Telegram របស់អ្នកនៅទីនេះ
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME.replace('@', '')}"

# ✍️ បញ្ជីលេខកូដ VIP ដែលអ្នកអនុញ្ញាតឱ្យប្រើ (អ្នកអាចបន្ថែមលេខកូដថ្មីៗនៅទីនេះ)
VALID_VIP_CODES = [
    "VIP-SECRET-2026",
    "VIP-PASS-8888",
    "VIP-PRO-9999",
    "CAM-VIP-1234"
]

TRIAL_LIMIT = 3  # ចំនួនវីដេអូសាកល្បង
LICENSE_FILE = "license.json"


# ==============================================================================
# 🛡️ MODULE គ្រប់គ្រង LICENSE (LICENSE MANAGER MODULE)
# ==============================================================================
class LicenseManager:
    @staticmethod
    def get_machine_id():
        """ទាញយក Hardware ID (MAC Address) តែមួយគត់របស់ម៉ាស៊ីន"""
        return str(uuid.getnode())

    @staticmethod
    def load_license():
        """អានទិន្នន័យ License ពី license.json ជាមួយ Error Handling ពេញលេញ"""
        default_data = {
            "license_key": "",
            "activated": False,
            "activation_date": "",
            "expiry_date": "",
            "machine_id": LicenseManager.get_machine_id(),
            "trial_used": 0
        }
        
        if not os.path.exists(LICENSE_FILE):
            return default_data

        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("machine_id", LicenseManager.get_machine_id())
                data.setdefault("trial_used", 0)
                return data
        except Exception as e:
            print(f"[Error] បរាជ័យក្នុងការអានឯកសារ License: {e}")
            return default_data

    @staticmethod
    def save_license(data):
        """រក្សាទុកទិន្នន័យ License ទៅក្នុង license.json"""
        try:
            with open(LICENSE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Error] បរាជ័យក្នុងការរក្សាទុកឯកសារ License: {e}")
            return False

    @staticmethod
    def check_license_status():
        """ពិនិត្យស្ថានភាព License ដោយស្វ័យប្រវត្តិ"""
        data = LicenseManager.load_license()
        
        if not data.get("activated"):
            return "Trial Version"
        
        # ពិនិត្យ Machine ID
        if data.get("machine_id") != LicenseManager.get_machine_id():
            return "Invalid Code"
            
        # ពិនិត្យថ្ងៃផុតកំណត់ (Expired Date)
        expiry_str = data.get("expiry_date", "")
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                if datetime.now() > expiry_date:
                    return "License Expired"
            except ValueError:
                return "Invalid Code"

        return "VIP Activated"

    @staticmethod
    def activate_vip(key):
        """ដំណើរការផ្ទៀងផ្ទាត់ និង Activate VIP Code"""
        key = key.strip()
        if not key:
            return False, "សូមបញ្ចូល Activation Code!"
        
        # ពិនិត្យមើលថាកូដនៅក្នុងបញ្ជី VALID_VIP_CODES ឬអត់
        if key in VALID_VIP_CODES:
            data = LicenseManager.load_license()
            now = datetime.now()
            expiry = now + timedelta(days=365)  # ផ្តល់សិទ្ធិ VIP រយៈពេល ១ឆ្នាំ
            
            data["license_key"] = key
            data["activated"] = True
            data["activation_date"] = now.strftime("%Y-%m-%d")
            data["expiry_date"] = expiry.strftime("%Y-%m-%d")
            data["machine_id"] = LicenseManager.get_machine_id()
            
            if LicenseManager.save_license(data):
                return True, "🎉 Activation ជោគជ័យ! កម្មវិធីរបស់អ្នកត្រូវបានដោះសោ VIP រួចរាល់។"
            else:
                return False, "មានបញ្ហាក្នុងការរក្សាទុកឯកសារ License!"
        else:
            return False, "Activation Code មិនត្រឹមត្រូវទេ (Invalid Code)!"

    @staticmethod
    def get_trial_remaining():
        """គណនាចំនួនវីដេអូសាកល្បងដែលនៅសល់"""
        data = LicenseManager.load_license()
        used = data.get("trial_used", 0)
        return max(0, TRIAL_LIMIT - used)

    @staticmethod
    def use_trial_video():
        """កាត់កាត់ចំនួនវីដេអូសាកល្បង"""
        data = LicenseManager.load_license()
        data["trial_used"] = data.get("trial_used", 0) + 1
        LicenseManager.save_license(data)
        return data["trial_used"]


# ==============================================================================
# 🎨 ផ្នែករចនា GUI (MODERN TKINTER INTERFACE)
# ==============================================================================
class VIPActivationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VIP Activation System - Video Tools")
        self.root.geometry("680x520")
        self.root.configure(bg="#F1F5F9")
        self.root.resizable(False, False)

        # កំណត់ Style សម្រាប់ Widget
        self.setup_styles()

        # បង្កើតសមាសភាគ GUI
        self.create_header()
        self.create_activation_card()
        self.create_main_content()

        # ពិនិត្យ License ពេលបើកកម្មវិធីភ្លាមៗ
        self.refresh_status()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def create_header(self):
        """Header Banner ផ្នែកខាងលើ"""
        header_frame = tk.Frame(self.root, bg="#1E293B", height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame, 
            text="🎬 VIDEO PROCESSING SOFTWARE", 
            font=("Segoe UI", 14, "bold"), 
            fg="#F8FAFC", 
            bg="#1E293B"
        )
        title_label.pack(side="left", padx=20, pady=15)

    def create_activation_card(self):
        """ប្រអប់បញ្ចូល VIP Activation កំពូល (Top / Right Layout)"""
        card = tk.Frame(self.root, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        card.pack(fill="x", padx=20, pady=15)

        # Title Label
        card_title = tk.Label(
            card, 
            text="🔑 VIP Activation Panel", 
            font=("Segoe UI", 11, "bold"), 
            fg="#0F172A", 
            bg="#FFFFFF"
        )
        card_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(12, 8))

        # Controls Grid
        tk.Label(card, text="Activation Code:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF").grid(row=1, column=0, sticky="w", padx=(15, 5), pady=5)

        self.entry_code = tk.Entry(
            card, 
            font=("Consolas", 10), 
            bg="#F8FAFC", 
            fg="#0F172A", 
            relief="solid", 
            bd=1, 
            width=22
        )
        self.entry_code.grid(row=1, column=1, padx=5, pady=5, ipady=4)

        # Button: Activate VIP
        btn_activate = tk.Button(
            card, text="Activate VIP", bg="#059669", fg="white", activebackground="#047857", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=12, pady=4,
            command=self.on_activate
        )
        btn_activate.grid(row=1, column=2, padx=5, pady=5)

        # Button: Check License
        btn_check = tk.Button(
            card, text="Check License", bg="#2563EB", fg="white", activebackground="#1D4ED8", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, pady=4,
            command=self.on_check_license
        )
        btn_check.grid(row=1, column=3, padx=(5, 15), pady=5)

        # Status Row
        tk.Label(card, text="ស្ថានភាព License:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF").grid(row=2, column=0, sticky="w", padx=(15, 5), pady=(5, 12))

        self.lbl_status = tk.Label(
            card, text="កំពុងពិនិត្យ...", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#64748B"
        )
        self.lbl_status.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=(5, 12))

        # Button: Buy VIP
        btn_buy = tk.Button(
            card, text="🛒 ទិញ VIP Code", bg="#D97706", fg="white", activebackground="#B45309", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, pady=4,
            command=self.on_buy_vip
        )
        btn_buy.grid(row=2, column=3, padx=(5, 15), pady=(5, 12))

    def create_main_content(self):
        """កន្លែងដំណើរការវីដេអូ និងការបង្ហាញលទ្ធផល"""
        main_card = tk.Frame(self.root, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        main_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # សារជូនដំណឹងពីចំនួន Trial
        self.lbl_trial_info = tk.Label(
            main_card, text="", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#D97706", anchor="w"
        )
        self.lbl_trial_info.pack(fill="x", padx=15, pady=(15, 5))

        # ប៊ូតុង Start Process
        self.btn_start = tk.Button(
            main_card, text="▶ ចាប់ផ្តើមដំណើរការវីដេអូ (Start Video)", 
            font=("Segoe UI", 11, "bold"), bg="#4F46E5", fg="white", activebackground="#4338CA", activeforeground="white",
            height=2, relief="flat", cursor="hand2", command=self.on_start_video
        )
        self.btn_start.pack(fill="x", padx=15, pady=10)

        # Console Log Box
        log_frame = tk.Frame(main_card, bg="#F1F5F9")
        log_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self.txt_log = tk.Text(
            log_frame, font=("Consolas", 9), bg="#0F172A", fg="#38BDF8", 
            bd=0, relief="flat", wrap="word"
        )
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_log.insert("1.0", f"SYSTEM LOG: កម្មវិធីបានបើកដំណើរការ...\n[Telegram ជំនួយ៖ {TELEGRAM_USERNAME}]\n" + "-"*50 + "\n")

    def refresh_status(self):
        """បច្ចុប្បន្នភាព GUI ផ្អែកលើស្ថានភាព License ជាក់ស្តែង"""
        status = LicenseManager.check_license_status()

        if status == "VIP Activated":
            self.lbl_status.config(text="VIP Activated ✅", fg="#059669")
            self.lbl_trial_info.config(text="🎉 គណនីរបស់អ្នកគឺ VIP! ដំណើរការបានគ្មានដែនកំណត់ និងបើកគ្រប់មុខងារ។", fg="#059669")
            self.btn_start.config(state="normal", bg="#4F46E5", cursor="hand2")
        else:
            remaining = LicenseManager.get_trial_remaining()

            if status == "License Expired":
                self.lbl_status.config(text="License Expired ❌", fg="#DC2626")
            elif status == "Invalid Code":
                self.lbl_status.config(text="Invalid Code ⚠️", fg="#DC2626")
            else:
                self.lbl_status.config(text="Trial Version ⏳", fg="#D97706")

            # ពិនិត្យចំនួនសាកល្បង
            if remaining > 0:
                self.lbl_trial_info.config(
                    text=f"⚠️ កំពុងប្រើប្រាស់ Trial Version (ចំនួនវីដេអូនៅសល់៖ {remaining}/{TRIAL_LIMIT})", 
                    fg="#D97706"
                )
                self.btn_start.config(state="normal", bg="#4F46E5", cursor="hand2")
            else:
                self.lbl_trial_info.config(
                    text=f"🚫 អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ ({TRIAL_LIMIT}/{TRIAL_LIMIT} វីដេអូ)!", 
                    fg="#DC2626"
                )
                self.btn_start.config(state="disabled", bg="#94A3B8", cursor="arrow")

    def on_activate(self):
        """ពេលចុចប៊ូតុង Activate VIP"""
        code = self.entry_code.get()
        success, msg = LicenseManager.activate_vip(code)
        
        if success:
            messagebox.showinfo("VIP Activated", msg)
            self.entry_code.delete(0, tk.END)
            self.txt_log.insert(tk.END, f"[SUCCESS] VIP Activated ជោគជ័យជាមួយ Code: {code}\n")
        else:
            messagebox.showerror("Activation Failed", msg)
            self.txt_log.insert(tk.END, f"[FAILED] ការបញ្ចូល Code បរាជ័យ៖ {msg}\n")
            
        self.txt_log.see(tk.END)
        self.refresh_status()

    def on_check_license(self):
        """ពេលចុចប៊ូតុង Check License"""
        status = LicenseManager.check_license_status()
        data = LicenseManager.load_license()
        
        if status == "VIP Activated":
            info = (
                f"=== ព័ត៌មាន VIP LICENSE ===\n\n"
                f"• ស្ថានភាព៖ {status} ✅\n"
                f"• License Key: {data.get('license_key')}\n"
                f"• ថ្ងៃ Activate: {data.get('activation_date')}\n"
                f"• ថ្ងៃផុតកំណត់: {data.get('expiry_date')}\n"
                f"• Machine ID: {data.get('machine_id')}"
            )
            messagebox.showinfo("License Status", info)
        else:
            remaining = LicenseManager.get_trial_remaining()
            info = f"ស្ថានភាពបច្ចុប្បន្ន៖ {status}\nវីដេអូសាកល្បងនៅសល់៖ {remaining}/{TRIAL_LIMIT}"
            messagebox.showwarning("License Status", info)
            
        self.refresh_status()

    def on_buy_vip(self):
        """ពេលចុចប៊ូតុង Buy VIP"""
        msg = f"សម្រាប់ទិញ VIP ឬទទួល Activation Code សូមទាក់ទង Telegram៖\n\n👉 {TELEGRAM_USERNAME}\n\nតើអ្នកចង់បើក Telegram ឥឡូវនេះទេ?"
        if messagebox.askyesno("Buy VIP License", msg):
            webbrowser.open(TELEGRAM_LINK)

    def on_start_video(self):
        """ពេលចុចប៊ូតុង Start Video Processing"""
        status = LicenseManager.check_license_status()
        
        if status == "VIP Activated":
            self.txt_log.insert(tk.END, "▶ [VIP MODE] កំពុងដំណើរការវីដេអូពេញលេញ (Unlimited)... រួចរាល់ 100%!\n")
            self.txt_log.see(tk.END)
        else:
            remaining = LicenseManager.get_trial_remaining()
            if remaining > 0:
                LicenseManager.use_trial_video()
                rem_after = LicenseManager.get_trial_remaining()
                self.txt_log.insert(tk.END, f"▶ [TRIAL MODE] កំពុងដំណើរការវីដេអូ... (ជោគជ័យ! នៅសល់ {rem_after} វីដេអូទៀត)\n")
                self.txt_log.see(tk.END)
                self.refresh_status()
                
                if rem_after == 0:
                    self.show_trial_expired_dialog()
            else:
                self.show_trial_expired_dialog()
                self.refresh_status()

    def show_trial_expired_dialog(self):
        """បង្ហាញសារជូនដំណឹងពេលអស់សិទ្ធិសាកល្បង"""
        msg = f"អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ {TELEGRAM_USERNAME}"
        if messagebox.askyesno("Trial Version Expired", msg + "\n\nតើអ្នកចង់ទាក់ទង Telegram ឥឡូវនេះទេ?"):
            webbrowser.open(TELEGRAM_LINK)


# ==============================================================================
# 🚀 MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = VIPActivationApp(root)
    root.mainloop()
