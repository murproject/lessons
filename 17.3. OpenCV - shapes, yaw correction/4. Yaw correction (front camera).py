# Пример корркетировки курса по полоске перед аппаратом.
#
# Учтите все особенности использования предыдущего скрипта (№3),
# т.к. в данном скрипте во многом всё аналогично.

import cv2
import numpy as np
import math

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

        if area < 50:
            return

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
def calc_error(drawing, cnt):
    moments = cv2.moments(cnt)

    try:
        x = int(moments['m10'] / moments['m00'])
        y = int(moments['m01'] / moments['m00'])
        cv2.circle(drawing, (x,y), 4, (0,0,255), -1, cv2.LINE_AA)

        error = (drawing.shape[1] / 2) - x
        return error
    except ZeroDivisionError:
        return 0


if __name__ == '__main__':
    color = (
        ( 20, 125,  80),
        ( 47, 255, 255)
    )

    cap = cv2.VideoCapture(0)

    while True:
        ok, img = cap.read()

        if not ok:
            break

        drawing = img.copy()
        contours = find_contours(img, color)

        error = 0

        if contours:
            # Вычисляем площадь для каждого контура, а затем берём контур с наибольшей
            # площадью, но только если он совпадает с искомой фигурой.
            areas = [
                cv2.contourArea(cnt) if (detect_shape(drawing, cnt) == 'rectangle') else 0 for cnt in contours
            ]

            if (len(areas) > 0) and (max(areas) > 500):
                cnt = contours[np.argmax(areas)]

                error = calc_error(drawing, cnt)
                print(error)

                cv2.line(drawing, (int(img.shape[1] / 2), 0), (int(img.shape[1] / 2), img.shape[0]), (255,255,255), 1)

                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(drawing, 'error: %d' % error, (5, 30), font, 1, (255,255,255), 1, cv2.LINE_AA)

        if IS_AUV:
            # Задаём тягу, прямо пропорциональную найденному углу отклонения.
            power = max(min(error * 0.1, 50), -50)
            auv.set_motor_power(1,  power)
            auv.set_motor_power(2, -power)

            if HAVE_AUV_VIDEO_SERVER:
                mur_view.show(drawing, 0)
        else:
            cv2.imshow('img', drawing)
            cv2.waitKey(1)

    cap.release()

    if IS_AUV and HAVE_AUV_VIDEO_SERVER:
        mur_view.stop()

    print("done")


