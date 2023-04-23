# PID in a nutshell

This is a testbed for control-theory applications: try to steer the ship to the center
of the screen, then write a program that does that.

# The story

**You'll note that this isn't finished yet...**

(see below for some explanations on maths, dependencies and internals)

When you start the `game.py` (after installing everything), you will have a simple game that you can play with your
arrow keys: press left to accelerate the ship left, press right to accelerate the ship right. The goal is simple: park 
the ship at the center line of the screen. If that ship is a solar probe, you'd essentially be a
[solar probe parker](https://de.wikipedia.org/wiki/Parker_Solar_Probe).

*screenshot*

That's pretty easy, right? Just some power to the right, then braking it down, maybe some fine adjustment, done. There's
no friction in space, so you have to stop and fine-adjust yourself, but apart from that: EASY!

*screenshot*

Now let's write a program to do the same thing. Some terms&conditions first.

*screenshot*: coordinate system, variable names etc

Here, the ship starts at position `ship.x == -1`, the goal is at position `x == 0` and the graphic at the top of the 
creen spans the range from -1 to +1 (and a little more). There are three diagrams on the screen: one for `X`, which is
the ships position (try to get that to a zero-line!), one for `T`, which is the thrust applied to the ship and one for
`V`, which is the velocity of the ship. With your arrow keys, you can only apply maximum thrust in either direction, but
our robotic pilot will be guiding the ship much more finely.

Writing a program to control the ship turns out to be much harder than doing it manually, because teaching a computer to
predict where the ship
is going to be and how it's going to react to some inputs is not obvious. The basic problem here is that we do
not control the ship's position directly. In fact, we don't even control the speed of the ship directly, instead we
control the thrust that is applied, or the acceleration. This is also called the second derivative of the position, see
below for the terms if you're unfamiliar with that.

But, for the moment, let's assume we can control position directly, and use position
as a direct input. Open the file `driver.py` and scroll down to the function `get_inputs`, which should look like this:

    def get_inputs(self, ct):

        return {
        }

As you can see, no inputs are given and the ship stays in place when the game starts (press `R` to reset the game back
to the start).

As we said, let's try to just _use_ the position as an input. It sounds reasonable, right? The further away from the
goal we are, the harder we need to push. Since this input is _proportional_ to the error, let's call it `p`. So let's
try it and see what happens. By the way, you can simply edit that file and save it, the game will automatically reload
your code every time it changes (see the section below for more information). Anyway, here's the code:

    def get_inputs(self, ct):

        return {
            'p': self.ship.x,
        }

What happens is this:

*gif of ship flying off*

Uh, well, looks like we pushed in the wrong direction. Let's fix it by flipping the sign:

    def get_inputs(self, ct):

        return {
            'p': -1 * self.ship.x,
        }

*gif of ship oscillating*

Well, that starts off very promising! Then it overshoots. Then it comes back. Then it ends up _exactly_ where it
started. Ok, alright, so, _on average_ we've moved the ship to the center, but now we're just swinging around the goal.
The problem here is that we keep pushing until we actually reach the goal, and then (since there's no friction)
overshooting by the exact same amount that we started with.

We need to brake the ship earlier. But how do we know when to brake?

What about this: when our ship is moving in the "right direction", let's ease off the gas a little. How do we know when
we are moving in the right direction? Well, the derivative of the ship's position is exactly that (see below if you're
unsure). So let's use that. Calculating the derivative in a discrete system like this is easy (see below), so here's
what that code looks like.

    def get_inputs(self, ct):

        # do not forget to initialize self.last_x = 0 in the constructor!
        derivative = self.ship.x - self.last_x
        self.last_x = self.ship.x

        return {
            'p': -1 * self.ship.x,
            'd': -1 * derivative,
        }

*gif of very slow approximation*

Well, that didn't help very much. But if you look _very_ closely, you'll see that it did help. Let's crank up the
derivative much higher and see what happens:

    def get_inputs(self, ct):

        # do not forget to initialize self.last_x = 0 in the constructor!
        derivative = self.ship.x - self.last_x
        self.last_x = self.ship.x

        return {
            'p': -1 * self.ship.x,
            'd': -200 * derivative,
        }

Note: the `p` and `d` variables are simply added up to determine the applied thrust. You could add them yourself, but
then you wouldn't get a nice little diagram at the bottom and would find it harder to debug what happens.

*gif of slow approximation*

Wow, that's great! It did exactly what we wanted: Pushed to the right, then slowly braked into the center. Amazing, how
we found the perfect combination of factors right away!

It's a little slow, though. So let's increase the speed a little bit:

    def get_inputs(self, ct):

        derivative = self.ship.x - self.last_x
        self.last_x = self.ship.x

        return {
            'factor': -10,
            'p': self.ship.x,
            'd': 60 * derivative,
        }

The `factor` is simply multiplied to the resulting throttle, so we can more easily scale the variables (and take that
silly `-1` out of there). This is how it looks:

*gif of super-good approximation*

Now _that's_ crazy-good. It parks like a pro: lot's of power at the beginning, nice and smooth breaking at the end.


## Why does this work?

So what's happening here is a _linear forecast_. We built a system that looks into the future under the assumption that
everything is linear. The position can then be calculated as:

    x(t + d) = x(t) + d * x'(t)
    
The predicted position will probably be inaccurate, but that doesn't matter too much, as long as it's good enough.

We also have a factor `factor` in our system above. This factor encapsulates _how_ we should react to the linear
prediction. It tells us how strong we need to push the throttle for a given error. Our throttle maxes out at `T = 1`, so
that factor just makes the "interesting control interval" smaller. You can play with that factor and see how it changes
things. A small value will make the approximation more "cautious" and more accurate, while a larger factor will make it
quicker but less accurate. For small factors you'll also need to crank up the "foresight" value, ie. scale `d` higher.
This dampens the system stronger and makes it converge quicker.


## Problems: solar wind

But there's a problem: our parking space is close to the local star, which sends out enormous quantities of solar wind.
Press `S` to start the solar wind simulation.

What happens is this:

*gif of ship struggling to keep up*

The solar wind adds a _constant_ pressure to the system that results in a steady state of _wrong parking_. We need to
add something to the system that can deal with constant deviations.

What we're going to do is that we're going to measure how long we've been deviating and by how much, and apply a very
small push in the opposite direction. Essentially, we're integrating over the error (see below). For this, we need
another variable, but then integration in our step-wise system is easy:

    def get_inputs(self, ct):

        derivative = self.ship.x - self.last_x
        self.last_x = self.ship.x
        self.i = self.i + 0.2 * self.ship.x

        return {
            'factor': -5,
            'p': 1 * self.ship.x,
            'd': 60 * derivative,
            'i': 0.0025 * self.i,
        }

*gif of ship perfectly parking against solar wind, then keeping it up*

Perfect! Again, we found the correct strength factors without any trials, amazing! What happens here is that the
controller notices that _it stays on the same wrong side for too long_ and applies a thrust value that is proportional
to that ongoing error.

The `i` parameter is the most tricky one: turn it up too high and you'll overshoot very much, turn it too low and it'll
not converge quickly. What's usually done is to either clamp the value of the parameter or deactivate it when the ship
is too far away from the goal value.

Now that's a very stable system. Try turning off the solar wind or pushing the ship around with the arrow keys, and
it'll always park back at the center. Not always super quick, but it'll be close very quickly and converge inwards
always.

Play around with it and try to make it even better!


## Some background

What we wrote here is a so-called [PID controller](https://en.wikipedia.org/wiki/PID_controller), which is the
most-widely used technique for indirectly controlling a value. There is lots of literature on how to make them suitable
for all kinds of situations and for finding the parameter factors.

Go and play with it!


# Getting started

## Dependencies

The only direct dependency for this project is `arcade`, which allows us to draw to
the screen and interact with the user. Install it using

    pip install -r requirements.txt
    
and you should be good to go.

## Reloadable

The file `reloadably.py` contains a class `Reloadable` that implements an interface
for allowing live-reloading of code in a running program. To do so, a subclass of
`Reloadable` must define all variables that it wants serialized during a reload in
the variable `serialize_vars`.

The most visible use of `Reloadable` is in the `Driver` class, which implements a
virtual pilot. This means you can start the game with

    python game.py
    
then edit `driver.py` to suit your needs and the driver will be automatically reloaded
every time you save the file. For even more convenience, the game will reset every
time the driver is reloaded, so each driver starts from the same position.


# Some maths background

We need some words for the discussion above, so we define and explain them here.
Feel free to skip any of these if you know them, or if you want to look them up
during the discussion above.

## Control values and their derivatives

In general, in control theory you want to, well, control some variable. For example
the position of a spaceship. If you could directly set the value of that variable,
all would be easy, you'd simply set the desired position (or interpolate between
the current position and the desired position so as not to bump the passengers too
much). Unfortunately, one can usually not control the world directly, but instead
we can only change some _other_ variable, like the speed at which a ship is moving.
In fact, we can not even set _that_ directly, but we must control the _throttle_ that
is applied to the ship, which (in our idealized case) corresponds to the "second
derivative of the position". But what does that mean?

A derivative of a function in time `f(t)` is the _rate of change over time_. So if a
function `f` has derivative `f'(t) = 5` everywhere, this means that during each unit
of time the value of `f` increases by 5. So, if your ship moves a velocity of 1 m/s,
it means that it'll be one meter further every second. The velocity of a ship is the
first derivative of its position.  
The same applies to the second derivative, which is called acceleration. An
acceleration of 1 m/s^2 means that each second, the _velocity_ changes by 1 m/s.
So if you hold the thruster on the ship, it's going to accelerate at a constant rate,
meaning it'll be faster and faster. This is very similar to falling, which you are
probably familiar with.

To make it quicker to see, we have short names for each of these things: `x` for the
position, `v` for the speed and `T` for thrust. Well, `a` for acceleration, actually,
but in our spaceship model we'll use thrust. When you start the game, you'll see nice
little diagrams for each of them, and now you'll understand them, too.



## Tick-based or stepwise functions

You know, calculus is pretty hard. Functions can do all
[kinds](https://en.wikipedia.org/wiki/Dirichlet_function)
[of](https://en.wikipedia.org/wiki/Cantor_function)
[weird](https://en.wikipedia.org/wiki/Wiener_process)
[stuff](https://en.wikipedia.org/wiki/Weierstrass_function)
if you're
not careful, and doing
[derivation](https://www.quora.com/What-is-frac-mathrm-d-y-mathrm-d-x-of-y-x-x-x-x-x-x-x-x-x) and
[integration](https://math.stackexchange.com/questions/223653/weird-and-difficult-integral-sqrt1-frac13x-dx) is definitely not easy in the
general case.

Luckily, we are not in the general case. Our functions are only defined for specific
points, which makes taking the derivative and integrals _much_ easier.

### Derivation

Let's assume you have a function that is sampled at specific points in time, and let's
say that these points are `delta t` units apart. Here's an image of how that looks.

*image of a linear function* 

Here, the derivative is really, really simple. It's:

    f'(x) = ((f(x_2) - f(x_1)) * delta t) / delta t = f(x_2) - f(x_1)

So, any time you need a derivative of a sampled function, simply calculate the difference
between the data points and you're good.


### Integration

Integration is similarly easy. Since the value of the function is not defined between the
sampled points, we can do what we want in-between. So let's make it a stepwise function.

*image of a stepwise function*

Calculating the area under the curve is now... rather easy, isn't it?

    integral(f, x1, x2) = x1 * delta t
    
If you assume that `delta t == 1` it's even easier. Since the integral will only be by a
constant factor off, that's fine (depending on the use case).

To get an integral over more than one interval, simply add the piecewise integrals up.


