import tkinter as tk
from tkinter import messagebox
import json
import os
import uuid
import datetime

# ================================================================
#  ផ្នែក LICENSE MANAGER (ប្រព័ន្ធគ្រប់គ្រង License)
# ================================================================

LICENSE_FILE = "license.json"

def get_machine_id():
    """បង្កើត Machine ID តែមួយគត់សម្រាប់ឧបករណ៍នេះ"""
    try:
        return str(uuid.getnode())
    except:
        return "unknown_device"

def default_license():
    """បង្កើតទិន្នន័យ License លំនាំដើម"""
    return {
        "license_key": "",
        "activated": False,
        "activation_date": None,
        "expiry_date": None,
        "machine_id": get_machine_id(),
        "videos_used": 0
    }

def load_license():
    """
    អានទិន្នន័យពី license.json
    ប្រើ Error Handling ដើម្បីការពារកំហុស
    """
    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # ត្រួតពិនិត្យថាមាន field ទាំងអស់
            required_fields = ["license_key", "activated", "activation_date", "expiry_date", "machine_id", "videos_used"]
            for field in required_fields:
                if field not in data:
                    return default_license()
            return data
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        # បើឯកសារមិនទាន់មាន ឬខូច បង្កើតថ្មី
        return default_license()

def save_license(data):
    """រក្សាទុកទិន្នន័យ License ទៅក្នុង license.json"""
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving license: {e}")
        return False

def check_license(data):
    """
    ពិនិត្យស្ថានភាព License
    Return: (is_valid, status_message)
    status_message: "VIP", "Trial", "Expired", "Invalid Machine"
    """
    if not data.get("activated", False):
        return False, "Trial"

    # ពិនិត្យ Machine ID (ការពារការចម្លង License)
    if data.get("machine_id") != get_machine_id():
        return False, "Invalid Machine"

    # ពិនិត្យថ្ងៃផុតកំណត់
    expiry = data.get("expiry_date")
    if expiry:
        try:
            exp_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
            if exp_date < datetime.datetime.now().date():
                return False, "Expired"
        except:
            pass  # បើមិនអាច parse ថ្ងៃ រំលងទៅ

    return True, "VIP"

