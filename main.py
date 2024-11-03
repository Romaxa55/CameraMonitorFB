import asyncio
from camera_display import CameraDisplay
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)


async def main():
    display = CameraDisplay()
    await display.display_streams()


if __name__ == "__main__":
    asyncio.run(main())
