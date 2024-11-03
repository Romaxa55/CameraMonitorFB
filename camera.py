import cv2
import numpy as np
import logging


class Camera:
    def __init__(self, url, position, label, border_thickness, border_color):
        self.url = url
        self.position = position
        self.label = label
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.cap = cv2.VideoCapture(url)
        self.width, self.height = self.position[2]
        self.logger = logging.getLogger("Camera")

        if not self.cap.isOpened():
            self.logger.error(f"Не удалось открыть поток {url} для камеры {label}")

    def get_frame(self):
        """Возвращает текущий кадр с камеры или чёрный экран с надписью 'No Signal'."""
        ret, frame = self.cap.read()
        if not ret:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(frame, "No Signal", (self.width // 4, self.height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            frame = cv2.resize(frame, (self.width, self.height))

        # Добавляем текст и рамки
        cv2.putText(frame, self.label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        frame = self.add_borders(frame)
        return frame

    def add_borders(self, frame):
        """Добавляет рамку к кадру."""
        # Убедимся, что цвет рамки корректно применяется ко всем каналам
        frame[:self.border_thickness, :, :] = self.border_color[:3]  # Верхний бордер
        frame[-self.border_thickness:, :, :] = self.border_color[:3]  # Нижний бордер
        frame[:, :self.border_thickness, :] = self.border_color[:3]  # Левый бордер
        frame[:, -self.border_thickness:, :] = self.border_color[:3]  # Правый бордер
        return frame

    def release(self):
        self.cap.release()
