import tkinter as tk
from tkinter import font as tkfont
from config import (
    COLORS,
    OUTPUT_DIR,
    FONT_FAMILY,
    FONT_SIZES,
    TEXT_REC_START,
    TEXT_MARK,
    TEXT_EMPTY_LOG,
    TEXT_STATUS_STANDBY,
    TEXT_TIMER_DEFAULT,
)
from .preview import CameraPreview


LOG_HEIGHT = 90
OUTER_PADX = 32
OUTER_PADY = 24

def build_fonts():
    return {
        "mono":    tkfont.Font(family=FONT_FAMILY, size=FONT_SIZES["mono"]),
        "mono_sm": tkfont.Font(family=FONT_FAMILY, size=FONT_SIZES["mono_sm"]),
        "mono_lg": tkfont.Font(family=FONT_FAMILY, size=FONT_SIZES["mono_lg"], weight="bold"),
        "label":   tkfont.Font(family=FONT_FAMILY, size=FONT_SIZES["label"]),
    }

def build_header(outer, fonts):
    hdr = tk.Frame(outer, bg=COLORS["BG"])
    hdr.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    tk.Label(hdr, text="● REC SYSTEM", bg=COLORS["BG"], fg=COLORS["MUTED"],
             font=fonts["label"]).pack(side="left")
    tk.Label(hdr, text="[F11] fullscreen", bg=COLORS["BG"], fg=COLORS["MUTED"],
             font=fonts["label"]).pack(side="left", padx=(12, 0))
    cam_status = tk.Label(hdr, text="", bg=COLORS["BG"], fg=COLORS["MUTED"], font=fonts["label"])
    cam_status.pack(side="left", padx=(12, 0))
    mic_status = tk.Label(hdr, text="", bg=COLORS["BG"], fg=COLORS["MUTED"], font=fonts["label"])
    mic_status.pack(side="left", padx=(6, 0))
    status_dot = tk.Label(hdr, text="○", bg=COLORS["BG"], fg=COLORS["MUTED"], font=fonts["label"])
    status_dot.pack(side="right")
    status_txt = tk.Label(hdr, text=TEXT_STATUS_STANDBY, bg=COLORS["BG"], fg=COLORS["MUTED"],
                          font=fonts["label"])
    status_txt.pack(side="right", padx=(0, 6))
    return cam_status, mic_status, status_dot, status_txt


def build_timer(outer, fonts):
    timer_frame = tk.Frame(outer, bg=COLORS["PANEL"], padx=24, pady=10)
    timer_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
    timer_inner = tk.Frame(timer_frame, bg=COLORS["PANEL"])
    timer_inner.pack()
    timer_var = tk.StringVar(value=TEXT_TIMER_DEFAULT)
    tk.Label(timer_inner, textvariable=timer_var,
             bg=COLORS["PANEL"], fg=COLORS["TEXT"], font=fonts["mono_lg"]).pack(side="left")
    tk.Label(timer_inner, text="  ELAPSED", bg=COLORS["PANEL"], fg=COLORS["MUTED"],
             font=fonts["label"]).pack(side="left", padx=(4, 0))
    return timer_var

