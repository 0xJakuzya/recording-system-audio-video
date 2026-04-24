import os
import queue
import threading
import time

import cv2

from config import VIDEO_FPS, VIDEO_FOURCC, VIDEO_CAMERA_INDEX


class VideoRecorder:
    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()
        self.frame_queue = queue.Queue(maxsize=2)
        self.error = None

    def start(self, session_dir, date_str):
        self.error = None
        cap = cv2.VideoCapture(VIDEO_CAMERA_INDEX)
        if not cap.isOpened():
            self.error = "Камера недоступна"
            return False

        path = os.path.join(session_dir, f"video_{date_str}.avi")
        fourcc = cv2.VideoWriter_fourcc(*VIDEO_FOURCC)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(path, fourcc, VIDEO_FPS, (w, h))

        self._stop_event.clear()

        def run():
            try:
                while not self._stop_event.is_set():
                    ret, frame = cap.read()
                    if ret:
                        writer.write(frame)
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        if not self.frame_queue.full():
                            self.frame_queue.put(rgb)
                    time.sleep(1 / VIDEO_FPS)
            finally:
                cap.release()
                writer.release()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._stop_event.set()
