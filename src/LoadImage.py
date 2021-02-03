import numpy as np
import cv2
import cairosvg
from urllib.request import urlretrieve, urlopen

output_path = 'output/'

def url_to_image(url):
    if url[:5] != 'http:':
        url = 'http:' + url

    def download_svg(svg_path):
        cairosvg.svg2png(url=svg_path, write_to=output_path + svg_path[-20:-4] + '.png', scale=40)
        return cv2.imread(output_path + svg_path[-20:-4] + '.png', cv2.IMREAD_UNCHANGED)

    if url[-3:] == 'svg':
        image = download_svg(url)
    else:
        with urlopen(url) as resp:
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
            # cv2.imwrite(output_path + url[-20:], image)
    if image.shape[-1] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        image[:, :, 3] = 255
    return image


def url_to_svg(svg_path):
    if svg_path[:5] != 'http:':
        svg_path = 'http:' + svg_path
    cairosvg.svg2png(url=svg_path, write_to=output_path + svg_path[-20:-4] + '.png', scale=40)
    return cv2.imread(output_path + svg_path[-20:-4] + '.png', cv2.IMREAD_UNCHANGED)


def load_image(path):
    if path[-3:] == 'svg':
        cairosvg.svg2png(path, './image/img1.png')
        image = cv2.imread('./image/img1.png', cv2.IMREAD_UNCHANGED)
    else:
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        image[:, :, 3] = 100
    return image
