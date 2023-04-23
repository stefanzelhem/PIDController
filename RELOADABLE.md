# Reloadable - runtime code reloading

In the file `reloadable.py`, there is a little module for reloading some class *while the program is running*. If you
want to use this functionality, copy that file into your project and follow the steps below.

To find this functionality useful, you need a program that runs all the time, while you are performing some changes in
your code. Like, your program runs a loop where you need to change some behaviour inside, or you control something that
is not easily re-startable. An example of this is the PID controller that is the main point of this repository, and can
be found in `game.py`.

Likely the simplest loop that would work would be this:

    my_reloadable_instance = MyReloadableClass()

    while True:
        my_reloadable_instance.do_something()
        my_reloadable_instance = my_reloadable_instance.reload()
        time.sleep(1)

Here, we simply call some function on an instance of a reloadable class, then reload it, then wait a little. And then,
we do it all over again. How would `my_reloadable_instance` look like? Well, something like this, probably:

    from reloadable import Reloadable

    class MyReloadableClass(Reloadable):
        def do_something():
            print("here's where you'd do something")

When you run the loop, it'll print `here's where you'd do something` every second. But if you edit that function and
save the file, the loop will automatically reload your class and do the new thing.

And that's it. There are no dependencies to install, no other setup to perform, just these few things:

1. A class that inherits from `reloadable.Reloadable`, from the file `reloadable.py` in this repository.
2. An instance of that class.
3. A loop that frequently calls `.reload()` on the instance _and replaces the instance with the return value_.

There is a demonstration loop in `intersin.py`, which is intended to demonstrate implementing a sine computation
algorithm, together with its reloadable sine calculator in `sinecalc.py`.

You can see a short demonstration of the module in this youtube video about it: https://www.youtube.com/watch?v=g0tKdAzfIY8
