import numpy as np
import asyncio
import time
import fcntl
import struct
import logging
from camera import Camera
import config


class CameraDisplay:
    def __init__(self, fb_path="/dev/fb0", fps=26, border_thickness=4, main_padding=(10, 10)):
        self.fb_path = fb_path
        self.fps = fps
        self.frame_interval = 1 / fps
        self.border_thickness = border_thickness
        self.main_padding = main_padding  # Отступ для основной камеры
        self.border_color = (50, 50, 50, 255)  # Цвет рамок
        self.logger = logging.getLogger("CameraDisplay")

        # Получаем размер фреймбуфера
        self.fb_width, self.fb_height = self.get_framebuffer_size()
        self.logger.info(f"Размер фреймбуфера: {self.fb_width}x{self.fb_height}")

        # Определяем размеры областей для камер
        self.main_camera_size = (
            self.fb_width // 2 - 2 * main_padding[0],
            self.fb_height // 2 - 2 * main_padding[1]
        )
        self.grid_camera_size = (
            self.fb_width // 4 - border_thickness,
            self.fb_height // 4 - border_thickness
        )

        # Позиции для адаптивной сетки камер
        self.camera_positions = self.define_camera_positions()
        self.cameras = self.create_cameras(config.BASE_URL, config.CHANNEL_ORDER)

    def get_framebuffer_size(self):
        """Получаем размеры фреймбуфера."""
        with open(self.fb_path, "rb") as fb:
            screeninfo = fcntl.ioctl(fb, 0x4600, struct.pack("8I", *[0] * 8))
            _, _, width, height, *_ = struct.unpack("8I", screeninfo)
        return width, height

    def define_camera_positions(self):
        """Определяем позиции для сетки камер с учётом обновлённых размеров и централизованного отображения."""
        main_width, main_height = self.main_camera_size
        grid_width, grid_height = self.grid_camera_size
        bt = self.border_thickness
        mp_x, mp_y = self.main_padding  # Main padding

        # Центрируем основную камеру
        positions = [(mp_x, mp_y, self.main_camera_size)]

        # Верхняя правая сетка 2x2
        for i in range(2):
            for j in range(2):
                x = main_width + mp_x + bt + j * (grid_width + bt)
                y = mp_y + i * (grid_height + bt)
                positions.append((x, y, (grid_width, grid_height)))

        # Нижняя сетка 4x4
        for i in range(4):
            for j in range(4):
                x = j * (grid_width + bt)
                y = main_height + mp_y + bt + i * (grid_height + bt)
                positions.append((x, y, (grid_width, grid_height)))

        return positions

    def create_cameras(self, base_url, channel_order):
        cameras = []
        for idx, channel in enumerate(channel_order):
            url = f"{base_url}={channel}&subtype=0"
            label = f"Camera {channel}"
            camera = Camera(url, self.camera_positions[idx], label, self.border_thickness, self.border_color)
            cameras.append(camera)
        return cameras

    async def display_streams(self):
        background = np.zeros((self.fb_height, self.fb_width, 4), dtype=np.uint8)

        try:
            fb = open(self.fb_path, "wb")
        except PermissionError:
            self.logger.error("Требуется запуск от sudo для записи в /dev/fb0.")
            return

        try:
            while True:
                start_time = time.time()

                for camera in self.cameras:
                    x, y, _ = camera.position
                    frame = camera.get_frame()
                    background[y:y + frame.shape[0], x:x + frame.shape[1], :3] = frame

                fb.seek(0)
                fb.write(background.tobytes())

                elapsed_time = time.time() - start_time
                await asyncio.sleep(max(0, self.frame_interval - elapsed_time))

        except KeyboardInterrupt:
            self.logger.info("Остановка по запросу пользователя.")
        finally:
            fb.close()
            for camera in self.cameras:
                camera.release()
