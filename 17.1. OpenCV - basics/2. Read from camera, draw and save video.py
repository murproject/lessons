# Получаем кадры с камеры, рисуем на каждом кадре дату и время,
# а также записываем видео в файл.

from datetime import datetime

import cv2
print('OpenCV version:', cv2.__version__)

# Определим функцию для получения строки с текущей датой и врменем.
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

font = cv2.FONT_HERSHEY_DUPLEX

# Открываем видеопоток с камеры.
cap = cv2.VideoCapture(0)

# Прочитаем один кадр, чтобы узнать его размер.
ok, img = cap.read()

if ok:
    height, width = img.shape[0], img.shape[1]
else:
    print('camera read error')
    exit()

# Инициализируем запись видео в файл. Получаем код
# для кодека MotionJPEG, а затем откроем файл на запись.
# Также указываем частоту кадров (например, 25 кадров в секунду),
# а также разрешение (размер кадра)

fourcc=cv2.VideoWriter_fourcc(*'MJPG')

vid = cv2.VideoWriter(
    'video_{}.mkv'.format(get_timestamp()),
    fourcc, 25.0, (width, height)
)

# Теперь в бесконечном цикле будем читать кадры, обрабатывать их,
# отображать в окне и сохранять в видео.

while True:
    # Читаем кадр и также получаем статус чтения.
    ok, img = cap.read()

    if ok: # Если кадр успешно прочитан
        # Создадим копию изображения, на которой будем рисовать.
        drawing = img.copy()

        # Выводим на изображении текущее время ("водяной знак").
        cv2.putText(drawing, get_timestamp(), (10, 20), font, 0.5, (255,255,255), 1)

        # Записываем текущий кадр в файл.
        vid.write(drawing)

        # Показываем текущий кадр в окне.
        cv2.imshow('camera', drawing)

        # Реализовываем прекращение работы при нажатии любой клавиши.
        pressed_key = cv2.waitKey(1)
        if pressed_key != -1:
            break

    else: # При ошибке чтения кадра.
        print('camera read error')
        break

# Освобождаем открытые видеопотоки.

cap.release()
vid.release()

# Закрываем все созданные окна.
cv2.destroyAllWindows()