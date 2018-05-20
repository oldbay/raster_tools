# import cv2
import numpy as np

from raster_tools import raster2multiarray, multiarray2multiraster

img_in = 'multi.tif'
img_out = 'out.tif'

img = raster2multiarray(img_in, 3, 2, 1)
img.array_type = "cv"
img.codage = np.uint8
img = img.get_std_dict()

# working in cv2 to img["array"]

multiarray2multiraster(img_out, img)()
