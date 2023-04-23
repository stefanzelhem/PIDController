from math import sin, sqrt, copysign
from random import random

import arcade

from reloadable import Reloadable


class Drawable:

    X = 0
    Y = 0
    WIDTH = 1800

    def __init__(self, X, Y):
        self.drawables = []
        self.X = X
        self.Y = Y

    def create_line(self, start_x, start_y, end_x, end_y, color, thickness):
        self.drawables.append(
            arcade.create_line(
                start_x + self.X, start_y + self.Y,
                end_x + self.X, end_y + self.Y,
                color, thickness
            )
        )

    def draw_line(self, start_x, start_y, end_x, end_y, color, thickness):
        arcade.draw_line(
            start_x + self.X, start_y + self.Y,
            end_x + self.X, end_y + self.Y,
            color, thickness
        )

    def draw(self):
        for d in self.drawables:
            d.draw()


class Diagram(Drawable):

    HEIGHT = 180
    LINE_COLOR = (0, 255, 255)
    PADDING = 15
    LEFT_WIDTH = 180
    TEXT_SIZE = 80

    def __init__(self, X, Y, label, line_color=None, value=0):
        super().__init__(X, Y)

        if line_color is not None:
            self.LINE_COLOR = line_color

        self.min_val = -1
        self.max_val = 1
        self.point_count = 100

        self.points = [
            self.f(value) for x in range(self.point_count)
        ]
        self.carriers = [
            self.carrier(i) for i in range(self.point_count)
        ]

        self.label = label

        self.create_line(0, 0, self.WIDTH, 0, self.LINE_COLOR, 1)
        self.create_line(0, self.HEIGHT, self.WIDTH, self.HEIGHT, self.LINE_COLOR, 1)
        self.create_line(0, 0, 0, self.HEIGHT, self.LINE_COLOR, 1)
        self.create_line(self.WIDTH, 0, self.WIDTH, self.HEIGHT, self.LINE_COLOR, 1)
        self.create_line(self.LEFT_WIDTH, 0, self.LEFT_WIDTH, self.HEIGHT, self.LINE_COLOR, 1)

        self.create_line(
            self.carrier(0) - self.X, self.f(0) - self.Y, self.carrier(100) - self.X, self.f(0) - self.Y, (50, 50, 50), 1
        )

    def f(self, v):
        h = self.HEIGHT - 2 * self.PADDING
        return self.PADDING + h / (self.max_val - self.min_val) * (v - self.min_val) + self.Y

    # off by one, but meh!
    def carrier(self, i):
        w = self.WIDTH - self.LEFT_WIDTH - 2 * self.PADDING
        return self.LEFT_WIDTH + self.PADDING + w / self.point_count * i + self.X

    def add_point(self, value):
        """Add another data point."""

        self.points.pop(0)
        self.points.append(
            self.f(value)
        )

    def draw(self):
        super().draw()

        arcade.draw_text(
            self.label,
            self.LEFT_WIDTH / 2 + self.X, self.HEIGHT / 2 + self.Y,
            self.LINE_COLOR, self.TEXT_SIZE,
            width=self.LEFT_WIDTH, align="center",
            anchor_x="center", anchor_y="center")

        points = list(zip(self.carriers, self.points))
        arcade.draw_line_strip(points, self.LINE_COLOR, 1)


def ssqrt(v):
    return copysign(sqrt(abs(v)), v)


class Stats(Reloadable):
    """Draw statistics on the screen and show interesting stuff."""

    serialize_vars = ()

    X = 0
    Y = 0

    def __init__(self, state=None, ship=None):

        self.X = Diagram(0, 900, "X", value=-1)
        self.T = Diagram(0, 720, "T/   ")
        self.V = Diagram(0, 720, "    V", (255, 0, 255))
        self.p_enabled = False
        self.P = Diagram(0, 540, "P", (0, 255, 0))
        self.d_enabled = False
        self.D = Diagram(0, 360, "D", (0, 255, 0))
        self.i_enabled = False
        self.I = Diagram(0, 180, "I", (0, 255, 0))

        self.ship = ship

        super().__init__(state)

    def draw(self):

        self.V.draw()
        self.T.draw()
        self.X.draw()
        if self.p_enabled:
            self.P.draw()
        if self.d_enabled:
            self.D.draw()
        if self.i_enabled:
            self.I.draw()

    def tick(self, ct, p, d, i):
        pass
        # if ct % 2 == 0:
        #     self.X.add_point(self.ship.x)
        #     self.T.add_point(self.ship.thrust + self.ship.control)
        #     self.V.add_point(
        #         copysign(sqrt(abs(self.ship.speed)), self.ship.speed) * 10
        #     )
        #     if p is not None:
        #         self.p_enabled = True
        #         self.P.add_point(p)
        #     if d is not None:
        #         self.d_enabled = True
        #         self.D.add_point(ssqrt(ssqrt(d)))
        #     if i is not None:
        #         self.i_enabled = True
        #         self.I.add_point(ssqrt(ssqrt(i)))




