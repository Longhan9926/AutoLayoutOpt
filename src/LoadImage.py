import numpy as np
import cv2
import cairosvg
from urllib.request import urlretrieve, urlopen


def url_to_image(url):
    url = 'http:' + url

    def download_svg(svg_path):
        urlretrieve(svg_path, './image/img1.svg')
        cairosvg.svg2png('./image/img1.svg', './image/img1.png')
        return cv2.imread('./image/img1.png', cv2.IMREAD_UNCHANGED)

    if url[-3:] == 'svg':
        image = download_svg(url)
    else:
        with urlopen(url) as resp:
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        image[:, :, 3] = 100
    return image


def load_image(path):
    if path[-3:] == 'svg':
        cairosvg.svg2png(path, './image/img1.png')
        image = cv2.imread('./image/img1.png', cv2.IMREAD_UNCHANGED)
    else:
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image.shape[3] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        image[:, :, 3] = 100
    return image
