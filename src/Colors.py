import colorsys
import math
import random

import numpy as np
from haishoku.haillow import joint_image, new_image
from haishoku.haishoku import Haishoku

N = 6
HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
hue_step = 2
sat_step = 0.1;
sat_step2 = 0.12;
lgt_step1 = 0.05;
lgt_step2 = 0.09;
lightColorCount = 5;
darkColorCount = 4;


def new_list(size):
    newlist = []
    for i in range(0, size):
        newlist.append([])
    return newlist


def distance_in_color_space(palette, color):
    """
    Calculate the distance between color and a palette in color space [hsv]
    :param palette: List of colors
    :param color: tuple of hsv
    :return: List of distance
    """
    Distance = []
    for c in palette:
        temp = [(c[x] - color[x]) * (c[x] - color[x]) for x in range(3)]
        Distance.append(sum(temp))
    return Distance


def get_dominant_color(image):
    dominant_color = Haishoku.getDominant(image)
    return dominant_color


def get_color_palette(image):
    palette = Haishoku.getPalette(image)
    return palette


def get_hue(color, i, isLight):
    h = color[0] * 360
    if 60 <= h <= 240:
        hue = h - hue_step * i if isLight else h + hue_step * i
    else:
        hue = h + hue_step * i if isLight else h - hue_step * i
    if hue < 0:
        hue += 360
    elif hue > 360:
        hue -= 360
    return hue/360


def get_sat(color, i, isLight):
    s = color[1]
    if isLight:
        sat = s - sat_step * i
    elif i == darkColorCount:
        sat = s + sat_step
    else:
        sat = s + sat_step2 * i
    sat = 1 if sat > 1 else sat
    sat = 0.1 if (isLight and i == lightColorCount and sat < 0.1) else sat
    sat = 0.06 if sat < 0.06 else sat
    return sat


def get_val(color, i, isLight):
    v = color[2]
    if isLight:
        val = v + lgt_step1 * i
    else:
        val = v - lgt_step2 * i
    val = 1 if val > 1 else val
    return val


def generate_tints_n_shades(color):
    """
    :param color: in hsv
    :return:
    """
    s = color[1] ** 0.3
    v = color[2] ** 0.3
    s = 0.7 if s < 0.7 else s
    v = 0.7 if v < 0.7 else v
    palette = []
    color_s = (color[0],s,v)
    for inx in range(10):
        index = inx + 1
        if index == 6:
            palette.append(color_s)
        else:
            isLight = index < 6
            i = lightColorCount + 1 - index if isLight else index - lightColorCount - 1
            h = get_hue(color_s, i, isLight)
            s = get_sat(color_s, i, isLight)
            v = get_val(color_s, i, isLight)
            palette.append((h,s,v))
    return palette


def generate_color_palette(n_color, dominant_color):
    """
    Given a dominant color and the number of required colors, return the color palette.
    :param strategy: the strategy to generate the color palette
    :param n_color: number of colors in the palette
    :param dominant_color: the dominant color of the color palette
    :return: a tuple of color palette
    """
    strategies = ['Complementary', 'angle', 'similar', 'contrast', 'any']
    strategy = np.random.choice(strategies)
    seed = random.randint(0, 999)
    np.random.seed(seed)
    color_palette = {}
    dominant_color_hsv = colorsys.rgb_to_hsv(dominant_color[0], dominant_color[1],
                                             dominant_color[2])  # convert the dominant color to hsv space
    prime_hue, prime_sat, prime_val = dominant_color_hsv
    color_palette["1"] = generate_tints_n_shades(dominant_color_hsv)

    def random_sat(sat, var):
        temps = sat + np.random.normal(loc=0, scale=var, size=None)
        if temps > 1:
            temps = 1
        elif temps < 0:
            temps = 0
        return temps

    while len(color_palette) < n_color:
        key = str(len(color_palette)+1)

        if strategy == 'Complementary':
            choice = 0.5
        elif strategy == 'contrast':
            choice = np.random.choice((1 / 3, -1 / 3))
        elif strategy == 'similar':
            choice = np.random.choice((1 / 20, -1 / 20))
        elif strategy == 'angle':
            choice = np.random.choice((1 / 4, -1 / 4))
        elif strategy == 'any':
            choice = np.random.choice((1 / 6, -1 / 6))
        temp_hue = prime_hue + choice
        temp_hue = temp_hue - math.floor(temp_hue)
        temp_sat = random_sat(prime_sat, 0.3)
        temp_val = random_sat(prime_val, 0.3)

        color_palette[key] = generate_tints_n_shades((temp_hue,temp_sat, temp_val))

    return color_palette


if __name__ == '__main__':
    n = 5
    dominant_color = get_dominant_color('../input/img/下载.jpeg')
    dominant_color = (dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255)
    palette = generate_color_palette(n, dominant_color)
    for key, item in palette.items():
        new_palette = []
        for color in palette[key]:
            color = colorsys.hsv_to_rgb(color[0], color[1], color[2])
            temp = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
            new_palette.append(temp)
        images = []
        for color_mean in new_palette:
            w = 1 / 10 * 400
            color_box = new_image('RGB', (int(w), 20), color_mean)
            images.append(color_box)

        # generate and show the palette
        joint_image(images)