def activate_license(key):
    """
    ដំណើរការ Activate VIP
    Return: (success, message)
    """
    # =======================================================
    # 🔑 បញ្ជី Code ត្រឹមត្រូវ (សម្រាប់សាកល្បង)
    # អ្នកអាចប្ដូរតាមចិត្ត
    # =======================================================
    valid_keys = [
        "VIP-2024-ABCD",
        "SUPER-VIP-2026",
        "TEAM-8888"
    ]

    if key not in valid_keys:
        return False, "Invalid Code"

    # បើ Code ត្រឹមត្រូវ រក្សាទុក
    data = load_license()
    data["license_key"] = key
    data["activated"] = True
    data["activation_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # កំណត់ថ្ងៃផុតកំណត់ (ឧទាហរណ៍៖ ៣៦៥ ថ្ងៃ)
    exp = datetime.datetime.now() + datetime.timedelta(days=365)
    data["expiry_date"] = exp.strftime("%Y-%m-%d")
    data["machine_id"] = get_machine_id()
    
    if save_license(data):
        return True, "Activated Successfully"
    else:
        return False, "Failed to save license"


# ================================================================
#  ផ្នែក GUI (កម្មវិធីមេ)
# ================================================================

class VIPApp:
    def __init__(self, root):
        self.root = root
        root.title("VIP Activation System")
        root.geometry("720x380")
        root.resizable(False, False)

        # ========== ទិន្នន័យដំបូង ==========
        self.license_data = load_license()
        self.videos_used = self.license_data.get("videos_used", 0)
        self.is_vip, self.status_reason = check_license(self.license_data)

        # ========== 1. ផ្នែកខាងលើ (Activation) ==========
        top_frame = tk.Frame(root, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Label "VIP Activation"
        lbl_title = tk.Label(top_frame, text="🔑 VIP Activation", font=("Arial", 14, "bold"), bg="#f0f0f0")
        lbl_title.pack(side=tk.LEFT, padx=10)

        # TextBox សម្រាប់បញ្ចូល Code
        self.entry_code = tk.Entry(top_frame, width=25, font=("Arial", 11))
        self.entry_code.pack(side=tk.LEFT, padx=10)

        # Button Activate VIP
        btn_activate = tk.Button(top_frame, text="Activate VIP", command=self.activate_vip, 
                                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10)
        btn_activate.pack(side=tk.LEFT, padx=2)

        # Button Check License
        btn_check = tk.Button(top_frame, text="Check License", command=self.check_license,
                              bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=10)
        btn_check.pack(side=tk.LEFT, padx=2)

        # Button Buy VIP (Telegram)
        btn_buy = tk.Button(top_frame, text="💬 Buy VIP", command=self.buy_vip,
                            bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10)
        btn_buy.pack(side=tk.LEFT, padx=2)

        # ========== 2. Status Label ==========
        self.status_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=8)

        # ========== 3. ផ្នែកចម្បង (Video Simulation) ==========
        main_frame = tk.Frame(root)
        main_frame.pack(pady=15)

        # Label បង្ហាញចំនួនវីដេអូនៅសល់ / VIP Status
        self.info_label = tk.Label(main_frame, text="", font=("Arial", 11))
        self.info_label.pack(pady=5)

        # Button Start Video (ក្លែងធ្វើ)
        self.start_btn = tk.Button(main_frame, text="▶ Start Video", command=self.start_video,
                                   width=22, height=2, bg="#008CBA", fg="white", font=("Arial", 11, "bold"))
        self.start_btn.pack(pady=10)

        # ========== 4. Update UI ដំបូង ==========
        self.update_ui()

    # ==========================================================
    #  FUNCTIONS
    # ==========================================================

    def update_ui(self):
        """ធ្វើបច្ចុប្បន្នភាព Interface តាមស្ថានភាព License"""
        self.license_data = load_license()
        self.videos_used = self.license_data.get("videos_used", 0)
        is_vip, reason = check_license(self.license_data)

        if is_vip:
            # ===== VIP MODE =====
            self.status_label.config(text="VIP Activated ✅", fg="green")
            self.info_label.config(text="🎉 VIP Mode - គ្មានដែនកំណត់", fg="green")
            self.start_btn.config(text="▶ Start Video (VIP)", state=tk.NORMAL, bg="#4CAF50")
        
        else:
            if reason == "Expired":
                # ===== EXPIRED =====
                self.status_label.config(text="License Expired ❌", fg="red")
                self.info_label.config(text="សូមទិញ VIP ដើម្បីបន្តប្រើប្រាស់", fg="red")
                self.start_btn.config(text="⛔ Expired", state=tk.DISABLED, bg="gray")
                return

            elif reason == "Invalid Machine":
                self.status_label.config(text="Invalid Device ❌", fg="red")
                self.info_label.config(text="License មិនត្រូវគ្នានឹងឧបករណ៍នេះទេ", fg="red")
                self.start_btn.config(text="⛔ Blocked", state=tk.DISABLED, bg="gray")
                return

            else:
                # ===== TRIAL MODE =====
                remaining = 3 - self.videos_used
                if remaining > 0:
                    self.status_label.config(text=f"📌 Trial Version ({remaining} videos remaining)", fg="#FF8C00")
                    self.info_label.config(text=f"នៅសល់ {remaining} ដង (ក្នុងចំណោម 3)", fg="#FF8C00")
                    self.start_btn.config(text=f"▶ Start Video ({remaining} left)", state=tk.NORMAL, bg="#008CBA")
                else:
                    # អស់សិទ្ធិ Trial
                    self.status_label.config(text="Trial Expired ⛔", fg="red")
                    self.info_label.config(text="អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ", fg="red")
                    self.start_btn.config(text="⛔ Trial Ended", state=tk.DISABLED, bg="gray")

    def start_video(self):
        """ក្លែងធ្វើការចាក់វីដេអូ"""
        is_vip, _ = check_license(self.license_data)

        if is_vip:
            # VIP - គ្មានដែនកំណត់
            messagebox.showinfo("🎬 Video Player", "កំពុងចាក់វីដេអូ... (VIP - Unlimited)")
            return

        # Trial Mode
        if self.videos_used < 3:
            self.videos_used += 1
            self.license_data["videos_used"] = self.videos_used
            save_license(self.license_data)
            
            remaining = 3 - self.videos_used
            messagebox.showinfo("🎬 Video Player", f"ចាក់វីដេអូរួចរាល់! (នៅសល់ {remaining} ដង)")
            self.update_ui()
        else:
            # បង្ហាញសារព្រមាន និងបិទប៊ូតុង (បានធ្វើរួចក្នុង update_ui ហើយ)
            messagebox.showwarning("Trial Ended", 
                "អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\n"
                "ដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")
            self.start_btn.config(state=tk.DISABLED)

    def activate_vip(self):
        """ដំណើរការ Activate ពី Code ដែលអ្នកប្រើបញ្ចូល"""
        code = self.entry_code.get().strip()
        if not code:
            messagebox.showerror("Error", "សូមបញ្ចូល Activation Code មុនពេល Activate")
            return

        success, msg = activate_license(code)
        if success:
            # ផ្ទុកទិន្នន័យថ្មី
            self.license_data = load_license()
            self.videos_used = self.license_data.get("videos_used", 0)
            messagebox.showinfo("🎉 Success", "VIP Activated ដោយជោគជ័យ!")
            self.update_ui()
        else:
            messagebox.showerror("Activation Failed", f"Code មិនត្រឹមត្រូវទេ។\n{msg}\n\nសូមទាក់ទង Telegram: @YOUR_TELEGRAM ដើម្បីទិញ Code")

    def check_license(self):
        """ពិនិត្យស្ថានភាព License បច្ចុប្បន្ន"""
        self.license_data = load_license()
        self.videos_used = self.license_data.get("videos_used", 0)
        is_vip, reason = check_license(self.license_data)

        if is_vip:
            expiry = self.license_data.get("expiry_date", "N/A")
            messagebox.showinfo("License Status", 
                f"✅ VIP Mode Active\n"
                f"📅 Expiry Date: {expiry}\n"
                f"🖥️ Machine ID: {get_machine_id()}")
        elif reason == "Expired":
            messagebox.showwarning("License Status", "⛔ License បានផុតកំណត់ហើយ។ សូមទិញថ្មី។")
        elif reason == "Invalid Machine":
            messagebox.showerror("License Status", "⛔ License នេះមិនត្រូវគ្នានឹងកុំព្យូទ័រនេះទេ។")
        else:
            remaining = 3 - self.videos_used
            messagebox.showinfo("License Status", 
                f"📌 Trial Mode\n"
                f"🎥 Videos remaining: {remaining} / 3")

        self.update_ui()

    def buy_vip(self):
        """បង្ហាញព័ត៌មានទាក់ទង Telegram"""
        messagebox.showinfo("💬 Buy VIP", 
            "សម្រាប់ទិញ VIP ឬទទួល Activation Code\n"
            "សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM\n\n"
            "(លុបពាក្យ YOUR_TELEGRAM ចេញ ហើយដាក់ឈ្មោះអ្នកវិញ)")


# ================================================================
#  ចាប់ផ្ដើមកម្មវិធី
# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = VIPApp(root)
    root.mainloop()
