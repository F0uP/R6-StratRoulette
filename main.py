import sys
import random
import json
import os
import pandas as pd
import win32con
import win32gui
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox,
    QComboBox, QDialog, QFormLayout, QDialogButtonBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import threading

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CSV_FILE = resource_path("strats.csv")
ICON_FILE = resource_path("icon.ico")
CONFIG_FILE = "config.json"

DEFAULT_HOTKEYS = {
    "Attacker": win32con.VK_F1,
    "Defender": win32con.VK_F2,
    "Both": win32con.VK_F3
}

DEFAULT_WINDOW_GEOMETRY = (100, 100, 500, 300)  # x, y, w, h

WM_APP_RELOAD_HOTKEYS = win32con.WM_APP + 1

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback Defaults
    return {
        "hotkeys": DEFAULT_HOTKEYS.copy(),
        "window_geometry": DEFAULT_WINDOW_GEOMETRY
    }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# Globale Config
config = load_config()
hotkeys = config.get("hotkeys", DEFAULT_HOTKEYS.copy())
window_geometry = config.get("window_geometry", DEFAULT_WINDOW_GEOMETRY)

class StratRoulette(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rainbow Six Siege Strat Roulette")
        self.setWindowIcon(QIcon(ICON_FILE))

        # Fensterposition/-größe laden
        x, y, w, h = window_geometry
        self.setGeometry(x, y, w, h)

        font_title = QFont("Arial", 16, QFont.Bold)
        font_content = QFont("Arial", 12)

        self.label_name = QLabel("🎲 Strat Name erscheint hier")
        self.label_name.setFont(font_title)
        self.label_name.setAlignment(Qt.AlignCenter)

        self.label_content = QLabel("📜 Strat Beschreibung erscheint hier")
        self.label_content.setFont(font_content)
        self.label_content.setAlignment(Qt.AlignCenter)
        self.label_content.setWordWrap(True)

        self.btn_attacker = QPushButton()
        self.btn_defender = QPushButton()
        self.btn_both = QPushButton()

        self.update_button_labels()

        self.btn_attacker.clicked.connect(lambda: self.roll_strat("Attacker"))
        self.btn_defender.clicked.connect(lambda: self.roll_strat("Defender"))
        self.btn_both.clicked.connect(lambda: self.roll_strat("Both"))

        btn_configure = QPushButton("🎛️ Hotkeys konfigurieren")
        btn_configure.clicked.connect(self.open_hotkey_config)

        layout = QVBoxLayout()
        layout.addWidget(self.label_name)
        layout.addWidget(self.label_content)
        layout.addWidget(self.btn_attacker)
        layout.addWidget(self.btn_defender)
        layout.addWidget(self.btn_both)
        layout.addWidget(btn_configure)
        self.setLayout(layout)

        self.load_strats()

    def closeEvent(self, event):
        # Fensterposition/-größe speichern beim Schließen
        geom = self.geometry()
        config["window_geometry"] = (geom.x(), geom.y(), geom.width(), geom.height())
        config["hotkeys"] = hotkeys
        save_config(config)
        super().closeEvent(event)

    def update_button_labels(self):
        self.btn_attacker.setText(f"Roll for Attacker ({self.key_name(hotkeys['Attacker'])})")
        self.btn_defender.setText(f"Roll for Defender ({self.key_name(hotkeys['Defender'])})")
        self.btn_both.setText(f"Roll for Both ({self.key_name(hotkeys['Both'])})")

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

    def open_hotkey_config(self):
        dialog = HotkeyConfigDialog(self)
        if dialog.exec_():
            # Speichern und Hotkeys aktualisieren
            save_config(config)
            self.update_button_labels()
            if hotkey_hwnd:
                win32gui.PostMessage(hotkey_hwnd, WM_APP_RELOAD_HOTKEYS, 0, 0)

    def key_name(self, vk_code):
        for name in dir(win32con):
            if name.startswith("VK_") and getattr(win32con, name) == vk_code:
                return name.replace("VK_", "")
        # Fallback falls nicht gefunden
        return f"KeyCode({vk_code})"

class HotkeyConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎛️ Hotkeys konfigurieren")
        self.setWindowIcon(QIcon(ICON_FILE))

        self.parent = parent

        layout = QFormLayout()
        self.combo_boxes = {}

        keys = self.available_keys()

        for role in ["Attacker", "Defender", "Both"]:
            combo = QComboBox()
            combo.addItems(keys)
            current_key = parent.key_name(hotkeys[role])
            if current_key in keys:
                combo.setCurrentText(current_key)
            combo.currentTextChanged.connect(lambda text, r=role: self.set_hotkey(r, text))
            self.combo_boxes[role] = combo
            layout.addRow(f"{role} Hotkey:", combo)

        btn_reset = QPushButton("Reset to Defaults")
        btn_reset.clicked.connect(self.reset_defaults)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        hlayout = QHBoxLayout()
        hlayout.addWidget(btn_reset)
        hlayout.addStretch()
        hlayout.addWidget(buttons)

        layout.addRow(hlayout)

        self.setLayout(layout)

    def available_keys(self):
        keys = [f"F{i}" for i in range(1, 13)]  # F1–F12
        keys += [chr(k) for k in range(ord('A'), ord('Z')+1)]  # A–Z
        keys += [str(n) for n in range(0, 10)]  # 0–9
        return keys

    def set_hotkey(self, role, key):
        vk = self.key_to_vk(key)
        if vk:
            hotkeys[role] = vk
            config["hotkeys"] = hotkeys

    def key_to_vk(self, key):
        if key.startswith("F") and key[1:].isdigit():
            fkey = int(key[1:])
            return getattr(win32con, f"VK_F{fkey}", None)
        elif len(key) == 1 and key.isalpha():
            return ord(key.upper())
        elif key.isdigit():
            return ord(key)
        return None

    def reset_defaults(self):
        global hotkeys, config
        hotkeys = DEFAULT_HOTKEYS.copy()
        config["hotkeys"] = hotkeys
        # ComboBoxes zurücksetzen
        for role, combo in self.combo_boxes.items():
            combo.setCurrentText(self.parent.key_name(hotkeys[role]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StratRoulette()
    window.show()

    # Hotkey-Listener Thread
    def hotkey_listener(app_instance):
        global hotkey_hwnd

        def win_proc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_HOTKEY:
                if wparam == 1:
                    app_instance.roll_strat("Attacker")
                elif wparam == 2:
                    app_instance.roll_strat("Defender")
                elif wparam == 3:
                    app_instance.roll_strat("Both")
            elif msg == WM_APP_RELOAD_HOTKEYS:
                unregister_hotkeys()
                register_hotkeys()
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = win_proc
        wc.lpszClassName = "HiddenHotkeyWindow"
        class_atom = win32gui.RegisterClass(wc)
        hotkey_hwnd = win32gui.CreateWindow(
            class_atom, "HiddenHotkeyWindow", 0,
            0, 0, 0, 0, 0, 0, 0, None
        )

        register_hotkeys()
        win32gui.PumpMessages()

    def register_hotkeys():
        win32gui.RegisterHotKey(hotkey_hwnd, 1, 0, hotkeys["Attacker"])
        win32gui.RegisterHotKey(hotkey_hwnd, 2, 0, hotkeys["Defender"])
        win32gui.RegisterHotKey(hotkey_hwnd, 3, 0, hotkeys["Both"])

    def unregister_hotkeys():
        for id in (1, 2, 3):
            try:
                win32gui.UnregisterHotKey(hotkey_hwnd, id)
            except Exception:
                pass

    threading.Thread(target=hotkey_listener, args=(window,), daemon=True).start()
    sys.exit(app.exec_())
