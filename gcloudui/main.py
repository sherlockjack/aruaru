import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class GCloudGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GCloud GUI Manager ☁️")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- UI ELEMENTS ---
        
        # 1. Title
        ttk.Label(root, text="Google Cloud CLI Manager", font=("Arial", 14, "bold")).pack(pady=15)
        
        # 2. Current Project Info
        self.current_project_var = tk.StringVar()
        self.current_project_var.set("Loading...")
        ttk.Label(root, text="Active Project:").pack()
        ttk.Label(root, textvariable=self.current_project_var, font=("Arial", 10, "bold"), foreground="blue").pack(pady=5)
        
        # 3. Project Selection
        ttk.Label(root, text="Select/Change Project:").pack(pady=(10,0))
        self.project_combo = ttk.Combobox(root, width=40, state="readonly")
        self.project_combo.pack(pady=5)
        
        # 4. Buttons Frame
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Set Active Project", command=self.set_project).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_data).grid(row=0, column=1, padx=5)
        
        # 5. Auth Frame
        auth_frame = ttk.Frame(root)
        auth_frame.pack(pady=15)
        
        ttk.Button(auth_frame, text="🔄 1-Click Re-Authenticate", command=self.reauthenticate).pack()

        # Load initial data
        self.refresh_data()

    def run_gcloud(self, command):
        """Helper to run gcloud commands"""
        try:
            # shell=True is useful for Windows to find gcloud in PATH
            result = subprocess.run(f"gcloud {command}", shell=True, capture_output=True, text=True)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), 1

    def refresh_data(self):
        """Fetch current project and project list"""
        self.current_project_var.set("Loading...")
        self.project_combo.set('')
        self.project_combo['values'] = []
        
        # Gunakan thread agar GUI tidak freeze
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def _fetch_data_thread(self):
        # Get active project
        stdout, stderr, code = self.run_gcloud("config get-value project")
        active_project = stdout if code == 0 else "None / Error"
        
        # Get list of projects
        stdout_list, stderr_list, code_list = self.run_gcloud("projects list --format=\"value(projectId)\"")
        projects = stdout_list.split('\n') if code_list == 0 else []
        
        # Update UI (must be done in main thread, but simple sets are usually safe in Tkinter)
        self.root.after(0, lambda: self.current_project_var.set(active_project))
        if projects:
            self.root.after(0, lambda: self._update_combo(projects, active_project))

    def _update_combo(self, projects, active_project):
        self.project_combo['values'] = projects
        if active_project in projects:
            self.project_combo.set(active_project)
        elif projects:
            self.project_combo.current(0)

    def set_project(self):
        selected = self.project_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "Pilih project terlebih dahulu!")
            return
            
        self.current_project_var.set("Setting project...")
        threading.Thread(target=self._set_project_thread, args=(selected,), daemon=True).start()

    def _set_project_thread(self, project_id):
        stdout, stderr, code = self.run_gcloud(f"config set project {project_id}")
        if code == 0:
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Project berhasil diubah ke: {project_id}"))
            self.root.after(0, self.refresh_data)
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal mengubah project:\n{stderr}"))
            self.root.after(0, self.refresh_data)

    def reauthenticate(self):
        answer = messagebox.askyesno("Re-Authenticate", "Ini akan membuka browser untuk login Google Cloud dan Application Default Credentials. Lanjutkan?")
        if answer:
            threading.Thread(target=self._auth_thread, daemon=True).start()

    def _auth_thread(self):
        # 1. Normal Auth Login
        self.run_gcloud("auth login")
        # 2. Application Default Login (ADC)
        self.run_gcloud("auth application-default login")
        self.root.after(0, lambda: messagebox.showinfo("Auth Selesai", "Proses otentikasi selesai. Silakan cek terminal/browser jika ada yang tersangkut."))

def main():
    root = tk.Tk()
    app = GCloudGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()