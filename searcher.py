import os
import re
import json
import tkinter as tk


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
        self.root.title("Searcher Mark 3 - Dark Mode")
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

        self.video_metadata = {}

        # Parole salvate manualmente dall'utente: {parola: conteggio}
        self.saved_words = {}  # es. {"vacanze 2023": 12}

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

        # Lista ricerche salvate

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
            text="Ricerche salvate",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold")
        )

        words_label.pack(
            pady=5
        )

        # Entry per aggiungere nuova parola
        self.new_word_var = tk.StringVar()
        self.new_word_entry = Entry(
            right_frame,
            textvariable=self.new_word_var,
            width=28,
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat"
        )
        self.new_word_entry.pack(pady=(0, 3))
        self.new_word_entry.bind("<Return>", lambda e: self.add_saved_word())

        self.add_word_button = Button(
            right_frame,
            text="Aggiungi ricerca",
            command=self.add_saved_word,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )
        self.add_word_button.pack(pady=(0, 5))

        self.words_listbox = Listbox(
            right_frame,
            width=35,
            bg=self.entry_bg,
            fg=self.fg_color,
            selectbackground=self.highlight_color,
            selectforeground=self.fg_color,
            relief="flat",
            font=("Courier New", 10)
        )
        self.words_listbox.pack(fill=tk.Y, expand=True)
        self.words_listbox.bind("<Double-Button-1>", self.search_from_saved)

        # Pulsante elimina parola
        self.delete_word_button = Button(
            right_frame,
            text="Elimina ricerca",
            command=self.delete_saved_word,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            relief="flat"
        )
        self.delete_word_button.pack(pady=5)

        tk.Label(
            right_frame,
            text="(doppio click = cerca)",
            bg=self.bg_color,
            fg="#888888",
            font=("Arial", 8)
        ).pack()

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

            self.video_metadata = data.get("video_metadata", {})

            # Carica le parole salvate manualmente e ricalcola i conteggi
            saved = data.get("saved_words", {})
            self.saved_words = {}
            for word in saved:
                self.saved_words[word] = self._count_files_for_term(word)

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

            "video_metadata": self.video_metadata,
            "saved_words": self.saved_words
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

        # Ricalcola conteggi per tutte le parole salvate
        for word in self.saved_words:
            self.saved_words[word] = self._count_files_for_term(word)

        self.update_video_list()

        self.update_words_display()

        self.save_cache()

        print("Scansione completata.")

    # Conta file per un termine di ricerca

    def _count_files_for_term(self, term):
        """Conta quanti file contengono il termine (case-insensitive, multi-parola)."""
        term_lower = term.lower()
        terms = term_lower.split()
        count = 0
        for video_name, video_path in self.video_files:
            name = video_name.lower()
            if all(t in name for t in terms):
                count += 1
        return count

    # Aggiungi parola salvata

    def add_saved_word(self):
        word = self.new_word_var.get().strip()
        if not word:
            return
        word_lower = word.lower()
        count = self._count_files_for_term(word_lower)
        self.saved_words[word_lower] = count
        self.new_word_var.set("")
        self.update_words_display()
        self.save_cache()
        print(f"Parola aggiunta: {word_lower} ({count} file)")

    # Elimina parola salvata

    def delete_saved_word(self):
        selection = self.words_listbox.curselection()
        if not selection:
            return
        line = self.words_listbox.get(selection[0])
        word = line.split("  ")[0].strip().lower()
        if word in self.saved_words:
            del self.saved_words[word]
            self.update_words_display()
            self.save_cache()
            print(f"Parola eliminata: {word}")

    # Cerca da parola salvata (doppio click)

    def search_from_saved(self, event=None):
        selection = self.words_listbox.curselection()
        if not selection:
            return
        line = self.words_listbox.get(selection[0])
        word = line.split("  ")[0].strip()
        self.search_var.set(word)
        self.search_videos()

    # Aggiorna display parole salvate

    def update_words_display(self):

        self.words_listbox.delete(0, tk.END)

        for word, count in sorted(
            self.saved_words.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            line = f"{word}  [{count}]"
            self.words_listbox.insert(tk.END, line)

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