import os
import sys
from datetime import datetime

SAMPLE_RATE = 44100
CHANNELS = 1
AUDIO_DTYPE = "int16"
AUDIO_BLOCKSIZE = 1024
AUDIO_SAMPWIDTH = 2

VIDEO_FPS = 20
VIDEO_FOURCC = "MJPG"
VIDEO_CAMERA_INDEX = 0

PREVIEW_W = 480
PREVIEW_H = 270
PREVIEW_BRACKET_LEN = 22
PREVIEW_BRACKET_PAD = 10

TICK_MS = 33

WINDOW_TITLE = "REC // Лаборатория"

COLORS = {
    "BG":     "#0d0d0f",
    "PANEL":  "#131316",
    "ACCENT": "#e63946",
    "DIM":    "#2a2a30",
    "TEXT":   "#e8e8ec",
    "MUTED":  "#555560",
}

MARKER_OPEN_BG = "#1e3a1e"
MARKER_CLOSED_BG = "#1e2a1e"
MARKER_GREEN = "#4ade80"
MARKER_ACTIVE_BG = "#253225"
REC_BUTTON_BG = "#222228"
REC_BUTTON_ACTIVE_BG = "#2a2a30"
REC_BUTTON_STOP_ACTIVE = "#c1121f"

FONT_FAMILY = "Courier New"
FONT_SIZES = {
    "mono": 11,
    "mono_sm": 9,
    "mono_lg": 28,
    "label": 8,
}

TEXT_REC_START = "▶  НАЧАТЬ ЗАПИСЬ"
TEXT_REC_STOP = "■  ОСТАНОВИТЬ"
TEXT_MARK = "◆  МЕТКА  [ПРОБЕЛ]"
TEXT_EMPTY_LOG = "— нет меток —"
TEXT_STATUS_REC = "REC"
TEXT_STATUS_STANDBY = "STANDBY"
TEXT_TIMER_DEFAULT = "00:00.000"
TEXT_NO_SIGNAL = "NO SIGNAL"
TEXT_REC_BADGE = "● REC"

USER_INFO_TITLE = "Данные участника"
USER_INFO_SUBJECT_LABEL = "ID участника (число)"
USER_INFO_SUBJECT_PLACEHOLDER = "1"
USER_INFO_DOB_LABEL = "Дата рождения (ДД.ММ.ГГГГ)"
USER_INFO_GENDER_LABEL = "Пол"
USER_INFO_SUBMIT = "Продолжить"
USER_INFO_ERROR_DOB = "Неверная дата. Формат: ДД.ММ.ГГГГ"
USER_INFO_ERROR_SUBJECT = "ID должен быть положительным числом"
USER_INFO_DOB_PLACEHOLDER = "01.01.2000"
USER_INFO_DOB_FORMAT = "%d.%m.%Y"
USER_INFO_GENDERS = ("Мужской", "Женский")
USER_INFO_FILENAME = "user_info.json"

if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(_BASE_DIR, "data")


def next_session_dir(subject_id):
    subject_dir = os.path.join(OUTPUT_DIR, str(subject_id))
    os.makedirs(subject_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(subject_dir, date_str)
    os.makedirs(path, exist_ok=True)
    return path, date_str
