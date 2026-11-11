import os
import sys
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem, QFrame, QHeaderView,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QColor, QDesktopServices

# Unità/cartelle da scansionare
DRIVES = ["F:/"]
VIDEO_EXT = (".mp4", ".mkv", ".avi", ".mov")
CACHE_FILE = "video_cache.json"

# colori (tema scuro, ispirato a Radarr/Sonarr)
BG_APP = "#0d0d0f"
BG_SIDE = "#111116"
BG_CARD = "#18181f"
BG_INPUT = "#1f1f2b"
BG_ROW_ALT = "#1a1a24"
ACCENT = "#7b68ee"
ACCENT_HOVER = "#9d8fff"
ACCENT_DIM = "#3d3566"
TEXT = "#e8e8f0"
TEXT_MUTED = "#7a7a9a"
BORDER = "#2a2a3a"
DANGER = "#e05c5c"
SUCCESS = "#4caf82"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {BG_APP}; color: {TEXT};
    font-family: "Segoe UI", sans-serif; font-size: 13px;
}}
#Sidebar {{ background: {BG_SIDE}; border-right: 1px solid {BORDER}; min-width: 200px; max-width: 200px; }}
#SideBtn {{
    background: transparent; color: {TEXT_MUTED}; border: none; border-radius: 6px;
    padding: 10px 16px; text-align: left;
}}
#SideBtn:hover {{ background: {BG_INPUT}; color: {TEXT}; }}

#Header {{ background: {BG_SIDE}; border-bottom: 1px solid {BORDER}; min-height: 54px; max-height: 54px; }}
#AppTitle {{ color: {ACCENT_HOVER}; font-size: 18px; font-weight: bold; letter-spacing: 1px; }}
#BadgeTotal {{ background: {ACCENT_DIM}; color: {ACCENT_HOVER}; border-radius: 10px; padding: 2px 10px; font-weight: bold; }}
#BadgeFiltered {{ background: {SUCCESS}; color: #fff; border-radius: 10px; padding: 2px 10px; font-weight: bold; }}

#SearchBar, #SavedInput {{
    background: {BG_INPUT}; border: 1px solid {BORDER}; border-radius: 8px;
    color: {TEXT}; padding: 6px 12px;
}}
#SearchBar:focus, #SavedInput:focus {{ border: 1px solid {ACCENT}; }}

#BtnPrimary {{ background: {ACCENT}; color: #fff; border: none; border-radius: 6px; font-weight: bold; }}
#BtnPrimary:hover {{ background: {ACCENT_HOVER}; }}
#BtnDanger {{ background: transparent; color: {DANGER}; border: 1px solid {DANGER}; border-radius: 6px; padding: 5px 12px; }}
#BtnDanger:hover {{ background: {DANGER}; color: #fff; }}

QTableWidget {{
    background: {BG_CARD}; alternate-background-color: {BG_ROW_ALT}; border: none;
    selection-background-color: {ACCENT_DIM}; selection-color: {TEXT};
}}
QTableWidget::item {{ padding: 6px 10px; }}
QHeaderView::section {{
    background: {BG_SIDE}; color: {TEXT_MUTED}; border: none;
    border-bottom: 1px solid {BORDER}; padding: 6px 10px; font-size: 11px;
}}

