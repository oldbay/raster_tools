from raster_tools import raster2array, array2raster, raster2calc
import numpy as np

in_file = "multi.tif"
out_file = "calc.tif"

# load bands
red = raster2array(in_file, 1)
green = raster2array(in_file, 2)
blue = raster2array(in_file, 3)

# calc function TGI
calc_func = lambda r,g,b: np.choose(
    np.not_equal(g-r+b-255.0, 0.0),
    (
        -9999.0,
        np.subtract(
            g,
            np.multiply(0.39, r),
            np.multiply(0.61, b)
        )
    )
)

# init calss calc
calc = raster2calc()
out = calc(
        calc_func,
        1000, 1000, 3000, 3000,
        r=red,
        g=green,
        b=blue
    )

# save raster
array2raster(None, out, "calc.tif")