def build_log(outer, fonts):
    log_outer = tk.Frame(outer, bg=COLORS["PANEL"])
    log_outer.grid(row=5, column=0, sticky="ew")
    tk.Label(log_outer, text="МАРКЕРЫ", bg=COLORS["PANEL"], fg=COLORS["MUTED"],
             font=fonts["label"], anchor="w").pack(fill="x", padx=12, pady=(10, 4))
    tk.Frame(log_outer, bg=COLORS["DIM"], height=1).pack(fill="x", padx=12)
    log_scroll_frame = tk.Frame(log_outer, bg=COLORS["PANEL"], height=LOG_HEIGHT)
    log_scroll_frame.pack(fill="x", padx=12, pady=(4, 0))
    log_scroll_frame.pack_propagate(False)
    log_canvas = tk.Canvas(log_scroll_frame, bg=COLORS["PANEL"],
                           highlightthickness=0, bd=0)
    scrollbar = tk.Scrollbar(log_scroll_frame, orient="vertical",
                             command=log_canvas.yview)
    log_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    log_canvas.pack(side="left", fill="both", expand=True)
    log_frame = tk.Frame(log_canvas, bg=COLORS["PANEL"])
    log_frame_id = log_canvas.create_window((0, 0), window=log_frame, anchor="nw")

    def on_resize(_):
        log_canvas.configure(scrollregion=log_canvas.bbox("all"))
        log_canvas.itemconfig(log_frame_id, width=log_canvas.winfo_width())
    log_frame.bind("<Configure>", on_resize)
    log_canvas.bind("<Configure>",
                    lambda ev: log_canvas.itemconfig(log_frame_id, width=ev.width))
    empty_label = tk.Label(log_frame, text=TEXT_EMPTY_LOG,
                           bg=COLORS["PANEL"], fg=COLORS["MUTED"], font=fonts["mono_sm"])
    empty_label.pack(anchor="w", pady=4, padx=4)
    return log_frame, log_canvas, empty_label

def build_ui(root, on_toggle_recording, on_place_marker):
    fonts = build_fonts()
    root.configure(bg=COLORS["BG"])
    outer = tk.Frame(root, bg=COLORS["BG"], padx=OUTER_PADX, pady=OUTER_PADY)
    outer.pack(fill="both", expand=True)
    outer.rowconfigure(1, weight=1)
    outer.columnconfigure(0, weight=1)
    cam_status, mic_status, status_dot, status_txt = build_header(outer, fonts)
    preview_frame = tk.Frame(outer, bg=COLORS["BG"])
    preview_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
    preview = CameraPreview(preview_frame, COLORS)
    timer_var = build_timer(outer, fonts)
    rec_btn = tk.Button(
        outer, text=TEXT_REC_START,
        bg=COLORS["ACCENT"], fg="white", activebackground="#c1121f",
        activeforeground="white", font=fonts["mono"], bd=0,
        padx=32, pady=14, cursor="hand2",
        command=on_toggle_recording, relief="flat",
    )
    rec_btn.grid(row=3, column=0, sticky="ew", pady=(0, 8))
    mark_row = tk.Frame(outer, bg=COLORS["BG"])
    mark_row.grid(row=4, column=0, sticky="ew", pady=(0, 12))
    mark_row.columnconfigure(0, weight=1)
    mark_btn = tk.Button(
        mark_row, text=TEXT_MARK,
        bg=COLORS["DIM"], fg=COLORS["MUTED"], activebackground="#3a3a44",
        activeforeground=COLORS["TEXT"], font=fonts["mono"], bd=0,
        padx=32, pady=14, cursor="hand2",
        command=on_place_marker, relief="flat", state="disabled",
    )
    mark_btn.grid(row=0, column=0, sticky="ew")
    mark_indicator = tk.Frame(mark_row, bg=COLORS["DIM"], height=3)
    mark_indicator.grid(row=1, column=0, sticky="ew")
    log_frame, log_canvas, empty_label = build_log(outer, fonts)
    tk.Label(outer, text=f"Папка: {OUTPUT_DIR}",
             bg=COLORS["BG"], fg=COLORS["MUTED"], font=fonts["label"],
             wraplength=600, justify="left").grid(
        row=6, column=0, sticky="w", pady=(10, 0))
        
    return {
        "fonts":          fonts,
        "timer_var":      timer_var,
        "preview":        preview,
        "rec_btn":        rec_btn,
        "mark_btn":       mark_btn,
        "mark_indicator": mark_indicator,
        "log_frame":      log_frame,
        "log_canvas":     log_canvas,
        "empty_label":    empty_label,
        "status_txt":     status_txt,
        "status_dot":     status_dot,
        "mic_status":     mic_status,
        "cam_status":     cam_status,
    }
