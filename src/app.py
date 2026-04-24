import json
import os
import time
import tkinter as tk
from tkinter import messagebox

from config import (
    COLORS,
    OUTPUT_DIR,
    TICK_MS,
    WINDOW_TITLE,
    TEXT_REC_START,
    TEXT_REC_STOP,
    TEXT_EMPTY_LOG,
    TEXT_STATUS_REC,
    TEXT_STATUS_STANDBY,
    TEXT_TIMER_DEFAULT,
    MARKER_OPEN_BG,
    MARKER_CLOSED_BG,
    MARKER_GREEN,
    MARKER_ACTIVE_BG,
    REC_BUTTON_BG,
    REC_BUTTON_ACTIVE_BG,
    REC_BUTTON_STOP_ACTIVE,
    USER_INFO_FILENAME,
    next_session_dir,
)
from .audio import AudioRecorder
from .video import VideoRecorder
from .markers import MarkerManager
from .ui.builder import build_ui


def format_time(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 1000)
    return f"{m:02d}:{s:02d}.{ms:03d}"


class RecorderApp:
    def __init__(self, root, user_info=None):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.resizable(True, True)

        self.user_info = user_info
        self.recording = False
        self.start_time = None
        self.session_dir = None
        self.date_str = None
        self.fullscreen = False

        self.audio = AudioRecorder()
        self.video = VideoRecorder()
        self.markers = MarkerManager()
        self.log_rows = []

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        self.w = build_ui(root, self.toggle_recording, self.place_marker)

        self._bind_keys()
        self._tick()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _bind_keys(self):
        self.root.bind("<space>", self._on_space)
        self.root.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self._exit_fullscreen())

    def _on_space(self, event):
        if self.recording:
            self.place_marker()
        return "break"

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def _exit_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)

    def toggle_recording(self):
        if self.recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self.session_dir, self.date_str = next_session_dir()
        self.markers.reset()
        self.log_rows = []
        self.start_time = time.time()
        self.recording = True

        self.w["rec_btn"].config(
            text=TEXT_REC_STOP,
            bg=REC_BUTTON_BG,
            fg=COLORS["ACCENT"],
            activebackground=REC_BUTTON_ACTIVE_BG,
        )
        self.w["mark_btn"].config(
            state="normal",
            bg=MARKER_CLOSED_BG,
            fg=MARKER_GREEN,
            activebackground=MARKER_ACTIVE_BG,
        )
        self._set_status(TEXT_STATUS_REC, COLORS["ACCENT"])
        self._clear_log()
        self.w["mark_indicator"].config(bg=COLORS["DIM"])
        self.w["preview"].set_recording(True)

        audio_ok = self.audio.start()
        video_ok = self.video.start(self.session_dir, self.date_str)

        warnings = []
        if not audio_ok:
            warnings.append(f"Аудио: {self.audio.error}")
        if not video_ok:
            warnings.append(f"Видео: {self.video.error}")

        self._set_device_status("mic", audio_ok)
        self._set_device_status("cam", video_ok)

        if warnings:
            messagebox.showwarning(
                "Устройства недоступны",
                "\n".join(warnings) + "\n\nЗапись продолжится без недоступных устройств.",
            )

    def _stop_recording(self):
        if self.markers.open:
            elapsed = time.time() - self.start_time
            self.markers.close_open_marker(elapsed)
            self._update_last_log(f"  ◀  авто-закрыто  {format_time(elapsed)}")
            self.w["mark_btn"].config(bg=MARKER_CLOSED_BG)
            self.w["mark_indicator"].config(bg=COLORS["DIM"])

        self.recording = False
        self.audio.stop()
        self.video.stop()
        self._save_session()

        self.w["rec_btn"].config(
            text=TEXT_REC_START,
            bg=COLORS["ACCENT"],
            fg="white",
            activebackground=REC_BUTTON_STOP_ACTIVE,
        )
        self.w["mark_btn"].config(state="disabled", bg=COLORS["DIM"], fg=COLORS["MUTED"])
        self.w["mark_indicator"].config(bg=COLORS["DIM"])
        self._set_status(TEXT_STATUS_STANDBY, COLORS["MUTED"])
        self._set_device_status("mic", None)
        self._set_device_status("cam", None)
        self.w["timer_var"].set(TEXT_TIMER_DEFAULT)
        self.w["preview"].set_recording(False)
        self.w["preview"].show_no_signal()

    def _save_session(self):
        if not self.session_dir:
            return
        self.audio.save(self.session_dir, self.date_str)
        self.markers.save(self.session_dir, self.date_str)
        if self.user_info:
            path = os.path.join(self.session_dir, USER_INFO_FILENAME)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.user_info, f, ensure_ascii=False, indent=2)

    def _on_close(self):
        if self.recording:
            self._stop_recording()
        self.root.destroy()

    def place_marker(self):
        if not self.recording:
            return
        elapsed = time.time() - self.start_time
        seg_idx, kind, dur = self.markers.place(elapsed)

        if kind == "start":
            self._add_log_row(f"#{seg_idx:02d}  ▶  {format_time(elapsed)}", "open")
            self.w["mark_btn"].config(
                bg=MARKER_OPEN_BG, fg=MARKER_GREEN, activebackground=MARKER_ACTIVE_BG
            )
            self.w["mark_indicator"].config(bg=MARKER_GREEN)
        else:
            self._update_last_log(
                f"#{seg_idx:02d}  ◀  {format_time(elapsed)}  [{format_time(dur)}]"
            )
            self.w["mark_btn"].config(
                bg=MARKER_CLOSED_BG, fg=MARKER_GREEN, activebackground=MARKER_ACTIVE_BG
            )
            self.w["mark_indicator"].config(bg=COLORS["DIM"])

    def _set_status(self, text, color):
        self.w["status_txt"].config(text=text, fg=color)
        self.w["status_dot"].config(fg=color)

    def _set_device_status(self, device, ok):
        key = f"{device}_status"
        if key not in self.w:
            return
        lbl = self.w[key]
        if ok is None:
            lbl.config(text="", bg=COLORS["BG"])
            return
        icon = "🎙" if device == "mic" else "📷"
        if ok:
            lbl.config(text=f"{icon} OK", fg=MARKER_GREEN, bg=COLORS["BG"])
        else:
            lbl.config(text=f"{icon} НЕТ", fg=COLORS["ACCENT"], bg=COLORS["BG"])

    def _clear_log(self):
        for child in self.w["log_frame"].winfo_children():
            child.destroy()
        self.w["empty_label"] = tk.Label(
            self.w["log_frame"],
            text=TEXT_EMPTY_LOG,
            bg=COLORS["PANEL"],
            fg=COLORS["MUTED"],
            font=self.w["fonts"]["mono_sm"],
        )
        self.w["empty_label"].pack(anchor="w", pady=4)
        self.log_rows = []

    def _add_log_row(self, text, state):
        el = self.w.get("empty_label")
        if el and el.winfo_exists():
            el.destroy()
        color = MARKER_GREEN if state == "open" else COLORS["TEXT"]
        lbl = tk.Label(
            self.w["log_frame"],
            text=text,
            bg=COLORS["PANEL"],
            fg=color,
            font=self.w["fonts"]["mono_sm"],
            anchor="w",
        )
        lbl.pack(fill="x", pady=1)
        self.log_rows.append(lbl)
        self.w["log_canvas"].update_idletasks()
        self.w["log_canvas"].yview_moveto(1.0)

    def _update_last_log(self, text):
        if self.log_rows:
            self.log_rows[-1].config(text=text, fg=COLORS["TEXT"])

    def _tick(self):
        if self.recording and self.start_time:
            elapsed = time.time() - self.start_time
            self.w["timer_var"].set(format_time(elapsed))

        if not self.video.frame_queue.empty():
            frame = self.video.frame_queue.get_nowait()
            self.w["preview"].push(frame)

        self.root.after(TICK_MS, self._tick)
