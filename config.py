import os

# Каналы и базовый URL для подключения к RTSP-потокам
BASE_URL = os.getenv("CAMERA_BASE_URL", "rtsp://user:password@127.0.0.1:554/cam/realmonitor?channel")

# Словарь каналов с параметрами
CHANNELS = {
    1: {"url": f"{BASE_URL}=1&subtype=0", "label": ""},
    2: {"url": f"{BASE_URL}=2&subtype=0", "label": ""},
    13: {"url": f"{BASE_URL}=13&subtype=0", "label": ""},
    4: {"url": f"{BASE_URL}=4&subtype=0", "label": ""},
    9: {"url": f"{BASE_URL}=9&subtype=1", "label": "2"},
    11: {"url": f"{BASE_URL}=11&subtype=1", "label": "3"},
    12: {"url": f"{BASE_URL}=12&subtype=1", "label": "3"},
    3: {"url": f"{BASE_URL}=3&subtype=1", "label": "4"},
    5: {"url": f"{BASE_URL}=5&subtype=1", "label": "4"},
    6: {"url": f"{BASE_URL}=6&subtype=1", "label": "5"},
    7: {"url": f"{BASE_URL}=7&subtype=1", "label": "5"},
    8: {"url": f"{BASE_URL}=8&subtype=0", "label": "6"},
}
