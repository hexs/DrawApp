import os
import json
import cv2
import numpy as np
from pygame import Rect
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton
from keras import models
from DrawApp import DrawApp
import pygame as pg
from DrawApp import put_text


def predict(model, img_array, class_name):
    predictions = model.predict_on_batch(img_array)
    exp_x = [2.7 ** x for x in predictions[0]]
    percent_score_list = [round(x * 100 / sum(exp_x)) for x in exp_x]
    highest_score_index = np.argmax(predictions[0])  # 3
    highest_score_name = class_name[highest_score_index]
    highest_score_percent = percent_score_list[highest_score_index]
    return highest_score_name, highest_score_percent


class Predict(DrawApp):
    def __init__(self):
        super().__init__()
        with open('class_names.json') as f:
            self.class_name = json.loads(f.read())
        self.model = models.load_model('model_name.h5')

    def get_can_wheel(self):
        return not any([obj.rect.collidepoint(self.mouse_pos) for obj in [
            self.panel0,
            self.panel1,
            self.panel2,
            self.show_list_button,
            self.show_details_button,

            self.predict_button,
        ]])

    def setup_ui(self):
        super().setup_ui()
        self.predict_button = UIButton(relative_rect=Rect((100, 0), (70, 30)), text='Predict', manager=self.manager,
                                       anchors={'left_target': self.show_list_button})
        self.auto_predict_button = UIButton(relative_rect=Rect((0, 0), (70, 30)), text='Auto', manager=self.manager,
                                            anchors={'left_target': self.predict_button})

    def show_rects_to_surface(self, frame_dict):
        super().show_rects_to_surface(frame_dict)
        for k, v in frame_dict.items():
            _xywh = np.array(v.get('xywh'))
            _x, _y, _w, _h = _xywh
            _x1y1wh = _xywh - [_w / 2, _h / 2, 0, 0]
            _x1y1wh_px = _x1y1wh * np.tile(self.img_size_vector, 2)

            font = pg.font.Font(None, 16)
            color = [(255, 100, 0), (255, 255, 255)]
            put_text(self.scaled_img_surface, f"{v.get('res_predict')}", font, color, _x1y1wh_px[:2] + [0, 12],
                     'bottomleft')

        # scaled_img_surface to dp
        self.dp.blit(self.scaled_img_surface,
                     ((self.window_size - self.img_size_vector) / 2 + self.img_offset_vector).tolist())
        if self.can_wheel:
            self.draw_at_mouse_position()

    def predict(self):
        H, W, _ = self.img_np.shape
        for name, v in self.frame_dict.items():
            x, y, w, h = v["xywh"]

            x1 = int((x - w / 2) * W)
            x2 = int((x + w / 2) * W)
            y1 = int((y - h / 2) * H)
            y2 = int((y + h / 2) * H)

            img_crop = self.img_np[y1:y2, x1:x2]

            img_resize = cv2.cvtColor(cv2.resize(img_crop, (180, 180)), cv2.COLOR_BGR2RGB)
            img_resize = np.expand_dims(img_resize, axis=0)

            res = predict(self.model, img_resize, self.class_name)
            v['res_predict'] = res
            print(name, res)

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.dp.fill((180, 180, 180))
            self.get_np_form_url('http://192.168.225.137:2000/old-image')
            self.get_surface_form_np()

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
                    if event.ui_element == self.auto_predict_button:
                        if self.auto_predict_button.text == 'Auto':
                            self.auto_predict_button.set_text('Stop')
                            self.predict_button.disable()
                        elif self.auto_predict_button.text == 'Stop':
                            self.auto_predict_button.set_text('Auto')
                            self.predict_button.enable()
                    if event.ui_element == self.predict_button:
                        self.predict()

            if self.auto_predict_button.text == 'Stop':
                self.predict()
            self.panels(events)
            self.show_rects_to_surface(self.frame_dict)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.dp)

            pg.display.update()


if __name__ == '__main__':
    app = Predict()
    app.run()
