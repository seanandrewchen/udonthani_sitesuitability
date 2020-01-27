########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from floodZoning import createBuffer, rasterizeVector, reclassifyRaster
import numpy as np
from osgeo import gdal

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def waterRiskZone(shapefile, bufferdistance, rasterfile):

    def waterBuffer(shapefile, bufferdistance, rasterfile):
        buffername = createBuffer.createBuffer(shapefile, bufferdistance)
        rasterbuffername = rasterizeVector.rasterizeShapefile(rasterfile, buffername)
        return rasterbuffername

    def waterReclassify(rasterbuffername):
        newbinvalues = [0.5, 0.9]
        waterraster = reclassifyRaster.binaryRasterReclass(rasterbuffername, newbinvalues)
        return waterraster

    rasterbuffername = waterBuffer(shapefile, bufferdistance, rasterfile)
    waterraster = waterReclassify(rasterbuffername)
    waterobject = gdal.Open(waterraster)
    water_arr = np.array(waterobject.GetRasterBand(1).ReadAsArray(), dtype=np.float16)
    return water_arr

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def demRiskZone(dem):
    newbins = reclassifyRaster.calculateNewBins(dem)
    newbinvalues = [0.9, 0.8, 0.7, 0.6, 0.5]
    demraster = reclassifyRaster.reclassifyRaster(dem, newbins, newbinvalues)
    demobject = gdal.Open(demraster)
    dem_arr = np.array(demobject.GetRasterBand(1).ReadAsArray(), dtype=np.float16)
    return dem_arr

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def array2raster(array, rasterin, rasterout):
    # Data from the original file
    raster = gdal.Open(rasterin)
    [cols, rows] = array.shape
    trans = raster.GetGeoTransform()
    proj = raster.GetProjection()

    # Create the file, using the information from the original file
    driver = gdal.GetDriverByName("GTiff")
    rasterOut = driver.Create(str(rasterout), rows, cols, 1, gdal.GDT_Float32)

    # Write the array to the file, which is the original array in this example
    rasterOut.GetRasterBand(1).WriteArray(array)

    # Georeference the image
    rasterOut.SetGeoTransform(trans)

    # Write projection information
    rasterOut.SetProjection(proj)

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def floodzoneMap(dem, ponds, streams, canals, ponds_distance, streams_distance, canals_distance, fileout, referenceraster):

    # Create dem array
    demzone = demRiskZone(dem)

    # Create array shapes
    xSize = demzone.shape[0]
    ySize = demzone.shape[1]
    arraySize = [xSize, ySize]

    # Create water arrays
    pondArray = waterRiskZone(ponds, ponds_distance, referenceraster)
    streamArray = waterRiskZone(streams, streams_distance, referenceraster)
    canalArray = waterRiskZone(canals, canals_distance, referenceraster)

    print pondArray.shape[0], pondArray[1]
    print streamArray.shape[0], streamArray[1]
    print canalArray.shape[0], canalArray[1]


    # Create array combining water arrays
    waterzone = np.zeros(arraySize, np.float32)

    # Populate array
    i = 0
    while i < xSize:
        j = 0
        while j < ySize:
            pd = pondArray[i][j]
            st = streamArray[i][j]
            cn = canalArray[i][j]
            if (pd != 0) & (st != 0) & (cn != 0):
                waterzone[i][j] = pd * st * cn
            elif (pd == 0) & (st == 0) & (cn == 0):
                waterzone[i][j] = 0
            elif (pd != 0) & (st == 0) & (cn == 0):
                waterzone[i][j] = pd
            elif (pd == 0) & (st != 0) & (cn == 0):
                waterzone[i][j] = st
            elif (pd == 0) & (st == 0) & (cn != 0):
                waterzone[i][j] = cn
            elif (pd != 0) & (st != 0) & (cn == 0):
                waterzone[i][j] = pd * st
            elif (pd != 0) & (st == 0) & (cn != 0):
                waterzone[i][j] = pd * cn
            elif (pd == 0) & (st != 0) & (cn != 0):
                waterzone[i][j] = st * cn
            j += 1
        i += 1

    # Create empty array for flood zone risk analysis
    floodzone = np.zeros(arraySize, np.float32)

    # Populate array
    i = 0
    while i < xSize:
        j = 0
        while j < ySize:
            floodzone[i][j] = waterzone[i][j] * demzone[i][j]
            j += 1
        i += 1

    # Output to GTiff
    array2raster(floodzone, referenceraster, fileout)


########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    dem = 'floodZoning/data/dem.tif'
    ponds = 'floodZoning/data/Ponds.shp'
    ponds_distance = 1000
    canals = 'floodZoning/data/Canals.shp'
    canals_distance = 500
    streams = 'floodzoning/data/Streams.shp'
    streams_distance = 1000
    fileout = 'floodzone.tif'

    floodzoneMap(dem, ponds, streams, canals, ponds_distance, streams_distance, canals_distance, fileout, dem)