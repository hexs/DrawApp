import json
import math
import os
import random
import urllib.request

import cv2
import numpy as np
from PIL import ImageGrab, Image
from typing import Union, Dict, Tuple, List, Optional, Any
import pygame as pg
from numpy import ndarray, dtype
from pygame import Rect
from pygame_gui import UIManager, UI_BUTTON_PRESSED
from pygame_gui.elements import UITextEntryLine, UIWindow, UIImage, UILabel
from pygame_gui.elements import UIButton
from pygame_gui.elements.ui_selection_list import UISelectionList
from pygame_gui.elements.ui_vertical_scroll_bar import UIVerticalScrollBar
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.ui_element import ObjectID
from pygame_gui.core.gui_type_hints import RectLike
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface


def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=5):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length

    if (x1 == x2):
        y_coordinates = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
        x_coordinates = [x1] * len(y_coordinates)
    elif (y1 == y2):
        x_coordinates = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
        y_coordinates = [y1] * len(x_coordinates)
    else:
        a = abs(x2 - x1)
        b = abs(y2 - y1)
        c = round(math.sqrt(a ** 2 + b ** 2))
        dx = dl * a / c
        dy = dl * b / c

        x_coordinates = [x for x in np.arange(x1, x2, dx if x1 < x2 else -dx)]
        y_coordinates = [y for y in np.arange(y1, y2, dy if y1 < y2 else -dy)]

    next_coordinates = list(zip(x_coordinates[1::2], y_coordinates[1::2]))
    last_coordinates = list(zip(x_coordinates[0::2], y_coordinates[0::2]))
    for (x1, y1), (x2, y2) in zip(next_coordinates, last_coordinates):
        start = (round(x1), round(y1))
        end = (round(x2), round(y2))
        pg.draw.line(surf, color, start, end, width)


def load_frame_dict():
    if 'frame_dict.json' in os.listdir():
        with open('frame_dict.json') as f:
            string = f.read()
        return json.loads(string)
    else:
        return {}


def write_frame_dict(frame_dict):
    with open('frame_dict.json', 'w') as f:
        f.write(json.dumps(frame_dict, indent=4))


def random_text(length=4, chars='abcdefghijklmnopqrstuvwxyz', skip_list=[]):
    n_loop = 0
    while True:
        res = '_' + (''.join(random.choice(chars) for _ in range(length)))
        if res not in skip_list:
            return res
        else:
            n_loop += 1
            if n_loop > 10:
                length += 1


def put_text(surface, text, font, color, xy, anchors=None):
    if len(color) == 2:
        color, color2 = color
    else:
        color2 = None
    text_surface = font.render(text, True, color, color2)
    text_rect = text_surface.get_rect()
    if anchors == 'topleft':
        text_rect.topleft = xy
    elif anchors == 'topright':
        text_rect.topright = xy
    elif anchors == 'bottomleft':
        text_rect.bottomleft = xy
    elif anchors == 'bottomright':
        text_rect.bottomright = xy
    else:
        text_rect.center = xy
    surface.blit(text_surface, text_rect)


