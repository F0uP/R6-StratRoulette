import sys
import random
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox, QShortcut
)
from PyQt5.QtGui import QFont, QKeySequence, QIcon
from PyQt5.QtCore import Qt


def resource_path(relative_path):
    """ Holt den absoluten Pfad zu Ressourcen (CSV, ICO), auch wenn gebundelt """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
CSV_FILE = resource_path("strats.csv")
ICON_FILE = resource_path("icon.ico")

class StratRoulette(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rainbow 6: Strat Roulette")
        self.setWindowIcon(QIcon(ICON_FILE))
        self.setGeometry(100, 100, 500, 350)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2c2c2c;
                border: 2px solid #444;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 2px solid #0078d7;
            }
            QLabel#title {
                font-size: 22px;
                font-weight: bold;
                color: #00ffcc;
            }
            QLabel#content {
                font-size: 16px;
                color: #dddddd;
            }
        """)

        # Lade die CSV-Daten
        try:
            self.strats = pd.read_csv(CSV_FILE)
        except FileNotFoundError:
            QMessageBox.critical(self, "Fehler", f"Die Datei {CSV_FILE} wurde nicht gefunden!")
            sys.exit(1)

        # UI Elemente
        self.label_name = QLabel("Rainbow Six Siege Strat Roulette")
        self.label_name.setObjectName("title")
        self.label_name.setAlignment(Qt.AlignCenter)

        self.label_content = QLabel("Drücke einen Button oder F1/F2 zum Rollen")
        self.label_content.setObjectName("content")
        self.label_content.setAlignment(Qt.AlignCenter)
        self.label_content.setWordWrap(True)

        self.btn_attacker = QPushButton("🎲 Roll for Attacker")
        self.btn_attacker.clicked.connect(lambda: self.roll_strat("Attacker"))

        self.btn_defender = QPushButton("🎯 Roll for Defender")
        self.btn_defender.clicked.connect(lambda: self.roll_strat("Defender"))

        # Shortcuts (Hotkeys)
        self.shortcut_attacker = QShortcut(QKeySequence("F1"), self)
        self.shortcut_attacker.activated.connect(lambda: self.roll_strat("Attacker"))

        self.shortcut_defender = QShortcut(QKeySequence("F2"), self)
        self.shortcut_defender.activated.connect(lambda: self.roll_strat("Defender"))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_name)
        layout.addSpacing(15)
        layout.addWidget(self.label_content)
        layout.addSpacing(20)
        layout.addWidget(self.btn_attacker)
        layout.addWidget(self.btn_defender)
        layout.setSpacing(10)
        self.setLayout(layout)

    def roll_strat(self, role):
        # Alle relevanten Strats für die Rolle holen
        filtered_strats = self.strats[
            (self.strats["DefOAtkStrat"].str.lower() == role.lower()) |
            (self.strats["DefOAtkStrat"].str.lower() == "both")
        ]

        if filtered_strats.empty:
            self.label_name.setText("⚠️ Keine Strat gefunden")
            self.label_content.setText(f"Keine Strats für {role} verfügbar.")
            return

        strat = filtered_strats.sample(1).iloc[0]
        self.label_name.setText(f"{strat['StratName']} ({strat['DefOAtkStrat']})")
        self.label_content.setText(strat['StratContent'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StratRoulette()
    window.show()
    sys.exit(app.exec_())