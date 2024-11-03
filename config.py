import os

# Каналы и базовый URL для подключения к RTSP-потокам
CHANNEL_ORDER = [1, 2, 13, 4, 9, 11, 12, 3, 5, 6, 7, 8]
BASE_URL = os.getenv("CAMERA_BASE_URL", "rtsp://user:password@127.0.0.1:554/cam/realmonitor?channel")
