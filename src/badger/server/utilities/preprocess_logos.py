import json
import pathlib

import imutils
import matplotlib
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt


def on_key(event):
    if event.key == 'd':
        pass


raw_path = pathlib.Path('../../../../assets/images/raw')
tag_lib_path = pathlib.Path('../../../../data/tags.json')

matplotlib.use('TkAgg')

tag_lib: dict
if tag_lib_path.exists():
    with tag_lib_path.open('r') as file:
        tag_lib = json.load(file)
else:
    tag_lib = {}

for path in raw_path.iterdir():
    print(path, end='')
    if path.stem in tag_lib.keys():
        tags = tag_lib[path.stem]
    else:
        tags = {}

    print(tags)
    image = cv.imread(path, cv.IMREAD_UNCHANGED)

    if image is None:
        continue

    fig = plt.figure(figsize=(18, 7))
    image = imutils.resize(image, width=600)
    bgr, alpha = image[:,:,:3], image[:,:,3]
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    plt.subplot(2, 2, 1)
    plt.imshow(image)
    plt.axis('off')
    plt.title('RAW')

    plt.subplot(2, 2, 2)
    plt.imshow(gray, cmap=plt.cm.gray)
    plt.axis('off')
    plt.title('gray')

    plt.ion ()
    plt.show()

    while True:
        plt.pause(1.0)
        key = cv.waitKey()
        if ord('n') == key:
            break
        elif ord('q') == key:
            exit(0)
        elif ord('d') == key:
            tags['display'] = 'ok'


    tag_lib[path.stem] = tags

    with tag_lib_path.open('w') as file:
        json.dump(tag_lib, file)
