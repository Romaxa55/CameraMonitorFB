import cv2
import numpy as np
import logging
import asyncio


class Camera:
    def __init__(self, url, position, label, border_thickness, border_color, reconnect_delay=5):
        self.url = url
        self.position = position
        self.label = label
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.reconnect_delay = reconnect_delay  # Задержка перед попыткой переподключения (в секундах)
        self.cap = None
        self.width, self.height = self.position[2]
        self.logger = logging.getLogger("Camera")

    async def connect(self):
        """Асинхронное подключение к камере."""
        self.cap = await asyncio.to_thread(cv2.VideoCapture, self.url)
        if not self.cap.isOpened():
            self.logger.error(f"Не удалось открыть поток {self.url} для камеры {self.label}")
        else:
            self.logger.info(f"Подключен к потоку {self.url} для камеры {self.label}")

    async def get_frame(self):
        """Асинхронно возвращает текущий кадр с камеры или чёрный экран с надписью 'No Signal'."""
        if not self.cap or not self.cap.isOpened():
            self.logger.warning(f"Поток {self.url} недоступен, попытка переподключения через {self.reconnect_delay} секунд...")
            await asyncio.sleep(self.reconnect_delay)
            await self.connect()
            return self._generate_no_signal_frame()

        # Пробуем захватить кадр
        ret, frame = await asyncio.to_thread(self.cap.read)
        if not ret:
            self.logger.warning(f"Ошибка при чтении потока {self.url} для камеры {self.label}")
            frame = self._generate_no_signal_frame()
        else:
            # Масштабируем кадр до нужного размера
            frame = cv2.resize(frame, (self.width, self.height))

        # Добавляем метку камеры и рамки
        label_color = (102, 178, 255)
        cv2.putText(frame, self.label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, label_color, 2, cv2.LINE_AA)
        frame = self.add_borders(frame)
        return frame

    def _generate_no_signal_frame(self):
        """Создаёт черный кадр с надписью 'No Signal'."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        text = "No Signal"
        text_x = self.width // 4
        text_y = self.height // 2
        text_color = (102, 178, 255)

        # Рисуем текст с легкой тенью
        shadow_offset = 2
        cv2.putText(frame, text, (text_x + shadow_offset, text_y + shadow_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2, cv2.LINE_AA)
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)
        return frame

    def add_borders(self, frame):
        """Добавляет рамку к кадру."""
        frame[:self.border_thickness, :, :] = self.border_color[:3]  # Верхний бордер
        frame[-self.border_thickness:, :, :] = self.border_color[:3]  # Нижний бордер
        frame[:, :self.border_thickness, :] = self.border_color[:3]  # Левый бордер
        frame[:, -self.border_thickness:, :] = self.border_color[:3]  # Правый бордер
        return frame

    async def release(self):
        """Освобождает поток камеры."""
        await asyncio.to_thread(self.cap.release)
        self.logger.info(f"Поток для камеры {self.label} освобождён.")
