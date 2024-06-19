import json
import os.path

import cv2
from os import makedirs
from os.path import join

filename = 'img (1).jpg'
img = cv2.imread(join(r'C:\PythonProjects\DrawApp\image', filename))
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
    for name, v in frame.items():
        x, y, w, h = v["xywh"]

        x1 = int((x - w / 2) * W)
        x2 = int((x + w / 2) * W)
        y1 = int((y - h / 2) * H)
        y2 = int((y + h / 2) * H)

        imgcrop = img[y1:y2, x1:x2]

        path = join("output")
        makedirs(path, exist_ok=True)
        image_path = join(path, "images")
        makedirs(image_path, exist_ok=True)
        label_path = join(path, "labels")
        makedirs(label_path, exist_ok=True)

        cv2.imwrite(os.path.join(image_path, fr"{filename}"), img)
        f = open(os.path.join(label_path, fr"{filename}".replace(".jpg", ".txt")), "w")
        f.write(f'0 {x} {y} {w} {h}\n')

crop_img(img, frame)

    # path = (os.path.join("C:\\", "PythonProjects", "Test folder1"))
    # # print(path)
    # os.makedirs(path, exist_ok=True)
    # cv2.imwrite(os.path.join(path ,fr"{name}.png"), imgcrop)
    #
    # path = (os.path.join("C:\\", "PythonProjects", "Test folder2"))
    # os.makedirs(path, exist_ok=True)
    #
    # path = (os.path.join("C:\\", "PythonProjects", "Test folder3"))
    # os.makedirs(path, exist_ok=True)
