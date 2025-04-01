# gui/dashboard.py
import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Add parent directory to sys.path so that modules can be imported correctly.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
print("Current directory:", current_dir)
print("Project root:", project_root)
sys.path.insert(0, project_root)
print("sys.path[0]:", sys.path[0])

# Check if config.py exists in the project root
config_path = os.path.join(project_root, "config.py")
print("config.py exists:", os.path.exists(config_path))

from config import MONITORED_DIRECTORY, BASELINE_FILE, LOG_FILE
# Import FIM functions. (Ensure these modules exist in your scripts folder.)
try:
    from scripts.baseline import create_baseline
except ImportError as e:
    messagebox.showerror("Import Error", f"Could not import create_baseline: {e}")

try:
    from scripts.monitor import start_monitoring
except ImportError as e:
    messagebox.showerror("Import Error", f"Could not import start_monitoring: {e}")

try:
    from scripts.manual_check import perform_check
except ImportError as e:
    messagebox.showerror("Import Error", f"Could not import perform_check: {e}")

# If setup_directories is not available from another module, we define a simple version here.
def setup_directories():
    if not os.path.exists(MONITORED_DIRECTORY):
        os.makedirs(MONITORED_DIRECTORY)
        return f"Created monitored directory: {MONITORED_DIRECTORY}"
    else:
        return f"Monitored directory already exists: {MONITORED_DIRECTORY}"

class FIMDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Integrity Monitoring System Dashboard")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")
        
        # Set up a ttk style for a modern look.
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.monitoring_thread = None
        self.monitoring_active = False
        
        self.create_widgets()
        # Auto-refresh log every 2 seconds.
        self.after(2000, self.refresh_log)
    
    def create_widgets(self):
        # Title Label.
        title_label = ttk.Label(
            self, text="FIM System Dashboard", font=("Helvetica", 18, "bold"),
            background="#f0f2f5", foreground="#333"
        )
        title_label.pack(pady=10)
        
        # Button frame.
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        # Setup Button.
        setup_btn = ttk.Button(btn_frame, text="Setup", command=self.run_setup)
        setup_btn.grid(row=0, column=0, padx=10)
        
        # Baseline Button.
        baseline_btn = ttk.Button(btn_frame, text="Create Baseline", command=self.run_baseline)
        baseline_btn.grid(row=0, column=1, padx=10)
        
        # Monitor Button.
        monitor_btn = ttk.Button(btn_frame, text="Start Monitoring", command=self.start_monitoring_thread)
        monitor_btn.grid(row=0, column=2, padx=10)
        
        # Check Integrity Button.
        check_btn = ttk.Button(btn_frame, text="Check Integrity", command=self.run_check)
        check_btn.grid(row=0, column=3, padx=10)
        
        # Log display area.
        self.log_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=90, height=25, state="disabled")
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Refresh Log Button.
        refresh_btn = ttk.Button(self, text="Refresh Log", command=self.refresh_log)
        refresh_btn.pack(pady=5)
    
    def run_setup(self):
        result = setup_directories()
        self.append_text(result + "\n")
        messagebox.showinfo("Setup", result)
    
    def run_baseline(self):
        def task():
            self.append_text("Creating baseline...\n")
            try:
                create_baseline()
                self.append_text("Baseline created successfully.\n")
                messagebox.showinfo("Baseline", "Baseline created successfully.")
            except Exception as e:
                self.append_text(f"Error creating baseline: {e}\n")
                messagebox.showerror("Error", f"Error creating baseline: {e}")
        threading.Thread(target=task, daemon=True).start()
    
    def start_monitoring_thread(self):
        if self.monitoring_active:
            messagebox.showinfo("Monitor", "Monitoring is already running.")
            return
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.run_monitoring, daemon=True)
        self.monitoring_thread.start()
        self.append_text("Monitoring started...\n")
    
    def run_monitoring(self):
        try:
            start_monitoring()
        except Exception as e:
            self.append_text(f"Error in monitoring: {e}\n")
    
    def run_check(self):
        def task():
            self.append_text("Performing integrity check...\n")
            try:
                perform_check()
                self.append_text("Integrity check completed.\n")
                messagebox.showinfo("Check", "Integrity check completed.")
            except Exception as e:
                self.append_text(f"Error during integrity check: {e}\n")
                messagebox.showerror("Error", f"Error during integrity check: {e}")
        threading.Thread(target=task, daemon=True).start()
    
    def refresh_log(self):
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    content = f.read()
                self.log_text.config(state="normal")
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, content)
                self.log_text.config(state="disabled")
        except Exception as e:
            self.append_text(f"Error refreshing log: {e}\n")
        self.after(2000, self.refresh_log)
    
    def append_text(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text)
        self.log_text.config(state="disabled")

if __name__ == "__main__":
    app = FIMDashboard()
    app.mainloop()

