# Пример распознавания объектов на изображении при помощи
# нейронной сети с использованием модуля Google Coral.
#
# При запуске на аппарате, вам потребуется скопировать
# обученные модели в директорию /home/pi/trained_models/

import os
import cv2
import time

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference

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

path_model = 'trained_models/rsub_model_edgetpu.tflite'
path_labels = 'trained_models/rsub_labels.txt'

threshold = 0.3
max_detections = 4

interpreter = make_interpreter(path_model)
interpreter.allocate_tensors()
labels = read_label_file(path_labels)
inference_size = input_size(interpreter)

start = time.time()
counter = 0

def process_img(img):
    global counter, start

    img_rgb = cv2.cvtColor(cv2.resize(img, inference_size), cv2.COLOR_BGR2RGB)

    time_pre = time.time()
    run_inference(interpreter, img_rgb.tobytes())
    print("inference time:", time.time() - time_pre)
    objs = get_objects(interpreter, threshold)[:max_detections]

    drawing = img.copy()

    height, width = img.shape[0], img.shape[1]
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]

    print("objects:")
    for obj in objs:
        box = obj.bbox.scale(scale_x, scale_y)
        point0 = (int(box.xmin), int(box.ymin))
        point1 = (int(box.xmax), int(box.ymax))

        percent = int(100 * obj.score)
        label = '{}% {}'.format(percent, labels[obj.id])
        print(label)
        font = cv2.FONT_HERSHEY_DUPLEX

        cv2.rectangle(drawing, point0, point1, (0, 255, 0), 1)
        cv2.putText(drawing, label, (point0[0], point0[1] + 20), font, 0.7, (255, 255, 255), 1)

    if IS_AUV:
        if HAVE_AUV_VIDEO_SERVER:
            mur_view.show(drawing, 0)
    else:
        cv2.imshow('img', drawing)
        cv2.waitKey(1)

    if counter > 10:
        cur_time = time.time()
        seconds = cur_time - start
        fps = counter / seconds
        print('fps:', fps)
        counter = 0
        start = time.time()

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

