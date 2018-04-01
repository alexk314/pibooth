# -*- coding: utf-8 -*-

from pibooth import pictures
from pibooth.utils import PoolingTimer

try:
    xrange
except NameError:
    # Python 3.x fallback
    xrange = range
try:
    from itertools import zip_longest
except ImportError:
    # Python 2.x fallback
    from itertools import izip_longest as zip_longest


def shake(magnitude, step=5):
    """
    This function creates our shake-generator it "moves" the surface to the left and
    right three times by yielding (-5, 0), (-10, 0), ... (-20, 0), (-15, 0) ... (20, 0),
    then keeps yieling (0, 0)
    """
    s = -1
    for _ in xrange(0, 3):
        for x in range(0, magnitude, step):
            yield (x * s, 0)
        for x in range(magnitude, 0, step):
            yield (x * s, 0)
        s *= -1
    while True:
        yield (0, 0)


def transpose(origin, target, step=5):
    """
    This function creates our transpose-generator it "moves" the surface along
    a ligne until the target is reached, then keeps yieling 'target'.
    """
    xend = abs(target[0] - origin[0])
    if origin[0] > target[0]:
        xs = -1
    else:
        xs = 1
    yend = abs(target[1] - origin[1])
    if origin[1] > target[1]:
        ys = -1
    else:
        ys = 1

    for pos in zip_longest(iter(xrange(0, xend, step)), iter(xrange(0, yend, step))):
        yield (xs * pos[0] if pos[0] is not None else xs * xend, ys * pos[1] if pos[1] is not None else ys * yend)

    while True:
        yield (xs * xend, ys * yend)


class Background(object):

    def __init__(self, image_name):
        self.rect = None
        self.name = image_name
        self.background = None

    def __str__(self):
        """Return background final name.
        """
        return self.name

    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        if self.rect != screen.get_rect():
            self.rect = screen.get_rect()
            self.background = pictures.get_image(self.name, (self.rect.width, self.rect.height))
            return True
        return False

    def animate(self, screen):
        """Animate the surfaces on the screen.
        """
        screen.fill((0, 0, 0))  # Clear background
        screen.blit(self.background, self.background.get_rect(center=self.rect.center))


class IntroBackground(Background):

    def __init__(self):
        Background.__init__(self, "intro.png")


class IntroWithPrintBackground(Background):

    def __init__(self):
        Background.__init__(self, "intro_with_print.png")


class ChooseBackground(Background):

    def __init__(self, choices):
        Background.__init__(self, "choose.png")
        self.choices = choices
        self.layout0 = None
        self.layout0_pos = None
        self.layout1 = None
        self.layout1_pos = None
        self.offset = None
        self.shake_timer = PoolingTimer(10)

    def resize(self, screen):
        if Background.resize(self, screen):
            size = (self.background.get_rect().width * 0.6, self.background.get_rect().height * 0.6)
            self.layout0 = pictures.get_image("layout{}.png".format(self.choices[0]), size)
            self.layout1 = pictures.get_image("layout{}.png".format(self.choices[1]), size)

            hinter = (self.rect.width - self.layout0.get_rect().width - self.layout1.get_rect().width) // 3
            vinter = int(self.background.get_rect(center=self.rect.center).top +
                         self.layout0.get_rect(center=self.background.get_rect().center).top * 1.3)

            self.layout0_pos = (hinter, vinter)
            self.layout1_pos = (hinter * 2 + self.layout0.get_rect().width, vinter)

    def animate(self, screen):
        if not self.offset or self.shake_timer.is_timeout():
            self.offset = shake(15)
            self.shake_timer.start()

        screen.fill((0, 0, 0))
        screen.blit(self.background, self.background.get_rect(center=self.rect.center))
        pos = next(self.offset)
        screen.blit(self.layout0, (self.layout0_pos[0] + pos[0], self.layout0_pos[1] + pos[1]))
        screen.blit(self.layout1, (self.layout1_pos[0] - pos[0], self.layout1_pos[1] - pos[1]))


class ChosenBackground(Background):

    def __init__(self, choices, selected):
        Background.__init__(self, "chosen.png")
        self.choices = choices
        self.selected = selected
        self.layout = None
        self.layout_pos = None
        self.offset = None
        self.transpose_timer = PoolingTimer(10)

    def __str__(self):
        return "chosen{}.png".format(self.selected)

    def resize(self, screen):
        if Background.resize(self, screen):
            size = (self.background.get_rect().width * 0.6, self.background.get_rect().height * 0.6)

            self.layout = pictures.get_image("layout{}.png".format(self.selected), size)

            hinter = (self.rect.width - self.layout.get_rect().width - self.layout.get_rect().width) // 3
            vinter = int(self.background.get_rect(center=self.rect.center).top +
                         self.layout.get_rect(center=self.background.get_rect().center).top * 1.3)

            if self.selected == self.choices[0]:
                self.layout_pos = (hinter, vinter)
            else:
                self.layout_pos = (hinter * 2 + self.layout.get_rect().width, vinter)

    def animate(self, screen):
        end_pos = (self.layout.get_rect(center=self.rect.center).left, self.layout_pos[1])
        if not self.offset or self.transpose_timer.is_timeout():
            self.offset = transpose(self.layout_pos, end_pos, 50)
            self.transpose_timer.start()

        screen.fill((0, 0, 0))
        screen.blit(self.background, self.background.get_rect(center=self.rect.center))
        pos = next(self.offset)
        screen.blit(self.layout, (self.layout_pos[0] + pos[0], self.layout_pos[1] + pos[1]))


class CaptureBackground(Background):

    def __init__(self):
        Background.__init__(self, "capture.png")


class ProcessingBackground(Background):

    def __init__(self):
        Background.__init__(self, "processing.png")


class PrintBackground(Background):

    def __init__(self):
        Background.__init__(self, "print.png")


class FinishedBackground(Background):

    def __init__(self):
        Background.__init__(self, "finished.png")


class OopsBackground(Background):

    def __init__(self):
        Background.__init__(self, "opps.png")