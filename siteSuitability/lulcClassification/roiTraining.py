########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal, ogr
import numpy as np

########################################################################################################################
#                                                                                                                      #
#                                          rasterize roi training shapefiles                                           #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

########################################################################################################################
########################################################################################################################
# One way to make a ROI training file is to download OSM data. It will give at least some data on land uses, though    #
# incomplete. What you do then is to create several shape files just based on each type of land use. Then you add two  #
# attributes in the shape file database: an id and a class. IDs are integers and classes are their string descriptions.#
# Then you can union all the separate shape files and then this will raster-ize that one file. It should end up that   #
# each pixel is either on or off and the ones that are on have an ID for a certain land use type.                      #
########################################################################################################################
########################################################################################################################

def rasterizeROIShapefile(rasterfile, shapefile, fileout):

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
    gdal.RasterizeLayer(out_raster_ds, [1], layer, options=["ALL_TOUCHED=TRUE", "ATTRIBUTE=id"])

    out_raster_ds = None


def checkRaster(raster):
    roi_ds = gdal.Open(raster, gdal.GA_ReadOnly)
    roi = roi_ds.GetRasterBand(1).ReadAsArray()

    # How many pixels are in each class?
    classes = np.unique(roi)
    # Iterate over all class labels in the ROI image, printing out some information
    for c in classes:
        print('Class {c} contains {n} pixels'.format(c=c, n=(roi == c).sum()))

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    rasterizeROIShapefile(raw_input('type in raster file: '), raw_input('type in shapefile: '), raw_input('type fileout: '))
    #checkRaster(raw_input('type in raster: '))