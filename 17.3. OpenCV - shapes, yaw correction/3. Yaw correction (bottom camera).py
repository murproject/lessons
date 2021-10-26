# Пример корркетировки курса по полоске на дне.
#
# Этот скрипт может быть запущен на аппарате MiddleAUV,
# тогда будут задействованы движители, а также обработанное
# изображение будет передаваться в MUR IDE, если такая
# возможность поддерживается вашим аппаратом.
#
# Имейте ввиду, что возможно вам потребуется скорректировать
# диапазоны цветов под ваши условия, установить номер камеры,
# а также индексы и направления движителей.
#
# Данный скрипт можно запустить и на компьютере (без аппарата),
# тогда будет лишь производиться обработка изображения и его
# вывод через imshow, а код управления моторами не будет использоваться.

import cv2
import numpy as np
import math

# Данная конструкция позволяет запускать скрипт как на аппарате MiddleAUV,
# так и на обычном компьюьтере или Raspberry Pi. В случае, если при попытке
# импорта библиотеки pymurapi возникает ошибка, то будем считать, что
# скрипт выполняется не на аппарате. И тогда для вывода изображений
# мы будем задействовать imshow.

try:
    import pymurapi as mur
    auv = mur.mur_init()
    IS_AUV = True

    try:
        mur_view = auv.get_videoserver()
        HAVE_AUV_VIDEO_SERVER = True
    except AttributeError:
        HAVE_AUV_VIDEO_SERVER = False

except ImportError:
    IS_AUV = False

def find_contours(img, color):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv, color[0], color[1])
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def detect_shape(drawing, cnt):
    try:
        area = cv2.contourArea(cnt)

        if area < 500:
            return None

        (circle_x, circle_y), circle_radius = cv2.minEnclosingCircle(cnt)
        circle_area = circle_radius ** 2 * math.pi

        rectangle = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rectangle)
        box = np.int0(box)
        rectangle_area = cv2.contourArea(box)
        rect_w, rect_h = rectangle[1][0], rectangle[1][1]
        aspect_ratio = max(rect_w, rect_h) / min(rect_w, rect_h)

        triangle = cv2.minEnclosingTriangle(cnt)[1]
        triangle = np.int0(triangle)
        triangle_area = cv2.contourArea(triangle)

        shapes_areas = {
            'circle': circle_area,
            'rectangle' if aspect_ratio > 1.2 else 'square': rectangle_area,
            'triangle': triangle_area,
        }

        diffs = {
            name: abs(area - shapes_areas[name]) for name in shapes_areas
        }

        shape_name = min(diffs, key=diffs.get)

        line_color = (255,255,255)

        if shape_name == 'circle':
            cv2.circle(drawing, (int(circle_x), int(circle_y)), int(circle_radius), line_color, 2, cv2.LINE_AA)

        if shape_name == 'rectangle' or shape_name == 'square':
            cv2.drawContours(drawing, [box], 0, line_color, 2, cv2.LINE_AA)

        if shape_name == 'triangle':
            cv2.drawContours(drawing, [triangle], 0, line_color, 2, cv2.LINE_AA)

        return shape_name
    except:
        return None

# Функция для вычисления угла отклонения от полоски.
def calc_angle(drawing, cnt):
    try:
        rectangle = cv2.minAreaRect(cnt)

        box = cv2.boxPoints(rectangle)
        box = np.int0(box)
        cv2.drawContours(drawing, [box], 0, (0,0,255), 3)

        # К сожалению, мы не можем использовать тот угол,
        # который входит в вывод функции minAreaRect,
        # т.к. нам необходимо ориентироваться именно по
        # длинной стороне полоски. Находим длинную сторону.

        edge_first = np.int0((box[1][0] - box[0][0], box[1][1] - box[0][1]))
        edge_second = np.int0((box[2][0] - box[1][0], box[2][1] - box[1][1]))

        edge = edge_first
        if cv2.norm(edge_second) > cv2.norm(edge_first):
            edge = edge_second

        # Вычисляем угол по длинной стороне.
        angle = -((180.0 / math.pi * math.acos(edge[0] / (cv2.norm((1, 0)) * cv2.norm(edge)))) - 90)

        return angle if not math.isnan(angle) else 0
    except:
        return 0

if __name__ == '__main__':
    color = (
        (  0,  80,  70),
        ( 14, 255, 255),
    )

    cap = cv2.VideoCapture(0)

    while True:
        ok, img = cap.read()

        if not ok:
            break

        drawing = img.copy()
        contours = find_contours(img, color)

        angle = 0

        if contours:
            # Вычисляем площадь для каждого контура, а затем берём контур с наибольшей
            # площадью, но только если он совпадает с искомой фигурой.
            areas = [
                cv2.contourArea(cnt) if (detect_shape(drawing, cnt) == 'rectangle') else 0 for cnt in contours
            ]

            if (len(areas) > 0) and (max(areas) > 500):
                cnt = contours[np.argmax(areas)]

                angle = calc_angle(drawing, cnt)
                print(angle)

                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(drawing, 'angle: %d' % angle, (5, 30), font, 1, (255,255,255), 1, cv2.LINE_AA)

        if IS_AUV:
            # Задаём тягу, прямо пропорциональную найденному углу отклонения.
            # Чем больше отклонение, тем сильнее будет тяга на движителях.
            #
            # angle - отклонение угла аппарата от угла вращения полоски.

            power = max(min(angle * 0.75, 50), -50)
            auv.set_motor_power(1, -power)
            auv.set_motor_power(2,  power)

            # Таким образом, у нас получился простейший
            # пропорциональный регулятор (proportional controller, он же P-регулятор).

            if HAVE_AUV_VIDEO_SERVER:
                mur_view.show(drawing, 0)
        else:
            cv2.imshow('img', drawing)
            cv2.waitKey(1)

    cap.release()

    if HAVE_AUV_VIDEO_SERVER:
        mur_view.stop()

    print("done")


