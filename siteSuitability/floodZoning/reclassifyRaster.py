########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import numpy as np
from osgeo import gdal, gdal_array
import pandas as pd
import math

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
    rasterOut = driver.Create(str(rasterout), rows, cols, 1, gdal.GDT_Float32)

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

def calculateNewBins(raster):
    dem = gdal.Open(raster)
    arr = np.array(dem.GetRasterBand(1).ReadAsArray(), dtype=np.float16)
    arr = np.log(arr)

    newarr = np.reshape(arr, (1, arr.shape[0]*arr.shape[1]))
    newarr = newarr.flatten()

    logbins = pd.qcut(newarr, 5, retbins=True)
    logbinvalues = logbins[1]

    i = 0
    while i <= 5:
        logbinvalues[i] = math.exp(float(logbinvalues[i]))
        i = i + 1

    return logbinvalues

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def reclassifyRaster(raster, bins, newbinvalues):

    #turn raster into numpy array
    rasterIn = gdal.Open(raster)
    arr = gdal_array.BandReadAsArray(rasterIn.GetRasterBand(1))

    print arr

    #conditional loop to reclassify
    arr[(bins[5] >= arr) & (arr > bins[4])] = newbinvalues[4]
    arr[(bins[4] >= arr) & (arr > bins[3])] = newbinvalues[3]
    arr[(bins[3] >= arr) & (arr > bins[2])] = newbinvalues[2]
    arr[(bins[2] >= arr) & (arr > bins[1])] = newbinvalues[1]
    arr[(bins[1] >= arr) & (arr > bins[0])] = newbinvalues[0]


    print arr

    #Array to raster
    rasterOut = raster.split('.')[0] + '_reclassified.TIF'
    array2raster(arr, rasterIn, rasterOut)
    return rasterOut

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def binaryRasterReclass(raster, newbinvalues):

    # Turn raster into numpy array
    rasterIn = gdal.Open(raster)
    arr = np.array(rasterIn.GetRasterBand(1).ReadAsArray())
    print arr

    # Create new array
    newarr = np.zeros((arr.shape[0], arr.shape[1]))

    # Loop through array populating it with conditionals
    i = 0
    while i < arr.shape[0]:
        j = 0
        while j < arr.shape[1]:
            if arr[i][j] == 0:
                newarr[i][j] = newbinvalues[0]
            else:
                newarr[i][j] = newbinvalues[1]
            j += 1
        i += 1
    print newarr

    # Array to raster
    rasterOut = raster.split('.')[0] + '_reclassified.TIF'
    array2raster(newarr, rasterIn, rasterOut)
    return rasterOut


########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    raster = raw_input('type in raster: ')
    whichtype = raw_input('type 1 to reclassify a dem or type 2 to reclassify a water raster: ')

    if whichtype == str(1):
        bins = calculateNewBins(raster)
        newbinvalues = [.9, .8, .7, .6, .5]
        print 'bins: ' + str(bins)
        print 'new bin values: ' + str(newbinvalues)
        reclassifyRaster(raster, bins, newbinvalues)

    elif whichtype == str(2):
        newbinvalues = [.5, .9]
        print 'new bin values: ' + str(newbinvalues)
        binaryRasterReclass(raster, newbinvalues)



