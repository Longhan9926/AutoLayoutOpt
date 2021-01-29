import colorsys
from haishoku.haishoku import Haishoku
from haishoku.haillow import joint_image, new_image
from PIL import Image
import cv2
import numpy as np
import random
import math

N = 6
HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)


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


"""
def get_dominant_color(image):
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    image = image.convert('RGBA')
    image.thumbnail((200, 200))

    max_score = None
    dominant_color = None

    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        if a == 0:
            continue

        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
        y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
        y = (y - 16.0) / (235 - 16)

        if y > 0.9:
            continue

        # Calculate the score, preferring highly saturated colors.
        # Add 0.1 to the saturation so we don't completely ignore grayscale
        # colors by multiplying the count by zero, but still give them a low
        # weight.
        score = (saturation + 0.1) * count

        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)

    return dominant_color
"""


def get_dominant_color(image):
    dominant_color = Haishoku.getDominant(image)
    return dominant_color


def get_color_palette(image):
    palette = Haishoku.getPalette(image)
    return palette


def generate_color_palette(n_color, dominant_color, strategy=None):
    """
    Given a dominant color and the number of required colors, return the color palette.
    :param strategy: the strategy to generate the color palette
    :param n_color: number of colors in the palette
    :param dominant_color: the dominant color of the color palette
    :return: a tuple of color palette
    """
    strategies = ["Monotone", 'Complementary', 'angle', 'similar', 'contrast']
    if strategy is None:
        strategy = np.random.choice(strategies)
    seed = random.randint(0, 999)
    np.random.seed(seed)
    color_palette = [dominant_color]
    dominant_color_hsv = colorsys.rgb_to_hsv(dominant_color[0], dominant_color[1],
                                             dominant_color[2])  # convert the dominant color to hsv space
    prime_hue = dominant_color_hsv[0]
    prime_sat = dominant_color_hsv[1]
    prime_val = dominant_color_hsv[2]

    def random_sat(sat, var):
        temps = sat + np.random.normal(loc=0, scale=var, size=None)
        if temps > 1:
            temps = 1
        elif temps < 0:
            temps = 0
        return temps

    while len(color_palette) < n_color:
        choice = np.random.choice(('hue', 'sat', 'val'))
        if len(color_palette) == 1:
            choice = 'hue'
        temp_hue, temp_sat, temp_val = prime_hue, prime_sat, prime_val
        prime_sat_com = prime_sat ** 0.65
        prime_val_com = prime_val ** 0.65
        if choice == 'hue':
            if strategy == 'Monotone':
                temp_hue = np.random.normal(loc=prime_hue, scale=0.08, size=None)
                temp_hue = temp_hue - math.floor(temp_hue)
            elif strategy == 'Complementary':
                choice = np.random.choice((0, 0.5))
                if len(color_palette) == 1:
                    choice = 0.5
                temp_hue = prime_hue + choice
                temp_hue = temp_hue - math.floor(temp_hue)
            elif strategy == 'contrast':
                choice = np.random.choice((0, 1 / 3, -1 / 3))
                if len(color_palette) == 1:
                    choice = np.random.choice((1 / 3, -1 / 3))
                temp_hue = prime_hue + choice
                temp_hue = temp_hue - math.floor(temp_hue)
            elif strategy == 'similar':
                choice = np.random.choice((0, 1 / 20, -1 / 20))
                if len(color_palette) == 1:
                    choice = np.random.choice((1 / 20, -1 / 20))
                temp_hue = prime_hue + choice
                temp_hue = temp_hue - math.floor(temp_hue)
            elif strategy == 'angle':
                choice = np.random.choice((0, 1 / 4, -1 / 4))
                if len(color_palette) == 1:
                    choice = np.random.choice((1 / 4, -1 / 4))
                temp_hue = prime_hue + choice
                temp_hue = temp_hue - math.floor(temp_hue)
            temp_sat = random_sat(prime_sat_com, 0.3)
            temp_val = random_sat(prime_val_com, 0.3)
        elif choice == 'sat':
            temp_sat = random_sat(prime_sat_com, 0.3)
            temp_val = random_sat(prime_val_com, 0.2)
        elif choice == 'val':
            temp_sat = random_sat(prime_sat_com, 0.3)
            temp_val = random_sat(prime_val_com, 0.2)
        curr = colorsys.hsv_to_rgb(temp_hue, temp_sat, temp_val)
        if max(distance_in_color_space(color_palette, curr)) < 0.02:
            continue
        if temp_val < 0.1 or temp_val > 0.95:
            continue
        if temp_sat < 0.1 or temp_sat > 0.98:
            continue
        color_palette.append(curr)
        # May need to drop some colors with high value
    return color_palette


if __name__ == '__main__':
    n = 5
    dominant_color = get_dominant_color('../input/img/free_stock_photo.jpg')
    dominant_color = (dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255)
    palette = generate_color_palette(n, dominant_color, strategy='angle')
    new_palette = []
    for color in palette:
        temp = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        new_palette.append(temp)
    images = []
    for color_mean in new_palette:
        w = 1 / n * 400
        color_box = new_image('RGB', (int(w), 20), color_mean)
        images.append(color_box)

    # generate and show the palette
    joint_image(images)
