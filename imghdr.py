"""
Compatibility stub for Python 3.14 since imghdr was removed from standard library.
Provides a 'what' function similar to original module using mimetypes.
"""

import mimetypes
import os


def what(file, h=None):
    """Guess the type of image contained in a file or byte stream."""
    # Try using file extension
    if isinstance(file, (str, bytes, os.PathLike)):
        filename = str(file)
        type_guess, _ = mimetypes.guess_type(filename)
        if type_guess and type_guess.startswith("image/"):
            return type_guess.split("/")[1]
    # Fallback: return None
    return None
