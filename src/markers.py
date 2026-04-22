import json
import os


class MarkerManager:
    def __init__(self):
        self.markers = []
        self.open = False

    def reset(self):
        self.markers = []
        self.open = False

    def place(self, elapsed):
        if not self.open:
            idx = len(self.markers) // 2
            self.markers.append({"type": "start", "time": elapsed, "segment": idx + 1})
            self.open = True
            return idx + 1, "start", None
        else:
            seg_idx = len([m for m in self.markers if m["type"] == "start"])
            self.markers.append({"type": "end", "time": elapsed, "segment": seg_idx})
            dur = elapsed - next(
                m["time"] for m in reversed(self.markers) if m["type"] == "start"
            )
            self.open = False
            return seg_idx, "end", dur

    def close_open_marker(self, elapsed):
        """Принудительно закрыть незакрытую метку при остановке записи."""
        if self.open:
            self.place(elapsed)

    def save(self, session_dir: str, date_str: str):
        path = os.path.join(session_dir, f"markers_{date_str}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"markers": self.markers},
                f, ensure_ascii=False, indent=2,
            )
