import numpy as np
import math
import cv2


def CalResolution(len_width, len_height, ppi = 300):
    """
    Calculate the resolution from size input.
    :param len_width: in millimeters
    :param len_height: in millimeters
    :param ppi: pixel per inch2, no smaller than 300
    :return: resolution of the desired output
    """
    area = len_width * len_height
    num_pixel = (math.ceil(area * ppi // 400) + 1)*400
    return math.sqrt(area/num_pixel)


def ConvertToPixel(len, a_pixel=3.7795275591):
    return math.ceil(len/a_pixel)


def InitCanvas(width, height, color=(255, 255, 255)):
    canvas = np.ones((height, width, 4), dtype="uint8") * 15
    canvas[:, :, :3] = 255
    return canvas


if __name__ == '__main__':
    ans = CalResolution(1200, 300)
    print(ans)