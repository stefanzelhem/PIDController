"""
Class for managing/drawing the ship.
"""
import random
from math import copysign, sin, sqrt

import arcade
from arcade import clamp
from params import GameParameters
from reloadable import Reloadable

X_OFFSET = 0
Y_OFFSET = 1080

WIDTH = 1800
HEIGHT = 200

MIN_Y = 0 + Y_OFFSET
CENTER_Y = HEIGHT / 2 + Y_OFFSET
MAX_Y = HEIGHT + Y_OFFSET

SHIP_X_OFFSET = 100
SHIP_MIN_X = SHIP_X_OFFSET + X_OFFSET
SHIP_MAX_X = (WIDTH - SHIP_X_OFFSET) + X_OFFSET
SHIP_X_WIDTH = WIDTH / 2 - SHIP_X_OFFSET
SHIP_X_CENTER = WIDTH / 2 + X_OFFSET
SHIP_GRAPHICS_X_OFFSET = 35

INDICATOR_Y = MIN_Y

LINE_COLOR = (0, 255, 0)

MAX_SPEED = 0.1
SPEED_INC = 0.0001
MAX_THRUST = 1


class StarLayer:
    def __init__(self, speed, no_of_stars, min_intensity=0, intensity_var=100, color_var=30):

        self.speed = speed
        self.no_of_stars = no_of_stars
        self.t = 0

        self.min_intensity = min_intensity
        self.intensity_var = intensity_var
        self.color_var = color_var

        self.stars0 = self.make_stars()
        self.stars1 = self.make_stars()
        self.stars1.move(WIDTH, 0)

    def make_stars(self):
        stars = arcade.ShapeElementList()
        for i in range(self.no_of_stars):
            center_x = X_OFFSET + random.randrange(WIDTH)
            center_y = Y_OFFSET + random.randrange(HEIGHT)
            intensity = self.min_intensity + random.randrange(self.intensity_var)
            color = (
                intensity + random.randrange(self.color_var),
                intensity + random.randrange(self.color_var),
                intensity + random.randrange(self.color_var),
            )
            stars.append(arcade.create_rectangle(center_x, center_y, 4, 4, color))
        return stars

    def draw(self):

        self.t += self.speed
        if self.t > WIDTH:
            self.t -= WIDTH
            self.stars0 = self.stars1
            self.stars1 = self.make_stars()
            self.stars1.move(WIDTH, 0)

        self.stars0.move(-self.speed, 0)
        self.stars1.move(-self.speed, 0)

        self.stars0.draw()
        self.stars1.draw()


