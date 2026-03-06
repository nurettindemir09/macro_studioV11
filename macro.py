import time
import threading
import sys
import json
import os
import customtkinter as ctk
from pynput import mouse, keyboard
from pynput.keyboard import Key, Listener as KListener, KeyCode
from pynput.mouse import Button, Controller as MController, Listener as MListener

# Comprehensive mapping for special keys
SPECIAL_KEYS = {
    "F1": Key.f1, "F2": Key.f2, "F3": Key.f3, "F4": Key.f4,
    "F5": Key.f5, "F6": Key.f6, "F7": Key.f7, "F8": Key.f8,
    "F9": Key.f9, "F10": Key.f10, "F11": Key.f11, "F12": Key.f12,
    "Home": Key.home, "End": Key.end, "Insert": Key.insert, "Delete": Key.delete,
    "Space": Key.space, "Enter": Key.enter, "Tab": Key.tab, "CapsLock": Key.caps_lock,
    "Shift": Key.shift, "Ctrl": Key.ctrl, "Alt": Key.alt, "Esc": Key.esc
}

# Create a list of all available hotkey names for the dropdown
HOTKEY_OPTIONS = (
    [f"F{i}" for i in range(1, 13)] +
    [chr(i) for i in range(ord('a'), ord('z') + 1)] +
    [str(i) for i in range(10)] +
    ["Tab", "CapsLock", "Space", "Enter", "Shift", "Ctrl", "Alt", "Esc"]
)

PROFILES_FILE = "profiles.json"

class EventRow(ctk.CTkFrame):
    def __init__(self, master, event_id, event_type, value, delay_ms, hold_ms=0, repeat=1, on_delete=None, on_move=None, on_clone=None, **kwargs):
        super().__init__(master, **kwargs)
        self.event_type = event_type
        self.on_delete = on_delete
        self.on_move = on_move
        self.on_clone = on_clone
        
        # Order / Move Buttons
        self.move_frame = ctk.CTkFrame(self, fg_color="transparent", width=40)
        self.move_frame.grid(row=0, column=0, padx=2)
        ctk.CTkButton(self.move_frame, text="▲", width=25, height=18, command=lambda: self.on_move(self, -1)).pack(pady=1)
        ctk.CTkButton(self.move_frame, text="▼", width=25, height=18, command=lambda: self.on_move(self, 1)).pack(pady=1)

        # Type Icon/Label
        type_colors = {"click": "#3498DB", "right_click": "#9B59B6", "double_click": "#2980B9", "key": "#E67E22", "key_hold": "#D35400", "wait": "#95A5A6"}
        self.lbl_type = ctk.CTkLabel(self, text=event_type.replace('_', ' ').upper(), width=85, anchor="w", 
                                     font=ctk.CTkFont(size=11, weight="bold"), text_color=type_colors.get(event_type, "white"))
        self.lbl_type.grid(row=0, column=1, padx=2, pady=2)

        # Value Entry
        self.val_var = ctk.StringVar(value=str(value))
        self.ent_val = ctk.CTkEntry(self, textvariable=self.val_var, width=110, font=ctk.CTkFont(size=12))
        self.ent_val.grid(row=0, column=2, padx=2, pady=2)

        # Timing Frame for Wait/Hold/Repeat
        self.details_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.details_frame.grid(row=0, column=3, padx=5)

        # Wait Entry
        ctk.CTkLabel(self.details_frame, text="Wait:", font=ctk.CTkFont(size=10)).pack(side="left", padx=1)
        self.delay_var = ctk.StringVar(value=str(delay_ms))
        self.ent_delay = ctk.CTkEntry(self.details_frame, textvariable=self.delay_var, width=45, font=ctk.CTkFont(size=11))
        self.ent_delay.pack(side="left", padx=1)

        # Hold Entry (Always present but labeled for Key Hold)
        self.hold_var = ctk.StringVar(value=str(hold_ms))
        if event_type == "key_hold":
            ctk.CTkLabel(self.details_frame, text="Hold:", font=ctk.CTkFont(size=10)).pack(side="left", padx=1)
            self.ent_hold = ctk.CTkEntry(self.details_frame, textvariable=self.hold_var, width=45, font=ctk.CTkFont(size=11))
            self.ent_hold.pack(side="left", padx=1)

        # Repeat Entry
        ctk.CTkLabel(self.details_frame, text="Repeat:", font=ctk.CTkFont(size=10)).pack(side="left", padx=1)
        self.repeat_var = ctk.StringVar(value=str(repeat))
        self.ent_repeat = ctk.CTkEntry(self.details_frame, textvariable=self.repeat_var, width=35, font=ctk.CTkFont(size=11))
        self.ent_repeat.pack(side="left", padx=1)
        
        ctk.CTkLabel(self.details_frame, text="ms", font=ctk.CTkFont(size=10)).pack(side="left", padx=1)

        # Clone Button
        self.btn_clone = ctk.CTkButton(self, text="📋", width=30, fg_color="#F1C40F", hover_color="#D4AC0D", text_color="black", command=lambda: self.on_clone(self))
        self.btn_clone.grid(row=0, column=4, padx=5, pady=2)

        # Delete Button
        self.btn_del = ctk.CTkButton(self, text="X", width=30, fg_color="#E74C3C", hover_color="#C0392B", command=self.delete_me)
        self.btn_del.grid(row=0, column=5, padx=5, pady=2)

    def delete_me(self):
        if self.on_delete: self.on_delete(self)
        self.destroy()

    def get_data(self):
        try:
            val_str = self.val_var.get()
            delay_sec = float(self.delay_var.get()) / 1000.0
            hold_sec = float(self.hold_var.get()) / 1000.0
            repeat_count = int(self.repeat_var.get())
            if repeat_count < 1: repeat_count = 1
            
            common = {"type": self.event_type, "delay": delay_sec, "repeat": repeat_count}
            
            if "click" in self.event_type:
                parts = val_str.replace('(', '').replace(')', '').split(',')
                return {**common, "x": int(parts[0]), "y": int(parts[1])}
            
            if self.event_type == "key_hold":
                return {**common, "key": val_str, "hold": hold_sec}
                
            return {**common, "key": val_str}
        except: return None

class MacroAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Antigravity Macro Studio v11 - Repeat Edition")
        self.geometry("1300x950")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Logic State
        self.mouse_controller = MController()
        self.keyboard_controller = keyboard.Controller()
        self.recording = False
        self.playing = False
        self.playback_lock = threading.Lock()
        self.event_rows = []
        self.last_event_time = 0
        self.pressed_keys_start = {}
        
        # Hotkeys
        self.rec_key = Key.f9
        self.capture_key = Key.f11
        self.hotkey_registry = {}
        
        self.profiles = self.load_profiles_file()
        self.rebuild_hotkey_registry()

        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT: PROFILES ---
        self.profile_panel = ctk.CTkFrame(self, width=220)
        self.profile_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)
        ctk.CTkLabel(self.profile_panel, text="MACRO PROFILES", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        self.btn_new_macro = ctk.CTkButton(self.profile_panel, text="+ START NEW MACRO", fg_color="#27AE60", hover_color="#1E8449", command=self.start_new_macro_flow)
        self.btn_new_macro.pack(pady=10, padx=10, fill="x")
        self.profile_list_frame = ctk.CTkScrollableFrame(self.profile_panel, height=400)
        self.profile_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.profile_name_entry = ctk.CTkEntry(self.profile_panel, placeholder_text="Profile Name")
        self.profile_name_entry.pack(pady=5, padx=10, fill="x")
        self.btn_save_profile = ctk.CTkButton(self.profile_panel, text="SAVE / UPDATE", fg_color="#2E86C1", command=self.save_current_as_profile)
        self.btn_save_profile.pack(pady=5, padx=10, fill="x")
        self.refresh_profile_list()

        # --- MIDDLE: BUILDER ---
        self.builder_panel = ctk.CTkFrame(self, width=260)
        self.builder_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        ctk.CTkLabel(self.builder_panel, text="STEP BUILDER", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        self.mouse_pos_label = ctk.CTkLabel(self.builder_panel, text="MOUSE: (0, 0)", font=ctk.CTkFont(size=12, family="Courier"))
        self.mouse_pos_label.pack(pady=5)
        ctk.CTkLabel(self.builder_panel, text="--- Click Actions ---", font=ctk.CTkFont(size=10)).pack(pady=2)
        ctk.CTkButton(self.builder_panel, text="Left Click (F11)", command=lambda: self.add_manual_click("click")).pack(pady=3, padx=10, fill="x")
        ctk.CTkButton(self.builder_panel, text="Right Click", command=lambda: self.add_manual_click("right_click"), fg_color="#8E44AD").pack(pady=3, padx=10, fill="x")
        ctk.CTkButton(self.builder_panel, text="Double Click", command=lambda: self.add_manual_click("double_click"), fg_color="#2980B9").pack(pady=3, padx=10, fill="x")
        ctk.CTkLabel(self.builder_panel, text="--- Key & Action ---", font=ctk.CTkFont(size=10)).pack(pady=10)
        self.key_entry = ctk.CTkEntry(self.builder_panel, placeholder_text="Key (w, tab, shift...)")
        self.key_entry.pack(pady=3, padx=10, fill="x")
        qk_frame = ctk.CTkFrame(self.builder_panel, fg_color="transparent")
        qk_frame.pack(fill="x", padx=10, pady=2)
        for k in ["Tab", "Space", "Enter", "Caps"]:
            ctk.CTkButton(qk_frame, text=k, width=50, height=25, font=ctk.CTkFont(size=10), command=lambda val=k: self.add_manual_key(val)).pack(side="left", padx=2)
        ctk.CTkButton(self.builder_panel, text="Add Instant Key", command=self.add_manual_key).pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.builder_panel, text="--- Custom Controls ---", font=ctk.CTkFont(size=10)).pack(pady=5)
        self.hold_entry = ctk.CTkEntry(self.builder_panel, placeholder_text="Hold ms")
        self.hold_entry.pack(pady=3, padx=10, fill="x")
        ctk.CTkButton(self.builder_panel, text="Add Key Hold Step", command=self.add_manual_hold, fg_color="#D35400").pack(pady=3, padx=10, fill="x")
        self.repeat_entry = ctk.CTkEntry(self.builder_panel, placeholder_text="Repeat count (e.g. 5)")
        self.repeat_entry.insert(0, "1")
        self.repeat_entry.pack(pady=5, padx=10, fill="x")
        self.delay_entry = ctk.CTkEntry(self.builder_panel, placeholder_text="Wait Before ms")
        self.delay_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(self.builder_panel, text="Add Wait Step", command=self.add_manual_delay, fg_color="#7F8C8D").pack(pady=3, padx=10, fill="x")

        # --- RIGHT: TIMELINE ---
        self.editor_panel = ctk.CTkFrame(self)
        self.editor_panel.grid(row=0, column=2, sticky="nsew", padx=5, pady=10)
        self.hk_frame = ctk.CTkFrame(self.editor_panel)
        self.hk_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(self.hk_frame, text="Activation Key:").grid(row=0, column=0, padx=5)
        self.hk_menu = ctk.CTkOptionMenu(self.hk_frame, values=HOTKEY_OPTIONS, width=125)
        self.hk_menu.set("F10")
        self.hk_menu.grid(row=0, column=1, padx=5)
        self.btn_play = ctk.CTkButton(self.hk_frame, text="▶ RUN CURRENT SEQUENCE", font=ctk.CTkFont(weight="bold"), command=self.start_playback_thread, fg_color="#27AE60", height=45)
        self.btn_play.grid(row=0, column=2, padx=20, sticky="ew")
        self.hk_frame.grid_columnconfigure(2, weight=1)
        self.label_status = ctk.CTkLabel(self.editor_panel, text="[ SYSTEM IDLE ]", font=ctk.CTkFont(size=14, weight="bold", family="Courier"))
        self.label_status.pack(pady=5)
        self.scroll_frame = ctk.CTkScrollableFrame(self.editor_panel, label_text="LOOPABLE MACRO TIMELINE")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.footer = ctk.CTkFrame(self.editor_panel)
        self.footer.pack(fill="x", pady=10, padx=10)
        self.btn_record = ctk.CTkButton(self.footer, text="🔴 START RECORDING (F9)", command=self.toggle_recording, fg_color="#C0392B", hover_color="#922B21")
        self.btn_record.pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.footer, text="Clear All", command=self.clear_events, fg_color="gray").pack(side="left", expand=True, padx=5)
        ctk.CTkButton(self.footer, text="Exit App", command=sys.exit, fg_color="#2C3E50").pack(side="right", expand=True, padx=5)

        self.overlay = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.overlay.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)
        ctk.CTkLabel(self.overlay, text="Macro Editor Locked", font=ctk.CTkFont(size=24, weight="bold")).pack(expand=True)
        ctk.CTkLabel(self.overlay, text="Click '+ Start New Macro' or select a Profile to begin", font=ctk.CTkFont(size=14)).place(relx=0.5, rely=0.55, anchor="center")

        KListener(on_press=self.on_global_press, on_release=self.on_global_release).start()
        self.update_mouse_pos_realtime()

    # --- Profile & Global Registry ---
    def rebuild_hotkey_registry(self):
        self.hotkey_registry = {}
        for name, data in self.profiles.items():
            hk_name = data.get("hotkey")
            if not hk_name: continue
            hk_obj = None
            u_hk = hk_name.upper()
            if u_hk == "CAPSLOCK": hk_obj = Key.caps_lock
            elif u_hk in SPECIAL_KEYS: hk_obj = SPECIAL_KEYS[u_hk]
            elif len(hk_name) == 1: hk_obj = KeyCode(char=hk_name.lower())
            if hk_obj: self.hotkey_registry[hk_obj] = data.get("steps", [])

    def load_profiles_file(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def save_profiles_file(self):
        with open(PROFILES_FILE, 'w') as f: json.dump(self.profiles, f, indent=4)
        self.rebuild_hotkey_registry()

    def refresh_profile_list(self):
        for w in self.profile_list_frame.winfo_children(): w.destroy()
        for name in sorted(self.profiles.keys()):
            f = ctk.CTkFrame(self.profile_list_frame, fg_color="transparent")
            f.pack(fill="x", pady=2)
            ctk.CTkButton(f, text=name, anchor="w", fg_color="#34495E", font=ctk.CTkFont(size=14), command=lambda n=name: self.load_profile(n)).pack(side="left", fill="x", expand=True, padx=2)
            ctk.CTkButton(f, text="X", width=25, fg_color="#943126", command=lambda n=name: self.delete_profile(n)).pack(side="right", padx=2)

    def save_current_as_profile(self):
        name = self.profile_name_entry.get().strip()
        if not name: return
        steps = [r.get_data() for r in self.event_rows if r.get_data()]
        if not steps: return
        self.profiles[name] = {"hotkey": self.hk_menu.get(), "steps": steps}
        self.save_profiles_file()
        self.refresh_profile_list()

    def load_profile(self, name):
        if name not in self.profiles: return
        self.unlock_editor()
        self.clear_events()
        data = self.profiles[name]
        self.profile_name_entry.delete(0, 'end'); self.profile_name_entry.insert(0, name)
        hk_val = data.get("hotkey", "F10")
        if hk_val in HOTKEY_OPTIONS: self.hk_menu.set(hk_val)
        for s in data.get("steps", []):
            if isinstance(s, dict):
                stype = s.get("type", "click")
                val = f"{s.get('x')},{s.get('y')}" if "x" in s else s.get("key")
                self.add_step(stype, val, int(s.get("delay", 0.5) * 1000), int(s.get("hold", 0) * 1000), s.get("repeat", 1))
            else: # Compatibility for old lists
                self.add_step(s[0], s[1], int(s[2] * 1000), int(s[3] * 1000) if len(s) > 3 else 0)

    def delete_profile(self, name):
        if name in self.profiles:
            del self.profiles[name]; self.save_profiles_file(); self.refresh_profile_list()

    # --- UI Logic ---
    def start_new_macro_flow(self):
        self.unlock_editor()
        self.clear_events()
        self.profile_name_entry.delete(0, 'end')
        self.hk_menu.set("F10")

    def unlock_editor(self): self.overlay.place_forget()

    def update_mouse_pos_realtime(self):
        def _track():
            m = MController()
            while True:
                try: self.mouse_pos_label.configure(text=f"MOUSE: {m.position}")
                except: break
                time.sleep(0.05)
        threading.Thread(target=_track, daemon=True).start()

    def on_global_press(self, key):
        if key == self.rec_key: self.toggle_recording()
        elif key == self.capture_key: self.add_manual_click("click")
        elif key in self.hotkey_registry and not self.playing and not self.recording:
            threading.Thread(target=self.playback, args=(self.hotkey_registry[key],), daemon=True).start()
        if self.recording and key not in self.pressed_keys_start:
            self.pressed_keys_start[key] = time.time()

    def on_global_release(self, key):
        if self.recording and key in self.pressed_keys_start:
            press_time = self.pressed_keys_start.pop(key)
            duration = int((time.time() - press_time) * 1000)
            delay = int((press_time - self.last_event_time) * 1000)
            self.last_event_time = time.time()
            val = str(key).replace("'", "")
            if "caps_lock" in val: val = "CapsLock"
            if "tab" in val.lower(): val = "Tab"
            if "space" in val.lower(): val = "Space"
            if "enter" in val.lower(): val = "Enter"
            if duration > 150: self.after(0, lambda: self.add_step('key_hold', val, delay, duration))
            else: self.after(0, lambda: self.add_step('key', val, delay))

    # --- Step Management ---
    def add_step(self, stype, value, delay_ms, hold_ms=0, repeat=1):
        row = EventRow(self.scroll_frame, len(self.event_rows)+1, stype, value, delay_ms, hold_ms, repeat,
                        on_delete=self.on_row_delete, on_move=self.move_row, on_clone=self.clone_row)
        row.pack(fill="x", pady=2, padx=5)
        self.event_rows.append(row)

    def on_row_delete(self, r):
        if r in self.event_rows: self.event_rows.remove(r)

    def move_row(self, r, dir):
        idx = self.event_rows.index(r); n_idx = idx + dir
        if 0 <= n_idx < len(self.event_rows):
            self.event_rows[idx], self.event_rows[n_idx] = self.event_rows[n_idx], self.event_rows[idx]
            for row in self.event_rows: row.pack_forget()
            for row in self.event_rows: row.pack(fill="x", pady=2, padx=5)

    def clone_row(self, r):
        d = r.get_data()
        if d:
            self.add_step(d['type'], f"{d.get('x')},{d.get('y')}" if "x" in d else d.get("key"), 
                          int(d['delay']*1000), int(d.get('hold', 0)*1000), d.get('repeat', 1))

    # --- Builder Actions ---
    def add_manual_click(self, stype):
        p = self.mouse_controller.position
        rep = int(self.repeat_entry.get()) if self.repeat_entry.get().isdigit() else 1
        del_val = int(self.delay_entry.get()) if self.delay_entry.get().isdigit() else 500
        self.add_step(stype, f"{p[0]},{p[1]}", del_val, repeat=rep)

    def add_manual_key(self, key_val=None):
        k = key_val if key_val else self.key_entry.get().strip()
        rep = int(self.repeat_entry.get()) if self.repeat_entry.get().isdigit() else 1
        del_val = int(self.delay_entry.get()) if self.delay_entry.get().isdigit() else 300
        if k: 
            self.add_step("key", k, del_val, repeat=rep)
            if not key_val: self.key_entry.delete(0, 'end')

    def add_manual_hold(self):
        k, h, rep = self.key_entry.get().strip(), self.hold_entry.get().strip(), self.repeat_entry.get().strip()
        del_val = int(self.delay_entry.get()) if self.delay_entry.get().isdigit() else 300
        if k and h.isdigit():
            self.add_step("key_hold", k, del_val, int(h), int(rep) if rep.isdigit() else 1)
            self.key_entry.delete(0, 'end'); self.hold_entry.delete(0, 'end')

    def add_manual_delay(self):
        ms = self.delay_entry.get().strip()
        if ms.isdigit(): self.add_step("wait", "None", ms); self.delay_entry.delete(0, 'end')

    # --- Playback Logic ---
    def toggle_recording(self):
        if not self.recording:
            self.unlock_editor()
            self.recording = True; self.last_event_time = time.time(); self.pressed_keys_start = {}
            self.btn_record.configure(text="⏹ STOP RECORDING", fg_color="#C0392B"); self.label_status.configure(text="[ RECORDING... ]", text_color="#E74C3C")
            self.m_list = MListener(on_click=self.on_click_rt); self.m_list.start()
        else:
            self.recording = False; self.m_list.stop()
            self.btn_record.configure(text="🔴 START RECORDING (F9)", fg_color="#C0392B"); self.label_status.configure(text="[ SYSTEM IDLE ]", text_color="white")

    def on_click_rt(self, x, y, btn, pressed):
        if self.recording and pressed:
            now = time.time(); delay = int((now - self.last_event_time) * 1000); self.last_event_time = now
            stype = "click" if btn == Button.left else "right_click"
            self.after(0, lambda: self.add_step(stype, f"{x},{y}", delay))

    def start_playback_thread(self):
        if not self.recording and not self.playing:
            steps = [r.get_data() for r in self.event_rows if r.get_data()]
            if not steps: return
            threading.Thread(target=self.playback, args=(steps,), daemon=True).start()

    def playback(self, steps):
        self.playing = True; self.label_status.configure(text="[ PLAYING... ]", text_color="#27AE60")
        for s in steps:
            if not self.playing: break
            
            # Extract data safely (handles both old list and new dict format)
            if isinstance(s, dict):
                stype, delay, repeat = s.get("type"), s.get("delay", 0), s.get("repeat", 1)
                x, y, key, hold = s.get("x"), s.get("y"), s.get("key"), s.get("hold", 0)
            else: # Fallback for old models
                stype, x, y, delay = s[0], s[1], s[2], s[3]
                repeat, hold = 1, 0

            for _ in range(repeat):
                if not self.playing: break
                if delay > 0: time.sleep(delay)
                
                if "click" in stype:
                    self.mouse_controller.position = (x, y)
                    btn = Button.right if stype == "right_click" else Button.left
                    self.mouse_controller.click(btn, 2 if stype == "double_click" else 1)
                elif stype in ['key', 'key_hold']:
                    try:
                        k = str(key).strip(); u_k = k.upper()
                        if u_k == "CAPSLOCK": k_obj = Key.caps_lock
                        elif u_k in SPECIAL_KEYS: k_obj = SPECIAL_KEYS[u_k]
                        elif k.startswith("Key."): k_obj = getattr(Key, k.split(".")[1])
                        else: k_obj = KeyCode(char=k)
                        if k_obj:
                            self.keyboard_controller.press(k_obj)
                            if stype == 'key_hold' and hold > 0: time.sleep(hold)
                            self.keyboard_controller.release(k_obj)
                    except: pass
        self.playing = False; self.label_status.configure(text="[ SYSTEM IDLE ]", text_color="white")

    def clear_events(self):
        for r in self.event_rows: r.destroy()
        self.event_rows = []

if __name__ == "__main__":
    MacroAppGUI().mainloop()
