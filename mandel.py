import numpy as np
import matplotlib.pyplot as plt

from view import view

w, h, R = 1280*4, 720*4, 100

@view
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
        for _ in range(0, 30):
            z = z**2 + c
        return 0 if abs(z) < R else 255
    except OverflowError:
        return 255

if __name__ == "__main__":
    mandel.prepare(width=512, height=512).run()
