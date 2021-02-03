import math
import cv2
import os
import json
import numpy as np
import imageio
import random
from .LoadImage import url_to_image, url_to_svg
from .RandomG import random_name
from .Salient import crop_salient
from .UploadImage import upload_image
import skimage

len_px = 3.7795275591
len_pt = 0.3528
open_file = open("input/basic_material.json")
urls = json.load(open_file)
mask_path = "input/mask"
mask_files = os.listdir(mask_path)

class ComponentLayer:
    def __init__(self, dec_type=None, prime_hue=None):
        """
        This class is the base class for one layer of the design components.
        :param dec_type:
        :param prime_hue:
        :param location:
        :param rotation:
        """
        self.layer = {"type": "img", "src": None, "style": {"top": 0, "left": 0, "width": 0, "height": 0}}
        self.style = self.layer["style"]
        self.type = 'basic'
        self.layer["can_set_color"] = 1
        self.layer["uuid"] = random_name(1)

    @property
    def location(self):
        return [self.style['top'], self.style['left']]

    @location.setter
    def location(self, value):
        if not (value[0] >= 0 and value[1] >= 0):
            raise ValueError('locations not valid')
        self.style['top'] = value[0]
        self.style['left'] = value[1]

    @property
    def size(self):
        return [self.style['width'], self.style['height']]

    @size.setter
    def size(self, value):
        self.style['width'] = value[0]
        self.style['height'] = value[1]

    @property
    def rotation(self):
        return self.style['rotate']

    @rotation.setter
    def rotation(self, value):
        self.style['rotation'] = self.style['rotation'] + value

    @property
    def opacity(self):
        return self.style['opacity']

    @opacity.setter
    def opacity(self, value):
        self.style['opacity'] = value

    def load_source(self, src):
        self.layer["src"] = src

    def load_layer(self, element: dict):
        self.layer = element
        self.style = element['style']
        self.style['top'] = math.floor(self.style['top'] * len_px)
        self.style['left'] = math.floor(self.style['left'] * len_px)
        self.style['height'] = math.ceil(self.style['height'] * len_px)
        self.style['width'] = math.ceil(self.style['width'] * len_px)


class Picture(ComponentLayer):
    def __init__(self, url):
        super().__init__()
        self.type = 'pic'
        self.url = url
        self.layer["src"] = url

    def crop_scale(self, size):
        """
        :param size: in resolutions [width, height]
        update layer src
        """
        origin = url_to_image(self.url)
        image = crop_salient(origin, size)
        cv2.imwrite('image.png', image)
        maskornot = np.random.choice([0,1])
        if maskornot == 1:
            # mask_pattern = random.choice(urls)
            # mask = url_to_image(mask_pattern)
            file = random.sample(mask_files, 1)
            mask = mask_path + '/' + file[0]
            print(mask)
            mask = cv2.imread(mask, cv2.IMREAD_UNCHANGED)
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
            image[:, :, 3] = np.where(mask[:, :, 3] > 0.5, 255, 0)
        cv2.imwrite('cropped.png', image)
        self.layer["src"] = upload_image('cropped.png')


class Decoration(ComponentLayer):
    def __init__(self, pattern='rectangle'):
        super().__init__()
        self.type = 'dec'
        self.layer["src"] = urls[pattern][0]
        self.layer["fills"] = [{"color": "rgba(0, 0, 0, 1)", "type": "globalFill"}]

    def set_color(self, color):
        color = [round(x * 255) for x in color]
        if len(color) == 3:
            a = 1
        else:
            a = color[3]
        self.layer["fills"] = [{"color": "rgba({0},{1},{2},{3})".format(str(color[0]), str(color[1]), \
                                                                        str(color[2]), str(a)),
                                "type": "globalFill"}]


class Title(ComponentLayer):
    def __init__(self, text: str, font_setting=None, font_path=None):
        super().__init__()
        if font_setting is None:
            font_setting = {"fontWeight": "normal", "fontStyle": "normal",
                            "color": "#FFFFFFFF", "fontSize": 60, "color_f": None}
        self.layer["value"] = text
        self.type = 'title'
        self.layer["type"] = "font"
        self.layer["src"] = "https://cdn.baoxiaohe.com/5225a97f-55e0-495f-a65e-ad2ad498e7a3.otf"
        # self.layer["thumb"] = "https://cdn.baoxiaohe.com/font/min/9aadf3b4-ee9f-4481-ad08-4eb25c29b39d.min.ttf"
        self.hue = None
        if font_setting:
            self.style["fontWeight"] = font_setting["fontWeight"]
            self.style["fontSize"] = font_setting["fontSize"]
        self.style["lineHeight"] = 35
        self.set_color(font_setting["color_f"])

    def cal_text_size(self):
        length = len(self.layer["value"])
        if length > self.style["width"] / self.style["height"]:
            self.style["lineHeight"] = self.style["height"]
            self.style["fontSize"] = self.style["width"] / length
        elif length < self.style["width"] / self.style["height"]:
            self.style["lineHeight"] = self.style["height"] * 0.8
            self.style["fontSize"] = self.style["height"] * 0.8

    def set_font(self, font_set):
        for key, item in font_set.items():
            self.style[key] = item

    def set_color(self, color=None):
        """
        :param color: in rgba/rgb
        :return: dict of "colorFilter"
        """
        colorFilter = {}
        if color is None:
            # Set to default color
            colorFilter["hsv"] = {"h": 43.30645161290333, "s": 0, "v": 0, "a": 1}
            colorFilter["rgba"] = {"r": 0, "g": 0, "b": 0, "a": 1}
        else:
            color = [round(x * 255) for x in color]
            colorFilter["rgba"] = {"r": color[0], "g": color[1], "b": color[2]}
            if len(color) == 3:
                colorFilter["rgba"]["a"] = 1
            elif len(color) == 4:
                colorFilter["rgba"]["a"] = color[3]
        self.style["fillFilter"] = colorFilter
        self.style["color"] = "rgba({0},{1},{2},{3})".format(str(colorFilter["rgba"]["r"]),
                                                             str(colorFilter["rgba"]["g"]),
                                                             str(colorFilter["rgba"]["b"]),
                                                             str(colorFilter["rgba"]["a"]))


