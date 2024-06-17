import os.path
import json
import cv2


def crop_img(img, frame):
    for name, v in frame.items():
        x, y, w, h = v["xywh"]

        x1 = int((x - w / 2) * W)
        x2 = int((x + w / 2) * W)
        y1 = int((y - h / 2) * H)
        y2 = int((y + h / 2) * H)

        imgcrop = img[y1:y2, x1:x2]
        os.makedirs('crop', exist_ok=True)
        cv2.imwrite(fr"crop\{name}.png", imgcrop)


if __name__ == '__main__':
    img = cv2.imread('img.png')
    H, W, _ = img.shape

    f = open("frame_dict.json")
    string = f.read()
    f.close()
    frame = json.loads(string)

    crop_img(img, frame)
