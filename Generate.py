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
    def __init__(self, top=0, bottom=1, left=0, right=1):
        self.top = top
        self.btm = bottom
        self.lft = left
        self.rgt = right

    def convert(self, size):
        self.lft_c = self.lft * size[0] // 100
        self.rgt_c = self.rgt * size[0] // 100
        self.btm_c = self.btm * size[1] // 100
        self.top_c = self.top * size[1] // 100


class Layout:
    def __init__(self):
        self.layout = {}
        self.pic = Location()
        self.txt = Location()
        self.logo = Location()

    def load_layout(self, file_path):
        self.layout = {}
        with open(file_path, 'r') as load_f:
            self.layout = json.load(load_f)
        for ele in self.layout:
            if ele["type"] == "pic":
                self.pic = Location(ele["position"]["top"], ele["position"]["bottom"], \
                                    ele["position"]["left"], ele["position"]["right"])


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
            if layer.type == "pic":
                layout.pic.convert(self.size)
                layer.style["top"] = layout.pic.top_c
                layer.style["left"] = layout.pic.lft_c
                layer.style["width"] = layout.pic.rgt_c - layout.pic.lft_c
                layer.style["height"] = layout.pic.btm_c - layout.pic.top_c
            elif layer.type == "title":
                layout.txt.convert(self.size)
                layer.style["top"] = layout.txt.top_c
                layer.style["left"] = layout.txt.lft_c
            elif layer.type == "logo":
                layout.logo.convert(self.size)
                layer.style["top"] = layout.logo.top_c
                layer.style["left"] = layout.logo.lft_c

    def implement_palette(self, color_palette):
        self.color_palette = color_palette
        for layer in self.design_str:
            if layer.type == 'dec':
                choice = np.random.choice(range(len(color_palette)))
                layer.hue = color_palette[choice]
            elif layer.type == 'title':
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
            f.write(json.dumps(temp).replace('\"','\\"'))#json.dump(temp, f, ensure_ascii=False, indent=4)


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