class Slogan(ComponentLayer):
    def __init__(self, text: str, font_setting=None, font_path=None):
        super().__init__()
        if font_setting is None:
            font_setting = {"fontWeight": "normal", "fontStyle": "normal",
                            "color": "#FFFFFFFF", "fontSize": 30, "color_f": None}
        self.layer["value"] = text
        self.type = 'slogan'
        self.layer["type"] = "font"
        self.layer["src"] = "https://cdn.baoxiaohe.com/5225a97f-55e0-495f-a65e-ad2ad498e7a3.otf"
        # self.layer["thumb"] = "https://cdn.baoxiaohe.com/font/min/9aadf3b4-ee9f-4481-ad08-4eb25c29b39d.min.ttf"
        self.hue = None
        self.style["lineHeight"] = 30
        self.set_color(font_setting["color_f"])

    def cal_text_size(self):
        length = len(self.layer["value"])
        self.style["fontSize"] = math.sqrt(self.style["height"] * self.style["width"] / length / 1.7)
        self.style["lineHeight"] = self.style["fontSize"] * 1.1

    def set_font(self, font_set):
        for key, item in font_set.items():
            self.style[key] = item

    def set_color(self, color=None):
        """
        :param color: in rgba/rgb
        :return: dict of "colorFilter"
        """
        colorFilter = {}
        if color is None:
            # Set to default color
            colorFilter["hsv"] = {"h": 43.30645161290333, "s": 0, "v": 0, "a": 1}
            colorFilter["rgba"] = {"r": 0, "g": 0, "b": 0, "a": 1}
        else:
            color = [round(x * 255) for x in color]
            colorFilter["rgba"] = {"r": color[0], "g": color[1], "b": color[2]}
            if len(color) == 3:
                colorFilter["rgba"]["a"] = 1
            elif len(color) == 4:
                colorFilter["rgba"]["a"] = color[3]
        self.style["fillFilter"] = colorFilter
        self.style["color"] = "rgba({0},{1},{2},{3})".format(str(colorFilter["rgba"]["r"]),
                                                             str(colorFilter["rgba"]["g"]),
                                                             str(colorFilter["rgba"]["b"]),
                                                             str(colorFilter["rgba"]["a"]))


class Text(ComponentLayer):
    def __init__(self, text: str, font_setting=None, font_path=None):
        super().__init__()
        if font_setting is None:
            font_setting = {"fontWeight": "normal", "fontStyle": "normal",
                            "color": "#FFFFFFFF", "fontSize": 15, "color_f": None}
        self.layer["value"] = text
        self.type = 'txt'
        self.layer["type"] = "font"
        self.layer["src"] = "https://cdn.baoxiaohe.com/5225a97f-55e0-495f-a65e-ad2ad498e7a3.otf"
        # self.layer["thumb"] = "https://cdn.baoxiaohe.com/font/min/9aadf3b4-ee9f-4481-ad08-4eb25c29b39d.min.ttf"
        self.hue = None
        self.style["lineHeight"] = 10
        self.style["fontSize"] = 8
        self.set_color(font_setting["color_f"])

    def cal_text_size(self):
        length = len(self.layer["value"])
        self.style["fontSize"] = max(math.sqrt(self.style["height"] * self.style["width"] / length / 1.5), 6 * len_pt)
        str = self.layer["value"]
        str = str.split('\n')
        n = math.floor(self.style["width"] / self.style["fontSize"])
        n_r = 0
        n_l = [len(s) for s in str]
        for s in str:
            n_r = n_r + len(s) // n + 1
        self.style["top"] = self.style["top"] + self.style["height"] - n_r * self.style["lineHeight"]
        self.style["lineHeight"] = self.style["fontSize"] * 1.1

    def set_font(self, font_set):
        for key, item in font_set.items():
            self.style[key] = item

    def set_color(self, color=None):
        """
        :param color: in rgba/rgb
        :return: dict of "colorFilter"
        """
        colorFilter = {}
        if color is None:
            # Set to default color
            colorFilter["hsv"] = {"h": 43.30645161290333, "s": 0, "v": 0, "a": 1}
            colorFilter["rgba"] = {"r": 0, "g": 0, "b": 0, "a": 1}
        else:
            color = [round(x * 255) for x in color]
            colorFilter["rgba"] = {"r": color[0], "g": color[1], "b": color[2]}
            if len(color) == 3:
                colorFilter["rgba"]["a"] = 1
            elif len(color) == 4:
                colorFilter["rgba"]["a"] = color[3]
        self.style["fillFilter"] = colorFilter
        self.style["color"] = "rgba({0},{1},{2},{3})".format(str(colorFilter["rgba"]["r"]),
                                                             str(colorFilter["rgba"]["g"]),
                                                             str(colorFilter["rgba"]["b"]),
                                                             str(colorFilter["rgba"]["a"]))


class Logo(ComponentLayer):
    def __init__(self, url=None):
        super().__init__()
        self.type = 'logo'
        self.layer["type"] = 'img'
        if url is not None:
            self.layer["src"] = url
        else:
            self.layer["src"] = "//cdn.baoxiaohe.com/73328f73-91d8-4470-bac7-e69ca56eaa1c.svg"
        image = url_to_svg(self.layer["src"])
        self.shape_origin = image.shape[1] / image.shape[0]
