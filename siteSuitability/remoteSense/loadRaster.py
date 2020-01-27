########################################################################################################################
#                                                                                                                      #
#                                                Load Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal

########################################################################################################################
#                                                                                                                      #
#                                                   loadRaster                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

class loadRaster:

    def __init__(self, filepath):
        self.filepath = filepath

    def findProjection(self):
        raster = gdal.Open(self.filepath, gdal.GA_ReadOnly)
        proj = raster.GetProjectionRF()
        return proj

    def rasterDimensions(self):
        raster = gdal.Open(self.filepath, gdal.GA_ReadOnly)
        ncol = raster.RasterXSize
        nrow = raster.RasterYSize
        return ncol, nrow

    def findGeotransform(self):
        raster = gdal.Open(self.filepath, gdal.GA_ReadOnly)
        ext = raster.GetGeoTransform()
        return ext

    def load(self):
        raster = gdal.Open(self.filepath, gdal.GA_ReadOnly)
        return raster

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    test_raster = loadRaster(raw_input('enter raster file path: '))
    test_raster_object = test_raster.load()

    print(test_raster.findProjection())
    print(test_raster.rasterDimensions())
    print(test_raster.findGeotransform())

