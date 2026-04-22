import math
import tkinter as tk


class Waveform:
    def __init__(self, canvas: tk.Canvas, colors: dict):
        self._canvas = canvas
        self._colors = colors
        self._bars = []
        self._init_bars()

    def _init_bars(self):
        c = self._canvas
        W, H = 480, 50
        n = 60
        bar_w = W / n
        for i in range(n):
            x = i * bar_w + bar_w / 2
            bar = c.create_rectangle(
                x - bar_w * 0.3, H / 2 - 2,
                x + bar_w * 0.3, H / 2 + 2,
                fill=self._colors["DIM"], outline="",
            )
            self._bars.append(bar)

    def animate(self, t: float, marker_open: bool):
        H = 50
        active_color = self._colors["ACCENT"] if not marker_open else "#4ade80"
        for i, bar in enumerate(self._bars):
            phase = t * 8 + i * 0.5
            amp = (
                math.sin(phase) * 0.4
                + math.sin(phase * 2.3 + 1) * 0.3
                + math.sin(phase * 0.7 + 2) * 0.3
            )
            height = abs(amp) * 22 + 2
            coords = self._canvas.coords(bar)
            cx = coords[0] + (coords[2] - coords[0]) / 2
            w2 = (coords[2] - coords[0]) / 2
            self._canvas.coords(bar, cx - w2, H / 2 - height, cx + w2, H / 2 + height)
            self._canvas.itemconfig(bar, fill=active_color)

    def reset(self):
        H = 50
        for bar in self._bars:
            coords = self._canvas.coords(bar)
            self._canvas.coords(bar, coords[0], H / 2 - 2, coords[2], H / 2 + 2)
            self._canvas.itemconfig(bar, fill=self._colors["DIM"])
