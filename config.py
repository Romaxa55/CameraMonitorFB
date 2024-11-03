import os

# Каналы и базовый URL для подключения к RTSP-потокам
BASE_URL = os.getenv("CAMERA_BASE_URL", "rtsp://user:password@127.0.0.1:554/cam/realmonitor?channel")

# Словарь каналов с параметрами
CHANNELS = {
    1: {"url": f"{BASE_URL}=1&subtype=0", "label": "Camera 1"},
    2: {"url": f"{BASE_URL}=2&subtype=0", "label": "Camera 2"},
    13: {"url": f"{BASE_URL}=13&subtype=0", "label": "Camera 13"},
    4: {"url": f"{BASE_URL}=4&subtype=0", "label": "Camera 4"},
    9: {"url": f"{BASE_URL}=9&subtype=0", "label": "Camera 9"},
    11: {"url": f"{BASE_URL}=11&subtype=0", "label": "Camera 11"},
    12: {"url": f"{BASE_URL}=12&subtype=0", "label": "Camera 12"},
    3: {"url": f"{BASE_URL}=3&subtype=0", "label": "Camera 3"},
    5: {"url": f"{BASE_URL}=5&subtype=0", "label": "Camera 5"},
    6: {"url": f"{BASE_URL}=6&subtype=0", "label": "Camera 6"},
    7: {"url": f"{BASE_URL}=7&subtype=0", "label": "Camera 7"},
    8: {"url": f"{BASE_URL}=8&subtype=0", "label": "Camera 8"},
}
