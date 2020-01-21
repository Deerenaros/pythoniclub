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
    def __init__(self, tl=vec(-1, 1), br=vec(1, -1), w=1, h=1):
        self.top_left = tl
        self.bot_right = br
        self.w, self.h = w, h
        self.surf = None
        self.g = None

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

    def binded(self, fn, g=None):
        self.fn = fn
        self.g = g
        return self

    def offblit(self, surf, g, off=(0,0), color=np.vectorize(lambda x: x)):
        c = color(self.unlazy().surf)
        msurf = pygame.surfarray.make_surface(c)
        oh = g.h - int(round((self.tl.y - g.tl.y)*g.h / (g.br.y - g.tl.y))) - self.h
        ow = int(round((self.tl.x - g.tl.x)*g.w / (g.br.x - g.tl.x)))
        surf.blit(msurf, (ow + off[0], oh + off[1]))

    def unlazy(self):
        if self.surf is None:
            self.surf = self.fn()
        return self

    def __floordiv__(self, val):
        x0, y1 = self.top_left
        x1, y0 = self.bot_right
        for i in range(0, val):
            tl = vec(x0 + (x1-x0)*i/val, y1)
            br = vec(x0 + (x1-x0)*(i+1)/val, y0)
            yield square(tl=tl, br=br, w=self.w//val, h=self.h)

    def __truediv__(self, val):
        x0, y0 = self.top_left
        x1, y1 = self.bot_right
        for i in range(0, val):
            tl = vec(x0, y0 + (y1-y0)*i/val)
            br = vec(x1, y0 + (y1-y0)*(i+1)/val)
            yield square(tl=tl, br=br, w=self.w, h=self.h//val)


class view(object):
    def __init__(self, fn, color=lambda x: x):
        self.fn = fn
        self.running = False

    def prepare(self, width=640, height=400, fps=30, color=np.vectorize(lambda x: x)):
        self.color = color

        self.g = square()
        self.width = self.g.w = width
        self.height = self.g.h = height

        self.c = vec(0, 0)
        self.offdrag = vec(0, 0)
        self.drag = False

        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.image = pygame.Surface((self.width, self.height))
        self.bg = pygame.Surface((self.width, self.height))
        self.bg.fill(pygame.Color(0, 0, 0, 0))
        
        self.queue = iter([])
        self.blitted = []
        
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)

        self.repopulate()

        return self

    def repopulate(self, reversd=False):
        from itertools import chain
        def populator():
            for row in self.g / 16:
                for sq in row // 16:
                    def filler():
                        return np.fromfunction(functools.partial(self.fn), sq.size(), g=sq)
                    yield sq.binded(filler, self.g)
        # self.queue = chain(populator(), self.queue)
        self.queue = populator()

    def zoom(self, f="in"):
        if "in" == f:
            self.g.top_left  *= 0.8
            self.g.bot_right *= 0.8
        elif "out" == f:
            self.g.top_left  *= 1.2
            self.g.bot_right *= 1.2
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
        
        self.screen.fill(pygame.Color(0, 0, 0))
        try:
            chunk = next(self.queue)
            self.blitted.append(chunk.unlazy())
        except StopIteration as e:
            pass

        for blit in self.blitted:
            blit.offblit(self.screen, self.g, self.c, self.color)

        FPS = f"FPS: {self.clock.get_fps():6.3}"
        PTIME = f"PLAYTIME: {self.playtime:6.3} SECONDS"
        TLPOINT = f"{self.g.top_left}"
        self.text_topleft(" | ".join((FPS, PTIME, TLPOINT)))
        self.text_botright(f"{self.c} | {self.g.bot_right}")

        pygame.display.flip()
        self.color.animate()

    def run(self):
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
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 255, 0))
        self.screen.blit(surface, (15, 15))
    
    def text_botright(self, text):
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 255, 0))
        self.screen.blit(surface, (self.width - 15 - fw, self.height - 15 - fh))

if __name__ == '__main__':
    view(640, 400, 60).run()


