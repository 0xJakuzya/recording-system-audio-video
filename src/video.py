import threading
import time
import os
import queue

try:
    import cv2
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False


class VideoRecorder:
    def __init__(self):
        self._writer = None
        self._thread = None
        self._recording = False
        self._stop_event = threading.Event()
        self.frame_queue: queue.Queue = queue.Queue(maxsize=2)
        self.error: str | None = None

    @property
    def available(self):
        return VIDEO_AVAILABLE

    def start(self, session_dir: str, date_str: str) -> bool:
        """Start recording. Returns True on success, False on failure."""
        if not VIDEO_AVAILABLE:
            self.error = "Библиотека opencv не установлена"
            return False
        self.error = None
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error = "Камера недоступна"
            return False

        fps = 20
        path = os.path.join(session_dir, f"video_{date_str}.avi")
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(path, fourcc, fps, (w, h))

        self._stop_event.clear()
        self._recording = True

        def run():
            try:
                while not self._stop_event.is_set():
                    ret, frame = cap.read()
                    if ret:
                        writer.write(frame)
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        if not self.frame_queue.full():
                            self.frame_queue.put(rgb)
                    time.sleep(1 / fps)
            finally:
                cap.release()
                writer.release()  # всегда сбрасываем буфер на диск

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._recording = False
        self._stop_event.set()  # сигнал треду завершиться чисто
