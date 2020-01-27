########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from scipy import ndimage
from osgeo import gdal
import numpy as np
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
    rasterOut = driver.Create(str(rasterout), rows, cols, 1, gdal.GDT_Byte)

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

def raster2array(rasterin):

    array = np.array(Image.open(rasterin))
    return array

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def cleanRaster(rasterin, iterations):

    img = raster2array(rasterin)

    ndimage.gaussian_filter(img, sigma=10)
    ndimage.median_filter(img, 5)

    open = ndimage.binary_opening(img)
    eroded = ndimage.binary_erosion(open, iterations=int(iterations))
    #cleaned = ndimage.binary_propagation(eroded, mask=img)


    open = None
    #eroded = None
    img = None

    return eroded

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':

    commandprompt = raw_input('type 1 for single and 2 for batch: ')

    if int(commandprompt) == 1:
        maindirectory = raw_input('type in directory: ')
        os.chdir(maindirectory)
        iterations = raw_input('type in iterations: ')

        rasterin = raw_input('type in raster to process: ')
        rasterout = rasterin.split('.')[0] + '_cleaned.TIF'
        raster_base = gdal.Open(rasterin)

        raster = cleanRaster(rasterin, iterations)
        array2raster(raster, raster_base, rasterout)
    else:
        maindirectory = raw_input('type in directory: ')
        iterations = raw_input('type in iterations: ')

        listoffiles = os.listdir(maindirectory)
        print(listoffiles)

        os.chdir(maindirectory)

        for rasterin in listoffiles:
            rasterout = rasterin.split('.')[0] + '_cleaned.TIF'
            raster_base = gdal.Open(rasterin)

            print(rasterin)
            print(rasterout)

            raster = cleanRaster(rasterin, iterations)
            array2raster(raster, raster_base, rasterout)
