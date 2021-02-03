import argparse
import colorsys
import json
import math
from typing import List

import numpy as np

import src

len_px = 3.7795275591
open_file = open("input/basic_material.json")
urls = json.load(open_file)


class Location:
    def __init__(self, top=0, btm=100, lft=0, rgt=100, size=[100, 100]):
        self.position = {
            "absolute": {"top": 0, "height": 0, "left": 0, "width": 0},
            "resolute": {"top": 0, "height": 0, "left": 0, "width": 0},
            "percentage": {"top": top, "btm": btm, "lft": lft, "rgt": rgt}
        }
        self.define_size(size, [0, 0], 0)
        self.font_set = {}

    def define_size(self, size, loc, safe):
        """
        :param size:in real length [mm] [width, height]
        """
        self.position["absolute"]["top"] = self.position["percentage"]["top"] * (size[1] - safe * 2) / 100 + loc[
            1] + safe
        self.position["absolute"]["left"] = self.position["percentage"]["lft"] * (size[0] - safe * 2) / 100 + loc[
            0] + safe
        self.position["absolute"]["height"] = self.position["percentage"]["btm"] * (size[1] - safe * 2) / 100 \
                                              - self.position["percentage"]["top"] * (size[1] - safe * 2) / 100
        self.position["absolute"]["width"] = self.position["percentage"]["rgt"] * (size[0] - safe * 2) / 100 \
                                             - self.position["percentage"]["lft"] * (size[0] - safe * 2) / 100
        # The following part is problematic
        self.position["resolute"]["top"] = math.floor(self.position["absolute"]["top"] * len_px)
        self.position["resolute"]["left"] = math.floor(self.position["absolute"]["left"] * len_px)
        self.position["resolute"]["height"] = math.floor(self.position["absolute"]["height"] * len_px)
        self.position["resolute"]["width"] = math.floor(self.position["absolute"]["width"] * len_px)

    def font_setting(self, setting):
        self.font_set = setting


class Layout:
    def __init__(self):
        self.layout = {}

    def load_layout(self, file_path):
        with open(file_path, 'r') as load_f:
            layouts = json.load(load_f)
        temp = np.random.choice(layouts)
        for key, ele in temp.items():
            self.layout[ele["type"]] = Location(ele["position"]["top"], ele["position"]["bottom"], \
                                                ele["position"]["left"], ele["position"]["right"])


class Design:
    def __init__(self, size, loc):
        """
        The class of a 2d model design
        :param size: in absolute size [mm] [width, height]
        """
        self.design_str: List[src.Layers.ComponentLayer] = []
        self.loc = loc
        self.size_a = size
        self.size = [math.floor(len_px * x) for x in size]
        # self.canvas = src.InitCanvas(self.size[0], self.size[1])
        self.mask = np.zeros(self.size)
        self.color_palette = None

    def insert_layer(self, new_layer, ind=-1):
        self.design_str.insert(ind, new_layer)

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
            layout.layout[layer.type].define_size(self.size_a, self.loc)
            for key in ["top", "left", "width", "height"]:
                layer.style[key] = layout.layout[layer.type].position["absolute"][key]
            if layer.type == 'pic':
                layer.crop_scale(
                    [math.floor(layer.style["width"] * len_px), math.floor(layer.style["height"] * len_px)])
            if layer.type == 'logo':
                layer.style.pop("height")
            if layer.type == 'txt' or layer.type == 'title':
                layer.style.pop("height")
                # layer.style.pop("width")

    def load_layout_b(self, layout, safe_distance, face_size, face_loc):
        for layer in self.design_str:
            layout[layer.type].define_size(face_size, face_loc, safe_distance)
            for key in ["top", "left", "width", "height"]:
                layer.style[key] = layout[layer.type].position["absolute"][key]
            if layer.type == 'pic':
                layer.crop_scale(
                    [math.floor(layer.style["width"] * len_px), math.floor(layer.style["height"] * len_px)])
            if layer.type == 'logo':
                height = layer.style["width"] / layer.shape_origin
                if layer.style["top"] / face_size[1] > 0.5:
                    layer.style["top"] = layer.style["top"] - height + layer.style["height"]
                    layer.style["height"] = height
                else:
                    layer.style["height"] = height
            if layer.type in ["title", "slogan", "txt", "text"]:
                layer.set_font(layout[layer.type].font_set)
                layer.cal_text_size()

    def load_layout_n(self, layout, safe_distance, face_size, face_loc):
        for layer in self.design_str:
            layout[layer.type].define_size(face_size, face_loc, safe_distance)
            for key in ["top", "left", "width", "height"]:
                layer.style[key] = layout[layer.type].position["absolute"][key]
            if layer.type == 'logo':
                height = layer.style["width"] / layer.shape_origin
                if layer.style["top"] / face_size[1] > 0.5:
                    layer.style["top"] = layer.style["top"] - height + layer.style["height"]
                    layer.style["height"] = height
                else:
                    layer.style["height"] = height
            if layer.type in ["title", "slogan", "txt", "text"]:
                layer.set_font(layout[layer.type].font_set)
                layer.cal_text_size()

    def implement_palette(self, color_palette):
        self.color_palette = color_palette
        for layer in self.design_str:
            if layer.type not in ["dec", "title", "slogan"]:
                continue
            elif layer.hue:
                layer.set_color(layer.hue)
            else:
                choice = np.random.choice(range(len(color_palette)))
                temp = color_palette[choice]
                layer.set_color(colorsys.hsv_to_rgb(temp[0],temp[1]**1.5,temp[2]**1.5))

    def save_design(self):
        temp = []
        for layer in self.design_str:
            temp.append(layer.layer)
        with open('design.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(temp))  # .replace('\"', '\\"'))

    def upload_design(self):
        with open('design.json', 'r') as load_f:
            design = json.load(load_f)
        with open('upload_raw.json', 'r') as f:
            collection = json.load(f)
            collection["design_data"] = json.dumps(design)
        src.http_put(collection)


def main(args):
    new_design = Design(args.size)

    # load the text, picture into the layout
    prime_pic = src.load_image(args.prime)
    dominant_color = src.get_dominant_color(args.prime)
    color_palette = src.generate_color_palette(3, dominant_color, strategy='Monotone')
    layout = Layout()
    layout.load_layout("input/layoutF.json")
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
    size = [430, 360]  # [width, height] [mm]
    loc = [45.5, 105.5]  # [left, top] [mm]
    prime = 'input/img/free_stock_photo.jpg'
    text = 'Hello'
    logo = None

    new_design = Design(size, loc)

    # load the text, picture into the layout
    dominant_color = src.get_dominant_color(prime)
    dominant_color = (dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255)
    color_palette = src.generate_color_palette(2, dominant_color, strategy='Monotone')
    layout = Layout()
    layout.load_layout('input/layoutF.json')
    prime_url = src.upload_image(prime)
    prime_layer = src.Picture(prime_url)
    bkg = src.Decoration()
    title = src.Title(text)
    new_design.insert_layer(bkg)
    new_design.insert_layer(prime_layer)
    new_design.insert_layer(title)
    if logo is not None:
        new_design.insert_layer(src.Logo(logo))
    else:
        new_design.insert_layer(src.Logo())
    new_design.load_layout(layout)
    new_design.implement_palette(color_palette)
    new_design.save_design()
    new_design.upload_design()
