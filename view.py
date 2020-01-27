"""
view.py

A little framework to painter-function visualization
Based on http://thepythongamebook.com/en:part2:pygame:step002

Tested on Python 3.7+

Author:  yipyip, deerenaros
License: Do What The Fuck You Want To Public License (WTFPL)
         See http://sam.zoy.org/wtfpl/
"""

import pygame
import numpy as np
import functools
import multiprocessing as mp

from pygame.locals import *

from gl import *

def translate(fn):
    from functools import wraps
    @wraps(fn)
    def wrapped(x, y, g=None):
        x = x/g.w
        x = x*(g.bot_right.x - g.top_left.x)
        x = x + g.top_left.x

        y = y/g.h
        y = y*(g.top_left.y - g.bot_right.y)
        y = y + g.bot_right.y
        return fn(x, y)
    return wrapped

def toggle_fullscreen():
    screen = pygame.display.get_surface()
    caption = pygame.display.get_caption()
    cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007 
    
    w,h = screen.get_width(),screen.get_height()
    bits = screen.get_bitsize()
    
    pygame.display.quit()
    pygame.display.init()
    
    pygame.display.set_mode((w, h), OPENGL | DOUBLEBUF | HWSURFACE | FULLSCREEN)
    pygame.display.set_caption(*caption)

    pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??

    pygame.mouse.set_cursor( *cursor )  # Duoas 16-04-2007
    
    return screen

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


class stripy:
    def __init__(self, sq=None):
        if sq is not None:
            self.points = [sq.tl, sq.br]
        else:
            self.points = []

    def __in__(self, sq):
        return all(sq.tl.x < pt.x < sq.br.x
                and sq.tl.y > pt.y > sq.br.y
                for pt in self.points)

    def __sub__(self, sq):
        if sq is None or self.points is None:
            return self
        res = stripy()
        res.points[:] = self.points


