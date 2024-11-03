import asyncio

import config
from camera_display import CameraDisplay
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)


async def main():
    display = CameraDisplay()
    await display.initialize_framebuffer()
    await display.create_cameras(config.CHANNELS)
    await display.display_streams()

    await display.close_framebuffer()

if __name__ == "__main__":
    asyncio.run(main())
