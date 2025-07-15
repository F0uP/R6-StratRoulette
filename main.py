import sys
import random
import pandas as pd
import win32con
import win32gui
import win32api
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import threading
import os

# Hilfsfunktion für Ressourcen
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CSV_FILE = resource_path("strats.csv")
ICON_FILE = resource_path("icon.ico")

class StratRoulette(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rainbow Six Siege: Strat Roulette")
        self.setWindowIcon(QIcon(ICON_FILE))
        self.setGeometry(100, 100, 500, 300)

        font_title = QFont("Arial", 16, QFont.Bold)
        font_content = QFont("Arial", 12)

        self.label_name = QLabel("🎲 Strat Name erscheint hier")
        self.label_name.setFont(font_title)
        self.label_name.setAlignment(Qt.AlignCenter)

        self.label_content = QLabel("📜 Strat Beschreibung erscheint hier")
        self.label_content.setFont(font_content)
        self.label_content.setAlignment(Qt.AlignCenter)
        self.label_content.setWordWrap(True)

        btn_attacker = QPushButton("Roll for Attacker (F1)")
        btn_attacker.clicked.connect(lambda: self.roll_strat("Attacker"))

        btn_defender = QPushButton("Roll for Defender (F2)")
        btn_defender.clicked.connect(lambda: self.roll_strat("Defender"))

        layout = QVBoxLayout()
        layout.addWidget(self.label_name)
        layout.addWidget(self.label_content)
        layout.addWidget(btn_attacker)
        layout.addWidget(btn_defender)
        self.setLayout(layout)

        self.load_strats()

    def load_strats(self):
        try:
            self.strats = pd.read_csv(CSV_FILE)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"CSV konnte nicht geladen werden:\n{e}")
            sys.exit(1)

    def roll_strat(self, role):
        filtered = self.strats[
            (self.strats["DefOAtkStrat"].str.lower() == role.lower()) |
            (self.strats["DefOAtkStrat"].str.lower() == "both")
        ]
        if filtered.empty:
            self.label_name.setText("⚠️ Keine Strat gefunden")
            self.label_content.setText(f"Keine Strats für {role} verfügbar.")
            return

        strat = filtered.sample(1).iloc[0]
        self.label_name.setText(f"{strat['StratName']} ({strat['DefOAtkStrat']})")
        self.label_content.setText(strat['StratContent'])

# 🔥 Funktion für das unsichtbare Hotkey-Fenster
def hotkey_listener(app_instance):
    def win_proc(hwnd, msg, wparam, lparam):
        if msg == win32con.WM_HOTKEY:
            if wparam == 1:  # F1
                app_instance.roll_strat("Attacker")
            elif wparam == 2:  # F2
                app_instance.roll_strat("Defender")
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = win_proc
    wc.lpszClassName = "HiddenHotkeyWindow"
    class_atom = win32gui.RegisterClass(wc)
    hwnd = win32gui.CreateWindow(
        class_atom,
        "HiddenHotkeyWindow",
        0,
        0, 0, 0, 0,
        0, 0, 0, None
    )

    # Hotkeys registrieren
    win32gui.RegisterHotKey(hwnd, 1, 0, win32con.VK_F1)
    win32gui.RegisterHotKey(hwnd, 2, 0, win32con.VK_F2)

    win32gui.PumpMessages()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StratRoulette()
    window.show()

    # 🔥 Start Hotkey-Thread
    threading.Thread(target=hotkey_listener, args=(window,), daemon=True).start()

    sys.exit(app.exec_())
