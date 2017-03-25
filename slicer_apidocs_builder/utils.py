
import errno
import os
import shlex
import subprocess

from contextlib import contextmanager


def mkdir_p(path):
    """Ensure directory ``path`` exists. If needed, parent directories
    are created.

    Adapted from http://stackoverflow.com/a/600612/1539918
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:  # pragma: no cover
            raise


@contextmanager
def working_dir(directory=None, make_directory=False):
    """
    Context manager to save and optionally change the current directory.

    :param directory:
      Path to set as current working directory. If ``None``
      is passed, ``os.getcwd()`` is used instead.

    :param make_directory:
      If True, ``directory`` is created.
    """
    old_cwd = os.getcwd()

    if directory:
        if make_directory:
            mkdir_p(directory)
        os.chdir(directory)
        print("\ncwd: %s" % os.getcwd())
    yield
    os.chdir(old_cwd)


def execute(cmd, capture=False, verbose=True):
    if verbose:
        print("\n> %s\n" % cmd)
    check_func = subprocess.check_call
    extra_kwargs = {}
    if capture:
        check_func = subprocess.check_output
        extra_kwargs = {"stderr": subprocess.STDOUT}
    return check_func(cmd if isinstance(cmd, list) else shlex.split(cmd), **extra_kwargs)
