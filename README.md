# Antigravity Macro Studio Pro 🚀

A powerful, high-precision automation tool built with Python and CustomTkinter. Designed for gamers and productivity enthusiasts who need reliable, concurrent macro management.

## ✨ Key Features

- **Global Multi-Macro System**: All saved profiles are active simultaneously. Trigger "Macro A" with `F1` and "Macro B" with `F2` without switching windows.
- **Precision Timing**: Uses a relative delay system (ms) for perfect execution accuracy.
- **Key Hold Support**: Record and playback timed key presses (e.g., hold 'W' for 2 seconds).
- **Event Repetition**: Loop individual steps (clicks or keys) multiple times with a single command.
- **Triple-Panel Interface**:
  - **Profiles**: Manage and persist macro sequences safely.
  - **Builder**: Manually construct steps with coordinates, delays, and repeats.
  - **Timeline**: Visual drag-and-drop-style sequence with full editability.
- **Universal Hotkeys**: Assign any key (F1-F12, Alphanumeric, Special keys like Tab/CapsLock) as a trigger.
- **Full Mouse Support**: Left, Right, and Double-click recording and manual entry.
- **Portable Profiles**: All macros are saved in a clean `profiles.json` format.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nurettindemir09/botForDso.git
   cd botForDso
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install customtkinter pynput
   ```

4. **Run the App**:
   ```bash
   python macro.py
   ```

## 🎮 Usage Guide

1. **Start New**: Click `+ START NEW MACRO` to unlock the editor.
2. **Record**: Press `F9` (default) to capture real-time mouse and keyboard actions.
3. **Build**: Use the Middle Panel to add specific coordinates or delays.
4. **Save**: Enter a profile name and select an activation hotkey, then hit `SAVE / UPDATE`.
5. **Execute**: Minimize the app and press your assigned hotkey!

## 📜 License
MIT License. Created by [nurettindemir09](https://github.com/nurettindemir09).
