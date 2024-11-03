import cv2
import numpy as np
import asyncio
import fcntl
import struct
import logging
from camera import Camera
import config


class CameraDisplay:
    def __init__(self, fb_path="/dev/fb0", fps=26, border_thickness=2, margin_x=30, margin_y=20):
        self.is_running = True
        self.fb_path = fb_path
        self.fps = fps
        self.frame_interval = 1 / fps
        self.border_thickness = border_thickness
        self.border_color = (50, 50, 50, 255)
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.logger = logging.getLogger("CameraDisplay")
        logging.basicConfig(level=logging.INFO)

        # Размеры фреймбуфера и камеры
        self.fb_width, self.fb_height = self.get_framebuffer_size()
        self.inner_width = self.fb_width - 2 * self.margin_x
        self.inner_height = self.fb_height - 2 * self.margin_y
        self.logger.info(f"Размер области отображения: {self.inner_width}x{self.inner_height}")

        # Определяем размеры областей для камер
        self.main_camera_size = (self.inner_width // 2, self.inner_height // 2)
        self.grid_camera_size = (self.inner_width // 4 - border_thickness, self.inner_height // 4 - border_thickness)
        self.camera_positions = self.define_camera_positions()
        self.cameras = []

    def get_framebuffer_size(self):
        try:
            with open(self.fb_path, "rb") as fb:
                screeninfo = fcntl.ioctl(fb, 0x4600, struct.pack("8I", *[0] * 8))
                _, _, width, height, *_ = struct.unpack("8I", screeninfo)
            return width, height
        except Exception as e:
            self.logger.error(f"Ошибка при получении размеров фреймбуфера: {e}")
            raise

    def define_camera_positions(self):
        main_width, main_height = self.main_camera_size
        grid_width, grid_height = self.grid_camera_size
        bt = self.border_thickness

        start_x = self.margin_x
        start_y = self.margin_y
        positions = [(start_x, start_y, self.main_camera_size)]
        self.logger.info(f"Позиция основной камеры: {positions[0]}")

        # Верхняя правая сетка 2x2
        upper_right_start_x = start_x + main_width + bt
        upper_right_start_y = start_y
        for i in range(2):
            for j in range(2):
                x = upper_right_start_x + j * (grid_width + bt)
                y = upper_right_start_y + i * (grid_height + bt)
                positions.append((x, y, (grid_width, grid_height)))
        self.logger.info("Позиции верхней правой сетки 2x2 определены.")

        # Нижняя сетка 4x4
        lower_start_y = start_y + main_height + bt
        for i in range(4):
            for j in range(4):
                x = start_x + j * (grid_width + bt)
                y = lower_start_y + i * (grid_height + bt)
                positions.append((x, y, (grid_width, grid_height)))
        self.logger.info("Позиции нижней сетки 4x4 определены.")
        return positions

    async def initialize_framebuffer(self):
        # Создаём начальное фоновое изображение
        self.background = np.zeros((self.fb_height, self.fb_width, 4), dtype=np.uint8)
        self.draw_initial_grid(self.background)
        self.logger.info("Сетка камер отрисована.")

        # Открываем фреймбуфер
        try:
            self.fb = open(self.fb_path, "wb")
            self.logger.info("Фреймбуфер открыт для записи.")
        except PermissionError:
            self.logger.error("Требуется запуск от sudo для записи в /dev/fb0.")
            raise
        except Exception as e:
            self.logger.error(f"Ошибка при открытии фреймбуфера: {e}")
            raise

        asyncio.create_task(self.write_to_framebuffer_loop())  # Задача для вывода на экран

    def draw_initial_grid(self, background):
        for idx, (x, y, (width, height)) in enumerate(self.camera_positions):
            cv2.rectangle(background, (x, y), (x + width, y + height), self.border_color, self.border_thickness)
            text = "No Signal"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = x + (width - text_size[0]) // 2
            text_y = y + (height + text_size[1]) // 2
            text_color = (102, 178, 255, 255)
            shadow_offset = 2
            cv2.putText(background, text, (text_x + shadow_offset, text_y + shadow_offset), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (50, 50, 50, 255), 2, cv2.LINE_AA)
            cv2.putText(background, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)

    async def create_cameras(self, channels):
        async def create_camera(idx, channel_id, channel_info):
            label = channel_info.get("label", f"Camera {channel_id}")
            camera = Camera(channel_info["url"], self.camera_positions[idx], label, self.border_thickness,
                            self.border_color)
            await camera.connect()
            self.logger.info(
                f"Создана камера {label} с URL: {channel_info['url']} на позиции {self.camera_positions[idx]}")
            self.cameras.append(camera)
            asyncio.create_task(self.update_camera_display(camera))

        for idx, (channel_id, channel_info) in enumerate(channels.items()):
            asyncio.create_task(create_camera(idx, channel_id, channel_info))
        self.logger.info("Камеры инициализированы как независимые задачи.")

    async def update_camera_display(self, camera):
        """Обновляет фон с кадрами от всех камер."""
        while self.is_running:
            frame = await camera.get_frame()
            x, y, _ = camera.position
            self.background[y:y + frame.shape[0], x:x + frame.shape[1], :3] = frame
            await asyncio.sleep(self.frame_interval)

    async def write_to_framebuffer_loop(self):
        """Постоянно записывает обновлённый фон в фреймбуфер."""
        while self.is_running:
            self.fb.seek(0)
            self.fb.write(self.background.tobytes())
            await asyncio.sleep(self.frame_interval)

    async def close_framebuffer(self):
        self.is_running = False  # Останавливаем цикл записи в буфер
        await asyncio.sleep(self.frame_interval)  # Ждем завершения текущей записи
        if not self.fb.closed:
            self.fb.close()
            self.logger.info("Фреймбуфер закрыт.")
        for camera in self.cameras:
            await camera.release()
            self.logger.info(f"Ресурсы камеры {camera.label} освобождены.")
