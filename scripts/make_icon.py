from PIL import Image, ImageDraw

SIZES = [256, 128, 64, 48, 32, 16]
BG = (13, 13, 15, 255)
PANEL = (19, 19, 22, 255)
ACCENT = (230, 57, 70, 255)
OUTPUT = "icon.ico"


def make(size):
    img = Image.new("RGBA", (size, size), BG)
    draw = ImageDraw.Draw(img)
    pad = max(1, size // 10)
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=max(1, size // 8),
        fill=PANEL,
        outline=ACCENT,
        width=max(1, size // 32),
    )
    cx, cy = size // 2, size // 2
    r = size // 4
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACCENT)
    return img


def main():
    base = make(SIZES[0])
    base.save(OUTPUT, format="ICO", sizes=[(s, s) for s in SIZES])
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
