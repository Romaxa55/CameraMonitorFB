import cv2
import numpy as np
import logging
import asyncio
import time


class Camera:
    def __init__(self, url, position, label, fps=25, border_thickness=2, border_color=(50, 50, 50, 255),
                 reconnect_interval=None):
        self.url = url
        self.position = position
        self.label = label
        self.fps = fps
        self.frame_interval = 1 / fps
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.last_frame = None
        self.cap = None
        self.width, self.height = self.position[2]
        self.logger = logging.getLogger("Camera")
        self.reconnect_interval = reconnect_interval
        self.last_reconnect_time = time.time()
        self.last_frame_time = 0

    async def connect(self):
        """Асинхронное подключение к камере."""
        self.cap = await asyncio.to_thread(cv2.VideoCapture, self.url)
        if not self.cap.isOpened():
            self.logger.error(f"Не удалось открыть поток {self.url} для камеры {self.label}")
        else:
            self.logger.info(f"Подключен к потоку {self.url} для камеры {self.label}")

    async def reconnect_if_needed(self):
        """Переподключается к камере, если прошло достаточно времени с последнего подключения."""
        current_time = time.time()
        if self.reconnect_interval is not None:
            if current_time - self.last_reconnect_time >= self.reconnect_interval:
                self.logger.info(f"Переподключение к камере {self.label} для сброса буфера.")
                await self.release()
                await self.connect()
                self.last_reconnect_time = current_time

    async def get_frame(self):
        """Возвращает новый кадр, если доступен и прошел достаточный интервал, иначе возвращает последний кадр."""
        await self.reconnect_if_needed()  # Проверка необходимости переподключения

        if self.cap is None or not self.cap.isOpened():
            await self.connect()

        current_time = time.time()

        # Пропускаем кадры, если они слишком быстро поступают
        if current_time - self.last_frame_time < self.frame_interval:
            return self.last_frame

        # Захват кадра
        ret, frame = await asyncio.to_thread(self.cap.read)
        if ret:
            self.last_frame = cv2.resize(frame, (self.width, self.height))
            self.last_frame_time = current_time  # Обновляем время последнего кадра

        return self.last_frame

    async def create_placeholder_frame(self):
        """Создает заглушку в случае, если кадр недоступен."""
        placeholder_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        text = "No Signal"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = (self.height + text_size[1]) // 2
        cv2.putText(placeholder_frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return placeholder_frame

    async def release(self):
        """Освобождает поток камеры."""
        if self.cap:
            await asyncio.to_thread(self.cap.release)
            self.cap = None
        self.logger.info(f"Поток для камеры {self.label} освобождён.")
