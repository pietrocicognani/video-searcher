import os
import tkinter as tk
from tkinter import Listbox, Scrollbar, Entry, Button

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Library")
        
        # Frame per la lista dei video
        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barra di ricerca
        self.search_var = tk.StringVar()
        self.search_entry = Entry(root, textvariable=self.search_var, width=40)
        self.search_entry.pack(padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.search_videos)
        
        # Lista dei video
        self.video_listbox = Listbox(self.frame, width=120, height=20)  # Aumentato la larghezza per visualizzare il percorso completo
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar per la lista
        scrollbar = Scrollbar(self.frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_listbox.yview)
        
        self.video_listbox.bind("<Double-Button-1>", self.play_video)
        
        # Pulsante per scansionare gli SSD
        self.scan_button = Button(root, text="Scansiona SSD", command=self.scan_ssds)
        self.scan_button.pack(pady=10)

        # Pulsante per ordinare per data
        self.sort_date_button = Button(root, text="Ordina per Data ↑", command=self.sort_by_date)
        self.sort_date_button.pack(pady=5)

        # Pulsante per ordinare per dimensione
        self.sort_size_button = Button(root, text="Ordina per Dimensione ↑", command=self.sort_by_size)
        self.sort_size_button.pack(pady=5)

        # Etichetta per mostrare il numero di video trovati
        # Viene aggiornata dopo ogni scansione o ricerca
        self.counter_label = tk.Label(root, text="Video trovati: 0", font=("Arial", 10))
        self.counter_label.pack(pady=5)

        # Elenco dei video
        self.video_files = []
        self.filtered_files = []

        # Stato iniziale per l'ordinamento (True = crescente, False = decrescente)
        self.sort_by_date_asc = True
        self.sort_by_size_asc = True
        
    def update_counter(self):
        # Conta quanti file video ci sono attualmente nella lista filtrata
        count = len(self.filtered_files)

        # Aggiorna il testo dell'etichetta con il numero
        self.counter_label.config(text=f"Video trovati: {count}")

    
    def scan_ssds(self):
        self.video_files.clear()
        self.filtered_files.clear()
        self.video_listbox.delete(0, tk.END)

        ssd_paths = ["E:/"]  # Cambia con le tue lettere di unità SSD

        for ssd in ssd_paths:
            for root, _, files in os.walk(ssd):
                for file in files:
                    if file.endswith((".mp4", ".mkv", ".avi", ".mov")):
                        full_path = os.path.join(root, file)
                        self.video_files.append((file, full_path))
        
        self.filtered_files = self.video_files.copy()
        self.update_video_list()
    
    def update_video_list(self):
        # Svuota la Listbox prima di aggiornarla
        self.video_listbox.delete(0, tk.END)

        # Usa font monospazio per allineare il testo in colonna (opzionale ma consigliato)
        self.video_listbox.config(font=("Courier New", 10))

        # Itera su ogni file filtrato
        for video in self.filtered_files:
            video_name, video_path = video
            try:
                # Ottieni la dimensione del file in byte
                size_bytes = os.path.getsize(video_path)

                # Determina l'unità più adatta (KB, MB, GB, TB)
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
                max_path_length = 30
                # Puoi regolarlo a piacere
                short_path = video_path if len(video_path) <= max_path_length else "..." + video_path[-max_path_length:]
                display_text = f"{short_path:<100} | {size_str}"              
                # Prepara la riga formattata: percorso + dimensione formattata
                display_text = f"{video_path:<100} | {size_str}"

            except Exception as e:
                # In caso di errore (es. file mancante)
                display_text = f"{video_path:<100} | Errore lettura"

            # Inserisce la riga nella lista
            self.video_listbox.insert(tk.END, display_text)
            # Aggiorna il contatore dei video trovati
            self.update_counter()




    def search_videos(self, event):
        # Ottieni il testo di ricerca e lo converti in minuscolo
        search_text = self.search_var.get().lower()

        # Suddividi il testo in singole parole (es. "fabio rossi" -> ['fabio', 'rossi'])
        search_terms = search_text.split()

        # Set per evitare duplicati nei risultati
        seen = set()

        # Lista che conterrà i file filtrati
        self.filtered_files = []

        # Itera su tutti i file video
        for video in self.video_files:
            # Prendi il nome del video in minuscolo
            video_name = video[0].lower()

            # Controlla se tutte le parole cercate sono presenti nel nome del video
            if all(term in video_name for term in search_terms):
                # Se il video non è già stato aggiunto, lo aggiungiamo
                if video[0] not in seen:
                    self.filtered_files.append(video)
                    seen.add(video[0])  # Segnalo che è stato aggiunto

        # Aggiorna la lista dei video mostrati
        self.update_video_list()





    def play_video(self, event):
        selected_index = self.video_listbox.curselection()
        if selected_index:
            video_path = self.filtered_files[selected_index[0]][1]
            os.startfile(video_path)  # Riproduce il video con il lettore predefinito di Windows (Film e TV o altro lettore predefinito)

    # Ordina i video per data di modifica (clic alterna crescente/decrescente)
    def sort_by_date(self):
        self.sort_by_date_asc = not self.sort_by_date_asc  # Inverti lo stato
        self.filtered_files.sort(
            key=lambda x: os.path.getmtime(x[1]),
            reverse=not self.sort_by_date_asc
        )
        # Aggiorna il testo del pulsante con freccia ↑/↓
        self.sort_date_button.config(
            text=f"Ordina per Data {'↑' if self.sort_by_date_asc else '↓'}"
        )
        self.update_video_list()

    # Ordina i video per dimensione (clic alterna crescente/decrescente)
    def sort_by_size(self):
        self.sort_by_size_asc = not self.sort_by_size_asc  # Inverti lo stato
        self.filtered_files.sort(
            key=lambda x: os.path.getsize(x[1]),
            reverse=not self.sort_by_size_asc
        )
        # Aggiorna il testo del pulsante con freccia ↑/↓
        self.sort_size_button.config(
            text=f"Ordina per Dimensione {'↑' if self.sort_by_size_asc else '↓'}"
        )
        self.update_video_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
