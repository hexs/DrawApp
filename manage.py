import os
import json
import cv2
from pygame import Rect
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton

from DrawApp import DrawApp
import pygame as pg


def manage(filename):
    img = cv2.imread(os.path.join('image', filename))
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
        os.makedirs(image_path, exist_ok=True)
        os.makedirs(label_path, exist_ok=True)

        # crop
        cv2.imwrite(os.path.join(image_crop_path, f"{name}.png"), imgcrop)

        # images
        print(os.path.join(image_path, fr"{filename}"))

        cv2.imwrite(os.path.join(image_path, fr"{filename}"), img)

        # labels
        file_label_name = fr"{filename}".replace(".jpg", ".txt").replace(".png", ".txt")
        with open(os.path.join(label_path, file_label_name), "w") as f:
            f.write(f'0 {x} {y} {w} {h}\n')


class Manage(DrawApp):

    def get_can_wheel(self):
        return not any([obj.rect.collidepoint(self.mouse_pos) for obj in [
            self.panel0,
            self.panel1,
            self.panel2,
            self.show_list_button,
            self.show_details_button,

            self.next_button,
            self.manage_button
        ]])

    def setup_ui(self):
        super().setup_ui()
        self.next_button = UIButton(relative_rect=Rect((100, 0), (70, 30)), text='Next', manager=self.manager,
                                    anchors={'left_target': self.show_list_button})
        self.manage_button = UIButton(relative_rect=Rect((0, 0), (70, 30)), text='Manage', manager=self.manager,
                                      anchors={'left_target': self.next_button})

    def run(self):
        listdir = os.listdir('image')
        listdir_n = 0
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.dp.fill((180, 180, 180))
            # get image surface
            # self.get_surface_from_display_capture()
            self.get_surface_from_file(os.path.join('image', listdir[listdir_n]))

            events = pg.event.get()
            for event in events:
                self.manager.process_events(event)
                self.handle_window_resize(event)
                self.wheel_drawing_moving(event)

                if event.type == pg.QUIT:
                    self.is_running = False
                # if event.type != pg.MOUSEMOTION:
                #     # if event.type == UI_BUTTON_PRESSED:
                #     print(event)
                if event.type == UI_BUTTON_PRESSED:
                    if event.ui_element == self.next_button:
                        listdir_n += 1
                        if listdir_n == len(listdir):
                            listdir_n = 0
                    if event.ui_element == self.manage_button:
                        manage(listdir[listdir_n])
                        listdir_n += 1
                        if listdir_n == len(listdir):
                            listdir_n = 0
                        self.frame_dict = {}
                        self.set_item_list()

            self.panels(events)
            self.show_rects_to_surface(self.frame_dict)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.dp)

            pg.display.update()


if __name__ == '__main__':
    app = Manage()
    app.run()
