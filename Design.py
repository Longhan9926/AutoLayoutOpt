import src
import Generate

import numpy as np
import json
import operator
from functools import reduce

faces_names = ["F", "H", "FR", "FL"]
element_types = ["background", "prime_picture", "decoration", "logo", "title", "slogan", "text"]
layer_types = ["src.Decoration", "src.Picture", "src.Decoration", "src.Logo", "src.Title", "src.Slogan", "src.Title"]


def new_list(size):
    newlist = []
    for i in range(0, size):
        newlist.append([])
    return newlist


class Box:
    def __init__(self, face_data, dominant_color, layout, n_palette=2):
        """

        :param face_data:
        :param dominant_color:
        :param layout: a dictionary of all faces layout, different from Design class
        :param n_palette:
        """
        self.face_data = face_data
        self.dominant_color = dominant_color
        self.color_palette = src.generate_color_palette(n_palette, self.dominant_color)
        self.layout = layout
        self.faces = {}

    def design_face(self, key="F", inputs={}):
        """

        :param key:
        :param inputs: list of input elements
        :return:
        """
        face_size = src.get_face_size(self.face_data[key])
        face_loc = src.get_face_loc(self.face_data[key])
        face = Generate.Design(face_size, face_loc)
        layers = new_list(len(element_types))
        for ele_type, input in inputs.items():
            rank = element_types.index(ele_type)
            temp_layer = eval(layer_types[rank] + "(input)")
            layers[rank].append(temp_layer)
        layers = reduce(operator.add, layers)
        for layer in layers:
            face.insert_layer(layer)
        face.load_layout_b(self.layout[key])
        face.implement_palette(self.color_palette)
        self.faces[key] = face

    def save_box(self):
        temp = []
        for key, face in self.faces.items():
            for layer in face.design_str:
                temp.append(layer.layer)
        with open('box.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(temp))

    def upload_box(self):
        with open('box.json', 'r') as load_f:
            box = json.load(load_f)
        with open('upload_raw.json', 'r') as f:
            collection = json.load(f)
            collection["design_data"] = json.dumps(box)
        src.http_put(collection)


if __name__ == '__main__':
    url = "https://www.baoxiaohe.com/api/bs/box/project/knifes?bleed=3&dpi=3.7795275591&id=200227"
    face_data = src.http_get_size(url)
    prime = 'input/img/下载.jpeg'
    prime_url = src.upload_image(prime)
    title = 'Hello'
    text = 'This is a text'
    logo = None
    n_palette = 2

    dominant_color = src.get_dominant_color(prime)
    dominant_color = (dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255)

    box_layout = {}
    for face_name in faces_names:
        try:
            with open('input/layout' + face_name + '.json', 'r') as load_f:
                layouts = json.load(load_f)
            temp = np.random.choice(layouts)
            face_layout = {}
            for key, ele in temp.items():
                face_layout[ele["type"]] = Generate.Location(ele["position"]["top"], ele["position"]["bottom"], \
                                                             ele["position"]["left"], ele["position"]["right"])
            box_layout[face_name] = face_layout
        except (RuntimeError, TypeError, NameError, FileNotFoundError):
            pass

    new_box = Box(face_data, dominant_color, box_layout, n_palette)

    F_inputs = {}
    F_inputs["prime_picture"] = prime_url
    F_inputs["title"] = title
    F_inputs["slogan"] = text
    F_inputs["logo"] = logo
    new_box.design_face(key="F", inputs=F_inputs)
    new_box.design_face(key="H", inputs=F_inputs)
    new_box.save_box()
    new_box.upload_box()
