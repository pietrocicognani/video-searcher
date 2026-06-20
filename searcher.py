import os
import re
import json
import tkinter as tk

from collections import Counter, defaultdict
from tkinter import (
    Listbox,
    Scrollbar,
    Entry,
    Button,
    Text,
    Frame
)


class VideoPlayerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("searcher mark 1 - Dark Mode")
        self.root.geometry("1500x800")

        # Tema

        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#2d2d2d"
        self.button_bg = "#3a3a3a"
        self.highlight_color = "#007acc"

        self.root.configure(bg=self.bg_color)

        # Cache

        self.cache_file = "video_cache.json"

        # Dati

        self.video_files = []
        self.filtered_files = []

        self.word_counter = Counter()
        self.word_map = defaultdict(list)

        self.video_metadata = {}

        # Ordinamento

        self.sort_by_date_asc = True
        self.sort_by_size_asc = True

        # Search bar

        self.search_var = tk.StringVar()

        self.search_entry = Entry(
            root,
            textvariable=self.search_var,
            width=50,
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat"
        )

        self.search_entry.pack(
            padx=10,
            pady=10
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.search_videos
        )

        # Pulsanti

        buttons_frame = Frame(
            root,
            bg=self.bg_color
        )

        buttons_frame.pack(
            pady=5
        )

        self.scan_button = Button(
            buttons_frame,
            text="Scansiona SSD",
            command=self.scan_ssds,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )

        self.scan_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.sort_date_button = Button(
            buttons_frame,
            text="Ordina per Data ↑",
            command=self.sort_by_date,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )

        self.sort_date_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.sort_size_button = Button(
            buttons_frame,
            text="Ordina per Dimensione ↑",
            command=self.sort_by_size,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )

        self.sort_size_button.pack(
            side=tk.LEFT,
            padx=5
        )

        # Contatore

        self.counter_label = tk.Label(
            root,
            text="Video trovati: 0",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )

        self.counter_label.pack(
            pady=5
        )

        # Frame principale

        main_frame = Frame(
            root,
            bg=self.bg_color
        )

        main_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        # Lista video

        left_frame = Frame(
            main_frame,
            bg=self.bg_color
        )

        left_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.video_listbox = Listbox(
            left_frame,
            width=140,
            height=30,
            bg=self.entry_bg,
            fg=self.fg_color,
            selectbackground=self.highlight_color,
            selectforeground=self.fg_color,
            relief="flat",
            font=("Courier New", 10)
        )

        self.video_listbox.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar = Scrollbar(
            left_frame,
            orient="vertical"
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill="y"
        )

        self.video_listbox.config(
            yscrollcommand=scrollbar.set
        )

        scrollbar.config(
            command=self.video_listbox.yview
        )

        self.video_listbox.bind(
            "<Double-Button-1>",
            self.play_video
        )

        # Lista parole

        right_frame = Frame(
            main_frame,
            bg=self.bg_color
        )

        right_frame.pack(
            side=tk.RIGHT,
            fill=tk.Y,
            padx=10
        )

        words_label = tk.Label(
            right_frame,
            text="Parole più frequenti",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        )

        words_label.pack(
            pady=5
        )

        self.words_text = Text(
            right_frame,
            width=35,
            bg=self.entry_bg,
            fg=self.fg_color,
            relief="flat",
            font=("Courier New", 10)
        )

        self.words_text.pack(
            fill=tk.Y,
            expand=True
        )

        # Carica cache

        self.load_cache()

    # Caricamento cache

    def load_cache(self):

        if not os.path.exists(self.cache_file):
            print("Cache non trovata.")
            return

        try:

            with open(
                self.cache_file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            self.video_files = [
                (v["name"], v["path"])
                for v in data["videos"]
            ]

            self.filtered_files = self.video_files.copy()

            self.word_counter = Counter(
                data["word_counter"]
            )

            self.word_map = defaultdict(
                list,
                data["word_map"]
            )

            self.video_metadata = data["video_metadata"]

            self.update_video_list()
            self.update_words_display()

            print("Cache caricata.")

        except Exception as e:

            print("Errore caricamento cache:")
            print(e)

    # Salvataggio cache

    def save_cache(self):

        data = {

            "videos": [
                {
                    "name": name,
                    "path": path
                }
                for name, path in self.video_files
            ],

            "word_counter": dict(self.word_counter),

            "word_map": dict(self.word_map),

            "video_metadata": self.video_metadata
        }

        with open(
            self.cache_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

        print("Cache salvata.")

    # Scansione SSD

    def scan_ssds(self):

        print("Scansione SSD...")

        self.video_files.clear()
        self.filtered_files.clear()
        self.video_metadata.clear()

        self.video_listbox.delete(
            0,
            tk.END
        )

        # Cambia qui le unità

        ssd_paths = [
            "F:/"
        ]

        supported_formats = (
            ".mp4",
            ".mkv",
            ".avi",
            ".mov"
        )

        for ssd in ssd_paths:

            for root, _, files in os.walk(ssd):

                for file in files:

                    if file.lower().endswith(
                        supported_formats
                    ):

                        full_path = os.path.join(
                            root,
                            file
                        )

                        self.video_files.append(
                            (file, full_path)
                        )

                        try:

                            self.video_metadata[
                                full_path
                            ] = {

                                "size": os.path.getsize(
                                    full_path
                                ),

                                "mtime": os.path.getmtime(
                                    full_path
                                )
                            }

                        except Exception:

                            self.video_metadata[
                                full_path
                            ] = {

                                "size": 0,
                                "mtime": 0
                            }

        self.filtered_files = self.video_files.copy()

        self.build_word_index()

        self.update_video_list()

        self.update_words_display()

        self.save_cache()

        print("Scansione completata.")

    # Costruzione indice parole

    def build_word_index(self):

        self.word_counter.clear()
        self.word_map.clear()

        ignored = {

            "1080p",
            "720p",
            "2160p",
            "480p",

            "x264",
            "x265",
            "h264",
            "h265",

            "bluray",
            "brrip",
            "webrip",
            "webdl",

            "mkv",
            "mp4",
            "avi",
            "mov",

            "ita",
            "eng",
            "sub",
            "multi"
        }

        for video_name, video_path in self.video_files:

            name = os.path.splitext(
                video_name
            )[0]

            words = re.findall(
                r'\b[a-zA-Z0-9]+\b',
                name.lower()
            )

            unique_words = set()

            for word in words:

                if len(word) < 3:
                    continue

                if word in ignored:
                    continue

                self.word_counter[word] += 1

                if word not in unique_words:

                    self.word_map[word].append(
                        video_path
                    )

                    unique_words.add(word)

        print("\nPAROLE PIÙ FREQUENTI:\n")

        for word, count in self.word_counter.most_common(30):

            print(
                f"{word:<20} {count}"
            )

    # Aggiorna display parole

    def update_words_display(self):

        self.words_text.delete(
            "1.0",
            tk.END
        )

        for word, count in self.word_counter.most_common(100):

            line = f"{word:<20} {count}\n"

            self.words_text.insert(
                tk.END,
                line
            )

    # Aggiorna lista video

    def update_video_list(self):

        self.video_listbox.delete(
            0,
            tk.END
        )

        for video_name, video_path in self.filtered_files:

            metadata = self.video_metadata.get(
                video_path,
                {}
            )

            size_bytes = metadata.get(
                "size",
                0
            )

            size_str = self.format_size(
                size_bytes
            )

            display_text = (
                f"{video_path:<120} | {size_str}"
            )

            self.video_listbox.insert(
                tk.END,
                display_text
            )

        self.update_counter()

    # Formatta dimensione

    def format_size(self, size_bytes):

        if size_bytes < 1024:
            return f"{size_bytes} B"

        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"

        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"

        elif size_bytes < 1024 ** 4:
            return f"{size_bytes / (1024 ** 3):.2f} GB"

        else:
            return f"{size_bytes / (1024 ** 4):.2f} TB"

    # Contatore

    def update_counter(self):

        count = len(self.filtered_files)

        self.counter_label.config(
            text=f"Video trovati: {count}"
        )

    # Search

    def search_videos(self, event=None):

        search_text = self.search_var.get().lower()

        search_terms = search_text.split()

        self.filtered_files = []

        for video in self.video_files:

            video_name = video[0].lower()

            if all(
                term in video_name
                for term in search_terms
            ):

                self.filtered_files.append(
                    video
                )

        self.update_video_list()

    # Play video

    def play_video(self, event):

        selected_index = (
            self.video_listbox.curselection()
        )

        if selected_index:

            video_path = self.filtered_files[
                selected_index[0]
            ][1]

            os.startfile(video_path)

    # Ordina per data

    def sort_by_date(self):

        self.sort_by_date_asc = (
            not self.sort_by_date_asc
        )

        self.filtered_files.sort(

            key=lambda x: self.video_metadata
            .get(x[1], {})
            .get("mtime", 0),

            reverse=not self.sort_by_date_asc
        )

        self.sort_date_button.config(

            text=f"Ordina per Data {'↑' if self.sort_by_date_asc else '↓'}"
        )

        self.update_video_list()

    # Ordina per dimensione

    def sort_by_size(self):

        self.sort_by_size_asc = (
            not self.sort_by_size_asc
        )

        self.filtered_files.sort(

            key=lambda x: self.video_metadata
            .get(x[1], {})
            .get("size", 0),

            reverse=not self.sort_by_size_asc
        )

        self.sort_size_button.config(

            text=f"Ordina per Dimensione {'↑' if self.sort_by_size_asc else '↓'}"
        )

        self.update_video_list()


# Main

if __name__ == "__main__":

    root = tk.Tk()

    app = VideoPlayerApp(root)

    root.mainloop()