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
            # Создаем черный экран с надписью "No Signal"
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # Позиция текста "No Signal"
            text = "No Signal"
            text_x = self.width // 4
            text_y = self.height // 2

            # Цвет текста и легкая тень
            text_color = (102, 178, 255)  # Мягкий светло-голубой
            shadow_offset = 2

            # Рисуем тень
            cv2.putText(frame, text, (text_x + shadow_offset, text_y + shadow_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2, cv2.LINE_AA)

            # Рисуем основной текст
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)
        else:
            # Масштабируем кадр до нужного размера, если он доступен
            frame = cv2.resize(frame, (self.width, self.height))

        # Добавляем метку камеры с рамками
        label_color = (102, 178, 255)
        cv2.putText(frame, self.label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, label_color, 2, cv2.LINE_AA)
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
