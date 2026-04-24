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
            idx = len(self.markers) // 2 + 1
            self.markers.append({"type": "start", "time": elapsed, "segment": idx})
            self.open = True
            return idx, "start", None

        seg_idx = sum(1 for m in self.markers if m["type"] == "start")
        start_time = next(m["time"] for m in reversed(self.markers) if m["type"] == "start")
        self.markers.append({"type": "end", "time": elapsed, "segment": seg_idx})
        self.open = False
        return seg_idx, "end", elapsed - start_time

    def close_open_marker(self, elapsed):
        if self.open:
            self.place(elapsed)

    def save(self, session_dir, date_str):
        path = os.path.join(session_dir, f"markers_{date_str}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"markers": self.markers}, f, ensure_ascii=False, indent=2)
