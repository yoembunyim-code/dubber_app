import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime, timedelta
import uuid, platform

LICENSE_FILE = "license.json"
VALID_KEY = "DEEPSEEK-VIP-2026"

def get_machine_id():
    return str(uuid.getnode()) + "_" + platform.node()

def load_license():
    default = {"license_key":"", "activated":False, "activation_date":"", "expiry_date":"", "machine_id":get_machine_id(), "videos_used":0}
    if not os.path.exists(LICENSE_FILE): return default
    try:
        with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for k in default:
                if k not in data: data[k] = default[k]
            return data
    except: return default

def save_license(data):
    try:
        with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except: return False

def check_status(data):
    if data.get("activated", False):
        expiry = data.get("expiry_date", "")
        if expiry:
            try:
                if datetime.now() > datetime.strptime(expiry, "%Y-%m-%d"):
                    return "expired"
            except: pass
        return "vip"
    return "trial"

def activate_license(key):
    data = load_license()
    if key.strip() == VALID_KEY:
        data["license_key"] = key.strip()
        data["activated"] = True
        data["activation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["expiry_date"] = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        data["machine_id"] = get_machine_id()
        data["videos_used"] = 0
        if save_license(data): return True, "VIP Activated! ✅", data
        return False, "Save failed.", data
    return False, "Invalid Code. ❌", data

class VIPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VIP Activation System")
        self.geometry("750x550")
        self.resizable(False, False)
        self.license_data = load_license()
        self.setup_ui()
        self.update_ui()

    def setup_ui(self):
        main = ttk.Frame(self, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Activation
        af = ttk.LabelFrame(main, text="🔑 VIP Activation", padding=15)
        af.pack(fill=tk.X, pady=(0,15))
        af.columnconfigure(0, weight=1)
        
        left = ttk.Frame(af)
        left.grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(left, text="Code:").pack(side=tk.LEFT, padx=(0,8))
        self.entry = ttk.Entry(left, width=30)
        self.entry.pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(left, text="✅ Activate", command=self.activate).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(left, text="🔍 Check", command=self.check).pack(side=tk.LEFT)
        
        right = ttk.Frame(af)
        right.grid(row=0, column=1, sticky="e", padx=5)
        self.status = ttk.Label(right, text="Status: Checking...", font=("Arial",11,"bold"))
        self.status.pack(side=tk.RIGHT)
        
        # Video
        vf = ttk.LabelFrame(main, text="▶️ Video Player", padding=15)
        vf.pack(fill=tk.BOTH, expand=True, pady=(0,15))
        
        self.remain = ttk.Label(vf, text="Videos Remaining: 3", font=("Arial",11))
        self.remain.pack(pady=(0,10))
        
        self.display = tk.Text(vf, height=8, state=tk.DISABLED, bg="#f4f4f4", font=("Arial",11))
        self.display.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        self.update_display("🎬 Press 'Start Video' to play.")
        
        cf = ttk.Frame(vf)
        cf.pack(fill=tk.X)
        self.start_btn = ttk.Button(cf, text="▶ Start Video", command=self.start_video, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=(0,15))
        ttk.Button(cf, text="💎 Buy VIP", command=self.show_telegram, width=15).pack(side=tk.LEFT)
        
        # Telegram
        tf = ttk.Frame(main)
        tf.pack(fill=tk.X)
        ttk.Label(tf, text="📱 Telegram: @YOUR_TELEGRAM", foreground="#1a73e8", font=("Arial",10,"bold")).pack(side=tk.RIGHT)

    def update_display(self, text):
        self.display.config(state=tk.NORMAL)
        self.display.delete(1.0, tk.END)
        self.display.insert(tk.END, text)
        self.display.config(state=tk.DISABLED)

    def update_ui(self):
        status = check_status(self.license_data)
        if status == "vip":
            self.status.config(text="✅ VIP Activated", foreground="green")
            self.remain.config(text="🎉 VIP - Unlimited")
            self.start_btn.config(state=tk.NORMAL)
        elif status == "expired":
            self.status.config(text="❌ Expired", foreground="red")
            self.remain.config(text="⛔ Please buy VIP")
            self.start_btn.config(state=tk.DISABLED)
        else:
            rem = 3 - self.license_data.get("videos_used",0)
            if rem < 0: rem = 0
            if rem > 0:
                self.status.config(text="🆓 Trial", foreground="orange")
                self.remain.config(text=f"📹 {rem} videos left")
                self.start_btn.config(state=tk.NORMAL)
            else:
                self.status.config(text="⛔ Trial Expired", foreground="red")
                self.remain.config(text="🚫 No trials left")
                self.start_btn.config(state=tk.DISABLED)
                self.update_display("⛔ អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\nដើម្បីដោះសោ VIP សូមទាក់ទង Telegram៖ @YOUR_TELEGRAM")

    def activate(self):
        success, msg, data = activate_license(self.entry.get())
        if success:
            self.license_data = data
            self.update_ui()
            self.update_display("✅ VIP Activated! 🎉")
            self.entry.delete(0, tk.END)
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Failed", msg)

    def check(self):
        self.license_data = load_license()
        self.update_ui()
        status = check_status(self.license_data)
        if status == "vip": msg = "✅ VIP Active"
        elif status == "expired": msg = "❌ Expired"
        else:
            rem = 3 - self.license_data.get("videos_used",0)
            msg = f"🆓 Trial: {rem if rem>0 else 0} videos left"
        messagebox.showinfo("License Status", msg)

    def start_video(self):
        status = check_status(self.license_data)
        if status == "expired":
            messagebox.showerror("Denied", "License expired. Buy VIP.")
            return
        if status == "vip":
            self.update_display("🎬 Playing... (VIP Unlimited)")
            return
        used = self.license_data.get("videos_used",0)
        if used >= 3:
            self.update_ui()
            messagebox.showwarning("Trial Expired", "អ្នកបានប្រើសិទ្ធិសាកល្បងអស់ហើយ។\n\nទាក់ទង Telegram: @YOUR_TELEGRAM")
            return
        self.license_data["videos_used"] = used + 1
        save_license(self.license_data)
        self.update_display(f"▶ Playing ({used+1}/3)")
        self.update_ui()
        if used + 1 >= 3:
            self.update_display("⛔ អស់សិទ្ធិសាកល្បងហើយ។\n\nទាក់ទង Telegram: @YOUR_TELEGRAM")

    def show_telegram(self):
        messagebox.showinfo("Buy VIP", "សម្រាប់ទិញ VIP សូមទាក់ទង Telegram៖\n\n📱 @YOUR_TELEGRAM")

if __name__ == "__main__":
    VIPApp().mainloop()
