# Описанные фигуры.
# Выделяем контур из картинки, а затем рисуем описанные вокруг него фигуры.

import cv2
import numpy as np
import math

def find_contours(img, color):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv, color[0], color[1])
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

if __name__ == '__main__':
    img = cv2.imread('imgs/pool_two_bins.jpg')
    drawing = img.copy()

    color = (
        ( 30,  80,   0),
        ( 70, 200, 255),
    )

    contours = find_contours(img, color)

    if contours:
        for cnt in contours:
            if cv2.contourArea(cnt) < 50:
                continue

            # Нарисуем выделенный контур
            cv2.drawContours(drawing, [cnt], 0, (255,255,255), 2)

            # Описанная окружность.
            (circle_x, circle_y), circle_radius = cv2.minEnclosingCircle(cnt)
            circle_area = circle_radius ** 2 * math.pi
            print('circle area:', circle_area)
            cv2.circle(drawing, (int(circle_x), int(circle_y)), int(circle_radius), (255,255,0), 2)

            # Описанный эллипс
            ellipse = cv2.fitEllipse(cnt)
            (ellipse_x, ellipse_y), (ellipse_h, ellipse_w), ellipse_angle = ellipse
            ellipse_area = math.pi * (ellipse_h / 2) * (ellipse_w / 2)
            print('ellipse_area:', ellipse_area)
            cv2.ellipse(drawing, ellipse, (255,0,0), 2)

            # Описанный прямоугольник (без вращения)
            (bounding_x, bounding_y, bounding_w, bounding_h) = cv2.boundingRect(cnt)
            bounding_pos1 = (bounding_x, bounding_y)
            bounding_pos2 = (bounding_x + bounding_w, bounding_y + bounding_h)
            cv2.rectangle(drawing, bounding_pos1, bounding_pos2, (255,0,255), 2)

            # Описанный прямоугольник (с вращением)
            rectangle = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rectangle)
            box = np.int0(box)
            rectangle_area = cv2.contourArea(box)
            print('rectangle_area:', rectangle_area)
            cv2.drawContours(drawing, [box], 0, (0,150,255), 2)

            # Описанный треугольник
            try:
                triangle = cv2.minEnclosingTriangle(cnt)[1]
                triangle = np.int0(triangle)
                triangle_area = cv2.contourArea(triangle)
                cv2.drawContours(drawing, [triangle], 0, (100,255,150), 2)
            except:
                triangle_area = 0
            print('triangle_area:', triangle_area)

            print()

    cv2.imshow('drawing', drawing)
    cv2.waitKey(0)