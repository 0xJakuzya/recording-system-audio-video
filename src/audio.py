import wave
import os

try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

from config import SAMPLE_RATE, CHANNELS


class AudioRecorder:
    def __init__(self):
        self.frames = []
        self._stream = None
        self.error: str | None = None  # set if device unavailable

    @property
    def available(self):
        return AUDIO_AVAILABLE

    def start(self) -> bool:
        """Start recording. Returns True on success, False on failure."""
        if not AUDIO_AVAILABLE:
            self.error = "Библиотека sounddevice не установлена"
            return False
        self.frames = []
        self.error = None
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=CHANNELS,
                dtype="int16", callback=self._callback,
                blocksize=1024,
            )
            self._stream.start()
            return True
        except Exception as e:
            self.error = f"Микрофон недоступен: {e}"
            self._stream = None
            return False

    def stop(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def save(self, session_dir: str, date_str: str):
        if not AUDIO_AVAILABLE or not self.frames:
            return
        path = os.path.join(session_dir, f"audio_{date_str}.wav")
        data = np.concatenate(self.frames, axis=0)
        with wave.open(path, "w") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(data.tobytes())

    def _callback(self, indata, frames, time_info, status):
        self.frames.append(indata.copy())
