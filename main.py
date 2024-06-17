import json
import cv2

img = cv2.imread('img.png')
H, W, _ = img.shape

f = open("frame_dict.json")
string = f.read()
f.close()
frame = json.loads(string)

for name, v in frame.items():
    x, y, w, h = v["xywh"]

    x1 = int((x - w / 2) * W)
    x2 = int((x + w / 2) * W)
    y1 = int((y - h / 2) * H)
    y2 = int((y + h / 2) * H)

    imgcrop = img[y1:y2, x1:x2]
    cv2.imshow('img2', imgcrop)
    cv2.waitKey(0)

    cv2.imwrite(fr"C:\PythonProjects\Test  Folder\{name}.png", imgcrop)
