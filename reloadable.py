#
# Copyright 2020, 2021 Johannes Spielmann
# Licensed under 3-clause BSD license, for details see the file LICENSE.txt
#

import os
from importlib import reload, import_module


class Reloadable:
    """
    Class that can be re-loaded and re-initialized.

    Put the names of the variables you need to be preserved during a reload into `serialize_vars`. The constructor will
    automatically set the values for you after the reload.

    Note that `.reload()` will give you the *new instance*, so you'll have to store that yourself. This implementation
    does not contain a proxy abstraction.

    So, using this reload functionality would look something like this:
    ```
    if now_is_a_good_time_to_reload():
        instance = instance.reload()
    ```
    Note that this performs a reload *only* if the file, where the class resides, changed.
    """
    serialize_vars = ()

    def __init__(self, state=None):
        self._module = import_module(self.__module__)
        self._mtime = os.stat(self._module.__file__).st_mtime

        if state:
            for var in self.serialize_vars:
                setattr(self, var, state.get(var))

    def reload(self, **kwargs):
        """Reload a new instance of this class with same values."""

        mtime = os.stat(self._module.__file__).st_mtime
        if mtime > self._mtime:
            print(f"reloading {self.__class__}")
            self._module = reload(self._module)
            state = self.capture_state()
            klass = getattr(self._module, self.__class__.__name__)
            instance = klass(state, **kwargs)
            return instance

        return self

    def capture_state(self):
        """Capture all necessary state for a reload."""
        state = {}
        for varname in self.serialize_vars:
            state[varname] = getattr(self, varname, None)

        return state