class Ship(Reloadable):

    serialize_vars = (
        "current_i",
        "current_j",
        "direction",
        "thrust",
        "x",
        "speed",
        "control",
        "star_wind",
        "star_wind_control",
    )

    def __init__(self, state=None):
        super().__init__(state)
        if not state:
            self.current_i = 0
            self.current_j = 0

            self.direction = True  # True -> right, False -> left
            self.thrust = 0
            self.control = 0
            self.x = -1
            self.speed = 0
            self.star_wind = 1
            self.star_wind_control = 0
            
            "Added for assignment"
            self.xAll = [-1]
            self.vAll = [0]
            self.t = 0
            self.tAll = [0]
            self.EQ = 0
            self.tEQ = []

        self.increase_ct = 0

        self.ships = []
        ls = [
            arcade.load_texture("sprites/rocket-00.png"),
            arcade.load_texture("sprites/rocket-00.png"),
            arcade.load_texture("sprites/rocket-00.png"),
        ]
        self.ships.append(ls)

        for i in range(10):
            ls = []
            # for j in range(2):
            #     filename = f"sprites/ship-{i+1:02}-{j}.png"
            #     ls.append(arcade.load_texture(filename))
            for j in range(3):
                filename = f"sprites/rocket-{i + 1:02}-{j}.png"
                ls.append(arcade.load_texture(filename))
            self.ships.append(ls)

        # lines
        self.lines = arcade.ShapeElementList()
        top_line = arcade.create_line(0 + X_OFFSET, MAX_Y, WIDTH + X_OFFSET, MAX_Y, LINE_COLOR, 2)
        center_y_line = arcade.create_line(0 + X_OFFSET, CENTER_Y, WIDTH + X_OFFSET, CENTER_Y, LINE_COLOR, 1)
        center = arcade.create_line(WIDTH / 2 + X_OFFSET, MIN_Y, WIDTH / 2 + X_OFFSET, MAX_Y, LINE_COLOR, 1)
        bottom_line = arcade.create_line(0 + X_OFFSET, MIN_Y, WIDTH + X_OFFSET, MIN_Y, LINE_COLOR, 2)
        self.lines.append(top_line)
        # self.lines.append(center_y_line)
        self.lines.append(center)
        self.lines.append(bottom_line)

        self.stars = [
            StarLayer(0, 30, min_intensity=20, intensity_var=20, color_var=10),
            StarLayer(0, 20, min_intensity=25, intensity_var=30, color_var=20),
            StarLayer(0, 10, min_intensity=50, intensity_var=40, color_var=30),
            StarLayer(0, 10, min_intensity=100, intensity_var=50, color_var=30),
        ]

        self.stars[0].speed = 0.5 * self.star_wind_control
        self.stars[1].speed = 1.0 * self.star_wind_control
        self.stars[2].speed = 1.5 * self.star_wind_control
        self.stars[3].speed = 2.0 * self.star_wind_control

    def reset(self):
        self.direction = True
        self.thrust = 0
        self.x = -1
        self.speed = 0
        self.control = 0
        
        "Added for assignment"
        self.xAll = [-1]
        self.vAll = [0]
        self.t = 0
        self.tAll = [0]
        self.EQ = 0
        self.tEQ = []

    def draw(self):
        def ship_x(x):
            """Compute screen-x from logical x, where x \\in [-1, 1]."""

            return SHIP_X_CENTER + x * SHIP_X_WIDTH

        # TODO: better Systems Hungarian

        self.lines.draw()
        for stars in self.stars:
            stars.draw()

        pos_x = ship_x(self.x)
        if self.direction:
            draw_x = pos_x - SHIP_GRAPHICS_X_OFFSET
        else:
            draw_x = pos_x + SHIP_GRAPHICS_X_OFFSET
        pos_y = CENTER_Y

        arcade.draw_line(pos_x, CENTER_Y, SHIP_X_CENTER, INDICATOR_Y, LINE_COLOR, 2)
        arcade.draw_scaled_texture_rectangle(
            draw_x, pos_y, self.ships[self.current_i][self.current_j], 3, -90 if self.direction else 90
        )

    def update(self):
        pass

    def tick(self, ct,parameters : GameParameters):
        self.current_j = (self.current_j + 1) % 3

        DECREASE_TIMER = 3

        self.increase_ct += 1

        self.control = clamp(self.control, -MAX_THRUST, MAX_THRUST)
        thrust = clamp(self.thrust + self.control, -MAX_THRUST, MAX_THRUST)
        if thrust != 0:
            self.direction = thrust > 0
            self.speed = self.speed + SPEED_INC * thrust
            self.current_i = int(10 * abs(thrust) ** 0.25)
        else:
            if self.increase_ct > DECREASE_TIMER:
                self.increase_ct = 0
                self.current_i = max(0, self.current_i - 1)

        self.speed -= 0.00001 * self.star_wind_control
        self.x += self.speed

        if(parameters.sigma!=0): # ik vind het nog steeds raar dat we rechtstreeks de positie aanpassen. Voelt een beetje als een hyperspace jump
            offset=random.gauss(0,parameters.sigma)
            self.x +=offset


        if self.star_wind_control != self.star_wind:
            if self.star_wind_control > self.star_wind:
                self.star_wind_control -= 0.01
            else:
                self.star_wind_control += 0.01

            if abs(self.star_wind_control - self.star_wind) < 0.11:
                self.star_wind_control = self.star_wind

            self.stars[0].speed = 0.5 * self.star_wind_control
            self.stars[1].speed = 1.0 * self.star_wind_control
            self.stars[2].speed = 1.5 * self.star_wind_control
            self.stars[3].speed = 2.0 * self.star_wind_control
