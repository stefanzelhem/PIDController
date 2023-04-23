from arcade import clamp
from params import GameParameters
from reloadable import Reloadable

# class DriverParameters:
#          def __init__(self, pars : GameParameters):
#             self.parameters=pars
#             # self.Kp=pars.p_factor
#             # self.Kd=pars.d_factor
#             # self.Ki=pars.i_factor
#             # self.Integraal_Factor=pars.i_weight
#             # self.Sigma=pars.sigma


class Driver(Reloadable):
    def __init__(self, state=None, ship=None):

        self.ship = ship
        self.reset = True

        self.last_x = 0
        self.i = 0        
        
        super().__init__(state)

    def tick(self, ct, parameters : GameParameters):
        Kp=parameters.p_factor
        Kd=parameters.d_factor
        Ki=parameters.i_factor
        Integraal_Factor=parameters.i_weight

        derivative = self.ship.x - self.last_x
        self.last_x = self.ship.x
        self.i = self.i + Integraal_Factor * self.ship.x
        return -5*(Kp*self.ship.x+Kd * derivative+Ki * self.i)

        # if inputs:
        #     inputs["enabled"] = True

        # if self.reset:
        #     inputs["reset"] = True
        #     self.reset = False




class ExampleDriver(Reloadable):

    serialize_vars = ()

    def __init__(self, state=None, ship=None):

        self.ship = ship
        self.reset = True

        self.last_x = self.ship.x
        self.i = 0

        super().__init__(state)
        print(self.ship)

    def tick(self, ct):
        inputs = self.get_inputs(ct)

        if inputs:
            inputs["enabled"] = True

        if self.reset:
            inputs["reset"] = True
            self.reset = False

        return inputs

    def get_inputs(self, ct):

        p = -1 * self.ship.x
        d = 125 * (self.last_x - self.ship.x)
        self.i = self.i + 0.2 * self.ship.x  # clamp(, -2000, 2000)

        self.last_x = self.ship.x

        return {
            "factor": 1,
            "p": p,
            "d": d,
            "i": -0.01 * self.i,
        }
