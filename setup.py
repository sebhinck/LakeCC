from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
import os
from glob import glob

extra_compile_args=["-O3", "-ffast-math"]

sources = ['cython/LakeCC.pyx']
sources += glob('c++/*.cc')
inc_dirs = [numpy.get_include()]
inc_dirs += ['c++/']

# Define the extension
extension = Extension("LakeCC",
                      sources=sources,
                      include_dirs=inc_dirs,
                      extra_compile_args=extra_compile_args,
                      language="c++")

setup(
    name = "LakeModelCC",
    version = "0.0.1",
    description = "Lake Model using Connected component labeling",
    long_description = """Uses the standard run-length encoding, 2-scan algorithm
and an array-based implementation of the 'union-find' structure. Includes a modification for
filling Lakes.""",
    author = "Sebastian Hinck",
    author_email = "sebastian.hinck@awi.de",
    url = "...",
    cmdclass = {'build_ext': build_ext},
    ext_modules = [extension]
)

