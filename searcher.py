import os
import json
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy,
    QHeaderView, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPalette


# Palette (stile Radarr / Sonarr)

BG_APP       = "#0d0d0f"      # sfondo globale
BG_SIDEBAR   = "#111116"      # sidebar sinistra
BG_HEADER    = "#111116"      # header top
BG_CARD      = "#18181f"      # card / pannelli
BG_INPUT     = "#1f1f2b"      # input fields
BG_ROW_ALT   = "#1a1a24"      # righe alternate tabella

ACCENT       = "#7b68ee"      # viola Arr (SlateBlue)
ACCENT_HOVER = "#9d8fff"
ACCENT_DIM   = "#3d3566"

TEXT_PRIMARY = "#e8e8f0"
TEXT_MUTED   = "#7a7a9a"
TEXT_BADGE   = "#ffffff"

BORDER       = "#2a2a3a"
DANGER       = "#e05c5c"
SUCCESS      = "#4caf82"


STYLESHEET = f"""
/* Global */
QMainWindow, QWidget {{
    background: {BG_APP};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}

/* Sidebar */
#Sidebar {{
    background: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
    min-width: 200px;
    max-width: 200px;
}}

/* Sidebar buttons */
#SideBtn {{
    background: transparent;
    color: {TEXT_MUTED};
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
}}
#SideBtn:hover {{
    background: {BG_INPUT};
    color: {TEXT_PRIMARY};
}}
#SideBtn[active=true] {{
    background: {ACCENT_DIM};
    color: {ACCENT_HOVER};
    font-weight: bold;
}}

/* Header */
#Header {{
    background: {BG_HEADER};
    border-bottom: 1px solid {BORDER};
    min-height: 54px;
    max-height: 54px;
}}
#AppTitle {{
    color: {ACCENT_HOVER};
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 1px;
}}
#BadgeTotal {{
    background: {ACCENT_DIM};
    color: {ACCENT_HOVER};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: bold;
}}
#BadgeFiltered {{
    background: {SUCCESS};
    color: #fff;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: bold;
}}

/* Search bar */
#SearchBar {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 6px 14px;
    font-size: 14px;
    selection-background-color: {ACCENT_DIM};
}}
#SearchBar:focus {{
    border: 1px solid {ACCENT};
}}

/* Pulsanti azione */
#BtnPrimary {{
    background: {ACCENT};
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: bold;
}}
#BtnPrimary:hover {{
    background: {ACCENT_HOVER};
}}
#BtnSecondary {{
    background: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 14px;
}}
#BtnSecondary:hover {{
    border-color: {ACCENT};
    color: {ACCENT_HOVER};
}}
#BtnDanger {{
    background: transparent;
    color: {DANGER};
    border: 1px solid {DANGER};
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
}}
#BtnDanger:hover {{
    background: {DANGER};
    color: #fff;
}}

/* Tabella video */
QTableWidget {{
    background: {BG_CARD};
    alternate-background-color: {BG_ROW_ALT};
    border: none;
    gridline-color: {BORDER};
    selection-background-color: {ACCENT_DIM};
    selection-color: {TEXT_PRIMARY};
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {BORDER};
}}
QHeaderView::section {{
    background: {BG_SIDEBAR};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 10px;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
QHeaderView::section:hover {{
    color: {TEXT_PRIMARY};
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: {BG_APP};
    width: 7px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT_DIM};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 7px;
    background: {BG_APP};
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
}}

/* Pannello ricerche */
#RightPanel {{
    background: {BG_SIDEBAR};
    border-left: 1px solid {BORDER};
    min-width: 240px;
    max-width: 260px;
}}
#PanelTitle {{
    color: {TEXT_MUTED};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 14px 16px 4px 16px;
}}

/* Lista ricerche salvate */
#SavedList {{
    background: transparent;
    border: none;
    outline: none;
}}
#SavedList::item {{
    background: transparent;
    color: {TEXT_PRIMARY};
    border-radius: 6px;
    padding: 5px 8px;
    margin: 1px 6px;
}}
#SavedList::item:hover {{
    background: {BG_INPUT};
}}
#SavedList::item:selected {{
    background: {ACCENT_DIM};
    color: {ACCENT_HOVER};
}}

/* Input ricerche */
#SavedInput {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {TEXT_PRIMARY};
    padding: 5px 10px;
    font-size: 12px;
}}
#SavedInput:focus {{
    border-color: {ACCENT};
}}

/* Separatore */
#HSep {{
    background: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}

/* Status bar */
QStatusBar {{
    background: {BG_SIDEBAR};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
    font-size: 11px;
}}
"""


