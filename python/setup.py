#!/usr/bin/python
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy
import sys

if sys.platform == "linux2" :
    include_talib_dir = "/usr/local/include/ta-lib/"
    lib_talib_dir = "/usr/local/lib/"
elif sys.platform == "win32":
    include_talib_dir = r"C:\work\ta-lib\c\include"
    lib_talib_dir = r"C:\work\ta-lib\c\lib"

ext = Extension("talib", ["talib.pyx"],
    include_dirs=[numpy.get_include(),
                  include_talib_dir],
    library_dirs=[lib_talib_dir],
    libraries=["ta_libc_cmr"]
)

setup(ext_modules=[ext],
    cmdclass = {'build_ext': build_ext})
