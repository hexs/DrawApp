import os
import json
import cv2


def manage(filename):
    img = cv2.imread(filename)
    with open("frame_dict.json") as f:
        string = f.read()
    frame = json.loads(string)

    for name, v in frame.items():
        H, W, _ = img.shape
        x, y, w, h = v["xywh"]

        x1 = int((x - w / 2) * W)
        x2 = int((x + w / 2) * W)
        y1 = int((y - h / 2) * H)
        y2 = int((y + h / 2) * H)

        imgcrop = img[y1:y2, x1:x2]
        path = os.path.join("output")
        image_crop_path = os.path.join(path, "crop")
        image_path = os.path.join(path, "images")
        label_path = os.path.join(path, "labels")
        os.makedirs(path, exist_ok=True)
        os.makedirs(image_crop_path, exist_ok=True)
        os.makedirs(label_path, exist_ok=True)
        os.makedirs(label_path, exist_ok=True)

        # crop
        cv2.imwrite(os.path.join(image_crop_path, f"{name}.png"), imgcrop)

        # images
        cv2.imwrite(os.path.join(image_path, fr"{filename}"), img)

        # labels
        file_label_name = fr"{filename}".replace(".jpg", ".txt").replace(".png", ".txt")
        with open(os.path.join(label_path, file_label_name), "w") as f:
            f.write(f'0 {x} {y} {w} {h}\n')


if __name__ == '__main__':
    filename = 'img.png'
    manage(filename)
