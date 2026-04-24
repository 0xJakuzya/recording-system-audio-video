import os
import wave

import sounddevice as sd
import numpy as np

from config import SAMPLE_RATE, CHANNELS, AUDIO_DTYPE, AUDIO_BLOCKSIZE, AUDIO_SAMPWIDTH


class AudioRecorder:
    def __init__(self):
        self.frames = []
        self._stream = None
        self.error = None

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
