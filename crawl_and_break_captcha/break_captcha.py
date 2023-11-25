"""
    Created by @namhainguyen2803 in 25/11/2023
"""


from PIL import Image
import matplotlib.pyplot as plt
import io
import numpy as np
from transformers import pipeline
from utils import *

CANDIDATE_LABEL = ["cow", "bird", "dog", "mouse",
                   "chicken", "pig", "tiger", "cat",
                   "horse", "rabbit", "buffalo", "duck", "elephant"]

def initialize_detector():
    checkpoint = "openai/clip-vit-large-patch14"
    detector = pipeline(model=checkpoint, task="zero-shot-image-classification")
    return detector

def break_captcha(captcha_image):

    checkpoint = "openai/clip-vit-large-patch14"
    detector = pipeline(model=checkpoint, task="zero-shot-image-classification")

    img = Image.open(captcha_image)

    width, height = img.size
    part_width = width // 4
    regions = []
    for i in range(4):
        left = i * part_width
        right = (i + 1) * part_width if i < 3 else width
        regions.append((left, 0, right, height))
    border_colors = []
    for region in regions:
        part = img.crop(region)
        border_pixels = []
        for x in range(part.width):
            for y in range(part.height):
                if x == 0 or y == 0 or x == part.width - 1 or y == part.height - 1:
                    border_pixels.append(part.getpixel((x, y)))
        border_pixels = np.array(border_pixels)
        color, count = np.unique(border_pixels, axis=0, return_counts=True)
        dominant_color = color[np.argmax(count)]

        border_colors.append(dominant_color)

    res = list()

    for i in range(len(border_colors)):
        if np.all(border_colors[i] == np.array([255, 255, 1, 255])):
            part = img.crop(regions[i])
            predictions = detector(part, candidate_labels=CANDIDATE_LABEL)
            res.append(predictions)
            plt.imshow(part)
            plt.show()

    res_captcha = ""
    final_res = post_process_result(res)
    for eng_name in final_res:
        vnese_name = remove_diacritics(map_to_vietnamese(eng_name))
        res_captcha += vnese_name
    return res_captcha