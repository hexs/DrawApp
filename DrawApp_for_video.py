import os
import json
import re
import cv2
from pygame import Rect
from pygame_gui import UI_BUTTON_PRESSED
from pygame_gui.elements import UIButton
import DrawApp
import pygame as pg


# remove File extension
def remove_extension(file_name, new_file_extension=''):
    name_without_extension = re.sub(r'\.[^.]+$', new_file_extension, file_name)
    return name_without_extension


class Manage(DrawApp.DrawApp):
    def get_frame_from_frame_dict_time(self):
        frames = self.frame_dict_time.get(f'{self.current_frame_n}')
        if frames:
            self.frame_dict = frames
        else:
            self.frame_dict = {}
        self.set_item_list()

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
                if event.type == UI_BUTTON_PRESSED and event.ui_element == self.add_button:
                    self.frame_dict_time[f'{self.current_frame_n}'] = self.frame_dict
                    self.write_frame_json(self.frame_dict_time, os.path.join('videos',json_file_name))

                if event.type == 32876:  # slider update
                    if event.ui_object_id == 'panel.horizontal_slider':
                        self.get_frame_from_frame_dict_time()
                if event.type == pg.KEYDOWN:
                    if event.kay == 1073741903: #r:


            self.show_rects_to_surface(self.frame_dict)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.dp)

            pg.display.update()


if __name__ == '__main__':
    app = Manage()
    app.run()
