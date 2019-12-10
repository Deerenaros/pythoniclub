import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

w, h, R = 1280*4, 720*4, 100

@np.vectorize
def mandel(y, x):
    c = (x-w/2)/(w/3) - 0.5 + (y-h/2)/(h/2)*1j
    z = c
    try:
        for _ in range(0, 30):
            z = z**2 + c
        return [1.0, 0.0][abs(z) < R]
    except OverflowError:
        return 1.0

buff = np.fromfunction(mandel, (h, w), dtype=np.float)

#plt.imshow(buff)
#plt.show()

rescaled = (255.0 / buff.max() * (buff - buff.min())).astype(np.uint8)
Image.fromarray(rescaled).save("mandel.png")
