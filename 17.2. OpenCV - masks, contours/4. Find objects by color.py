# Пример выделения контуров объектов по заданным цветам.

import cv2
import numpy as np

# Для начала, создадим словарь, который хранит
# диапазоны цветов и их наименования.

colors = {
    'orange': ((  0,   0,   0), ( 30, 200, 255)),
    'yellow': (( 30,  80,   0), ( 70, 200, 255)),
    'blue':   (( 94,  96,  96), (120, 255, 255)),
}

# В последствии мы захотим раскрашивать контуры в те цвета,
# которым они соответствуют. Для дальнейшего удобства,
# опищем функцию, которая преобразует верхнее значение
# диапазона к BGR-цвету.
#
# Сначала создадим изображение из одного пикселя с нужным нам цветом,
# (отнимем от оттенка верхнего диапазона небольшое число, чтобы
# чтобы цвет был немного смещен от границы диапазона), далее произведём
# преобразование уже знакомой нам функцией cvtColor, после чего
# возвращаем массив, содержащий каждый из компонентов цвета.

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

# Выделим поиск контуров в отдельную функцию.

def find_contours(img, color):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_mask = cv2.inRange(img_hsv, color[0], color[1])
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

# Напишем функцию для отрисовки контуров, которая включает
# отсеивание слишком маленьких контуров, вычисление координат
# центра контура, а также отрисовку как самого контура, так и
# его центра с подписью соответствующего цвета.

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

# Теперь опишем основной алгоритм работы. Благодаря
# разделению на функции, мы получили более читаемый
# и простой код, глядя на который сразу становится понятно,
# что именно будет происходить в основном цикле:
# после поулчения изображения мы находим контуры для
# каждого из цветов в словаре, и при наличии контуров
# вызываем отрисовку каждого контура.

if __name__ == '__main__':
    img = cv2.imread('imgs/pool_line_bin.jpg')
    drawing = img.copy()

    for name in colors:
        contours = find_contours(img, colors[name])

        if not contours:
            continue

        for cnt in contours:
            draw_object_contour(drawing, cnt, name)

    cv2.imshow('drawing', drawing)
    cv2.waitKey(0)
