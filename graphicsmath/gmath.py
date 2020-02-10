import numpy as np


class vec(np.ndarray):
    def __new__(self, *args):
        v = np.ndarray.__new__(vec, (len(args),), dtype=np.float)
        v[:] = args
        return v

    def __str__(self):
        return "<%s>" % ", ".join(f"{float(v):.2}" for v in self)

    def __repr__(self):
        return "vec<%s>" % ", ".join(f"{float(v):.2}" for v in self)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    @x.setter
    def x(self, val):
        self[0] = val

    @y.setter
    def y(self, val):
        self[1] = val

    @z.setter
    def z(self, val):
        self[2] = val


def point_inside_polygon(x, y, poly):  # graphicsmath package
    """Thanks to this guy wrote this article
    http://www.ariel.com.au/a/python-point-int-poly.html"""

    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


class square:  # graphicsmath package
    def __init__(self, tl=vec(-1, 1), br=vec(1, -1), w=1, h=1, g=None, fn=None):  # semi inhertance
        self.top_left = tl
        self.bottom_right = br
        self.w, self.h = w, h
        self.surface = None
        self.g = g  # global variables' spaces
        self.fn = fn  # function with calc

    @property
    def topleft(self):
        return self.top_left

    @property
    def bottomright(self):
        return self.bottom_right

    @property
    def points(self):
        return ((self.topleft.x, self.topleft.y),
                (self.bottomright.x, self.topleft.y),
                (self.topleft.x, self.bottomright.y),
                (self.bottomright.x, self.bottomright.y))

    def __contains__(self, point):
        return point_inside_polygon(*point, self.points)

    def __str__(self):
        import itertools
        chain, at = itertools.chain(self.top_left, self.bottom_right), ""
        if self.g:
            g = self.g
            oh = int(round((self.topleft.y - g.topleft.y) * g.h / (g.bottomright.y - g.topleft.y)))
            ow = int(round((self.topleft.x - g.topleft.x) * g.w / (g.bottomright.x - g.topleft.x)))
            at = "@ %s %s" % (ow, oh)
        return "|%s|" % " ".join(f"{float(v):.2}" for v in chain) + at

    def size(self):
        return self.w, self.h



    def __floordiv__(self, val):  # semi
        cls = type(self)
        x0, y1 = self.top_left
        x1, y0 = self.bottom_right
        for i in range(0, val):
            tl = vec(x0 + (x1 - x0) * i / val, y1)
            br = vec(x0 + (x1 - x0) * (i + 1) / val, y0)
            yield cls(tl=tl, br=br, w=self.w // val, h=self.h, g=self, fn=self.fn)

    def __truediv__(self, val):  # semi
        cls = type(self)
        x0, y0 = self.top_left
        x1, y1 = self.bottom_right
        for i in range(0, val):
            tl = vec(x0, y0 + (y1 - y0) * i / val)
            br = vec(x1, y0 + (y1 - y0) * (i + 1) / val)
            yield cls(tl=tl, br=br, w=self.w, h=self.h // val, g=self, fn=self.fn)

