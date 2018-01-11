from rtools import raster2array, array2raster, raster2multi, repair2reload

valid_file = "valid.tif"
invalid_file = "invalid.tif"
repair_file = "repair.tif"

# test valid raster
raster_valid = raster2array(valid_file, 1)
print raster_valid.is_valid()

# test valid raster
raster_invalid = raster2array(invalid_file, 1)
print raster_invalid.is_valid()

# write new valid raster from invalid
array2raster(None, invalid_file.repair(), repair_file)

# repair invalid raster
repair2reload(invalid_file)
