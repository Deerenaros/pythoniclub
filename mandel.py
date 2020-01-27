import numpy as np
import matplotlib.pyplot as plt

import cv2

from view import view, translate

R = 30
L = 4

class colormap:
    def __init__(self):
        self.img = cv2.imread("cmap.png")
        self.K = self.img.shape[1] / 256
        self.R = []
        self.R.append((0, 0, 0))
        self.R += [tuple(self.img[0, round(i*self.K)]/255) for i in range(1, 255)]
        self.R.append((1, 1, 1))

    def flush(self):
        return f"{{ {','.join('vec4(%f,%f,%f,1)' % col for col in self.R)} }}"

    def __call__(self, arr2d):
        return np.array([[self.R[pixel] for pixel in row] for row in arr2d])

    def animate(self):
        self.R = self.R[1:-1] + self.R[0:1] + self.R[-1:]

@view(width=384, height=384, fps=100500, color=colormap(), fs=False)
@np.vectorize
@translate
def mandel(x, y):
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
