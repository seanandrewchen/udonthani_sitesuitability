########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal, ogr

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def rasterizeShapefile(rasterfile, shapefile):

    fileout = shapefile.split('.')[0] + '.TIF'

    #Open raster image
    raster_ds = gdal.Open(rasterfile, gdal.GA_ReadOnly)

    #Fetch number of rows and columns
    ncol = raster_ds.RasterXSize
    nrow = raster_ds.RasterYSize

    #Fetch projection and extent
    proj = raster_ds.GetProjectionRef()
    ext = raster_ds.GetGeoTransform()

    raster_ds = None

    #Create the raster dataset
    memory_driver = gdal.GetDriverByName('GTiff')
    out_raster_ds = memory_driver.Create(fileout, ncol, nrow, 1, gdal.GDT_Byte)

    #Set the ROI image's projection and extent to our input raster's projection and extent
    out_raster_ds.SetProjection(proj)
    out_raster_ds.SetGeoTransform(ext)

    #Fill our output band with the 0 blank, no class label, value
    b = out_raster_ds.GetRasterBand(1)
    b.Fill(0)

    #Get layer
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shapefile, 0)
    layer = dataSource.GetLayer()

    #Raster the shapefile layer to our new dataset
    gdal.RasterizeLayer(out_raster_ds, [1], layer, None, None, [1], options=["ALL_TOUCHED=TRUE", "ATTRIBUTE=id"])

    return fileout

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    rasterizeShapefile(raw_input('type in raster: '), raw_input('type in shapefile: '))
