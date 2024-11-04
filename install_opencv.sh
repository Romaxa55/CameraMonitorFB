#!/bin/bash

# Обновляем и устанавливаем необходимые зависимости
sudo apt update
sudo apt install -y build-essential cmake git pkg-config libswscale-dev libavcodec-dev libavutil-dev

# Устанавливаем дополнительные Python пакеты
pip3 install numpy

cd opencv || exit
mkdir build
cd build || exit

# Запускаем CMake с заданными параметрами
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D WITH_TBB=ON \
      -D BUILD_NEW_PYTHON_SUPPORT=ON \
      -D WITH_V4L=ON \
      -D INSTALL_C_EXAMPLES=ON \
      -D INSTALL_PYTHON_EXAMPLES=ON \
      -D BUILD_EXAMPLES=ON \
      -D WITH_QT=ON \
      -D WITH_OPENGL=ON \
      -D WITH_GSTREAMER=ON \
      -D WITH_FFMPEG=ON \
      -D WITH_VA=ON \
      -D WITH_VA_INTEL=ON \
      -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules ..

# Собираем и устанавливаем OpenCV
make -j$(nproc)  # Используем все доступные ядра для ускорения сборки
sudo make install
sudo ldconfig  # Обновляем ссылки на библиотеки

# Проверка установки
echo "OpenCV установлен!"
pkg-config --modversion opencv4
