import time
import tkinter as tk
from tkinter import messagebox

import os
from config import COLORS, OUTPUT_DIR, next_session_dir
from .audio import AudioRecorder
from .video import VideoRecorder
from .markers import MarkerManager
from .ui.builder import build_ui


def _fmt(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 1000)
    return f"{m:02d}:{s:02d}.{ms:03d}"


class RecorderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("REC // Лаборатория")
        self.root.resizable(True, True)

        self.recording = False
        self.start_time = None
        self.session_dir = None
        self._date_str = None
        self._fullscreen = False

        self._audio = AudioRecorder()
        self._video = VideoRecorder()
        self._markers = MarkerManager()
        self._log_rows = []

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        widgets = build_ui(root, self._toggle_recording, self._place_marker)
        self._w = widgets

        self._bind_keys()
        self._tick()

        # Сохранить сессию если закрывают окно крестиком
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Keys ────────────────────────────────────────────────────

    def _bind_keys(self):
        self.root.bind("<space>", self._on_space)
        self.root.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self._exit_fullscreen())

    def _on_space(self, event):
        if self.recording:
            self._place_marker()
        return "break"  # не даём пробелу активировать кнопки

    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)

    def _exit_fullscreen(self):
        if self._fullscreen:
            self._fullscreen = False
            self.root.attributes("-fullscreen", False)

    # ── Recording control ────────────────────────────────────────

    def _toggle_recording(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self.session_dir, self._date_str = next_session_dir()
        self._markers.reset()
        self._log_rows = []
        self.start_time = time.time()
        self.recording = True

        C = COLORS
        self._w["rec_btn"].config(
            text="■  ОСТАНОВИТЬ", bg="#222228",
            fg=C["ACCENT"], activebackground="#2a2a30",
        )
        self._w["mark_btn"].config(
            state="normal", bg="#1e2a1e",
            fg="#4ade80", activebackground="#253225",
        )
        self._set_status("REC", C["ACCENT"])
        self._clear_log()
        self._w["mark_indicator"].config(bg=COLORS["DIM"])
        self._w["preview"].set_recording(True)

        audio_ok = self._audio.start()
        video_ok = self._video.start(self.session_dir, self._date_str)

        # Показать предупреждения если устройства недоступны
        warnings = []
        if not audio_ok:
            warnings.append(f"Аудио: {self._audio.error}")
            self._set_device_status("mic", False)
        else:
            self._set_device_status("mic", True)

        if not video_ok:
            warnings.append(f"Видео: {self._video.error}")
            self._set_device_status("cam", False)
        else:
            self._set_device_status("cam", True)

        if warnings:
            messagebox.showwarning(
                "Устройства недоступны",
                "\n".join(warnings) + "\n\nЗапись продолжится без недоступных устройств.",
            )

    def _stop_recording(self):
        # Закрыть незакрытую метку перед сохранением
        if self._markers.open:
            elapsed = time.time() - self.start_time
            self._markers.close_open_marker(elapsed)
            self._update_last_log(
                f"  ◀  авто-закрыто  {_fmt(elapsed)}"
            )
            self._w["mark_btn"].config(bg="#1e2a1e")
            self._w["mark_indicator"].config(bg=COLORS["DIM"])

        self.recording = False
        self._audio.stop()
        self._video.stop()
        self._save_session()

        C = COLORS
        self._w["rec_btn"].config(
            text="▶  НАЧАТЬ ЗАПИСЬ", bg=C["ACCENT"],
            fg="white", activebackground="#c1121f",
        )
        self._w["mark_btn"].config(state="disabled", bg=C["DIM"], fg=C["MUTED"])
        self._w["mark_indicator"].config(bg=C["DIM"])
        self._set_status("STANDBY", C["MUTED"])
        self._set_device_status("mic", None)
        self._set_device_status("cam", None)
        self._w["timer_var"].set("00:00.000")
        self._w["preview"].set_recording(False)
        self._w["preview"].show_no_signal()

    def _save_session(self):
        if not self.session_dir:
            return
        self._audio.save(self.session_dir, self._date_str)
        self._markers.save(self.session_dir, self._date_str)

    def _on_close(self):
        if self.recording:
            self._stop_recording()
        self.root.destroy()

    # ── Markers ──────────────────────────────────────────────────

    def _place_marker(self):
        if not self.recording:
            return
        elapsed = time.time() - self.start_time
        seg_idx, kind, dur = self._markers.place(elapsed)

        if kind == "start":
            self._add_log_row(f"#{seg_idx:02d}  ▶  {_fmt(elapsed)}", "open")
            self._w["mark_btn"].config(bg="#1e3a1e", fg="#4ade80",
                                       activebackground="#253225")
            self._w["mark_indicator"].config(bg="#4ade80")
        else:
            self._update_last_log(
                f"#{seg_idx:02d}  ◀  {_fmt(elapsed)}  [{_fmt(dur)}]"
            )
            self._w["mark_btn"].config(bg="#1e2a1e", fg="#4ade80",
                                       activebackground="#253225")
            self._w["mark_indicator"].config(bg=COLORS["DIM"])

    # ── UI helpers ───────────────────────────────────────────────

    def _set_status(self, text, color):
        self._w["status_txt"].config(text=text, fg=color)
        self._w["status_dot"].config(fg=color)

    def _set_device_status(self, device: str, ok):
        """Update mic/cam status labels. ok=True/False/None(reset)."""
        key = f"{device}_status"
        if key not in self._w:
            return
        lbl = self._w[key]
        if ok is None:
            lbl.config(text="", bg=COLORS["BG"])
        elif ok:
            icon = "🎙" if device == "mic" else "📷"
            lbl.config(text=f"{icon} OK", fg="#4ade80", bg=COLORS["BG"])
        else:
            icon = "🎙" if device == "mic" else "📷"
            lbl.config(text=f"{icon} НЕТ", fg=COLORS["ACCENT"], bg=COLORS["BG"])

    def _clear_log(self):
        for child in self._w["log_frame"].winfo_children():
            child.destroy()
        C = COLORS
        fonts = self._w["fonts"]
        self._w["empty_label"] = tk.Label(
            self._w["log_frame"], text="— нет меток —",
            bg=C["PANEL"], fg=C["MUTED"], font=fonts["mono_sm"],
        )
        self._w["empty_label"].pack(anchor="w", pady=4)
        self._log_rows = []

    def _add_log_row(self, text, state):
        el = self._w.get("empty_label")
        if el and el.winfo_exists():
            el.destroy()
        C = COLORS
        color = "#4ade80" if state == "open" else C["TEXT"]
        lbl = tk.Label(
            self._w["log_frame"], text=text,
            bg=C["PANEL"], fg=color,
            font=self._w["fonts"]["mono_sm"], anchor="w",
        )
        lbl.pack(fill="x", pady=1)
        self._log_rows.append(lbl)
        self._w["log_canvas"].update_idletasks()
        self._w["log_canvas"].yview_moveto(1.0)

    def _update_last_log(self, text):
        if self._log_rows:
            self._log_rows[-1].config(text=text, fg=COLORS["TEXT"])

    # ── Tick ─────────────────────────────────────────────────────

    def _tick(self):
        if self.recording and self.start_time:
            elapsed = time.time() - self.start_time
            self._w["timer_var"].set(_fmt(elapsed))

        try:
            frame = self._video.frame_queue.get_nowait()
            self._w["preview"].push(frame)
        except Exception:
            pass

        self.root.after(33, self._tick)
