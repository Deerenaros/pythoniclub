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
from pygame.locals import *

from gl import *
from graphicsmath import vec
from graphicsmath import square as gsquare


class square(gsquare):
    def rebinded(self, g, fn):  # inhertance
        self.g = g
        self.fn = fn
        return self

    def offblit(self, surf, g, off=(0, 0), color=np.vectorize(lambda x: x)):  # inhertance
        oh = g.h - int(round((self.topleft.y - g.topleft.y) * g.h / (g.bottomright.y - g.topleft.y))) - self.h
        ow = int(round((self.topleft.x - g.topleft.x) * g.w / (g.bottomright.x - g.topleft.x)))
        surf.blit(self.unlazy().msurf, (ow + off[0], oh + off[1]))

    def unlazy(self):  # inhertance
        if self.surface is None:
            self.surface = np.array([[[k, k, k] for k in col] for col in self.fn(self)], dtype=np.uint8)
            msurf = self.msurf = pygame.surfarray.make_surface(self.surface)
        return self


def translate(fn):
    from functools import wraps
    @wraps(fn)
    def wrapped(x, y, g=None):
        x = x / g.w
        x = x*(g.bottomright.x - g.topleft.x)
        x = x + g.topleft.x

        y = y/g.h
        y = y*(g.topleft.y - g.bottomright.y)
        y = y + g.bottomright.y
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


class view(object):
    def __call__(self, fn):
        self.fn = fn
        self.running = False
        return self

    def __init__(self, width=640, height=400, fps=30, color=np.vectorize(lambda x: x), fs=False):  #fs?
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

        # using opengl
        #if self.fs:
        #    pygame.display.set_mode((0, 0), OPENGL | DOUBLEBUF | HWSURFACE | FULLSCREEN)
        #else:
        #    pygame.display.set_mode((self.width, self.height), OPENGL | DOUBLEBUF | HWSURFACE)
        self.scrn = pygame.display.set_mode((self.width, self.height), DOUBLEBUF) # comment if using opengl

        self.queue = iter([])
        self.blitted = []

        self.clock = pygame.time.Clock()
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)


    def repopulate(self):
        def populator():
            for row in self.g / 16:
                for sq in row // 16:
                    yield sq
        # self.queue = chain(populator(), self.queue)
        self.queue = populator()

    def zoom(self, f="in"):
        x0, y1 = self.g.top_left
        x1, y0 = self.g.bottom_right
        if "in" == f:
            shiftx, shifty = (x1 - x0)/10, (y1 - y0)/10
        elif "out" == f:
            shiftx, shifty = (x0 - x1)/10, (y0 - y1)/10
        self.g.top_left  = vec(x0 + shiftx, y1 - shifty)
        self.g.bottom_right = vec(x1 - shifty, y0 + shifty)
        self.repopulate()

    def rescope(self):
        width = self.g.bottom_right.x - self.g.top_left.x
        offset = self.c / self.g.size() * width
        self.g.bottom_right -= offset
        self.g.top_left  -= offset
        self.c[:] = 0

    def update(self): # have to be simplified
        # controls
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

        # misc
        milliseconds = self.clock.tick(self.fps)
        self.playtime += milliseconds / 1000.0

        # drawing
        self.image.fill(pygame.Color(0, 0, 0))
        try:
            while True:
                chunk = next(self.queue)
                if not all(any(p in blit for blit in self.blitted) for p in chunk.points):
                    self.blitted.append(chunk.unlazy())
                    break
        except StopIteration as e:
            pass

        for blit in self.blitted:
            blit.offblit(self.image, self.g, self.c, self.color)

        # misc
        FPS = f"FPS: {self.clock.get_fps():6.3}"
        PTIME = f"PLAYTIME: {self.playtime:6.3} SECONDS"
        TLPOINT = f"{self.g.top_left}"
        self.text_topleft(" | ".join((FPS, PTIME, TLPOINT)))
        self.text_botright(f"{self.c} | {self.g.bottom_right}")

        # drawing
        self.scrn.blit(self.image, (0, 0)) # comment if using opengl
        # renderSplash(self.image, cmap=self.color.flush(), time=self.playtime)
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
        pass # using opengl i missed HUD, would be nice to return it back
        # fw, fh = self.font.size(text)
        #surface = self.font.render(text, True, (0, 255, 0))
        # self.screen.blit(surface, (self.width - 15 - fw, self.height - 15 - fh))


if __name__ == '__main__':
    view(640, 400, 60).run()