# Thread scansione (non blocca la UI)

class ScanThread(QThread):
    progress   = pyqtSignal(str)
    finished   = pyqtSignal(list, dict)

    SSD_PATHS  = ["F:/"]
    FORMATS    = (".mp4", ".mkv", ".avi", ".mov")

    def run(self):
        videos   = []
        metadata = {}

        for ssd in self.SSD_PATHS:
            if not os.path.exists(ssd):
                self.progress.emit(f"Percorso non trovato: {ssd}")
                continue

            for root_dir, _, files in os.walk(ssd):
                for file in files:
                    if file.lower().endswith(self.FORMATS):
                        full_path = os.path.join(root_dir, file)
                        videos.append((file, full_path))
                        try:
                            metadata[full_path] = {
                                "size":  os.path.getsize(full_path),
                                "mtime": os.path.getmtime(full_path),
                            }
                        except Exception:
                            metadata[full_path] = {"size": 0, "mtime": 0}

        self.progress.emit(f"Trovati {len(videos)} file.")
        self.finished.emit(videos, metadata)


# Main window

class SearcherMark3(QMainWindow):

    CACHE_FILE = "video_cache.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Searcher  ·  Mark 4")
        self.resize(1420, 820)

        self.video_files    = []
        self.filtered_files = []
        self.video_metadata = {}
        self.saved_words    = {}

        self.sort_col       = -1
        self.sort_asc       = True

        self._build_ui()
        self.load_cache()

    # Build UI

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("Header")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 0, 20, 0)
        h_lay.setSpacing(12)

        logo = QLabel("◈  SEARCHER")
        logo.setObjectName("AppTitle")
        h_lay.addWidget(logo)

        self.badge_total = QLabel("0 totali")
        self.badge_total.setObjectName("BadgeTotal")
        h_lay.addWidget(self.badge_total)

        self.badge_filtered = QLabel("0 risultati")
        self.badge_filtered.setObjectName("BadgeFiltered")
        h_lay.addWidget(self.badge_filtered)

        h_lay.addStretch()

        # Search bar in header
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("🔍  Cerca per nome…")
        self.search_bar.setFixedWidth(360)
        self.search_bar.textChanged.connect(self.search_videos)
        h_lay.addWidget(self.search_bar)

        root_layout.addWidget(header)

        # Body (sidebar + content + right panel)
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        body_lay.addWidget(self._build_sidebar())
        body_lay.addWidget(self._build_content(), 1)
        body_lay.addWidget(self._build_right_panel())

        root_layout.addWidget(body, 1)

        # Status bar
        self.statusBar().showMessage("  Pronto  —  carica la cache o scansiona l'SSD")

    # Sidebar

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(10, 16, 10, 16)
        lay.setSpacing(4)

        mark_label = QLabel("MARK III")
        mark_label.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; letter-spacing:2px; padding-left:6px;")
        lay.addWidget(mark_label)

        self._add_sep(lay)

        self.btn_scan = self._sidebar_btn("⟳   Scansiona SSD", self.start_scan)
        lay.addWidget(self.btn_scan)

        self.btn_sort_date = self._sidebar_btn("↕   Ordina per Data", self.sort_by_date)
        lay.addWidget(self.btn_sort_date)

        self.btn_sort_size = self._sidebar_btn("↕   Ordina per Dimensione", self.sort_by_size)
        lay.addWidget(self.btn_sort_size)

        lay.addStretch()
        self._add_sep(lay)

        ver = QLabel("Mark 4  ·  PyQt6")
        ver.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; padding:6px;")
        lay.addWidget(ver)

        return sidebar

    def _sidebar_btn(self, text, slot):
        btn = QPushButton(text)
        btn.setObjectName("SideBtn")
        btn.setProperty("active", False)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def _add_sep(self, layout):
        sep = QFrame()
        sep.setObjectName("HSep")
        layout.addWidget(sep)

    # Content (tabella video)

    def _build_content(self):
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["PERCORSO", "DIMENSIONE"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(False)
        self.table.doubleClicked.connect(self.play_video)
        self.table.horizontalHeader().sectionClicked.connect(self.header_clicked)

        lay.addWidget(self.table)
        return widget

    # Right panel (ricerche salvate)

    def _build_right_panel(self):
        panel = QFrame()
        panel.setObjectName("RightPanel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 12)
        lay.setSpacing(6)

        title = QLabel("RICERCHE SALVATE")
        title.setObjectName("PanelTitle")
        lay.addWidget(title)

        self._add_sep(lay)

        # Input + aggiungi
        input_row = QHBoxLayout()
        input_row.setContentsMargins(8, 8, 8, 0)
        input_row.setSpacing(6)
        self.saved_input = QLineEdit()
        self.saved_input.setObjectName("SavedInput")
        self.saved_input.setPlaceholderText("es. vacanze 2023")
        self.saved_input.returnPressed.connect(self.add_saved_word)
        input_row.addWidget(self.saved_input, 1)

        btn_add = QPushButton("+")
        btn_add.setObjectName("BtnPrimary")
        btn_add.setFixedSize(30, 30)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.add_saved_word)
        input_row.addWidget(btn_add)
        lay.addLayout(input_row)

        # Lista
        self.saved_list = QListWidget()
        self.saved_list.setObjectName("SavedList")
        self.saved_list.itemDoubleClicked.connect(self.search_from_saved)
        lay.addWidget(self.saved_list, 1)

        # Pulsante elimina
        btn_del = QPushButton("✕  Elimina selezionata")
        btn_del.setObjectName("BtnDanger")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(self.delete_saved_word)

        del_row = QHBoxLayout()
        del_row.setContentsMargins(8, 0, 8, 0)
        del_row.addWidget(btn_del)
        lay.addLayout(del_row)

        hint = QLabel("doppio click = cerca")
        hint.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; padding: 0 10px;")
        lay.addWidget(hint)

        return panel

    # Cache

    def load_cache(self):
        if not os.path.exists(self.CACHE_FILE):
            self.statusBar().showMessage("  Cache non trovata — scansiona l'SSD per iniziare")
            return
        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.video_files    = [(v["name"], v["path"]) for v in data["videos"]]
            self.filtered_files = self.video_files.copy()
            self.video_metadata = data.get("video_metadata", {})

            # Compatibile con vecchio e nuovo formato JSON
            saved = data.get("saved_words", {})
            self.saved_words = {}
            if isinstance(saved, dict):
                words_list = list(saved.keys())
            elif isinstance(saved, list):
                words_list = saved
            else:
                words_list = []

            for word in words_list:
                # Ricalcola il conteggio dai file attuali
                self.saved_words[word] = self._count_files_for_term(word)

            self.refresh_table()
            self.refresh_saved_list()
            self._update_badges()
            self.statusBar().showMessage(f"  Cache caricata  ·  {len(self.video_files)} file")
        except Exception as e:
            self.statusBar().showMessage(f"  Errore cache: {e}")

    def save_cache(self):
        data = {
            "videos": [{"name": n, "path": p} for n, p in self.video_files],
            "video_metadata": self.video_metadata,
            "saved_words": self.saved_words,
        }
        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Scansione

    def start_scan(self):
        self.btn_scan.setText("⟳   Scansione in corso…")
        self.btn_scan.setEnabled(False)
        self.statusBar().showMessage("  Scansione SSD in corso…")

        self._scan_thread = ScanThread()
        self._scan_thread.progress.connect(lambda m: self.statusBar().showMessage(f"  {m}"))
        self._scan_thread.finished.connect(self.on_scan_done)
        self._scan_thread.start()

    def on_scan_done(self, videos, metadata):
        self.video_files    = videos
        self.video_metadata = metadata
        self.filtered_files = videos.copy()

        for word in self.saved_words:
            self.saved_words[word] = self._count_files_for_term(word)

        self.refresh_table()
        self.refresh_saved_list()
        self._update_badges()
        self.save_cache()

        self.btn_scan.setText("⟳   Scansiona SSD")
        self.btn_scan.setEnabled(True)
        self.statusBar().showMessage(f"  Scansione completata  ·  {len(self.video_files)} file trovati")

    # Ricerca

    def search_videos(self, text=""):
        text = self.search_bar.text().lower().strip()
        terms = text.split() if text else []

        if not terms:
            self.filtered_files = self.video_files.copy()
        else:
            self.filtered_files = [
                (n, p) for n, p in self.video_files
                if all(t in n.lower() for t in terms)
            ]

        self.refresh_table()
        self._update_badges()

    # Tabella

    def refresh_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.filtered_files))

        for row, (name, path) in enumerate(self.filtered_files):
            meta = self.video_metadata.get(path, {})
            size = self._fmt_size(meta.get("size", 0))

            item_path = QTableWidgetItem(path)
            item_size = QTableWidgetItem(size)
            item_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_size.setForeground(QColor(TEXT_MUTED))

            self.table.setItem(row, 0, item_path)
            self.table.setItem(row, 1, item_size)

        self.table.setRowHeight

    def _update_badges(self):
        self.badge_total.setText(f"{len(self.video_files):,} totali")
        self.badge_filtered.setText(f"{len(self.filtered_files):,} risultati")

    def header_clicked(self, col):
        if self.sort_col == col:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_col = col
            self.sort_asc = True

        if col == 0:
            self.filtered_files.sort(key=lambda x: x[1].lower(), reverse=not self.sort_asc)
        elif col == 1:
            self.filtered_files.sort(
                key=lambda x: self.video_metadata.get(x[1], {}).get("size", 0),
                reverse=not self.sort_asc
            )
        self.refresh_table()

    # ORDINAMENTO (sidebar)

    def sort_by_date(self):
        self.sort_asc = not self.sort_asc
        self.filtered_files.sort(
            key=lambda x: self.video_metadata.get(x[1], {}).get("mtime", 0),
            reverse=not self.sort_asc
        )
        arrow = "↑" if self.sort_asc else "↓"
        self.btn_sort_date.setText(f"{arrow}   Ordina per Data")
        self.refresh_table()

    def sort_by_size(self):
        self.sort_asc = not self.sort_asc
        self.filtered_files.sort(
            key=lambda x: self.video_metadata.get(x[1], {}).get("size", 0),
            reverse=not self.sort_asc
        )
        arrow = "↑" if self.sort_asc else "↓"
        self.btn_sort_size.setText(f"{arrow}   Ordina per Dimensione")
        self.refresh_table()

    # Play

    def play_video(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_files):
            path = self.filtered_files[row][1]
            os.startfile(path)

    # Ricerche salvate

    def _count_files_for_term(self, term):
        terms = term.lower().split()
        return sum(
            1 for name, _ in self.video_files
            if all(t in name.lower() for t in terms)
        )

    def add_saved_word(self):
        word = self.saved_input.text().strip().lower()
        if not word:
            return
        self.saved_words[word] = self._count_files_for_term(word)
        self.saved_input.clear()
        self.refresh_saved_list()
        self.save_cache()
        self.statusBar().showMessage(f"  Aggiunto: '{word}'  ·  {self.saved_words[word]} file")

    def delete_saved_word(self):
        item = self.saved_list.currentItem()
        if not item:
            return
        word = item.data(Qt.ItemDataRole.UserRole)
        if word and word in self.saved_words:
            del self.saved_words[word]
            self.refresh_saved_list()
            self.save_cache()
            self.statusBar().showMessage(f"  Rimosso: '{word}'")

    def search_from_saved(self, item):
        word = item.data(Qt.ItemDataRole.UserRole)
        if word:
            self.search_bar.setText(word)
            self.search_videos()

    def refresh_saved_list(self):
        self.saved_list.clear()
        for word, count in sorted(self.saved_words.items(), key=lambda x: x[1], reverse=True):
            # Badge conteggio inline nel testo
            badge = f"[{count}]"
            display = f"  {word}"
            item = QListWidgetItem(f"{display}   {badge}")
            item.setData(Qt.ItemDataRole.UserRole, word)
            item.setForeground(QColor(TEXT_PRIMARY))
            # badge color
            item.setToolTip(f"{count} file trovati per '{word}'")
            self.saved_list.addItem(item)

    # Utility

    @staticmethod
    def _fmt_size(b):
        if b < 1024:
            return f"{b} B"
        elif b < 1024 ** 2:
            return f"{b/1024:.1f} KB"
        elif b < 1024 ** 3:
            return f"{b/1024**2:.2f} MB"
        elif b < 1024 ** 4:
            return f"{b/1024**3:.2f} GB"
        else:
            return f"{b/1024**4:.2f} TB"


# Entry point

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    window = SearcherMark3()
    window.show()

    sys.exit(app.exec())