class square:
    def __init__(self, tl=vec(-1, 1), br=vec(1, -1), w=1, h=1, g=None, fn=None):
        self.top_left = tl
        self.bot_right = br
        self.w, self.h = w, h
        self.surf = None
        self.g = g
        self.fn = fn

    @property
    def tl(self):
        return self.top_left
    
    @property
    def br(self):
        return self.bot_right

    def __str__(self):
        import itertools
        chain, at = itertools.chain(self.top_left, self.bot_right), ""
        if self.g:
            g = self.g
            oh = int(round((self.tl.y - g.tl.y)*g.h / (g.br.y - g.tl.y)))
            ow = int(round((self.tl.x - g.tl.x)*g.w / (g.br.x - g.tl.x)))
            at = "@ %s %s" % (ow, oh)
        return "|%s|" % " ".join(f"{float(v):.2}" for v in chain) + at

    def size(self):
        return self.w, self.h

    def rebinded(self, g, fn):
        self.g = g
        self.fn = fn
        return self

    def offblit(self, surf, g, off=(0,0), color=np.vectorize(lambda x: x)):
        oh = g.h - int(round((self.tl.y - g.tl.y)*g.h / (g.br.y - g.tl.y))) - self.h
        ow = int(round((self.tl.x - g.tl.x)*g.w / (g.br.x - g.tl.x)))
        surf.blit(self.unlazy().msurf, (ow + off[0], oh + off[1]))

    def unlazy(self):
        if self.surf is None:
            self.surf = np.array([[[k,k,k] for k in col] for col in self.fn(self)], dtype=np.uint8)
            msurf = self.msurf = pygame.surfarray.make_surface(self.surf)
        return self

    def __floordiv__(self, val):
        cls = type(self)
        x0, y1 = self.top_left
        x1, y0 = self.bot_right
        for i in range(0, val):
            tl = vec(x0 + (x1-x0)*i/val, y1)
            br = vec(x0 + (x1-x0)*(i+1)/val, y0)
            yield cls(tl=tl, br=br, w=self.w//val, h=self.h, g=self, fn=self.fn)

    def __truediv__(self, val):
        cls = type(self)
        x0, y0 = self.top_left
        x1, y1 = self.bot_right
        for i in range(0, val):
            tl = vec(x0, y0 + (y1-y0)*i/val)
            br = vec(x1, y0 + (y1-y0)*(i+1)/val)
            yield cls(tl=tl, br=br, w=self.w, h=self.h//val, g=self, fn=self.fn)


class view(object):
    def __call__(self, fn):
        self.fn = fn
        self.running = False
        return self

    def __init__(self, width=640, height=400, fps=30, color=np.vectorize(lambda x: x), fs=False):
        def filler(sq):
            return np.fromfunction(self.fn, sq.size(), g=sq)
        self.g = square(fn=filler)
        if fs:
            self.width = self.g.w = 1920
            self.height = self.g.h = 1080
        else:
            self.width = self.g.w = width
            self.height = self.g.h = height
        self.fps = fps
        self.fs = fs
        self.color = color

    def start(self):
        self.c = vec(0, 0)
        self.offdrag = vec(0, 0)
        self.drag = False

        pygame.init()
        pygame.display.set_caption("Press ESC to quit")

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(pygame.Color(0, 0, 0, 255))
        
        if self.fs:
            pygame.display.set_mode((0, 0), OPENGL | DOUBLEBUF | HWSURFACE | FULLSCREEN)
        else:
            pygame.display.set_mode((self.width, self.height), OPENGL | DOUBLEBUF | HWSURFACE)


        self.queue = iter([])
        self.blitted = []

        self.clock = pygame.time.Clock()
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)

    def repopulate(self):
        from itertools import chain
        def populator():
            for row in self.g / 16:
                for sq in row // 16:
                    yield sq
        # self.queue = chain(populator(), self.queue)
        self.queue = populator()

    def zoom(self, f="in"):
        x0, y1 = self.g.top_left
        x1, y0 = self.g.bot_right
        if "in" == f:
            shiftx, shifty = (x1 - x0)/10, (y1 - y0)/10
        elif "out" == f:
            shiftx, shifty = (x0 - x1)/10, (y0 - y1)/10
        self.g.top_left  = vec(x0 + shiftx, y1 - shifty)
        self.g.bot_right = vec(x1 - shifty, y0 + shifty)
        self.repopulate()

    def rescope(self):
        width = self.g.bot_right.x - self.g.top_left.x
        offset = self.c / self.g.size() * width
        self.g.bot_right -= offset
        self.g.top_left  -= offset
        self.c[:] = 0

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.zoom("in")
                elif event.key == pygame.K_DOWN:
                    self.zoom("out")
                elif event.key == pygame.K_RETURN:
                    toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drag = True
                self.offdrag[:] = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                self.drag = False
                self.rescope()
                self.repopulate()
            elif event.type == pygame.MOUSEMOTION:
                if self.drag:
                    self.c += (-self.offdrag + event.pos)
                    self.offdrag[:] = event.pos

        milliseconds = self.clock.tick(self.fps)
        self.playtime += milliseconds / 1000.0
        
        self.image.fill(pygame.Color(0, 0, 0))
        try:
            chunk = next(self.queue)
            self.blitted.append(chunk.unlazy())
        except StopIteration as e:
            pass

        for blit in self.blitted:
            blit.offblit(self.image, self.g, self.c, self.color)

        FPS = f"FPS: {self.clock.get_fps():6.3}"
        PTIME = f"PLAYTIME: {self.playtime:6.3} SECONDS"
        TLPOINT = f"{self.g.top_left}"
        self.text_topleft(" | ".join((FPS, PTIME, TLPOINT)))
        self.text_botright(f"{self.c} | {self.g.bot_right}")

        # self.scrn.blit(self.image, (0, 0))
        renderSplash(self.image, cmap=self.color.flush(), time=self.playtime)
        pygame.display.flip()

    def run(self):
        self.start()
        self.repopulate()
        self.running = True
        while self.running:
            try:
                self.update()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(str(e))

        pygame.quit()

    def text_topleft(self, text):
        pygame.display.set_caption(text)
        # fw, fh = self.font.size(text)
        # surface = self.font.render(text, True, (0, 255, 0))
        # self.screen.blit(surface, (15, 15))
    
    def text_botright(self, text):
        pass
        # fw, fh = self.font.size(text)
        #surface = self.font.render(text, True, (0, 255, 0))
        # self.screen.blit(surface, (self.width - 15 - fw, self.height - 15 - fh))

if __name__ == '__main__':
    view(640, 400, 60).run()
