from PIL import Image
from PIL import ImageDraw
import numpy as np
import random
import colorsys


def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n - 1)

    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t ** i for i in range(n))
            upowers = reversed([(1 - t) ** i for i in range(n)])
            coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result

    return bezier


def pascal_row(n, memo={}):
    # This returns the nth row of Pascal's Triangle
    if n in memo:
        return memo[n]
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    memo[n] = result
    return result


def generate_dec(im, size, color, pt1, pt2, is_down=True, n_control=2):
    draw = ImageDraw.Draw(im)
    ts = [t / 100.0 for t in range(101)]
    pt3 = (pt2[0], size[1]) if is_down else (pt2[0], 0)
    pt4 = (pt1[0], size[1]) if is_down else (pt1[0], 0)

    xys = [pt1, pt2]
    while len(xys) < n_control:
        xys.insert(1, (np.random.uniform(low=pt1[0], high=pt2[0]),
                       np.random.normal(loc=(pt1[1] + pt2[1]) / 2, scale=abs(pt1[1] - pt2[1]) * 1.5 + 20)))

    bezier = make_bezier(xys)
    points = bezier(ts)

    xys = [pt2, pt3]
    bezier = make_bezier(xys)
    points.extend(bezier(ts))

    xys = [pt3, pt4]
    bezier = make_bezier(xys)
    points.extend(bezier(ts))

    xys = [pt4, pt1]
    bezier = make_bezier(xys)
    points.extend(bezier(ts))

    color = tuple(int(x*255) for x in color)
    draw.polygon(points, fill=color)
    return im


def generate_combine(im, palette, size, pt1, pt2, is_down=True, n_control=None, n_layer=None):
    h_1 = size[1] - pt1[1] if is_down else pt1[1]
    h_2 = size[1] - pt2[1] if is_down else pt2[1]

    # def get_loc(loc):
    #     length = loc * (h_1 + h_2 + size[0])
    #     if length < h_1:
    #         x = 0
    #         y = pt1[1] + length
    #     elif length > h_1 + size[0]:
    #         x = size[0]
    #         y = size[1] + size[0] + h_1 - length
    #     else:
    #         x = length - h_1
    #         y = size[1]
    #     return (x, y)
    #
    # b,e = 0,1

    n_layer = n_layer if n_layer else np.random.choice([0, 1, 2])
    palette_c = random.sample(palette[:-1], n_layer-1)
    palette_c = palette_c + [palette[-1]]
    n_control = n_control if n_control else np.random.randint(2, 7)
    bkg_color = palette_c[0]
    bkg_color = colorsys.hsv_to_rgb(bkg_color[0], bkg_color[1] ** 1.5, bkg_color[2] ** 1.5)
    try:
        for i in range(1, n_layer):
            l = random.uniform(0,h_1)
            r = random.uniform(0,h_2)
            pt1_c = (0, l+pt1[1])
            pt2_c = (size[0], r + pt2[1])
            im = generate_dec(im, size, palette_c[i], pt1_c, pt2_c, is_down, n_control)
            # im.save('out'+str(i)+'.png')
    except:
        pass
    im = generate_dec(im, size, bkg_color, pt1, pt2, is_down, n_control)

    return im


if __name__ == '__main__':
    size = [2000, 2000]
    im = Image.new('RGBA', tuple(size), (0, 0, 0, 0))
    palette = [(225, 0, 0), (200, 0, 0), (150, 0, 0), (100, 0, 0)]
    im = generate_combine(im, palette, size, (0, 1600), (2000, 1800), n_control=3, n_layer=2)
    im = generate_combine(im, palette, size, (0, 200), (2000, 300), is_down=False, n_control=3, n_layer=2)

    im.save('out.png')
