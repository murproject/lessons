# Пример распознавания объектов по форме.
# Сначала выделяем контуры зелёных объектов, а затем определяем
# наиболее похожую фигуру и делаем соответствующую подпись.

import cv2
import numpy as np
import math

def find_contours(img, color):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv, color[0], color[1])
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

if __name__ == '__main__':
    img = cv2.imread('imgs/green_shapes.jpg')
    drawing = img.copy()

    color = (
        ( 56, 192,  90),
        ( 74, 255, 255),
    )

    contours = find_contours(img, color)

    if contours:
        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area < 500:
                continue

            # Описанная окружность.
            (circle_x, circle_y), circle_radius = cv2.minEnclosingCircle(cnt)
            circle_area = circle_radius ** 2 * math.pi

            # Описанный прямоугольник (с вращением)
            rectangle = cv2.minAreaRect(cnt)

            # Получим контур описанного прямоугольника
            box = cv2.boxPoints(rectangle)
            box = np.int0(box)

            # Вычислим площадь и соотношение сторон прямоугольника.
            rectangle_area = cv2.contourArea(box)
            rect_w, rect_h = rectangle[1][0], rectangle[1][1]
            aspect_ratio = max(rect_w, rect_h) / min(rect_w, rect_h)

            # Описанный треугольник
            try:
                triangle = cv2.minEnclosingTriangle(cnt)[1]
                triangle = np.int0(triangle)
                triangle_area = cv2.contourArea(triangle)
            except:
                triangle_area = 0

            # Заполним словарь, который будет содержать площади каждой из описанных фигур
            shapes_areas = {
                'circle': circle_area,
                'rectangle' if aspect_ratio > 1.25 else 'square': rectangle_area,
                'triangle': triangle_area,
            }

            # Теперь заполним аналогичный словарь, который будет содержать
            # разницу между площадью контора и площадью каждой из фигур.
            diffs = {
                name: abs(area - shapes_areas[name]) for name in shapes_areas
            }

            # Получаем имя фигуры с наименьшей разницой площади.
            shape_name = min(diffs, key=diffs.get)

            line_color = (0,100,255)

            # Нарисуем соответствующую описанную фигуру вокруг контура

            if shape_name == 'circle':
                cv2.circle(drawing, (int(circle_x), int(circle_y)), int(circle_radius), line_color, 2, cv2.LINE_AA)

            if shape_name == 'rectangle' or shape_name == 'square':
                cv2.drawContours(drawing, [box], 0, line_color, 2, cv2.LINE_AA)

            if shape_name == 'triangle':
                cv2.drawContours(drawing, [triangle], 0, line_color, 2, cv2.LINE_AA)

            # вычислим центр, нарисуем в центре окружность и ниже подпишем
            # текст с именем фигуры, которая наиболее похожа на исследуемый контур.

            moments = cv2.moments(cnt)

            try:
                x = int(moments['m10'] / moments['m00'])
                y = int(moments['m01'] / moments['m00'])
                cv2.circle(drawing, (x,y), 4, line_color, -1, cv2.LINE_AA)

                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(drawing, shape_name, (x-40, y+31), font, 1, (  0,  0,  0), 4, cv2.LINE_AA)
                cv2.putText(drawing, shape_name, (x-41, y+30), font, 1, (255,255,255), 2, cv2.LINE_AA)
            except ZeroDivisionError:
                pass

    cv2.imshow('drawing', drawing)
    cv2.waitKey(0)
