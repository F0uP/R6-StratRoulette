# Rainbow Six Siege Strat Roulette

🎲 A handy desktop app to randomly select attack, defense, or both strategies for Rainbow Six Siege — complete with global hotkeys and easy configuration.

---

## Features

- Load strategies from a built-in CSV file (no setup needed).
- Random roll buttons for **Attacker**, **Defender**, and **Both** roles.
- Configurable global hotkeys with support for modifier keys (Ctrl, Alt, Shift).
- Persistent settings including hotkeys, window position, and last-used configurations.
- Dark-themed PyQt5 interface.
- Reset hotkeys to defaults with a single click.
- Small and lightweight, Windows-only.

---

## Installation

1. Clone or download this repository:

   ```bash
   git clone https://github.com/F0uP/R6-StratRoulette.git
   cd r6-strat-roulette
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

---

## Packaging as Executable
To create a standalone .exe with pyinstaller including the CSV and icon files:
   ```bash
   pyinstaller --onefile --windowed --add-data "strats.csv;." --add-data "icon.ico;." main.py
   ```

---

## Usage

- Click the buttons to roll a random strat for Attacker, Defender, or Both.

- Open Settings → Hotkeys to customize hotkeys and their modifiers.

- Global hotkeys work even when the app is in the background.

- Use Reset to Defaults in hotkey settings to restore original keybindings.

---

## CSV Format
The `strats.csv` file should have the following columns (without headers):
   ```csv
   StratID,Role,StratName,StratContent
   ```

- Role: `Attacker`, `Defender` or `Both`

---

## Configuration
Settings like hotkeys and window position are saved automatically and loaded on startup.

---

## Contribution
Feel free to open issues or submit pull requests, especially on new strats!

---

## License
MIT License © F0uP