class UISelectionListWithDelete(UISelectionList):
    def __init__(self,
                 relative_rect: RectLike,
                 item_list: Union[List[str], List[Tuple[str, str]]],
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 parent_element: Optional[UIElement] = None,
                 object_id: Optional[Union[ObjectID, str]] = None,
                 anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
                 visible: int = 1,
                 default_selection: Optional[Union[
                     str, Tuple[str, str],  # Single-selection lists
                     List[str], List[Tuple[str, str]]  # Multi-selection lists
                 ]] = None,
                 ):
        super().__init__(
            relative_rect=relative_rect,
            item_list=item_list,
            manager=manager,
            allow_multi_select=False,
            allow_double_clicks=True,
            container=container,
            starting_height=1,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
            default_selection=default_selection
        )

    def update(self, time_delta: float):
        super().update(time_delta)

        if self.scroll_bar is not None and self.scroll_bar.check_has_moved_recently():
            list_height_adjustment = min(self.scroll_bar.start_percentage *
                                         self.total_height_of_list,
                                         self.lowest_list_pos)
            for index, item in enumerate(self.item_list):
                new_height = int((index * self.list_item_height) - list_height_adjustment)
                if -self.list_item_height <= new_height <= self.item_list_container.relative_rect.height:
                    if item['delete_button'] is not None:
                        item['delete_button'].set_relative_position(
                            (self.item_list_container.relative_rect.width - 20, new_height))
                else:
                    if item['delete_button'] is not None:
                        item['delete_button'].kill()
                        item['delete_button'] = None

    def set_item_list(self, new_item_list: Union[List[str], List[Tuple[str, str]]]):
        self._raw_item_list = new_item_list
        self.item_list = []
        index = 0
        for new_item in new_item_list:
            if isinstance(new_item, str):
                new_item_list_item = {'text': new_item,
                                      'button_element': None,
                                      'delete_button': None,
                                      'selected': False,
                                      'object_id': '#item_list_item',
                                      'height': index * self.list_item_height}
            elif isinstance(new_item, tuple):
                new_item_list_item = {'text': new_item[0],
                                      'button_element': None,
                                      'delete_button': None,
                                      'selected': False,
                                      'object_id': new_item[1],
                                      'height': index * self.list_item_height}
            else:
                raise ValueError('Invalid item list')

            self.item_list.append(new_item_list_item)
            index += 1

        self.total_height_of_list = self.list_item_height * len(self.item_list)
        self.lowest_list_pos = (self.total_height_of_list -
                                self.list_and_scroll_bar_container.relative_rect.height)
        inner_visible_area_height = self.list_and_scroll_bar_container.relative_rect.height

        if self.total_height_of_list > inner_visible_area_height:
            # we need a scroll bar
            self.current_scroll_bar_width = self.scroll_bar_width
            percentage_visible = inner_visible_area_height / max(self.total_height_of_list, 1)

            if self.scroll_bar is not None:
                self.scroll_bar.reset_scroll_position()
                self.scroll_bar.set_visible_percentage(percentage_visible)
                self.scroll_bar.start_percentage = 0
            else:
                self.scroll_bar = UIVerticalScrollBar(Rect(-self.scroll_bar_width,
                                                           0,
                                                           self.scroll_bar_width,
                                                           inner_visible_area_height),
                                                      visible_percentage=percentage_visible,
                                                      manager=self.ui_manager,
                                                      parent_element=self,
                                                      container=self.list_and_scroll_bar_container,
                                                      anchors={'left': 'right',
                                                               'right': 'right',
                                                               'top': 'top',
                                                               'bottom': 'bottom'})
                self.join_focus_sets(self.scroll_bar)
        else:
            if self.scroll_bar is not None:
                self.scroll_bar.kill()
                self.scroll_bar = None
            self.current_scroll_bar_width = 0

        # create button list container
        if self.item_list_container is not None:
            self.item_list_container.clear()
            if (self.item_list_container.relative_rect.width !=
                    (self.list_and_scroll_bar_container.relative_rect.width -
                     self.current_scroll_bar_width)):
                container_dimensions = (self.list_and_scroll_bar_container.relative_rect.width -
                                        self.current_scroll_bar_width,
                                        self.list_and_scroll_bar_container.relative_rect.height)
                self.item_list_container.set_dimensions(container_dimensions)
        else:
            self.item_list_container = UIContainer(
                Rect(0, 0,
                     self.list_and_scroll_bar_container.relative_rect.width -
                     self.current_scroll_bar_width,
                     self.list_and_scroll_bar_container.relative_rect.height),
                manager=self.ui_manager,
                starting_height=0,
                parent_element=self,
                container=self.list_and_scroll_bar_container,
                object_id='#item_list_container',
                anchors={'left': 'left',
                         'right': 'right',
                         'top': 'top',
                         'bottom': 'bottom'})
            self.join_focus_sets(self.item_list_container)

        item_y_height = 0
        for item in self.item_list:
            if item_y_height <= self.item_list_container.relative_rect.height:
                button_rect = Rect(0, item_y_height,
                                   self.item_list_container.relative_rect.width - 20,
                                   self.list_item_height)
                item['button_element'] = UIButton(relative_rect=button_rect,
                                                  text=item['text'],
                                                  manager=self.ui_manager,
                                                  parent_element=self,
                                                  container=self.item_list_container,
                                                  object_id=ObjectID(object_id=item['object_id'],
                                                                     class_id='@selection_list_item'),
                                                  allow_double_clicks=self.allow_double_clicks,
                                                  anchors={'top': 'top',
                                                           'left': 'left',
                                                           'bottom': 'top',
                                                           'right': 'right',
                                                           })
                self.join_focus_sets(item['button_element'])

                delete_button_rect = Rect(-20, item_y_height,
                                          20, self.list_item_height)
                item['delete_button'] = UIButton(relative_rect=delete_button_rect,
                                                 text='X',
                                                 manager=self.ui_manager,
                                                 parent_element=self,
                                                 container=self.item_list_container,
                                                 object_id=ObjectID(class_id='@delete_button',
                                                                    object_id=f'#delete_button.{item["object_id"]}'),
                                                 anchors={'top': 'top',
                                                          'left': 'right',
                                                          'bottom': 'top',
                                                          'right': 'right',

                                                          },

                                                 )

                self.join_focus_sets(item['delete_button'])

                item_y_height += self.list_item_height
            else:
                break


