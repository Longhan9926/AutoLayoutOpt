import src
import Generate

import numpy as np
import os
import json
import random
import operator
from functools import reduce
import colorsys
import copy

random.seed(random.randint(0, 10000))
faces_names = ["F", "H", "FR", "FL"]
element_types = ["background", "prime_picture", "decoration", "logo", "title", "slogan", "text"]
layer_types = ["src.Decoration", "src.Picture", "src.Decoration", "src.Logo", "src.Title", "src.Slogan", "src.Text"]


def new_list(size):
    newlist = []
    for i in range(0, size):
        newlist.append([])
    return newlist


def determine_layout():
    box_layout = {}
    for face_name in faces_names:
        try:
            with open('input/layout' + face_name + '.json', 'r') as load_f:
                layouts = json.load(load_f)
            # temp = np.random.choice(layouts)
            temp = layouts[-1]
            face_layout = {}
            for key, ele in temp.items():
                face_layout[ele["type"]] = Generate.Location(ele["position"]["top"], ele["position"]["bottom"], \
                                                             ele["position"]["left"], ele["position"]["right"])
                if ele["type"] in ["title", "slogan", "txt"]:
                    face_layout[ele["type"]].font_setting(ele["FontSetting"])
                    if ele["type"] in ["title", "slogan"]:
                        choice = np.random.choice(["bold", "normal"])
                        face_layout[ele["type"]].font_set["fontWeight"] = choice
            box_layout[face_name] = face_layout
        except FileNotFoundError:
            pass
    return box_layout


class Box:
    def __init__(self, face_data, dominant_color, layout, n_palette=2, safe_distance=5):
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
        self.safe = safe_distance
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
        face.load_layout_b(self.layout[key], self.safe, face_size, face_loc)
        face.implement_palette(self.color_palette["1"])
        self.faces[key] = face

    def copy_face(self, old, new):
        self.faces[new] = copy.deepcopy(self.faces[old])
        face_size_new = src.get_face_size(self.face_data[new])
        face_loc_new = src.get_face_loc(self.face_data[new])
        face_size_old = src.get_face_size(self.face_data[old])
        face_loc_old = src.get_face_loc(self.face_data[old])
        self.faces[new].load_layout_n(self.layout[new], self.safe, face_size_new, face_loc_new)
        self.faces[old].load_layout_n(self.layout[old], self.safe, face_size_old, face_loc_old)

    def set_face_color(self, palette):
        raise NotImplementedError

    def implement_color_palette(self):
        with open('upload_raw.json', 'r') as f:
            collection = json.load(f)
        # prime_palette = self.color_palette["1"]
        index = random.randint(2, n_palette)
        bkg_palette = self.color_palette[str(index)]
        bkg_color = random.choice(bkg_palette)
        bkg_color = colorsys.hsv_to_rgb(bkg_color[0], bkg_color[1] ** 1.5, bkg_color[2] ** 1.5)
        with open('upload_raw.json', 'w') as f:
            choice = np.random.choice([1, 0, 2, 3])
            if choice == 1:
                collection["background"] = "rgba({0},{1},{2},{3})".format(str(bkg_color[0] * 255),
                                                                          str(bkg_color[1] * 255),
                                                                          str(bkg_color[2] * 255), str(150))
                faces_color = {}
                for key in ["F", "H"]:
                    faces_color[key] = {}
                    faces_color[key]["rgba"] = "rgba(255,255,255,255)"
            elif choice == 2:
                collection["background"] = "rgba(255,255,255,255)"
                faces_color = {}
                for key in ["FR", "FL"]:
                    faces_color[key] = {}
                    faces_color[key]["rgba"] = "rgba({0},{1},{2},{3})".format(str(bkg_color[0] * 255),
                                                                              str(bkg_color[1] * 255),
                                                                              str(bkg_color[2] * 255), str(150))
            elif choice == 3:
                collection["background"] = "rgba({0},{1},{2},{3})".format(str(bkg_color[0] * 255),
                                                                          str(bkg_color[1] * 255),
                                                                          str(bkg_color[2] * 255), str(150))
                faces_color = {}
                for key in ["F", "H", "FR", "FL"]:
                    faces_color[key] = {}
                    faces_color[key]["rgba"] = "rgba(255,255,255,255)"
            else:
                collection["background"] = ""
                faces_color = {}
            collection["face_background"] = json.dumps(faces_color)
            f.write(json.dumps(collection))

    def save_box(self):
        temp = []
        for key, face in self.faces.items():
            for layer in face.design_str:
                temp.append(layer.layer)
        with open('box.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(temp))

    def upload_box(self, id):
        with open('box.json', 'r') as load_f:
            box = json.load(load_f)
        with open('upload_raw.json', 'r') as f:
            collection = json.load(f)
            collection["design_data"] = json.dumps(box)
            collection["project_id"] = id
        src.http_put(collection)


if __name__ == '__main__':
    id = 217642 # 200227  # 215561
    url = "https://www.baoxiaohe.com/api/bs/box/project/knifes?bleed=3&dpi=3.7795275591&id=" + str(id)
    face_data = src.http_get_size(url)
    prime = 'input/img'
    files = os.listdir(prime)
    files.remove('.DS_Store')
    file = random.sample(files, 1)
    prime = prime + '/下载.jpeg'
    # prime = prime + '/' + file[0]
    prime_url = src.upload_image(prime)

    title_file = json.load(open("input/title.json"))
    title = random.choice(title_file)
    slogan_file = json.load(open("input/slogan.json"))
    slogan = random.choice(slogan_file)
    text_file = json.load(open("input/text.json"))
    text1 = random.choice(text_file)
    text2 = "产品名称：红酒开酒器\n外箱尺寸：424×204×258mm\n规         格：10个/箱\n企业代码：313454654645\n执行标准：564654515645\n生  产  商：杭州片段网络科技有限公司\n地         址：杭州市西湖区西湖国际大厦B2座\n客服电话：0571-87150783\n官         网： www.baoxiaohe.com\n"
    logo = None
    n_palette = 5

    dominant_color = src.get_dominant_color(prime)
    dominant_color = (dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255)

    box_layout = determine_layout()
    box_layout["H"] = box_layout["F"]
    box_layout["FR"] = box_layout["FL"]

    safe_distance = 3
    new_box = Box(face_data, dominant_color, box_layout, n_palette, safe_distance)

    F_inputs = {}
    F_inputs["prime_picture"] = prime_url
    F_inputs["title"] = title
    F_inputs["slogan"] = slogan
    F_inputs["text"] = text1
    F_inputs["logo"] = logo
    new_box.design_face(key="F", inputs=F_inputs)

    FR_inputs = {}
    FR_inputs["text"] = text2
    FR_inputs["title"] = "CODEHERE"
    new_box.design_face(key="FR", inputs=FR_inputs)

    new_box.copy_face("F", "H")
    new_box.copy_face("FR", "FL")

    new_box.implement_color_palette()

    new_box.save_box()
    new_box.upload_box(id)
