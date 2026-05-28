import os
import time
import wave

import sounddevice as sd
import numpy as np

from config import (
    SAMPLE_RATE,
    CHANNELS,
    AUDIO_DTYPE,
    AUDIO_BLOCKSIZE,
    AUDIO_SAMPWIDTH,
    AUDIO_SIGNAL_CHECK_SECONDS,
    AUDIO_SIGNAL_MIN_RMS,
    AUDIO_SIGNAL_MIN_PEAK,
)


class AudioRecorder:
    def __init__(self):
        self.frames = []
        self._stream = None
        self.error = None
        self.last_signal_rms = 0.0
        self.last_signal_peak = 0

    def start(self):
        self.frames = []
        self.error = None
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=AUDIO_DTYPE,
                callback=self._callback,
                blocksize=AUDIO_BLOCKSIZE,
            )
            self._stream.start()
            return True
        except Exception as e:
            self.error = f"Микрофон недоступен: {e}"
            self._stream = None
            return False

    def check_signal(self):
        self.last_signal_rms = 0.0
        self.last_signal_peak = 0

        if not self.start():
            return False

        try:
            time.sleep(AUDIO_SIGNAL_CHECK_SECONDS)
        finally:
            self.stop()

        if not self.frames:
            self.error = "Микрофон не получает сигнал"
            return False

        data = np.concatenate(self.frames, axis=0).astype(np.float32)
        self.last_signal_rms = float(np.sqrt(np.mean(data ** 2)))
        self.last_signal_peak = int(np.max(np.abs(data)))
        self.frames = []

        if (
            self.last_signal_rms < AUDIO_SIGNAL_MIN_RMS
            and self.last_signal_peak < AUDIO_SIGNAL_MIN_PEAK
        ):
            self.error = "Микрофон подключен, но не получает звук"
            return False

        self.error = None
        return True

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def save(self, session_dir, date_str):
        if not self.frames:
            return
        path = os.path.join(session_dir, f"audio_{date_str}.wav")
        data = np.concatenate(self.frames, axis=0)
        with wave.open(path, "w") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(AUDIO_SAMPWIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(data.tobytes())

    def _callback(self, indata, frames, time_info, status):
        self.frames.append(indata.copy())
