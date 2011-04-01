import os
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib
from Cython.Distutils import build_ext

sources = ["quikdde.cpp","quik.pyx"]

ext = Extension("quik", sources,
                include_dirs = [os.path.join(get_python_lib(), "win32", "Include")],
                library_dirs = [os.path.join(get_python_lib(), "win32", "Libs"),"."],
                language="c++",
                libraries=["trans2quik"],
                )

setup(
    name="Quik python interface",
    version="1.0",
    ext_modules=[ext],
    cmdclass = {'build_ext':build_ext}
)
