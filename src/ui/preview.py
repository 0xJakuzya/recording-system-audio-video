import tkinter as tk

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

PREVIEW_W = 480
PREVIEW_H = 270  # default 16:9


class CameraPreview:
    """
    Live camera preview. Canvas fills parent and resizes with it.
    Feed frames via push(rgb_ndarray).
    """

    def __init__(self, parent: tk.Frame, colors: dict):
        self._colors = colors
        self._photo = None
        self._img_item = None

        self.canvas = tk.Canvas(
            parent,
            bg=colors["PANEL"], highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind resize so overlays track canvas size
        self.canvas.bind("<Configure>", self._on_resize)

        # Static overlay items — repositioned on resize
        self._bg_rect = self.canvas.create_rectangle(
            0, 0, PREVIEW_W, PREVIEW_H,
            fill=colors["PANEL"], outline="",
        )
        self._no_signal = self.canvas.create_text(
            PREVIEW_W // 2, PREVIEW_H // 2,
            text="NO SIGNAL", fill=colors["MUTED"],
            font=("Courier New", 13),
        )
        self._rec_badge = self.canvas.create_text(
            14, 14,
            text="● REC", fill=colors["ACCENT"],
            font=("Courier New", 9, "bold"),
            anchor="nw", state="hidden",
        )
        self._brackets = self._draw_brackets(PREVIEW_W, PREVIEW_H)
        self._recording = False

    # ── Public API ───────────────────────────────────────────────

    def set_recording(self, active: bool):
        self._recording = active
        state = "normal" if active else "hidden"
        self.canvas.itemconfig(self._rec_badge, state=state)
        for item in self._brackets:
            self.canvas.itemconfig(item, state=state)

    def push(self, rgb_frame):
        """Render a raw RGB numpy frame onto the canvas (main thread only)."""
        if not PIL_AVAILABLE:
            return
        try:
            W = self.canvas.winfo_width() or PREVIEW_W
            H = self.canvas.winfo_height() or PREVIEW_H

            img = Image.fromarray(rgb_frame)
            # Fit frame into canvas keeping aspect ratio, then centre
            src_w, src_h = img.size
            scale = min(W / src_w, H / src_h)
            nw, nh = int(src_w * scale), int(src_h * scale)
            img = img.resize((nw, nh), Image.BILINEAR)

            self._photo = ImageTk.PhotoImage(img)

            if self._img_item is None:
                self._img_item = self.canvas.create_image(
                    W // 2, H // 2, anchor="center", image=self._photo
                )
            else:
                self.canvas.coords(self._img_item, W // 2, H // 2)
                self.canvas.itemconfig(self._img_item, image=self._photo)

            self.canvas.itemconfig(self._bg_rect, state="hidden")
            self.canvas.itemconfig(self._no_signal, state="hidden")
            # Keep overlays on top
            self.canvas.tag_raise(self._rec_badge)
            for b in self._brackets:
                self.canvas.tag_raise(b)
        except Exception:
            pass

    def show_no_signal(self):
        if self._img_item:
            self.canvas.delete(self._img_item)
            self._img_item = None
        W = self.canvas.winfo_width() or PREVIEW_W
        H = self.canvas.winfo_height() or PREVIEW_H
        self.canvas.coords(self._bg_rect, 0, 0, W, H)
        self.canvas.coords(self._no_signal, W // 2, H // 2)
        self.canvas.itemconfig(self._bg_rect, state="normal")
        self.canvas.itemconfig(self._no_signal, state="normal")

    # ── Internals ────────────────────────────────────────────────

    def _on_resize(self, event):
        W, H = event.width, event.height
        self.canvas.coords(self._bg_rect, 0, 0, W, H)
        self.canvas.coords(self._no_signal, W // 2, H // 2)
        self.canvas.coords(self._rec_badge, 14, 14)
        self._reposition_brackets(W, H)

    def _draw_brackets(self, W, H):
        C = self._colors["ACCENT"]
        items = []
        for coords in self._bracket_coords(W, H):
            item = self.canvas.create_line(*coords, fill=C, width=2, state="hidden")
            items.append(item)
        return items

    def _reposition_brackets(self, W, H):
        for item, coords in zip(self._brackets, self._bracket_coords(W, H)):
            self.canvas.coords(item, *coords)

    @staticmethod
    def _bracket_coords(W, H):
        L, pad = 22, 10
        return [
            (pad, pad + L, pad, pad, pad + L, pad),                          # top-left
            (W - pad - L, pad, W - pad, pad, W - pad, pad + L),              # top-right
            (pad, H - pad - L, pad, H - pad, pad + L, H - pad),              # bottom-left
            (W - pad - L, H - pad, W - pad, H - pad, W - pad, H - pad - L),  # bottom-right
        ]
