#!/usr/bin/python
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy
import sys

if sys.platform == "linux2" :
    include_talib_dir = "/usr/local/include/ta-lib/"
    lib_talib_dir = "/usr/local/lib/"
    libraries=["ta_lib"]
elif sys.platform == "win32":
    include_talib_dir = r"C:\work\ta-lib\c\include"
    lib_talib_dir = r"C:\work\ta-lib\c\lib"
    libraries=["ta_libc_cmr","ta_abstract_cmr","ta_common_cmr","ta_func_cmr"]

ext = Extension("talib", ["talib.pyx"], include_dirs=[numpy.get_include(), include_talib_dir], library_dirs=[lib_talib_dir], libraries=libraries)

setup(ext_modules=[ext], cmdclass = {'build_ext': build_ext})
