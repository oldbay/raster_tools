from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='raster_tools',
    version='0.1',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README')).read(),
    entry_points={
        'console_scripts':
        ['raster_tools_calc = raster_calc.util:run']
    },
    install_requires=[
        'GDAL',
        'numpy'
    ]
)
