import asyncio

import config
from camera_display import CameraDisplay
import logging

from utils import initialize_display_environment

# Настройка логгера
logging.basicConfig(level=logging.INFO)


async def main():
    await initialize_display_environment(tty_number=7)
    display = CameraDisplay()
    await display.initialize_framebuffer()  # Инициализация фреймбуфера и запуск цикла записи
    await display.create_cameras(config.CHANNELS)  # Создание камер и их отображение в фоновом режиме

    try:
        # Периодическое обновление, удерживающее основную программу активной
        while True:
            await asyncio.sleep(1)  # Поддерживаем цикл, пока не будет получен сигнал завершения
    except KeyboardInterrupt:
        pass
    finally:
        await display.close_framebuffer()  # Корректное завершение при выходе из программы

if __name__ == "__main__":
    asyncio.run(main())
