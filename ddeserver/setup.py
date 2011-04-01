import os
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib

sources = ["serv.cpp","market.cpp","market_wrap.cxx"]

ext = Extension("win32_extension", sources,
                include_dirs = [os.path.join(get_python_lib(), "win32", "Include")],
                library_dirs = [os.path.join(get_python_lib(), "win32", "Libs"),"."],
                libraries=["trans2quik"],
                )

setup(
    name="DDE server for Quik", 
    version="1.0",
    ext_modules=[ext],
)