QScrollBar:vertical {{ background: {BG_APP}; width: 7px; border: none; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

#RightPanel {{ background: {BG_SIDE}; border-left: 1px solid {BORDER}; min-width: 240px; max-width: 260px; }}
#PanelTitle {{ color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 1px; padding: 14px 16px 4px 16px; }}
#SavedList {{ background: transparent; border: none; outline: none; }}
#SavedList::item {{ border-radius: 6px; padding: 5px 8px; margin: 1px 6px; }}
#SavedList::item:hover {{ background: {BG_INPUT}; }}
#SavedList::item:selected {{ background: {ACCENT_DIM}; color: {ACCENT_HOVER}; }}
#HSep {{ background: {BORDER}; max-height: 1px; min-height: 1px; }}

QStatusBar {{ background: {BG_SIDE}; color: {TEXT_MUTED}; border-top: 1px solid {BORDER}; font-size: 11px; }}
"""


def format_size(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return f"{size:.2f} TB"


def matches(name, terms):
    name = name.lower()
    return all(t in name for t in terms)


class ScanThread(QThread):
    """Scansione dei dischi in un thread separato, così la UI non si blocca."""
    progress = pyqtSignal(str)
    scan_finished = pyqtSignal(list, dict)
    scan_failed = pyqtSignal(str)

    def run(self):
        videos, metadata = [], {}
        try:
            for drive in DRIVES:
                if not os.path.isdir(drive):
                    self.progress.emit(f"Percorso non disponibile: {drive}")
                    continue
                for folder, _, files in os.walk(drive):
                    for f in files:
                        if not f.lower().endswith(VIDEO_EXT):
                            continue
                        path = os.path.join(folder, f)
                        try:
                            st = os.stat(path)
                        except OSError:
                            continue
                        videos.append((f, path))
                        metadata[path] = {"size": st.st_size, "mtime": st.st_mtime}
            self.scan_finished.emit(videos, metadata)
        except Exception as e:
            self.scan_failed.emit(str(e))


class Searcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Searcher · Mark 4")
        self.resize(1420, 820)

        self.video_files = []
        self.filtered_files = []
        self.metadata = {}
        self.saved_searches = {}
        self.sort_col = -1
        self.sort_asc = True

        self.build_ui()
        self.load_cache()

    # ---------- UI ----------

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.build_header())

        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)
        body_lay.addWidget(self.build_sidebar())
        body_lay.addWidget(self.build_table(), 1)
        body_lay.addWidget(self.build_saved_panel())
        layout.addWidget(body, 1)

        self.statusBar().showMessage("  Pronto — carica la cache o scansiona l'SSD")

    def build_header(self):
        header = QFrame()
        header.setObjectName("Header")
        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)

        title = QLabel("SEARCHER")
        title.setObjectName("AppTitle")
        lay.addWidget(title)

        self.badge_total = QLabel("0 totali")
        self.badge_total.setObjectName("BadgeTotal")
        lay.addWidget(self.badge_total)
        self.badge_filtered = QLabel("0 risultati")
        self.badge_filtered.setObjectName("BadgeFiltered")
        lay.addWidget(self.badge_filtered)
        lay.addStretch()

        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Cerca per nome...")
        self.search_bar.setFixedWidth(360)
        self.search_bar.textChanged.connect(self.search_videos)
        lay.addWidget(self.search_bar)
        return header

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(10, 16, 10, 16)
        lay.setSpacing(4)

        self.btn_scan = self.side_button("⟳   Scansiona SSD", self.start_scan)
        self.btn_date = self.side_button("↕   Ordina per Data", self.sort_by_date)
        self.btn_size = self.side_button("↕   Ordina per Dimensione", self.sort_by_size)
        for b in (self.btn_scan, self.btn_date, self.btn_size):
            lay.addWidget(b)
        lay.addStretch()

        ver = QLabel("Mark 4 · PyQt6")
        ver.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; padding:6px;")
        lay.addWidget(ver)
        return sidebar

    def side_button(self, text, slot):
        btn = QPushButton(text)
        btn.setObjectName("SideBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def build_table(self):
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["PERCORSO", "DIMENSIONE"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.sectionClicked.connect(self.header_clicked)
        self.table.setColumnWidth(1, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self.play_video)
        return self.table

    def build_saved_panel(self):
        panel = QFrame()
        panel.setObjectName("RightPanel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 12)
        lay.setSpacing(6)

        title = QLabel("RICERCHE SALVATE")
        title.setObjectName("PanelTitle")
        lay.addWidget(title)
        sep = QFrame()
        sep.setObjectName("HSep")
        lay.addWidget(sep)

        row = QHBoxLayout()
        row.setContentsMargins(8, 8, 8, 0)
        self.saved_input = QLineEdit()
        self.saved_input.setObjectName("SavedInput")
        self.saved_input.setPlaceholderText("es. vacanze 2023")
        self.saved_input.returnPressed.connect(self.add_saved_search)
        row.addWidget(self.saved_input, 1)
        btn_add = QPushButton("+")
        btn_add.setObjectName("BtnPrimary")
        btn_add.setFixedSize(30, 30)
        btn_add.clicked.connect(self.add_saved_search)
        row.addWidget(btn_add)
        lay.addLayout(row)

        self.saved_list = QListWidget()
        self.saved_list.setObjectName("SavedList")
        self.saved_list.itemDoubleClicked.connect(self.search_from_saved)
        lay.addWidget(self.saved_list, 1)

        btn_del = QPushButton("✕  Elimina selezionata")
        btn_del.setObjectName("BtnDanger")
        btn_del.clicked.connect(self.delete_saved_search)
        del_row = QHBoxLayout()
        del_row.setContentsMargins(8, 0, 8, 0)
        del_row.addWidget(btn_del)
        lay.addLayout(del_row)

        hint = QLabel("doppio click = cerca")
        hint.setStyleSheet(f"color:{TEXT_MUTED}; font-size:10px; padding: 0 10px;")
        lay.addWidget(hint)
        return panel

    # ---------- cache ----------

    def load_cache(self):
        if not os.path.exists(CACHE_FILE):
            self.statusBar().showMessage("  Cache non trovata — scansiona l'SSD per iniziare")
            return
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.video_files = [(v["name"], v["path"]) for v in data.get("videos", [])]
            self.metadata = data.get("video_metadata", {})
            self.filtered_files = self.video_files.copy()
            # compatibile sia con il vecchio formato (lista) che con il nuovo (dict)
            for s in data.get("saved_words", []):
                self.saved_searches[s] = self.count_matches(s)
            self.refresh_all()
            self.statusBar().showMessage(f"  Cache caricata · {len(self.video_files)} file")
        except (OSError, ValueError, KeyError, TypeError) as e:
            self.statusBar().showMessage(f"  Errore cache: {e}")

    def save_cache(self):
        data = {
            "videos": [{"name": n, "path": p} for n, p in self.video_files],
            "video_metadata": self.metadata,
            "saved_words": self.saved_searches,
        }
        tmp = CACHE_FILE + ".tmp"
        try:
            # scrivo prima su un file temporaneo per non corrompere la cache
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, CACHE_FILE)
        except OSError as e:
            self.statusBar().showMessage(f"  Impossibile salvare la cache: {e}")

    # ---------- scansione ----------

    def start_scan(self):
        self.btn_scan.setText("⟳   Scansione in corso...")
        self.btn_scan.setEnabled(False)
        self.scan_thread = ScanThread()
        self.scan_thread.progress.connect(lambda m: self.statusBar().showMessage(f"  {m}"))
        self.scan_thread.scan_finished.connect(self.on_scan_done)
        self.scan_thread.scan_failed.connect(self.on_scan_failed)
        self.scan_thread.start()

    def on_scan_done(self, videos, metadata):
        self.video_files = videos
        self.metadata = metadata
        self.filtered_files = videos.copy()
        for s in self.saved_searches:
            self.saved_searches[s] = self.count_matches(s)
        self.refresh_all()
        self.save_cache()
        self.reset_scan_button()
        self.statusBar().showMessage(f"  Scansione completata · {len(videos)} file trovati")

    def on_scan_failed(self, message):
        self.reset_scan_button()
        QMessageBox.warning(self, "Errore durante la scansione", message)

    def reset_scan_button(self):
        self.btn_scan.setText("⟳   Scansiona SSD")
        self.btn_scan.setEnabled(True)

    # ---------- ricerca e tabella ----------

    def search_videos(self):
        terms = self.search_bar.text().lower().split()
        self.filtered_files = [v for v in self.video_files if matches(v[0], terms)]
        self.refresh_table()
        self.update_badges()

    def refresh_all(self):
        self.refresh_table()
        self.refresh_saved_list()
        self.update_badges()

    def refresh_table(self):
        self.table.setRowCount(len(self.filtered_files))
        for row, (_, path) in enumerate(self.filtered_files):
            size_item = QTableWidgetItem(format_size(self.metadata.get(path, {}).get("size", 0)))
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            size_item.setForeground(QColor(TEXT_MUTED))
            self.table.setItem(row, 0, QTableWidgetItem(path))
            self.table.setItem(row, 1, size_item)

    def update_badges(self):
        self.badge_total.setText(f"{len(self.video_files):,} totali")
        self.badge_filtered.setText(f"{len(self.filtered_files):,} risultati")

    def sort_files(self, key):
        self.filtered_files.sort(key=lambda x: self.metadata.get(x[1], {}).get(key, 0),
                                 reverse=not self.sort_asc)

    def header_clicked(self, col):
        self.sort_asc = not self.sort_asc if self.sort_col == col else True
        self.sort_col = col
        if col == 0:
            self.filtered_files.sort(key=lambda x: x[1].lower(), reverse=not self.sort_asc)
        else:
            self.sort_files("size")
        self.refresh_table()

    def sort_by_date(self):
        self.sort_asc = not self.sort_asc
        self.sort_files("mtime")
        self.btn_date.setText(f"{'↑' if self.sort_asc else '↓'}   Ordina per Data")
        self.refresh_table()

    def sort_by_size(self):
        self.sort_asc = not self.sort_asc
        self.sort_files("size")
        self.btn_size.setText(f"{'↑' if self.sort_asc else '↓'}   Ordina per Dimensione")
        self.refresh_table()

    def play_video(self, index):
        row = index.row()
        if not 0 <= row < len(self.filtered_files):
            return
        path = self.filtered_files[row][1]
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File non disponibile", f"Il file non esiste:\n{path}")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(path)))

    # ---------- ricerche salvate ----------

    def count_matches(self, search):
        terms = search.lower().split()
        return sum(1 for name, _ in self.video_files if matches(name, terms))

    def add_saved_search(self):
        s = self.saved_input.text().strip().lower()
        if not s:
            return
        self.saved_searches[s] = self.count_matches(s)
        self.saved_input.clear()
        self.refresh_saved_list()
        self.save_cache()

    def delete_saved_search(self):
        item = self.saved_list.currentItem()
        if item:
            self.saved_searches.pop(item.data(Qt.ItemDataRole.UserRole), None)
            self.refresh_saved_list()
            self.save_cache()

    def search_from_saved(self, item):
        self.search_bar.setText(item.data(Qt.ItemDataRole.UserRole))

    def refresh_saved_list(self):
        self.saved_list.clear()
        for s, count in sorted(self.saved_searches.items(), key=lambda x: x[1], reverse=True):
            item = QListWidgetItem(f"  {s}   [{count}]")
            item.setData(Qt.ItemDataRole.UserRole, s)
            item.setToolTip(f"{count} file trovati per '{s}'")
            self.saved_list.addItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = Searcher()
    window.show()
    sys.exit(app.exec())
