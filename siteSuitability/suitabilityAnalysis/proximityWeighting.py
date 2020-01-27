########################################################################################################################
#                                                                                                                      #
#                                                    libraries                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal, ogr
import numpy as np
from scipy import ndimage
import os
import Image

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def array2raster(array, rasterin, rasterout):
    # Data from the original file
    [cols, rows] = array.shape
    trans = rasterin.GetGeoTransform()
    proj = rasterin.GetProjection()

    # Create the file, using the information from the original file
    driver = gdal.GetDriverByName("GTiff")
    rasterOut = driver.Create(str(rasterout), rows, cols, 1, gdal.GDT_Float64)

    # Write the array to the file
    rasterOut.GetRasterBand(1).WriteArray(array)

    # Georeference and reproject the image
    rasterOut.SetGeoTransform(trans)
    rasterOut.SetProjection(proj)


########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def subdivideRaster(rasterin):
    raster_ds = gdal.Open(rasterin)
    raster_ar = raster_ds.GetRasterBand(1).ReadAsArray()
    xSize = raster_ar.shape[0]
    ySize = raster_ar.shape[1]

    urban_ar = np.zeros((xSize, ySize), np.int64)
    agri_ar = np.zeros((xSize, ySize), np.int64)
    water_ar = np.zeros((xSize, ySize), np.int64)
    natural_ar = np.zeros((xSize, ySize), np.int64)

    #LULC Codes
    # 1 = URBAN
    # 2 = FOREST
    # 3 = WATER
    # 4 = AGRICULTURAL

    i = 0
    while i < raster_ar.shape[0]:
        j = 0
        while j < raster_ar.shape[1]:
            if raster_ar[i][j] == 1:
                urban_ar[i][j] = 1
                agri_ar[i][j] = 0
                water_ar[i][j] = 0
                natural_ar[i][j] = 0
            elif raster_ar[i][j] == 2:
                urban_ar[i][j] = 0
                agri_ar[i][j] = 0
                water_ar[i][j] = 0
                natural_ar[i][j] = 1
            elif raster_ar[i][j] == 3:
                urban_ar[i][j] = 0
                agri_ar[i][j] = 0
                water_ar[i][j] = 1
                natural_ar[i][j] = 0
            elif raster_ar[i][j] == 4:
                urban_ar[i][j] = 0
                agri_ar[i][j] = 1
                water_ar[i][j] = 0
                natural_ar[i][j] = 0
            j += 1
        i += 1

    urban_rasterout = rasterin.split('.')[0] + '_urban.TIF'
    agri_rasterout = rasterin.split('.')[0] + '_agri.TIF'
    water_rasterout = rasterin.split('.')[0] + '_water.TIF'
    natural_rasterout = rasterin.split('.')[0] + '_natural.TIF'

    array2raster(urban_ar, raster_ds, urban_rasterout)
    array2raster(agri_ar, raster_ds, agri_rasterout)
    array2raster(water_ar, raster_ds, water_rasterout)
    array2raster(natural_ar, raster_ds, natural_rasterout)

    return [urban_rasterout, water_rasterout, natural_rasterout, agri_rasterout]


########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def raster2array(rasterin):

    array = np.array(Image.open(rasterin))
    return array


########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def reclassifyArray(array, newvalue):

    i = 0
    while i < array.shape[0]:
        j = 0
        while j < array.shape[1]:
            if array[i][j] == 1:
                array[i][j] = newvalue
            j += 1
        i += 1
    return array

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def bufferRaster(rasterin, numberpixels):
    raster_array_0 = raster2array(rasterin)

    raster_array_1 = ndimage.binary_dilation(raster_array_0, iterations=int(numberpixels))
    final_array_0 = np.subtract(raster_array_1, raster_array_0)

    final_array_0 = reclassifyArray(final_array_0, .5)

    raster_array_2 = ndimage.binary_dilation(raster_array_1, iterations=int(numberpixels))
    final_array_1 = np.subtract(raster_array_2, raster_array_1)

    final_array_1 = reclassifyArray(final_array_1, .25)

    final_array = np.add(final_array_0, final_array_1)

    rasterout = rasterin.split('.')[0] + '_buffer.TIF'
    rasterin = gdal.Open(rasterin)
    array2raster(final_array, rasterin, rasterout)


########################################################################################################################
#                                                                                                                      #
#                                                        __main___                                                     #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    commandinput = raw_input('type 1 to subdivide rasters and 2 to buffer them: ')

    if int(commandinput) == 1:

        maindirectory = raw_input('type in directory: ')
        listoffiles = os.listdir(maindirectory)
        os.chdir(maindirectory)

        for raster in listoffiles:
            subdivideRaster(raster)

    else:
        numberpixels = raw_input('type in number of pixels: ')

        maindirectory = raw_input('type in directory: ')
        listoffiles = os.listdir(maindirectory)
        os.chdir(maindirectory)

        for raster in listoffiles:
            bufferRaster(raster, numberpixels)







