import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.scrolledtext as scrolledtext
import subprocess
import threading
import queue
import sys
import os

class GCloudGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GCloud GUI Manager")
        self.root.geometry("650x750") 
        self.root.configure(bg="#F3F3F3") 
        
        self.font_title = ("Segoe UI", 16, "bold")
        self.font_label = ("Segoe UI", 10)
        self.font_project = ("Segoe UI", 11, "bold")
        self.font_btn = ("Segoe UI", 9)
        self.font_term = ("Consolas", 10)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("Accent.TButton", font=self.font_btn, foreground="white", background="#0078D4", borderwidth=0, padding=8)
        self.style.map("Accent.TButton", background=[('active', '#005A9E')])
        self.style.configure("Secondary.TButton", font=self.font_btn, background="white", padding=8)
        self.style.configure("TCombobox", padding=5, font=self.font_label)

        self.all_projects = []
        self.filtered_projects = []
        
        # --- UI ELEMENTS --- (Sama seperti sebelumnya)
        main_frame = tk.Frame(root, bg="#F3F3F3")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        tk.Label(main_frame, text="Google Cloud CLI Manager", font=self.font_title, bg="#F3F3F3", fg="#202020").pack()
        
        self.current_project_var = tk.StringVar()
        self.current_project_var.set("Loading...")
        tk.Label(main_frame, text="Active Project:", font=self.font_label, bg="#F3F3F3", fg="#505050").pack(pady=(10, 0))
        tk.Label(main_frame, textvariable=self.current_project_var, font=self.font_project, bg="#F3F3F3", fg="#0078D4").pack(pady=(0, 15))
        
        tk.Label(main_frame, text="Select/Change Project:", font=self.font_label, bg="#F3F3F3", fg="#505050").pack(anchor="w")
        
        search_frame = tk.Frame(main_frame, bg="#F3F3F3")
        search_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(search_frame, text="🔍", font=self.font_label, bg="#F3F3F3").pack(side=tk.LEFT, padx=(5, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_projects)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.font_label)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Search Projects...")
        self.search_entry.bind('<FocusIn>', self.clear_placeholder)
        self.search_entry.bind('<FocusOut>', self.add_placeholder)
        
        self.project_combo = ttk.Combobox(main_frame, font=self.font_label, state="readonly")
        self.project_combo.pack(fill=tk.X, pady=(5, 15))
        
        btn_frame = tk.Frame(main_frame, bg="#F3F3F3")
        btn_frame.pack()
        ttk.Button(btn_frame, text="Set Active Project", command=self.set_project, style="Accent.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_data, style="Secondary.TButton").grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="🔐 1-Click Re-Auth", command=self.reauthenticate, style="Secondary.TButton").grid(row=0, column=2, padx=5)

        # --- TERMINAL SECTION ---
        term_container = tk.Frame(main_frame, bg="#1E1E1E", bd=1, relief=tk.SUNKEN)
        term_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        self.term_output = scrolledtext.ScrolledText(term_container, bg="#1E1E1E", fg="#CCCCCC", font=self.font_term, state=tk.DISABLED, wrap=tk.WORD, bd=0)
        self.term_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        input_frame = tk.Frame(term_container, bg="#1E1E1E")
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(0, 5))
        
        # Label ">" dihilangkan karena prompt asli dari cmd (C:\...>) bakal muncul di output layar atas
        self.cmd_entry = tk.Entry(input_frame, bg="#333333", fg="#00FF00", font=self.font_term, insertbackground="white", bd=1)
        self.cmd_entry.pack(side=LEFT, fill=tk.X, expand=True)
        self.cmd_entry.bind("<Return>", self.execute_terminal_cmd)

        self.refresh_data()
        
        # --- START REAL NATIVE TERMINAL SESSION ---
        self.output_queue = queue.Queue()
        self.start_persistent_shell()
        self.root.after(50, self.process_queue_to_gui) # Polling update GUI

    # --- PERSISTENT NATIVE SHELL LOGIC ---
    def start_persistent_shell(self):
        """Memulai satu proses cmd.exe asli yang hidup terus selama GUI terbuka"""
        kwargs = {}
        if sys.platform == "win32":
            kwargs['creationflags'] = 0x08000000 # Menyembunyikan jendela cmd asli

        # Gunakan cmd.exe bawaan sistem
        shell_exe = os.environ.get("COMSPEC", "cmd.exe")
        
        self.shell_process = subprocess.Popen(
            shell_exe,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            **kwargs
        )
        
        # Baca output cmd secara live dari thread terpisah
        threading.Thread(target=self._read_shell_output, daemon=True).start()

    def _read_shell_output(self):
        """Membaca setiap karakter dari cmd.exe (termasuk prompt) lalu kirim ke queue"""
        while True:
            char = self.shell_process.stdout.read(1)
            if not char: # Jika shell mati
                break
            self.output_queue.put(char)

    def process_queue_to_gui(self):
        """Memindahkan text dari antrean ke dalam ScrolledText tanpa bikin GUI hang"""
        chars = []
        while not self.output_queue.empty():
            chars.append(self.output_queue.get())
            
        if chars:
            self.term_output.config(state=tk.NORMAL)
            self.term_output.insert(tk.END, "".join(chars))
            self.term_output.see(tk.END)
            self.term_output.config(state=tk.DISABLED)
            
        # Panggil lagi fungsi ini 50 milidetik kemudian
        self.root.after(50, self.process_queue_to_gui)

    def execute_terminal_cmd(self, event):
        """Melempar perintah yang kamu ketik ke dalam cmd.exe yang sedang jalan"""
        cmd = self.cmd_entry.get()
        self.cmd_entry.delete(0, tk.END)
        
        if self.shell_process and self.shell_process.poll() is None:
            # Tulis perintah yang kamu ketik + Enter ke dalam cmd
            self.shell_process.stdin.write(cmd + "\n")
            self.shell_process.stdin.flush()
            # Opsional: Bikin input box fokus lagi
            self.cmd_entry.focus()

    # --- CORE GCLOUD LOGIC (Tombol-tombol GUI tetap pakai sistem independent biar ga ganggu cmd) ---
    def run_gcloud(self, command):
        try:
            result = subprocess.run(f"gcloud {command}", shell=True, capture_output=True, text=True)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), 1

    def refresh_data(self):
        self.current_project_var.set("Loading...")
        self.project_combo.set('')
        self.project_combo['values'] = []
        self.search_var.set("Search Projects...")
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def _fetch_data_thread(self):
        stdout, stderr, code = self.run_gcloud("config get-value project")
        active_project = stdout if code == 0 and stdout else "None / Error"
        
        stdout_list, stderr_list, code_list = self.run_gcloud("projects list --format=\"value(projectId)\"")
        if code_list == 0:
            self.all_projects = [p for p in stdout_list.split('\n') if p.strip()]
        else:
            self.all_projects = []
        
        self.root.after(0, lambda: self._update_ui_after_fetch(active_project))

    def _update_ui_after_fetch(self, active_project):
        self.current_project_var.set(active_project)
        self.filtered_projects = self.all_projects
        self.project_combo['values'] = self.filtered_projects
        if active_project in self.filtered_projects:
            self.project_combo.set(active_project)
        elif self.filtered_projects:
            self.project_combo.current(0)

    def filter_projects(self, *args):
        search_term = self.search_var.get().lower()
        if search_term == "search projects..." or not search_term:
            self.filtered_projects = self.all_projects
        else:
            self.filtered_projects = [p for p in self.all_projects if search_term in p.lower()]
        
        self.project_combo['values'] = self.filtered_projects
        if self.filtered_projects:
            self.project_combo.current(0)
        else:
            self.project_combo.set('')

    def set_project(self):
        selected = self.project_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "Pilih project terlebih dahulu!")
            return
        
        self.current_project_var.set("Setting project...")
        # Beri info di terminal bahwa tombol diklik
        self.term_output.config(state=tk.NORMAL)
        self.term_output.insert(tk.END, f"\n[GUI] Changing project to {selected}...\n")
        self.term_output.see(tk.END)
        self.term_output.config(state=tk.DISABLED)
        
        threading.Thread(target=self._set_project_thread, args=(selected,), daemon=True).start()

    def _set_project_thread(self, project_id):
        stdout, stderr, code = self.run_gcloud(f"config set project {project_id}")
        if code == 0:
            self.root.after(0, lambda: self.search_var.set("Search Projects..."))
            self.root.after(0, self.refresh_data)
        else:
            self.root.after(0, self.refresh_data)

    def reauthenticate(self):
        answer = messagebox.askyesno("Re-Authenticate", "Buka browser untuk login Google Cloud & ADC?")
        if answer:
            threading.Thread(target=self._auth_thread, daemon=True).start()

    def _auth_thread(self):
        self.run_gcloud("auth login")
        self.run_gcloud("auth application-default login")
        self.root.after(0, lambda: messagebox.showinfo("Auth Selesai", "Proses otentikasi selesai."))

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