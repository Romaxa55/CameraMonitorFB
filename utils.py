import os
import asyncio


async def initialize_display_environment(tty_number=1):
    """
    Инициализирует среду для отображения, переключаясь на указанный TTY,
    отключая курсор и очищая экран.

    :param tty_number: Номер TTY для переключения (по умолчанию 1).
    """
    # Отключаем курсор
    os.system(f"sudo setterm -cursor off > /dev/tty{tty_number}")
    # Переключаемся на указанный TTY
    os.system(f"sudo chvt {tty_number}")
    # Устанавливаем черный фон и очищаем экран
    os.system(f"sudo setterm -background black -clear > /dev/tty{tty_number}")

    # Добавляем задержку для стабилизации
    await asyncio.sleep(0.5)
