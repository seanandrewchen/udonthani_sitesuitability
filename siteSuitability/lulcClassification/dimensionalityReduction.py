########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal, gdal_array
import numpy as np
from spectral import principal_components
import os

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def array2raster(array, rasterin, rasterout):
    # Data from the original file
    [cols, rows, bands] = array.shape
    trans = rasterin.GetGeoTransform()
    proj = rasterin.GetProjection()

    # Create the file, using the information from the original file
    driver = gdal.GetDriverByName("GTiff")
    rasterOut = driver.Create(str(rasterout), rows, cols, bands, gdal.GDT_Float32)

    # Write the array to the file
    for b in range(bands):
        rasterOut.GetRasterBand(b+1).WriteArray(array[:,:,b])

    # Georeference and reproject the image
    rasterOut.SetGeoTransform(trans)
    rasterOut.SetProjection(proj)

########################################################################################################################
#                                                                                                                      #
#                                                     PCA REDUCTION                                                    #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def pcaRaster(raster):

    # Open up raster image and load into an n dimensional array where n is number of bands
    image = gdal.Open(raster)
    data = np.zeros((image.RasterYSize, image.RasterXSize, image.RasterCount), gdal_array.GDALTypeCodeToNumericTypeCode(image.GetRasterBand(1).DataType))
    for b in range(data.shape[2]):
        data[:, :, b] = image.GetRasterBand(b + 1).ReadAsArray()

    # Load nd-array into PCA class object
    pca = principal_components(data)

    # Print eigenvalues
    eigenvalues = pca.eigenvalues
    print eigenvalues

    # Reduce data array to where 99% of data variance is explained
    pcdata = pca.reduce(fraction=.99).transform(data)

    # Save data array into a GTiff raster
    rasterout = raster.split('.')[0] + '_PCAReduced.TIF'
    array2raster(pcdata, image, rasterout)

    return pcdata

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    rasterdirectory = raw_input('type in directory name: ')
    listoffiles = os.listdir(rasterdirectory)
    os.chdir(rasterdirectory)

    for file in listoffiles:
        pcaRaster(file)