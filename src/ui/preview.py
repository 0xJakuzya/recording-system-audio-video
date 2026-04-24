import tkinter as tk
from PIL import Image, ImageTk
from config import (
    COLORS,
    PREVIEW_W,
    PREVIEW_H,
    PREVIEW_BRACKET_LEN,
    PREVIEW_BRACKET_PAD,
    FONT_FAMILY,
    TEXT_NO_SIGNAL,
    TEXT_REC_BADGE,
)

class CameraPreview:
    def __init__(self, parent, colors=None):
        self._colors = colors or COLORS
        self._photo = None
        self._img_item = None

        self.canvas = tk.Canvas(parent, bg=self._colors["PANEL"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        self._bg_rect = self.canvas.create_rectangle(
            0, 0, PREVIEW_W, PREVIEW_H,
            fill=self._colors["PANEL"], outline="",
        )
        self._no_signal = self.canvas.create_text(
            PREVIEW_W // 2, PREVIEW_H // 2,
            text=TEXT_NO_SIGNAL, fill=self._colors["MUTED"],
            font=(FONT_FAMILY, 13),
        )
        self._rec_badge = self.canvas.create_text(
            14, 14,
            text=TEXT_REC_BADGE, fill=self._colors["ACCENT"],
            font=(FONT_FAMILY, 9, "bold"),
            anchor="nw", state="hidden",
        )
        self._brackets = self.draw_brackets(PREVIEW_W, PREVIEW_H)

    def set_recording(self, active):
        state = "normal" if active else "hidden"
        self.canvas.itemconfig(self._rec_badge, state=state)
        for item in self._brackets:
            self.canvas.itemconfig(item, state=state)

    def push(self, rgb_frame):
        W = self.canvas.winfo_width() or PREVIEW_W
        H = self.canvas.winfo_height() or PREVIEW_H

        img = Image.fromarray(rgb_frame)
        src_w, src_h = img.size
        scale = min(W / src_w, H / src_h)
        img = img.resize((int(src_w * scale), int(src_h * scale)), Image.BILINEAR)

        self._photo = ImageTk.PhotoImage(img)

        if self._img_item is None:
            self._img_item = self.canvas.create_image(
                W // 2, H // 2, anchor="center", image=self._photo,
            )
        else:
            self.canvas.coords(self._img_item, W // 2, H // 2)
            self.canvas.itemconfig(self._img_item, image=self._photo)

        self.canvas.itemconfig(self._bg_rect, state="hidden")
        self.canvas.itemconfig(self._no_signal, state="hidden")
        self.canvas.tag_raise(self._rec_badge)
        for b in self._brackets:
            self.canvas.tag_raise(b)

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

    def on_resize(self, event):
        W, H = event.width, event.height
        self.canvas.coords(self._bg_rect, 0, 0, W, H)
        self.canvas.coords(self._no_signal, W // 2, H // 2)
        self.canvas.coords(self._rec_badge, 14, 14)
        self.reposition_brackets(W, H)

    def draw_brackets(self, W, H):
        items = []
        for coords in self._bracket_coords(W, H):
            item = self.canvas.create_line(
                *coords, fill=self._colors["ACCENT"], width=2, state="hidden",
            )
            items.append(item)
        return items

    def reposition_brackets(self, W, H):
        for item, coords in zip(self._brackets, self._bracket_coords(W, H)):
            self.canvas.coords(item, *coords)

    @staticmethod
    def _bracket_coords(W, H):
        L, pad = PREVIEW_BRACKET_LEN, PREVIEW_BRACKET_PAD
        return [
            (pad, pad + L, pad, pad, pad + L, pad),
            (W - pad - L, pad, W - pad, pad, W - pad, pad + L),
            (pad, H - pad - L, pad, H - pad, pad + L, H - pad),
            (W - pad - L, H - pad, W - pad, H - pad, W - pad, H - pad - L),
        ]
