import tkinter as tk
from tkinter import font as tkfont

from config import COLORS, OUTPUT_DIR
from .preview import CameraPreview


def build_fonts():
    try:
        return {
            "mono":    tkfont.Font(family="Courier New", size=11),
            "mono_sm": tkfont.Font(family="Courier New", size=9),
            "mono_lg": tkfont.Font(family="Courier New", size=28, weight="bold"),
            "label":   tkfont.Font(family="Courier New", size=8),
        }
    except Exception:
        return {
            "mono":    tkfont.Font(size=11),
            "mono_sm": tkfont.Font(size=9),
            "mono_lg": tkfont.Font(size=28, weight="bold"),
            "label":   tkfont.Font(size=8),
        }


def build_ui(root: tk.Tk, on_toggle_recording, on_place_marker):
    C = COLORS
    fonts = build_fonts()

    root.configure(bg=C["BG"])

    outer = tk.Frame(root, bg=C["BG"], padx=32, pady=24)
    outer.pack(fill="both", expand=True)
    outer.rowconfigure(1, weight=1)   # row 1 = preview, expands
    outer.columnconfigure(0, weight=1)

    # ── Header  (row 0) ──────────────────────────────────────────
    hdr = tk.Frame(outer, bg=C["BG"])
    hdr.grid(row=0, column=0, sticky="ew", pady=(0, 12))

    tk.Label(hdr, text="● REC SYSTEM", bg=C["BG"], fg=C["MUTED"],
             font=fonts["label"]).pack(side="left")
    tk.Label(hdr, text="[F11] fullscreen", bg=C["BG"], fg=C["MUTED"],
             font=fonts["label"]).pack(side="left", padx=(12, 0))

    # Device status indicators
    cam_status = tk.Label(hdr, text="", bg=C["BG"], fg=C["MUTED"], font=fonts["label"])
    cam_status.pack(side="left", padx=(12, 0))
    mic_status = tk.Label(hdr, text="", bg=C["BG"], fg=C["MUTED"], font=fonts["label"])
    mic_status.pack(side="left", padx=(6, 0))

    status_dot = tk.Label(hdr, text="○", bg=C["BG"], fg=C["MUTED"], font=fonts["label"])
    status_dot.pack(side="right")
    status_txt = tk.Label(hdr, text="STANDBY", bg=C["BG"], fg=C["MUTED"], font=fonts["label"])
    status_txt.pack(side="right", padx=(0, 6))

    # ── Camera preview  (row 1, expands) ─────────────────────────
    preview_frame = tk.Frame(outer, bg=C["BG"])
    preview_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
    preview = CameraPreview(preview_frame, C)

    # ── Timer  (row 2) ───────────────────────────────────────────
    timer_frame = tk.Frame(outer, bg=C["PANEL"], padx=24, pady=10)
    timer_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))

    timer_inner = tk.Frame(timer_frame, bg=C["PANEL"])
    timer_inner.pack()
    timer_var = tk.StringVar(value="00:00.000")
    tk.Label(timer_inner, textvariable=timer_var,
             bg=C["PANEL"], fg=C["TEXT"], font=fonts["mono_lg"]).pack(side="left")
    tk.Label(timer_inner, text="  ELAPSED", bg=C["PANEL"], fg=C["MUTED"],
             font=fonts["label"]).pack(side="left", padx=(4, 0))

    # ── REC button  (row 3) ──────────────────────────────────────
    rec_btn = tk.Button(
        outer, text="▶  НАЧАТЬ ЗАПИСЬ",
        bg=C["ACCENT"], fg="white", activebackground="#c1121f",
        activeforeground="white", font=fonts["mono"], bd=0,
        padx=32, pady=14, cursor="hand2",
        command=on_toggle_recording, relief="flat",
    )
    rec_btn.grid(row=3, column=0, sticky="ew", pady=(0, 8))

    # ── Marker button + indicator  (row 4) ───────────────────────
    mark_row = tk.Frame(outer, bg=C["BG"])
    mark_row.grid(row=4, column=0, sticky="ew", pady=(0, 12))
    mark_row.columnconfigure(0, weight=1)

    mark_btn = tk.Button(
        mark_row, text="◆  МЕТКА  [ПРОБЕЛ]",
        bg=C["DIM"], fg=C["MUTED"], activebackground="#3a3a44",
        activeforeground=C["TEXT"], font=fonts["mono"], bd=0,
        padx=32, pady=14, cursor="hand2",
        command=on_place_marker, relief="flat", state="disabled",
    )
    mark_btn.grid(row=0, column=0, sticky="ew")

    # Indicator strip below the button — changes colour on marker press
    mark_indicator = tk.Frame(mark_row, bg=C["DIM"], height=3)
    mark_indicator.grid(row=1, column=0, sticky="ew")

    # ── Markers log  (row 5, fixed height) ───────────────────────
    log_outer = tk.Frame(outer, bg=C["PANEL"])
    log_outer.grid(row=5, column=0, sticky="ew")

    tk.Label(log_outer, text="МАРКЕРЫ", bg=C["PANEL"], fg=C["MUTED"],
             font=fonts["label"], anchor="w").pack(fill="x", padx=12, pady=(10, 4))
    tk.Frame(log_outer, bg=C["DIM"], height=1).pack(fill="x", padx=12)

    # Scrollable log — fixed height so it never pushes preview
    log_scroll_frame = tk.Frame(log_outer, bg=C["PANEL"], height=90)
    log_scroll_frame.pack(fill="x", padx=12, pady=(4, 0))
    log_scroll_frame.pack_propagate(False)  # keep fixed height

    log_canvas = tk.Canvas(log_scroll_frame, bg=C["PANEL"],
                           highlightthickness=0, bd=0)
    scrollbar = tk.Scrollbar(log_scroll_frame, orient="vertical",
                             command=log_canvas.yview)
    log_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    log_canvas.pack(side="left", fill="both", expand=True)

    log_frame = tk.Frame(log_canvas, bg=C["PANEL"])
    log_frame_id = log_canvas.create_window((0, 0), window=log_frame, anchor="nw")

    def _on_log_frame_resize(e):
        log_canvas.configure(scrollregion=log_canvas.bbox("all"))
        log_canvas.itemconfig(log_frame_id, width=log_canvas.winfo_width())

    log_frame.bind("<Configure>", _on_log_frame_resize)
    log_canvas.bind("<Configure>",
                    lambda ev: log_canvas.itemconfig(log_frame_id, width=ev.width))

    empty_label = tk.Label(log_frame, text="— нет меток —",
                           bg=C["PANEL"], fg=C["MUTED"], font=fonts["mono_sm"])
    empty_label.pack(anchor="w", pady=4, padx=4)

    # ── Footer  (row 6) ──────────────────────────────────────────
    tk.Label(outer, text=f"Папка: {OUTPUT_DIR}",
             bg=C["BG"], fg=C["MUTED"], font=fonts["label"],
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
