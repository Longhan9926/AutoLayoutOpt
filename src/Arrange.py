import os
import sys
import argparse
import cv2
from .Layers import Design, Title, BKG

output_folder = "./test_output"

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--img', type=str, help='input img', default=None)
    parser.add_argument('--img_folder', type=str, help='input img folder', default=None)
    parser.add_argument('--txt', type=str, help='input text', default=None)
    parser.add_argument('--hue', type=str, help='input color palette', default=None)

    return parser.parse_args(argv)


def arrange(args):
    design = Design

    img_pth = os.listdir(args.img)
    bkgs = BKG(img_pth)


    patterns = []

    txts = []
    texts = open(args.txt, "r")
    lines = texts.readlines()
    for line in lines:
        txts.append(Title(line))






if __name__ == '__main__':
    arrange(parse_arguments(sys.argv[1:]))