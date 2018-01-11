from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='raster_tools',
    version='0.4',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README')).read(),
    install_requires=[
        'GDAL',
        'numpy'
    ]
)
