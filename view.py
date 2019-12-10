"""
002_display_fps_pretty.py

Display framerate and playtime.
Works with Python 2.7 and 3.3+.

URL:     http://thepythongamebook.com/en:part2:pygame:step002
Author:  yipyip
License: Do What The Fuck You Want To Public License (WTFPL)
         See http://sam.zoy.org/wtfpl/
"""
import pygame


class coords(tuple):
    def __init__(self, *args):
        tuple.__init__(self, args)

    def __str__(self):
        return "(" + ",".join(f"{v:.2}" for v in self) + ")"

class view(object):
    def __init__(self, width=640, height=400, fps=30):
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)

        self.c = coords(0, 0)
        self.s = (coords(-1, 1), coords(-1, 1))

    def zoom(self, f="in"):
        x, y = self.s
        xx = (x[1] - x[0])*0.2
        yy = (y[1] - y[0])*0.2
        if "in" == f:
            self.s = (coords(x[0] + xx/2, x[1] - xx/2),
                      coords(y[0] + yy/2, y[1] - yy/2))
        elif "out" == f:
            self.s = (coords(x[0] - xx/2, x[1] + xx/2),
                      coords(y[0] - yy/2, y[1] + yy/2))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.zoom("in")
                    elif event.key == pygame.K_DOWN:
                        self.zoom("out")

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            self.text_topleft(f"FPS: {self.clock.get_fps():6.3}  PLAYTIME: {self.playtime:6.3} SECONDS")

            self.text_botright(f"c: {self.c} x: {self.s[0]} y: {self.s[1]}")

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

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


