import os
import tkinter as tk
from tkinter import Listbox, Scrollbar, Entry, Button

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Library - Dark Mode")

        # Colori tema scuro
        self.bg_color = "#1e1e1e"     # sfondo principale
        self.fg_color = "#ffffff"     # testo bianco
        self.entry_bg = "#2d2d2d"     # input e listbox
        self.button_bg = "#3a3a3a"
        self.highlight_color = "#007acc"  # azzurro stile VSCode

        # Applica sfondo alla finestra
        self.root.configure(bg=self.bg_color)
        
        # Frame per la lista dei video
        self.frame = tk.Frame(root, bg=self.bg_color)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barra di ricerca
        self.search_var = tk.StringVar()
        self.search_entry = Entry(
            root, textvariable=self.search_var, width=40,
            bg=self.entry_bg, fg=self.fg_color,
            insertbackground=self.fg_color,  # colore cursore
            relief="flat"
        )
        self.search_entry.pack(padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.search_videos)
        
        # Lista dei video
        self.video_listbox = Listbox(
            self.frame, width=120, height=20,
            bg=self.entry_bg, fg=self.fg_color,
            selectbackground=self.highlight_color,
            selectforeground=self.fg_color,
            relief="flat"
        )
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar per la lista
        scrollbar = Scrollbar(self.frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_listbox.yview)
        
        self.video_listbox.bind("<Double-Button-1>", self.play_video)
        
        # Pulsante per scansionare gli SSD
        self.scan_button = Button(
            root, text="Scansiona SSD",
            command=self.scan_ssds,
            bg=self.button_bg, fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )
        self.scan_button.pack(pady=10)

        # Pulsante per ordinare per data
        self.sort_date_button = Button(
            root, text="Ordina per Data ↑",
            command=self.sort_by_date,
            bg=self.button_bg, fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )
        self.sort_date_button.pack(pady=5)

        # Pulsante per ordinare per dimensione
        self.sort_size_button = Button(
            root, text="Ordina per Dimensione ↑",
            command=self.sort_by_size,
            bg=self.button_bg, fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )
        self.sort_size_button.pack(pady=5)

        # Etichetta per mostrare il numero di video trovati
        self.counter_label = tk.Label(
            root, text="Video trovati: 0", font=("Arial", 10),
            bg=self.bg_color, fg=self.fg_color
        )
        self.counter_label.pack(pady=5)

        # Elenco dei video
        self.video_files = []
        self.filtered_files = []

        # Stato iniziale per l'ordinamento
        self.sort_by_date_asc = True
        self.sort_by_size_asc = True

    def update_counter(self):
        count = len(self.filtered_files)
        self.counter_label.config(text=f"Video trovati: {count}")

    def scan_ssds(self):
        self.video_files.clear()
        self.filtered_files.clear()
        self.video_listbox.delete(0, tk.END)

        ssd_paths = ["F:/"]# Cambia con le tue lettere di unità SSD

        for ssd in ssd_paths:
            for root, _, files in os.walk(ssd):
                for file in files:
                    if file.endswith((".mp4", ".mkv", ".avi", ".mov")):
                        full_path = os.path.join(root, file)
                        self.video_files.append((file, full_path))
        
        self.filtered_files = self.video_files.copy()
        self.update_video_list()
    
    def update_video_list(self):
        self.video_listbox.delete(0, tk.END)
        self.video_listbox.config(font=("Courier New", 10))
        for video in self.filtered_files:
            video_name, video_path = video
            try:
                size_bytes = os.path.getsize(video_path)
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 ** 2:
                    size_str = f"{size_bytes / 1024:.2f} KB"
                elif size_bytes < 1024 ** 3:
                    size_str = f"{size_bytes / (1024 ** 2):.2f} MB"
                elif size_bytes < 1024 ** 4:
                    size_str = f"{size_bytes / (1024 ** 3):.2f} GB"
                else:
                    size_str = f"{size_bytes / (1024 ** 4):.2f} TB"

                display_text = f"{video_path:<100} | {size_str}"
            except Exception:
                display_text = f"{video_path:<100} | Errore lettura"

            self.video_listbox.insert(tk.END, display_text)
            self.update_counter()

    def search_videos(self, event):
        search_text = self.search_var.get().lower()
        search_terms = search_text.split()
        seen = set()
        self.filtered_files = []
        for video in self.video_files:
            video_name = video[0].lower()
            if all(term in video_name for term in search_terms):
                if video[0] not in seen:
                    self.filtered_files.append(video)
                    seen.add(video[0])
        self.update_video_list()

    def play_video(self, event):
        selected_index = self.video_listbox.curselection()
        if selected_index:
            video_path = self.filtered_files[selected_index[0]][1]
            os.startfile(video_path)

    def sort_by_date(self):
        self.sort_by_date_asc = not self.sort_by_date_asc
        self.filtered_files.sort(
            key=lambda x: os.path.getmtime(x[1]),
            reverse=not self.sort_by_date_asc
        )
        self.sort_date_button.config(
            text=f"Ordina per Data {'↑' if self.sort_by_date_asc else '↓'}"
        )
        self.update_video_list()

    def sort_by_size(self):
        self.sort_by_size_asc = not self.sort_by_size_asc
        self.filtered_files.sort(
            key=lambda x: os.path.getsize(x[1]),
            reverse=not self.sort_by_size_asc
        )
        self.sort_size_button.config(
            text=f"Ordina per Dimensione {'↑' if self.sort_by_size_asc else '↓'}"
        )
        self.update_video_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
