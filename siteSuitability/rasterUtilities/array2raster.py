########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal

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
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    array2raster(raw_input('type in array: '), raw_input('type in rasterin: '), raw_input('type in rasterout: '))
