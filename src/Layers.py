import math
import cv2
from PIL import ImageFont, ImageDraw, Image
from .LoadImage import url_to_image
import colorsys
import palettes

len_px = 3.7795275591


class ComponentLayer:
    def __init__(self, dec_type=None, prime_hue=None):
        """
        This class is the base class for one layer of the design components.
        :param dec_type:
        :param prime_hue:
        :param location:
        :param rotation:
        """
        self.layer = {}
        self.style = {}

        self.dec_type = dec_type
        self.prime_hue = prime_hue
        self.feature_vector = []

    @property
    def location(self):
        return [self.style['top'], self.style['left']]

    @location.setter
    def location(self, value):
        if not (value[0] >= 0 and value[1] >=0):
            raise ValueError('locations not valid')
        self.style['top'] = value[0]
        self.style['left'] = value[1]

    def load_layer(self, element: dict):
        self.layer = element
        self.style = element['style']
        self.style['top'] = math.floor(self.style['top'] * len_px)
        self.style['left'] = math.floor(self.style['left'] * len_px)
        self.style['height'] = math.ceil(self.style['height'] * len_px)
        self.style['width'] = math.ceil(self.style['width'] * len_px)


class Background(ComponentLayer):
    def __init__(self):
        super().__init__()
        self.design_str = []


class Title(ComponentLayer):
    def __init__(self, text: str, font_setting: dict = {'size':}, font_path=None):
        super().__init__()
        self.text = text
        if font_path:
            self.font = ImageFont.load(font_path)
        else:
            self.font = ImageFont.load_default()
        self.font_setting = font_setting
        self.hue = []

    def cal_text_size(self):
        raise NotImplementedError

    def generate_pic(self):



class Patterns(ComponentLayer):
    def __init__(self):
        super().__init__()
        self.color_palette = []

    def generate_pic(self):
        pic = url_to_image(self.layer['src'])
        pic = cv2.resize(pic, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

        return pic
