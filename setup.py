from setuptools import setup, find_packages
from os.path import join, dirname
from raster_tools import __version__

setup(
    name='raster_tools',
    version=__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README')).read(),
    entry_points={
        'console_scripts':
        ['raster_tools_util = raster_norms.util:run']
    },
    install_requires=[
        'GDAL'
    ]
)
