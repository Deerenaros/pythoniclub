import cv2
import numpy as np
import matplotlib.pyplot as plt

from view import view
from PIL import Image

w, h, R = 1280*4, 720*4, 100

@view
@np.vectorize
def mandel(x, y, g=None):
    x = x/g.w
    x = x*(g.s[0][1] - g.s[0][0])
    x = x + g.s[0][0]

    y = y/g.h
    y = y*(g.s[0][1] - g.s[0][0])
    y = y + g.s[0][0]

    c = x + y*1j
    z = c
    try:
        for _ in range(0, 30):
            z = z**2 + c
        return [255, 0][abs(z) < R]
    except OverflowError:
        return 255


mandel.prepare(width=1024, height=1024).run()
