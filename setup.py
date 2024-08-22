import os
from distutils.extension import Extension

from setuptools import setup, find_packages
from Cython.Build import cythonize


def get_ext_modules():
    ext_modules = []
    for root, _, files in os.walk("modules"):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                module_name = os.path.splitext(path)[0].replace(os.path.sep, '.')
                ext_modules.append(Extension(module_name, [path]))

    for root, _, files in os.walk("entities"):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                module_name = os.path.splitext(path)[0].replace(os.path.sep, '.')
                ext_modules.append(Extension(module_name, [path]))
    return ext_modules


setup(
    name="ai-mate",
    version="0.1",
    packages=find_packages(),
    ext_modules=cythonize(
        get_ext_modules(),
        compiler_directives={'language_level': "3", 'c_string_encoding': 'utf8'}
    ),
)
