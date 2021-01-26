from typing import List

import src
import sys
import math
import numpy as np
import cv2
import json
import argparse

len_px = 3.7795275591
open_file = open("input/basic_material.json")
urls = json.load(open_file)


class Location:
    def __init__(self, top=0, btm=100, lft=0, rgt=100, size = [100,100]):
        self.position = {
            "absolute": {"top": 0, "height": 0, "left": 0, "width": 0},
            "resolute": {"top": 0, "height": 0, "left": 0, "width": 0},
            "percentage": {"top": top, "btm": btm, "lft": lft, "rgt": rgt}
        }
        self.define_size(size)

    def define_size(self, size):
        """
        :param size:in real length
        """
        self.position["absolute"]["top"] = self.position["percentage"]["top"] * size[1] / 100
        self.position["absolute"]["left"] = self.position["percentage"]["lft"] * size[0] / 100
        self.position["absolute"]["height"] = self.position["percentage"]["btm"] * size[1] / 100 \
                                              - self.position["percentage"]["top"] * size[1] / 100
        self.position["absolute"]["width"] = self.position["percentage"]["rgt"] * size[0] / 100 \
                                             - self.position["percentage"]["lft"] * size[0] / 100
        self.position["resolute"]["top"] = math.floor(self.position["absolute"]["top"] * len_px)
        self.position["resolute"]["left"] = math.floor(self.position["absolute"]["left"] * len_px)
        self.position["resolute"]["height"] = math.floor(self.position["absolute"]["height"] * len_px)
        self.position["resolute"]["width"] = math.floor(self.position["absolute"]["width"] * len_px)


class Layout:
    def __init__(self):
        self.layout = {}

    def load_layout(self, file_path):
        with open(file_path, 'r') as load_f:
            temp = json.load(load_f)
        for ele in temp:
            self.layout[ele["type"]] = Location(ele["position"]["top"],ele["position"]["bottom"],\
                                                ele["position"]["left"],ele["position"]["right"])


class Design:
    def __init__(self, size):
        self.design_str: List[src.Layers.ComponentLayer] = []
        self.size = size
        self.canvas = src.InitCanvas(self.size[0], self.size[1])
        self.mask = np.zeros(self.size)
        self.color_palette = None

    def insert_layer(self, new_layer, ind=-1):
        self.design_str.insert(ind, new_layer)

    def load_pic(self, pic):
        raise NotImplementedError

    def load_text(self, text=str):
        raise NotImplementedError

    def load_design(self, file_path="output/a.json"):
        self.design_str = []
        with open(file_path, 'r') as load_f:
            load_dict = json.load(load_f)
        for new_layer in load_dict:
            temp = src.ComponentLayer()
            temp.load_layer(new_layer)
            self.insert_layer(temp)

    def load_layout(self, layout: Layout):
        for layer in self.design_str:
            layout.layout[layer.type].define_size(self.size)
            for key in ["top", "left", "width", "height"]:
                layer.style[key] = layout.layout[layer.type].position["absolute"][key]

    def implement_palette(self, color_palette):
        self.color_palette = color_palette
        for layer in self.design_str:
            if layer.type not in ["dec", "title"]:
                continue
            else:
                choice = np.random.choice(range(len(color_palette)))
                layer.hue = color_palette[choice]

    def show_image(self):
        for layer in self.design_str:
            self.canvas[layer.style['top']:layer.style['top'] + layer.style['height'], \
            layer.style['left']:layer.style['left'] + layer.style['width']] \
                = layer.generate_pic()
        return self.canvas

    def save_design(self):
        temp = []
        for layer in self.design_str:
            temp.append(layer.layer)
        with open('design.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(temp).replace('\"', '\\"'))

    def upload_design(self):
        raise NotImplementedError


def main(args):
    new_design = Design(args.size)

    # load the text, picture into the layout
    prime_pic = src.load_image(args.prime)
    dominant_color = src.get_dominant_color(args.prime)
    color_palette = src.generate_color_palette(3, dominant_color, strategy='Monotone')
    layout = Layout()
    layout.load_layout("input/layout.json")
    bkg = src.Decoration()
    prime_layer = src.Picture(prime_pic)
    title = src.Title()
    new_design.insert_layer(bkg)
    new_design.insert_layer(prime_layer)
    new_design.insert_layer(title)
    new_design.load_layout(layout)
    new_design.implement_palette(color_palette)
    new_design.save_design()


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--title', type=str,
                        help='input title', default=None)
    parser.add_argument('--prime', type=str,
                        help='input prime picture', default=None)
    parser.add_argument('--text', type=str,
                        help='input ad text', default=None)
    parser.add_argument('--layout', type=str,
                        help='input a layout template', default='basic')
    parser.add_argument('--size', type=list,
                        help='input size as in [width, height, thickness]', default=[100, 100, 100])
    return parser.parse_args(argv)


if __name__ == '__main__':
    # main(parse_arguments(sys.argv[1:]))
    size = [400, 400]
    prime = 'input/img/free_stock_photo.jpg'
    text = 'Hello'

    new_design = Design(size)

    # load the text, picture into the layout
    prime_pic = src.load_image(prime)
    dominant_color = src.get_dominant_color(prime)
    dominant_color = (dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255)
    color_palette = src.generate_color_palette(3, dominant_color, strategy='Monotone')
    layout = Layout()
    layout.load_layout('input/layout.json')
    prime_url = src.upload_image(prime)
    prime_layer = src.Picture(prime_url)
    bkg = src.Decoration()
    title = src.Title(text)
    new_design.insert_layer(bkg)
    new_design.insert_layer(prime_layer)
    new_design.insert_layer(title)
    new_design.load_layout(layout)
    new_design.implement_palette(color_palette)
    new_design.save_design()
