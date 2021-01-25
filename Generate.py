import src
import sys
import math
import json
import argparse

len_px = 3.7795275591


class Layout:
    def __init__(self):
        self.layout = {}

    def load_layout(self, file_path):
        self.layout = {}
        with open(file_path, 'r') as load_f:
            self.layout = json.load(load_f)


class Design:
    def __init__(self, width, height):
        self.design_str = []
        self.width = math.ceil(width * len_px)
        self.height = math.ceil(height * len_px)
        self.canvas = src.InitCanvas(self.width, self.height)
        self.color_palette = None
        self.dominant_color = None

    def insert_layer(self, new_layer):
        self.design_str.append(new_layer)

    def load_pic(self, file_path):
        raise NotImplementedError

    def load_design(self, file_path="output/a.json"):
        self.design_str = []
        with open(file_path, 'r') as load_f:
            load_dict = json.load(load_f)
        for new_layer in load_dict:
            temp = src.ComponentLayer()
            temp.load_layer(new_layer)
            self.insert_layer(temp)

    def get_dominant_color(self):
        image = self.show_image()
        self.dominant_color = src.get_dominant_color(image)

    def get_color_palette(self):
        image = self.show_image()
        self.color_palette = src.get_color_palette(image)

    def show_image(self):
        for layer in self.design_str:
            pic = layer.generate_pic()
            self.canvas[layer.top:layer.top + layer.height, layer.left:layer.left + layer.width, :] = pic
        return self.canvas


def main(args):
    new_design = Design()

    # load the text, picture into the layout
    prime_pic = src.load_image(args.prime)
    dominant_color = src.get_dominant_color(prime_pic)
    color_palette = src.generate_color_palette(3, dominant_color, strategy='Monotone')



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
    main(parse_arguments(sys.argv[1:]))
