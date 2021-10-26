# Пример захвата изображения с камеры на аппарате MiddleAUV.
# Имейте ввиду, что возможность вывода видеопотока в MUR IDE
# с помощью auv.get_videoserver доступна лишь в достаточно
# новых аппаратах (MiddleAUV, произведённые с мая 2021 года)

from time import sleep
from datetime import datetime
import cv2

import pymurapi as mur

auv = mur.mur_init()
mur_view = auv.get_videoserver()

cap = cv2.VideoCapture(0)

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

font = cv2.FONT_HERSHEY_DUPLEX

while True:
    ok, img = cap.read()

    if ok: # Если кадр успешно прочитан
        # Создадим копию изображения, на которой будем рисовать.
        drawing = img.copy()

        # Выводим на изображении текущее время ("водяной знак").
        cv2.putText(drawing, get_timestamp(), (10, 30), font, 1, (255,255,255), 2)

        # Отображаем обработанный кадр в MUR IDE
        mur_view.show(drawing, 0)

    else: # При ошибке чтения кадра.
        print('camera read error')
        break

cap.release()
mur_view.stop()
print("done")
