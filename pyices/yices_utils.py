import ctypes
import sys

import yices_lib as libyices
import fix_env

# Printing to <stderr> from C
ctypes.pythonapi.PyFile_AsFile.argtypes = [ctypes.py_object]
ctypes.pythonapi.PyFile_AsFile.restype = libyices.POINTER(libyices.FILE)
c_stderr = ctypes.pythonapi.PyFile_AsFile(sys.stderr)

def d_yices_error():
    """
    Print the last Yices error to stderr.
    """
    libyices.yices_print_error(c_stderr)
