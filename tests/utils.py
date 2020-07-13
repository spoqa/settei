import contextlib
import os
import typing


@contextlib.contextmanager
def os_environ(d: typing.Mapping):
    os.environ.update(d)
    yield
    for k in d:
        del os.environ[k]
