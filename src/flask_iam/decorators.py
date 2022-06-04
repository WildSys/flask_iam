#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
from functools import update_wrapper
import typing as t

# Type function
FUNC = t.TypeVar('F', bound=t.Callable[..., t.Any])


def setupmethod(f: FUNC) -> FUNC:
    """Transform class method to decorator"""
    # f_name = f.__name__

    def wrapper(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        # self._check_setup_finished(f_name)
        return f(self, *args, **kwargs)

    return t.cast(FUNC, update_wrapper(wrapper, f))
