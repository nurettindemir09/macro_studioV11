# Macro Studio Pro ⚡

Powerful, high-precision automation tool designed for gamers and productivity enthusiasts. Manage multiple macro profiles concurrently with ease.

## ✨ Key Features

- **Global Multi-Macro System**: All saved profiles are active simultaneously. Trigger separate macros with different hotkeys without switching.
- **Precision Timing**: Millisecond-accurate relative delay system.
- **Key Hold & Repetition**: Support for timed key presses and per-event loop counts.
- **Portable & Persistent**: Profiles are saved safely in your system's AppData to prevent data loss.
- **Modern UI**: Dark-themed, responsive interface with a scrollable step builder.
- **Custom Branding**: Created by [nurettindemir09](https://github.com/nurettindemir09).

## 🚀 Installation (Direct Setup)

No coding knowledge required! Follow these steps to get started:

1. **Download the Installer**: Go to the [Releases](https://github.com/nurettindemir09/macro_studioV11/releases) page (if available) or download the `setup` folder.
2. **Run Setup**: Open `MacroStudioPro_Setup.exe`.
3. **Follow the Wizard**: Click Next, Next, and Finish.
4. **Custom Greeting**: Look out for the special greeting from Nurettin Demir at the end! 🌩️
5. **Start Using**: Launch from the Desktop shortcut or Start Menu.

## 🛠️ Developer Installation (From Source)

1. **Clone**: `git clone https://github.com/nurettindemir09/macro_studioV11.git`
2. **Setup Venv**: `python -m venv .venv` and activate it.
3. **Dependencies**: `pip install customtkinter pynput Pillow`
4. **Run**: `python macro.py`
5. **Build EXE**: `pyinstaller --noconsole --onefile --clean --icon=macro.ico macro.py`

## 🎮 Usage Guide

1. **New Macro**: Click `+ START NEW MACRO` to begin.
2. **Record**: Press `F9` to capture real-time actions.
3. **Add Steps**: Manually add clicks, keys, or holds using the Builder.
4. **Save**: Enter a profile name, choose a hotkey, and click `SAVE / UPDATE`.
5. **Trigger**: Use your hotkey globally while the app is in the background.

## 📜 License
MIT License.
