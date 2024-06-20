import json
import os.path
from datetime import datetime

import cv2
from os import makedirs
from os.path import join

filename = '001.jpg'
cap = cv2.VideoCapture('http://192.168.225.137:2000/video')
_, img = cap.read()
H, W, _ = img.shape

f = open("frame_dict.json")
string = f.read()
f.close()
frame = json.loads(string)


# for name, v in frame.items():
#     x, y, w, h = v["xywh"]
#
#     x1 = int((x - w / 2) * W)
#     x2 = int((x + w / 2) * W)
#     y1 = int((y - h / 2) * H)
#     y2 = int((y + h / 2) * H)
#
#     imgcrop = img[y1:y2, x1:x2]
#     cv2.imshow('img2', imgcrop)
#     cv2.waitKey(0)
#
#     cv2.imwrite(fr"C:\PythonProjects\Test  Folder\{name}.png", imgcrop)

def crop_img(img, frame):
    output_path = join("output")
    makedirs(output_path, exist_ok=True)

    for name, v in frame.items():
        x, y, w, h = v["xywh"]

        x1 = int((x - w / 2) * W)
        x2 = int((x + w / 2) * W)
        y1 = int((y - h / 2) * H)
        y2 = int((y + h / 2) * H)

        imgcrop = img[y1:y2, x1:x2]

        image_path = join(output_path, name)
        makedirs(image_path, exist_ok=True)
        cv2.imwrite(os.path.join(image_path, datetime.now().strftime('%H%M%S.jpg')), imgcrop)


if __name__ == '__main__':
    crop_img(img, frame)
