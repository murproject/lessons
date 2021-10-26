# Пример распознавания объектов на изображении
# при помощи нейронной сети (без модуля Google Coral).
#
# При запуске на аппарате, вам потребуется скопировать
# обученные модели в директорию /home/pi/trained_models/

import os
import cv2
import time

# Воспользуемся некоторыми возможностями из библиотеки pycoral,
# чтобы примеры скриптов были более идентичными.

import tflite_runtime.interpreter as tflite
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file

try:
    import pymurapi as mur
    auv = mur.mur_init()
    IS_AUV = True

    os.chdir('/home/pi/')

    try:
        mur_view = auv.get_videoserver()
        HAVE_AUV_VIDEO_SERVER = True
    except AttributeError:
        HAVE_AUV_VIDEO_SERVER = False

except ImportError:
    IS_AUV = False

# Указываем пути к модели и списку классов.

path_model = 'trained_models/rsub_model.tflite'
path_labels = 'trained_models/rsub_labels.txt'

threshold = 0.3     # ограничение минимальной вероятности распознавания
max_detections = 4  # ограничение на максимальное число объектов в кадре

# Загружаем модель и инициализируем нейросеть.

interpreter = tflite.Interpreter(path_model)
interpreter.allocate_tensors()
labels = read_label_file(path_labels)
inference_size = common.input_size(interpreter)

# Зафиксируем время запуска для расчёта FPS.

start = time.time()
counter = 0

def process_img(img):
    global counter, start

    # Изменим размер изображения под требования модели,
    # а такжже преобразуем цветовую модель в RGB.

    img_rgb = cv2.cvtColor(cv2.resize(img, inference_size), cv2.COLOR_BGR2RGB)
    common.set_input(interpreter, img_rgb)

    # Запускаем распознавание, фиксирумя время работы.

    time_pre = time.time()
    interpreter.invoke()
    print("invoke time:", time.time() - time_pre)

    # Получаем результаты: список объектов с их границами,
    # классом и уровнем вероятности.

    objs = detect.get_objects(interpreter, threshold)[:max_detections]

    # При рисовании нам нужно будет учесть,
    # что у изображения был изменен размер,
    # а отображать объекты мы будем на оригинальном кадре.

    drawing = img.copy()
    height, width = img.shape[0], img.shape[1]
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]

    print(objs)

    exit()

    # Пройдёмся по каждому объекту в списке.

    print("objects:")
    for obj in objs:
        # Получаем границы с учётом измененённого размера изображения.
        box = obj.bbox.scale(scale_x, scale_y)
        p0 = (int(box.xmin), int(box.ymin))
        p1 = (int(box.xmax), int(box.ymax))

        percent = int(100 * obj.score)
        label = '{}% {}'.format(percent, labels[obj.id])
        print(label)
        font = cv2.FONT_HERSHEY_DUPLEX

        # Рисуем границы и подпись.
        cv2.rectangle(drawing, p0, p1, (0, 255, 0), 1)
        cv2.putText(drawing, label, (p0[0], p0[1] + 20), font, 0.7, (255, 255, 255), 1)

    # Выводим обработанное изображение.

    if IS_AUV:
        if HAVE_AUV_VIDEO_SERVER:
            mur_view.show(drawing, 0)
    else:
        cv2.imshow('img', drawing)
        cv2.waitKey(1)

    # Считаем и выводим FPS каждые 10 кадров
    if counter > 10:
        cur_time = time.time()
        seconds = cur_time - start
        fps = counter / seconds
        print('fps:', fps)
        counter = 0
        start = time.time()

# Основной цикл: поулчаем кадры и запускаем обработку.

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    while True:
        ok, img = cap.read()

        if not ok:
            print('cam read error')
            break

        process_img(img)
        counter += 1
        print()

    cap.release()

    if IS_AUV and HAVE_AUV_VIDEO_SERVER:
        mur_view.stop()

    print('done')
