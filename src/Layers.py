import math
import cv2
from .Plot import InitCanvas
from .LoadImage import url_to_image, load_image

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

        self.top, self.left, self.width, self.height = 0, 0, 0, 0
        self.dec_type = dec_type
        self.prime_hue = prime_hue
        self.feature_vector = []

    def load_layer(self, element: dict):
        self.layer = element
        self.style = element['style']
        self.top = math.floor(self.style['top'] * len_px)
        self.left = math.floor(self.style['left'] * len_px)
        self.height = math.ceil(self.style['height'] * len_px)
        self.width = math.ceil(self.style['width'] * len_px)

    def generate_pic(self):
        pic = url_to_image(self.layer['src'])
        pic = cv2.resize(pic, (self.width, self.height), interpolation=cv2.INTER_NEAREST)
        return pic


class BKG(ComponentLayer):
    def __init__(self):
        self.design_str = []


class Title(ComponentLayer):
    def __init__(self):
        self.design_str = []


class Design:
    def __init__(self, width, height):
        self.design_str = []
        self.width = math.ceil(width * len_px)
        self.height = math.ceil(height * len_px)
        self.canvas = InitCanvas(self.width, self.height)

    def insert_layer(self, new_layer: ComponentLayer):
        self.design_str.append(new_layer)

    def show_image(self):
        for layer in self.design_str:
            pic = layer.generate_pic()
            self.canvas[layer.top:layer.top+layer.height,layer.left:layer.left+layer.width,:] = pic
        return self.canvas
