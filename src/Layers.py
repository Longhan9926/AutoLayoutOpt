import math
import cv2
import json
from PIL import ImageFont, ImageDraw, Image
from .LoadImage import url_to_image

len_px = 3.7795275591
open_file = open("input/basic_material.json")
urls = json.load(open_file)


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
    def __init__(self, img):
        super().__init__()
        self.type = 'pic'


class Picture(ComponentLayer):
    def __init__(self, img):
        super().__init__()
        self.type = 'pic'


class Decoration(ComponentLayer):
    def __init__(self, pattern='rectangle'):
        super().__init__()
        self.type = 'dec'
        self.layer["src"] = urls[pattern]


class Title(ComponentLayer):
    def __init__(self, text: str, font_setting=None, font_path=None):
        super().__init__()
        self.layer["value"] = text
        self.type = 'title'
        self.layer["type"] = "font"
        self.layer["src"] = "//cdn.baoxiaohe.com/5225a97f-55e0-495f-a65e-ad2ad498e7a3.otf"
        self.layer["thumb"] = "//cdn.baoxiaohe.com/font/min/9aadf3b4-ee9f-4481-ad08-4eb25c29b39d.min.ttf"
        if font_path:
            self.font = ImageFont.load(font_path)
        else:
            self.font = ImageFont.load_default()
        self.font_setting = font_setting
        self.hue = []

    def cal_text_size(self):
        raise NotImplementedError


class Slogan(ComponentLayer):
    def __init__(self, text: str, font_setting, font_path=None):
        super().__init__()
        self.text = text
        self.type = 'slogan'
        if font_path:
            self.font = ImageFont.load(font_path)
        else:
            self.font = ImageFont.load_default()
        self.font_setting = font_setting
        self.hue = []


class Logo(ComponentLayer):
    def __init__(self):
        super().__init__()
        self.type = 'logo'

    def generate_pic(self):
        pic = url_to_image(self.layer['src'])
        pic = cv2.resize(pic, (self.width, self.height), interpolation=cv2.INTER_NEAREST)
        raise NotImplementedError

    def save_layer(self):
        self.layer["type"] = "img"