class DrawApp:
    start_point: ndarray[Any, dtype[Any]]
    stop_point: ndarray[Any, dtype[Any]]

    def __init__(self):
        pg.init()
        pg.display.set_caption('draw')
        self.clock = pg.time.Clock()

        # ความกว้างของ window dp ใน computer dp _px
        self.window_size = np.array([int(1920 * 0.8), int(1080 * 0.8)])
        self.mouse_pos = None
        self.canter_img_pos = None
        self.left_img_pos = None
        self.img_size_vector = None
        self.xywh = None

        self.dp = pg.display.set_mode(self.window_size.tolist(), pg.RESIZABLE)
        self.manager = UIManager(self.dp.get_size(), theme_path=self.setup_theme())
        self.frame_dict = load_frame_dict()
        self.setup_ui()
        self.set_item_list()
        self.scale_factor = 1.0
        self.img_offset_vector = np.array([100, 0])
        self.start_point = self.stop_point = np.array([0, 0])

        self.c = False
        self.drawing = False
        self.moving = False
        self.is_running = True
        self.img_np = np.full((500, 500, 3), [0, 255, 0], dtype=np.uint8)

        self.can_drawing = True
        self.can_moving = True
        self.can_zoom = True

    def setup_theme(self):
        self.theme = {
            '#close_button': {
                "colours": {
                    "hovered_bg": "rgb(232,17,35)",
                }
            },
            '@panel_window.#title_bar': {
                "colours": {
                    "normal_bg": "rgb(229,243,255)",
                }
            },
            "button": {
                "colours": {
                    "normal_bg": "#F3F3F3",
                    "hovered_bg": "rgb(229,243,255)",
                    "disabled_bg": "#F3F3F3",
                    "selected_bg": "rgb(204,232,255)",
                    "active_bg": "rgb(204,232,255)",
                    "normal_text": "#000",
                    "hovered_text": "#000",
                    "selected_text": "#000",
                    "disabled_text": "#A6A6A6",
                    "active_text": "#000",
                    "normal_border": "#CCCCCC",
                    "hovered_border": "#A6A6A6",
                    "disabled_border": "#CCCCCC",
                    "selected_border": "#A6A6A6",
                    "active_border": "#0078D7",
                    "normal_text_shadow": "#00000000",
                    "hovered_text_shadow": "#00000000",
                    "disabled_text_shadow": "#00000000",
                    "selected_text_shadow": "#00000000",
                    "active_text_shadow": "#00000000"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "4",
                    "border_width": "1",
                    "shadow_width": "0",
                    "tool_tip_delay": "1.0",
                    "text_horiz_alignment": "center",
                    "text_vert_alignment": "center",
                    "text_horiz_alignment_padding": "10",
                    "text_vert_alignment_padding": "5",
                    "text_shadow_size": "0",
                    "text_shadow_offset": "0,0",
                    "state_transitions": {
                        "normal_hovered": "0.2",
                        "hovered_normal": "0.2"
                    }
                }
            },
            "label": {
                "colours": {
                    "normal_text": "#000",
                },
                "misc": {
                    "text_horiz_alignment": "left"
                }
            },
            "window": {
                "colours": {
                    "dark_bg": "#F9F9F9",
                    "normal_border": "#888"
                },

                "misc": {
                    "shape": "rounded_rectangle",
                    #         "shape_corner_radius": "10",
                    #         "border_width": "1",
                    #         "shadow_width": "15",
                    #         "title_bar_height": "20"
                }
            },
            "selection_list": {
                "colours": {
                    "dark_bg": "#F9F9F9",
                    "normal_border": "#999999"
                },
            },
            "text_entry_line": {
                "colours": {
                    "dark_bg": "#fff",
                    "normal_text": "#000",
                    "text_cursor": "#000"
                },
            }
        }
        self.theme['@delete_button'] = self.theme['#close_button']
        return self.theme

    def set_panel0(self):
        self.panel0 = UIWindow(rect=Rect((0, 0), (230, 200)),
                               manager=self.manager, resizable=True,
                               window_display_title='Details',
                               object_id=ObjectID(class_id='@panel_window',
                                                  object_id='#details.panel_window')
                               )

        # panel0 Manual
        UILabel(Rect((3, 24 * 0), (100, 24)), container=self.panel0, text='fps')
        UILabel(Rect((3, 24 * 1), (100, 24)), container=self.panel0, text='mouse pos')
        UILabel(Rect((3, 24 * 2), (100, 24)), container=self.panel0, text='scale_factor')
        UILabel(Rect((3, 24 * 3), (100, 24)), container=self.panel0, text='img_offset')
        UILabel(Rect((3, 24 * 4), (100, 24)), container=self.panel0, text='img_size')
        UILabel(Rect((3, 24 * 5), (100, 24)), container=self.panel0, text='x1y1wh')
        UILabel(Rect((3, 24 * 6), (100, 24)), container=self.panel0, text='x1y1wh_px')
        self.t1 = UILabel(Rect((85, 24 * 0), (200, 24)), container=self.panel0, text=f':')
        self.t2 = UILabel(Rect((85, 24 * 1), (200, 24)), container=self.panel0, text=f':')
        self.t3 = UILabel(Rect((85, 24 * 2), (200, 24)), container=self.panel0, text=f':')
        self.t4 = UILabel(Rect((85, 24 * 3), (200, 24)), container=self.panel0, text=f':')
        self.t5 = UILabel(Rect((85, 24 * 4), (200, 24)), container=self.panel0, text=f':')
        self.t6 = UILabel(Rect((85, 24 * 5), (200, 24)), container=self.panel0, text=f':')
        self.t7 = UILabel(Rect((85, 24 * 6), (200, 24)), container=self.panel0, text=f':')

    def set_panel1(self):
        self.panel1 = UIWindow(rect=Rect((0, 200), (230, 350)),
                               manager=self.manager, resizable=True,
                               window_display_title='List',
                               object_id=ObjectID(class_id='@panel_window',
                                                  object_id='#rect_list.panel_window')
                               )
        self.panel1.minimum_dimensions = (230, 300)

        self.rect_list = UISelectionListWithDelete(relative_rect=Rect(4, 4, 220, 250),
                                                   item_list=list(self.frame_dict.keys()),
                                                   manager=self.manager,
                                                   container=self.panel1,
                                                   anchors={'top': 'top',
                                                            'left': 'left',
                                                            'bottom': 'bottom',
                                                            'right': 'right',
                                                            })
        self.name_entry = UITextEntryLine(relative_rect=Rect((4, -65), (220, 30)),
                                          manager=self.manager,
                                          container=self.panel1,
                                          anchors={'left': 'left',
                                                   'right': 'right',
                                                   'top': 'bottom',
                                                   'bottom': 'bottom'})
        self.add_button = UIButton(relative_rect=Rect((4, -34), (92, 30)), text='Add',
                                   container=self.panel1,
                                   anchors={'top': 'bottom',
                                            'left': 'left',
                                            'bottom': 'bottom',
                                            'right': 'left'})
        self.delete_button = UIButton(relative_rect=Rect((4, -34), (92, 30)), text='Delete',
                                      container=self.panel1,
                                      anchors={'top': 'bottom',
                                               'left': 'left',
                                               'bottom': 'bottom',
                                               'right': 'left',
                                               'left_target': self.add_button})

    def set_panel2(self):
        self.panel2 = UIWindow(rect=Rect((0, 550), (230, 350)),
                               manager=self.manager, resizable=True,
                               window_display_title='Manual',
                               object_id=ObjectID(class_id='@panel_window',
                                                  object_id='#manual.panel_window')
                               )
        self.get_static_surface()
        UIImage(self.mouse_icon_surface.get_rect(), self.mouse_icon_surface, container=self.panel2)
        UILabel(relative_rect=Rect((100, 45 * 0 + 10), (100, 30)), container=self.panel2, text=': Drawing')
        UILabel(relative_rect=Rect((100, 45 * 1 + 10), (100, 30)), container=self.panel2, text=': Zoom in')
        UILabel(relative_rect=Rect((100, 45 * 2 + 10), (100, 30)), container=self.panel2, text=': Zoom out')
        UILabel(relative_rect=Rect((100, 45 * 3 + 10), (100, 30)), container=self.panel2, text=': Move')
        UILabel(relative_rect=Rect((100, 45 * 4 + 10), (100, 30)), container=self.panel2, text=': Reset layout')

    def setup_ui(self):
        self.set_panel0()
        self.set_panel1()
        self.set_panel2()

        # panel0 Manual
        self.show_details_button = UIButton(relative_rect=Rect((300, 0), (70, 30)), text='Details',
                                            manager=self.manager)
        self.show_details_button.disable()
        # panel1 Manual
        self.show_list_button = UIButton(relative_rect=Rect((0, 0), (70, 30)), text='Lists', manager=self.manager,
                                         anchors={'left_target': self.show_details_button})
        self.show_list_button.disable()
        # panel2 Manual

    def set_item_list(self):
        self.rect_list.set_item_list(zip(self.frame_dict.keys(), self.frame_dict.keys()))
        write_frame_dict(self.frame_dict)

    def get_point_on_img_surface(self):
        return (self.mouse_pos - self.canter_img_pos + self.img_size_vector / 2) / self.img_size_vector

    def get_static_surface(self):
        pil_image = Image.open("mouse_icon.png")
        pil_image = pil_image.resize((int(pil_image.size[0] * 0.5), int(pil_image.size[1] * 0.5)))
        self.mouse_icon_surface = pg.image.frombuffer(pil_image.tobytes(), pil_image.size, pil_image.mode)

    def get_surface_from_display_capture(self):
        pil_image = ImageGrab.grab()
        self.img_surface = pg.image.frombuffer(pil_image.tobytes(), pil_image.size, pil_image.mode)
        self.scaled_img_surface = pg.transform.scale(self.img_surface, (
            int(self.img_surface.get_width() * self.scale_factor),
            int(self.img_surface.get_height() * self.scale_factor)))

    def get_surface_from_file(self, path: str):
        pil_image = Image.open(path)
        self.img_surface = pg.image.frombuffer(pil_image.tobytes(), pil_image.size, pil_image.mode)
        self.scaled_img_surface = pg.transform.scale(self.img_surface, (
            int(self.img_surface.get_width() * self.scale_factor),
            int(self.img_surface.get_height() * self.scale_factor)))

    def setup_cap(self, path):
        self.cap = cv2.VideoCapture(path)

    def get_np_form_cap(self):
        _, img = self.cap.read()
        if _:
            self.img_np = img

    def get_np_form_url(self, url):
        req = urllib.request.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        self.img_np = cv2.imdecode(arr, -1)

    def get_surface_form_np(self):
        self.img_surface = pg.image.frombuffer(self.img_np.tobytes(), self.img_np.shape[1::-1], "BGR")
        self.scaled_img_surface = pg.transform.scale(self.img_surface, (
            int(self.img_surface.get_width() * self.scale_factor),
            int(self.img_surface.get_height() * self.scale_factor)))

    def handle_window_resize(self, event):
        minimum = (500, 500)
        if event.type == pg.VIDEORESIZE:
            x, y = event.size
            # ความกว้างของ window dp ใน computer dp _px
            self.window_size = np.array([
                max(x, minimum[0]),
                max(y, minimum[1])
            ])
            self.dp = pg.display.set_mode(self.window_size.tolist(), pg.RESIZABLE)
            self.manager.set_window_resolution(self.window_size.tolist())

    def get_can_wheel(self):
        return not any([obj.rect.collidepoint(self.mouse_pos) for obj in [
            self.panel0,
            self.panel1,
            self.panel2,
            self.show_list_button,
            self.show_details_button
        ]])

    def wheel_drawing_moving(self, event):
        # mouse pos เทียบกับซ้ายบน  _px
        self.mouse_pos = np.array(pg.mouse.get_pos())
        # canter of img pos เทียบกับซ้ายบน  _px
        self.canter_img_pos = self.window_size / 2 + self.img_offset_vector
        # ความกว้างของ img ใน window dp _px
        self.img_size_vector = np.array(self.scaled_img_surface.get_size())
        # left of img pos เทียบกับซ้ายบน  _px
        self.left_img_pos = self.canter_img_pos - self.img_size_vector / 2

        self.can_wheel = self.get_can_wheel()

        if self.can_wheel:
            # drawing
            if self.can_drawing:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.drawing = True
                    self.start_point = self.get_point_on_img_surface()
                    self.stop_point = self.start_point
            # moving
            if self.can_moving:
                if event.type == pg.MOUSEBUTTONDOWN and event.button in [2, 3]:
                    self.moving = True

            # zoom in / zoom out
            if self.can_zoom:
                if event.type == pg.MOUSEWHEEL:
                    factor = (1 + event.y / 10)
                    self.scale_factor *= factor
                    a = self.img_size_vector
                    a1 = self.mouse_pos - self.left_img_pos
                    b = a * factor
                    b1 = a1 * factor
                    canter_img_pos_b = self.mouse_pos - b1 + b / 2
                    offset = self.canter_img_pos - canter_img_pos_b
                    self.img_offset_vector = self.img_offset_vector - offset

                    # update img_size_vector
                    self.scaled_img_surface = pg.transform.scale(self.img_surface, (
                        int(self.img_surface.get_width() * self.scale_factor),
                        int(self.img_surface.get_height() * self.scale_factor)
                    ))
                    self.img_size_vector = np.array(self.scaled_img_surface.get_size())

        # moving
        if self.moving:
            if event.type == pg.MOUSEMOTION:  # move mouse
                if event.buttons[1]:
                    self.img_offset_vector += np.array(event.rel)
                if event.buttons[2]:  # Right mouse button is held down
                    if math.sqrt(sum(a ** 2 for a in event.rel)) > 20:  # ขยับเมาส์ 20 หน่วย
                        self.scale_factor = 1.0
                        self.img_offset_vector = np.array([0, 0])
            if event.type == pg.MOUSEBUTTONUP and event.button == 2:
                self.moving = False

        # drawing
        if self.drawing:
            if event.type == pg.MOUSEMOTION and event.buttons[0]:
                self.stop_point = self.get_point_on_img_surface()
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.drawing = False

    def panels(self, events):
        for event in events:
            # enable or disable
            if event.type == 32867:
                if event.ui_object_id == '#details.panel_window.#close_button':
                    self.show_details_button.enable()
                if event.ui_object_id == '#rect_list.panel_window.#close_button':
                    self.show_list_button.enable()
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == self.show_details_button:
                    self.show_details_button.disable()
                if event.ui_element == self.show_list_button:
                    self.show_list_button.disable()

            # add item in frame_dict
            if event.type == UI_BUTTON_PRESSED and event.ui_element == self.add_button:
                name = self.name_entry.get_text()
                self.name_entry.set_text('')
                if name == '':
                    name = random_text(skip_list=list(self.frame_dict.keys()))
                if not self.frame_dict.get(name):
                    self.frame_dict[name] = {}
                self.frame_dict[name]['xywh'] = self.xywh.tolist()
                self.set_item_list()

            # delete item in frame_dict
            if event.type == UI_BUTTON_PRESSED and event.ui_element == self.delete_button:
                name = self.rect_list.get_single_selection()
                if name is not None:
                    self.frame_dict.pop(name)
                    self.set_item_list()
            if event.type == 32867 and '#rect_list.panel_window.selection_list.#delete_button.' in event.ui_object_id:
                name = event.ui_object_id.replace('#rect_list.panel_window.selection_list.#delete_button.', '')
                self.frame_dict.pop(name)
                self.set_item_list()

            # show or hide panels
            if event.type == UI_BUTTON_PRESSED and event.ui_element == self.show_details_button:
                self.set_panel0()
            if event.type == UI_BUTTON_PRESSED and event.ui_element == self.show_list_button:
                self.set_panel1()
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_object_id == '#details.panel_window.#close_button':
                    self.panel0.set_position((-300, 0))
                if event.ui_object_id == '#rect_list.panel_window.#close_button':
                    self.panel1.set_position((-300, 0))
                if event.ui_object_id == '#manual.panel_window.#close_button':
                    self.panel2.set_position((-300, 0))

        x1 = max(min(self.start_point[0], self.stop_point[0], 1), 0)
        y1 = max(min(self.start_point[1], self.stop_point[1], 1), 0)
        x2 = min(max(self.start_point[0], self.stop_point[0], 0), 1)
        y2 = min(max(self.start_point[1], self.stop_point[1], 0), 1)

        xyxy = np.array([x1, y1, x2, y2])
        self.xywh = (xyxy + [x2, y2, -x1, -y1]) / [2, 2, 1, 1]
        x1y1wh = xyxy - [0, 0, x1, y1]
        x1y1wh_px = x1y1wh * np.tile(self.img_size_vector, 2)

        self.t1.set_text(f': {round(self.clock.get_fps())}')
        self.t2.set_text(f': {pg.mouse.get_pos()}')
        self.t3.set_text(f': {round(self.scale_factor, 2)}')
        self.t4.set_text(f': {self.img_offset_vector.astype(int)}')
        self.t5.set_text(f': {self.img_size_vector}')
        self.t6.set_text(f': {x1y1wh_px.astype(int)}')
        self.t7.set_text(f': {np.round(x1y1wh, 2)}')

        # drawing
        pg.draw.rect(self.scaled_img_surface, (255, 255, 0), Rect((x1y1wh_px + [-1, -1, 2, 2]).tolist()), 3)
        pg.draw.rect(self.scaled_img_surface, (0, 0, 255), Rect(x1y1wh_px.tolist()), 1)

    def draw_at_mouse_position(self):
        pg.draw.line(self.dp, (0, 0, 0), (self.mouse_pos[0], 0),
                     (self.mouse_pos[0], self.window_size[1]))
        pg.draw.line(self.dp, (0, 0, 0), (0, self.mouse_pos[1]),
                     (self.window_size[0], self.mouse_pos[1]))

        draw_dashed_line(self.dp, (255, 255, 255), (self.mouse_pos[0], 0),
                         (self.mouse_pos[0], self.window_size[1]))
        draw_dashed_line(self.dp, (255, 255, 255), (0, self.mouse_pos[1]),
                         (self.window_size[0], self.mouse_pos[1]))

    def show_rects_to_surface(self, frame_dict):
        for k, v in frame_dict.items():
            _xywh = np.array(v.get('xywh'))
            _x, _y, _w, _h = _xywh
            _x1y1wh = _xywh - [_w / 2, _h / 2, 0, 0]
            _x1y1wh_px = _x1y1wh * np.tile(self.img_size_vector, 2)

            pg.draw.rect(self.scaled_img_surface, (200, 255, 255), Rect((_x1y1wh_px + [-1, -1, 2, 2]).tolist()), 3)
            pg.draw.rect(self.scaled_img_surface, (200, 255, 0), Rect(_x1y1wh_px.tolist()), 1)

            font = pg.font.Font(None, 16)
            color = [(0, 0, 255), (255, 255, 255)]
            put_text(self.scaled_img_surface, f"{k}", font, color, _x1y1wh_px[:2], 'bottomleft')

        # scaled_img_surface to dp
        self.dp.blit(self.scaled_img_surface,
                     ((self.window_size - self.img_size_vector) / 2 + self.img_offset_vector).tolist())
        if self.can_wheel:
            self.draw_at_mouse_position()

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.dp.fill((180, 180, 180))
            # get image surface
            # self.get_surface_from_display_capture()
            # self.get_surface_from_file('image/img (1).jpg')
            # self.get_surface()
            self.get_np_form_url('http://192.168.225.137:2000/old-image')
            self.get_surface_form_np()
            events = pg.event.get()
            for event in events:
                self.manager.process_events(event)
                self.handle_window_resize(event)
                self.wheel_drawing_moving(event)

                if event.type == pg.QUIT:
                    self.is_running = False
                if event.type != pg.MOUSEMOTION:
                    # if event.type == UI_BUTTON_PRESSED:
                    print(event)

            self.panels(events)
            self.show_rects_to_surface(self.frame_dict)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.dp)

            pg.display.update()


if __name__ == "__main__":
    app = DrawApp()
    app.run()
