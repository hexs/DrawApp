import os
import json
import re
from pprint import pprint
import random
from typing import Union
import os
from typing import Union, Dict, List
import cv2
import numpy as np
from pygame import Rect
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton
import DrawApp
import pygame as pg
import shutil
from PIL import ImageEnhance, Image


# remove File extension
def remove_extension(file_name, new_file_extension=''):
    name_without_extension = re.sub(r'\.[^.]+$', new_file_extension, file_name)
    return name_without_extension


def write_data_YOLO(frame_dict_time, video_file):
    base_path = 'output_for_YOLO'

    # delete old file
    if base_path in os.listdir():
        shutil.rmtree(base_path)

    # write new data
    paths = {
        'train': {'images': os.path.join(base_path, 'train', 'images'),
                  'labels': os.path.join(base_path, 'train', 'labels')},
        'valid': {'images': os.path.join(base_path, 'valid', 'images'),
                  'labels': os.path.join(base_path, 'valid', 'labels')}
    }

    for path in paths.values():
        for subpath in path.values():
            os.makedirs(subpath, exist_ok=True)

    cap = cv2.VideoCapture(os.path.join('videos', video_file))

    for frame_n, frames in frame_dict_time.items():
        frame_n = int(frame_n)
        set_type = 'train' if random.randint(0, 5) else 'valid'

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n - 1)
        img = cap.read()[1]

        for i in range(5):
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            if i:  # if i == 0 save original image
                enhancers = [
                    ImageEnhance.Brightness(pil_img),
                    ImageEnhance.Contrast(pil_img),
                    ImageEnhance.Sharpness(pil_img),
                    ImageEnhance.Color(pil_img)
                ]

                for enhancer in enhancers:
                    factor = random.uniform(0.5, 1.5)
                    pil_img = enhancer.enhance(factor)

            base_name = f'{remove_extension(video_file)} {frame_n} {i}'
            pil_img.save(os.path.join(paths[set_type]['images'], f'{base_name}.png'))

            with open(os.path.join(paths[set_type]['labels'], f'{base_name}.txt'), 'w') as f:
                f.write('\n'.join(f"{name[0]} {' '.join(map(str, v['xywh']))}" for name, v in frames.items()))

        print(frame_n, '\n'.join(f"{name[0]} {' '.join(map(str, v['xywh']))}" for name, v in frames.items()), '',
              sep='\n')


class Manage(DrawApp.DrawApp):
    def get_frame_from_frame_dict_time(self):
        frames = self.frame_dict_time.get(f'{self.current_frame_n}')
        if frames:
            self.frame_dict = frames
        else:
            self.frame_dict = {}
        self.set_item_list()

    def setup_ui(self):
        super().setup_ui()
        self.save_data_for_YOLO_button = UIButton(relative_rect=Rect((100, 0), (150, 30)),
                                                  text='Save data for YOLO',
                                                  manager=self.manager,
                                                  anchors={'left_target': self.show_list_button})

    def run(self):
        video_file_name = '240626-141535.avi'
        json_file_name = remove_extension(video_file_name, '.json')
        video_file_path = os.path.join('videos', video_file_name)

        self.setup_video_file(video_file_path)
        self.frame_dict_time = self.load_frame_json('videos', json_file_name)
        self.get_frame_from_frame_dict_time()

        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.dp.fill((180, 180, 180))
            self.get_np_form_video_file()

            events = pg.event.get()

            for event in events:
                self.manager.process_events(event)
                self.handle_window_resize(event)
                self.wheel_drawing_moving(event)

            self.update_panels(events)
            for event in events:
                if event.type == pg.QUIT:
                    self.is_running = False

                # PRESSED add_button
                if event.type == UI_BUTTON_PRESSED and event.ui_element == self.save_data_for_YOLO_button:
                    write_data_YOLO(self.frame_dict_time, video_file_name)

                if event.type == UI_BUTTON_PRESSED and event.ui_element == self.add_button:
                    self.frame_dict_time[f'{self.current_frame_n}'] = self.frame_dict
                    self.write_frame_json(self.frame_dict_time, os.path.join('videos', json_file_name))

                if event.type == 32876:  # slider update
                    if event.ui_object_id == 'panel.horizontal_slider':
                        self.get_frame_from_frame_dict_time()
                if event.type == pg.KEYDOWN:
                    if event.kay == 1073741903:  # r:
                        pass

            self.show_rects_to_surface(self.frame_dict)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.dp)

            pg.display.update()


if __name__ == '__main__':
    app = Manage()
    app.run()

file_path = r'C:\PythonProjects\j\DrawApp\videos\240626-141535.json'
dir_path = r'C:\PythonProjects\j\DrawApp\videos'
videos_path = r'C:\PythonProjects\j\DrawApp\videos'
file_name = '240626-141535.json'
base_name = '240626-141535'
