import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class GCloudGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GCloud GUI Manager")
        self.root.geometry("500x420")
        self.root.configure(bg="#F3F3F3") # Warna background bersih ala Win11
        
        # Konfigurasi Font Modern
        self.font_title = ("Segoe UI", 16, "bold")
        self.font_label = ("Segoe UI", 10)
        self.font_project = ("Segoe UI", 11, "bold")
        self.font_btn = ("Segoe UI", 9)

        # Style untuk Tombol & Dropdown
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Styling Tombol Utama (Biru)
        self.style.configure("Accent.TButton", 
                            font=self.font_btn, 
                            foreground="white", 
                            background="#0078D4", 
                            borderwidth=0, 
                            focuscolor="none",
                            padding=8)
        self.style.map("Accent.TButton", background=[('active', '#005A9E')])

        # Styling Tombol Sekunder (Putih/Abu)
        self.style.configure("Secondary.TButton", 
                            font=self.font_btn, 
                            background="white", 
                            padding=8)

        # styling Dropdown
        self.style.configure("TCombobox", padding=5, font=self.font_label)

        # --- DATA & STATE ---
        self.all_projects = []
        self.filtered_projects = []

        # --- UI ELEMENTS ---
        
        # Main Container with padding
        main_frame = tk.Frame(root, bg="#F3F3F3")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 1. Title
        tk.Label(main_frame, text="Google Cloud CLI Manager", font=self.font_title, bg="#F3F3F3", fg="#202020").pack(pady=(0, 20))
        
        # 2. Current Project Info
        self.current_project_var = tk.StringVar()
        self.current_project_var.set("Loading...")
        tk.Label(main_frame, text="Active Project:", font=self.font_label, bg="#F3F3F3", fg="#505050").pack()
        tk.Label(main_frame, textvariable=self.current_project_var, font=self.font_project, bg="#F3F3F3", fg="#0078D4").pack(pady=(5, 20))
        
        # 3. Project Search & Selection Area
        tk.Label(main_frame, text="Select/Change Project:", font=self.font_label, bg="#F3F3F3", fg="#505050").pack(anchor="w")
        
        # --- Bagian Search Bar ---
        search_frame = tk.Frame(main_frame, bg="#F3F3F3")
        search_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Ikon Search (pakai karakter unicode aja biar simpel)
        tk.Label(search_frame, text="🔍", font=self.font_label, bg="#F3F3F3").pack(side=tk.LEFT, padx=(5, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_projects) # Trigger filter saat ketik
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.font_label)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Placeholder text
        self.search_entry.insert(0, "Search Projects...")
        self.search_entry.bind('<FocusIn>', self.clear_placeholder)
        self.search_entry.bind('<FocusOut>', self.add_placeholder)
        
        # --- Bagian Dropdown ---
        self.project_combo = ttk.Combobox(main_frame, font=self.font_label, state="readonly")
        self.project_combo.pack(fill=tk.X, pady=(5, 20))
        
        # 4. Buttons Frame (Side-by-side)
        btn_frame = tk.Frame(main_frame, bg="#F3F3F3")
        btn_frame.pack(pady=0)
        
        self.btn_set = ttk.Button(btn_frame, text="Set Active Project", command=self.set_project, style="Accent.TButton")
        self.btn_set.grid(row=0, column=0, padx=10)
        
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_data, style="Secondary.TButton").grid(row=0, column=1, padx=10)
        
        # 5. Auth Frame (Satu tombol besar di bawah)
        auth_frame = tk.Frame(main_frame, bg="#F3F3F3")
        auth_frame.pack(fill=tk.X, pady=(40, 0))
        
        # Tombol Re-Auth dengan ikon kunci
        ttk.Button(auth_frame, text="🔐 1-Click Re-Authenticate", command=self.reauthenticate, style="Secondary.TButton").pack(fill=tk.X)

        # Load initial data
        self.refresh_data()

    # --- LOGIC & HELPER FUNCTIONS ---

    def run_gcloud(self, command):
        """Helper to run gcloud commands"""
        try:
            # Gunakan shell=True agar gcloud ditemukan di PATH
            result = subprocess.run(f"gcloud {command}", shell=True, capture_output=True, text=True)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), 1

    def refresh_data(self):
        """Fetch current project and project list"""
        self.current_project_var.set("Loading...")
        self.project_combo.set('')
        self.project_combo['values'] = []
        self.search_var.set("Search Projects...") # Reset search
        
        # Gunakan thread agar GUI tidak freeze
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def _fetch_data_thread(self):
        # Get active project
        stdout, stderr, code = self.run_gcloud("config get-value project")
        active_project = stdout if code == 0 and stdout else "None / Error"
        
        # Get list of projects
        stdout_list, stderr_list, code_list = self.run_gcloud("projects list --format=\"value(projectId)\"")
        if code_list == 0:
            self.all_projects = stdout_list.split('\n')
            # Hapus baris kosong jika ada
            self.all_projects = [p for p in self.all_projects if p.strip()]
        else:
            self.all_projects = []
        
        # Update UI di main thread
        self.root.after(0, lambda: self._update_ui_after_fetch(active_project))

    def _update_ui_after_fetch(self, active_project):
        self.current_project_var.set(active_project)
        self.filtered_projects = self.all_projects
        self.project_combo['values'] = self.filtered_projects
        
        if active_project in self.filtered_projects:
            self.project_combo.set(active_project)
        elif self.filtered_projects:
            self.project_combo.current(0)

    # --- LOGIKA FILTER PENCARIAN ---
    def filter_projects(self, *args):
        search_term = self.search_var.get().lower()
        
        # Jangan filter kalau masih teks placeholder
        if search_term == "search projects..." or not search_term:
            self.filtered_projects = self.all_projects
        else:
            self.filtered_projects = [p for p in self.all_projects if search_term in p.lower()]
        
        # Update nilai dropdown
        self.project_combo['values'] = self.filtered_projects
        
        # Pilih item pertama hasil filter kalau ada
        if self.filtered_projects:
            self.project_combo.current(0)
        else:
            self.project_combo.set('') # Kosongkan kalau nggak ketemu

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
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Project berhasil diubah ke:\n{project_id}"))
            # Reset search bar setelah sukses
            self.root.after(0, lambda: self.search_var.set("Search Projects..."))
            self.root.after(0, self.refresh_data)
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal mengubah project:\n{stderr}"))
            self.root.after(0, self.refresh_data)

    def reauthenticate(self):
        answer = messagebox.askyesno("Re-Authenticate", "Ini akan membuka browser untuk login Google Cloud dan ADC. Lanjutkan?")
        if answer:
            threading.Thread(target=self._auth_thread, daemon=True).start()

    def _auth_thread(self):
        # 1. Normal Auth Login
        self.run_gcloud("auth login")
        # 2. Application Default Login (ADC)
        self.run_gcloud("auth application-default login")
        self.root.after(0, lambda: messagebox.showinfo("Auth Selesai", "Proses otentikasi selesai.\nCek browser Anda."))

    # Helper untuk placeholder
    def clear_placeholder(self, event):
        if self.search_var.get() == "Search Projects...":
            self.search_var.set("")
            
    def add_placeholder(self, event):
        if not self.search_var.get():
            self.search_var.set("Search Projects...")

def main():
    root = tk.Tk()
    app = GCloudGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()