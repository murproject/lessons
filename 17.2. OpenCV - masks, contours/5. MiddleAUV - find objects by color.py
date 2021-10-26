# Пример выделения объектов по цветам, с использованием аппарата MiddleAUV.
# Этот скрипт основан на ранее описанном коде, но в этот раз мы в цикле
# будем получать кадры с камеры, обрабатывать их и выводить обработанные
# изображения в  MUR IDE.

import cv2
import numpy as np

import pymurapi as mur

auv = mur.mur_init()
mur_view = auv.get_videoserver()

colors = {
    'orange': ((  0,  80,  70), ( 14, 255, 255)),
    'yellow': (( 20, 125,  80), ( 47, 255, 255)),
    'green':  (( 54, 191, 100), ( 73, 255, 255)),
    'blue':   (( 96, 191,  85), (130, 255, 255)),
}

def calc_line_color(color):
    result = np.uint8([[[
        color[0][0] + 5,
        color[1][1],
        color[1][2],
    ]]])

    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

    result = (
        int(result[0][0][0]),
        int(result[0][0][1]),
        int(result[0][0][2]),
    )

    return result

def find_contours(img, color):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv, color[0], color[1])
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def draw_object_contour(img, contour, name):
    if cv2.contourArea(contour) < 500:
        return

    line_color = calc_line_color(colors[name])
    cv2.drawContours(drawing, [contour], 0, line_color, 2)

    moments = cv2.moments(contour)

    try:
        x = int(moments['m10'] / moments['m00'])
        y = int(moments['m01'] / moments['m00'])
        cv2.circle(drawing, (x,y), 4, line_color, -1)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(img, name, (x-30, y+30), font, 1, (255,255,255), 1)
    except ZeroDivisionError:
        pass

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    while True:
        ok, img = cap.read()

        if ok:
            drawing = img.copy()

            for name in colors:
                contours = find_contours(img, colors[name])

                if not contours:
                    continue

                for cnt in contours:
                    draw_object_contour(drawing, cnt, name)

            mur_view.show(drawing, 0)
        else:
            print('cam read error')
            break

    cap.release()
    mur_view.stop()
    print("done")


