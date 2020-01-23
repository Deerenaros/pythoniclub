import numpy as np
import matplotlib.pyplot as plt

import cv2

from view import view

R = 30
L = 4

class colormap:
    def __init__(self):
        self.img = cv2.imread("cmap.png")
        self.K = self.img.shape[1] / 256
        self.R = [tuple(self.img[0, round(i*self.K)]/255) for i in range(0, 255)]
        self.R.append((1, 1, 1))

    def flush(self):
        return f"{{ {','.join('vec4(%f,%f,%f,1)' % col for col in self.R)} }}"

    def __call__(self, arr2d):
        return np.array([[self.R[pixel] for pixel in row] for row in arr2d])

    def animate(self):
        self.R = self.R[1:-1] + self.R[0:1] + self.R[-1:]

@view(width=384, height=384, color=colormap())
@np.vectorize
def mandel(x, y, g=None):
    x = x/g.w
    x = x*(g.bot_right.x - g.top_left.x)
    x = x + g.top_left.x

    y = y/g.h
    y = y*(g.top_left.y - g.bot_right.y)
    y = y + g.bot_right.y

    c = x + y*1j
    z = c
    try:
        for k in range(1, R+1):
            z = z**2 + c
            if abs(z) > L:
                break
        return 255 if k == R else k
    except OverflowError:
        return 255


if __name__ == "__main__":
    mandel.run()
