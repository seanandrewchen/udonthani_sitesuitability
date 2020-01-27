########################################################################################################################
#                                                                                                                      #
#                                                    libraries                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import gdal, gdal_array
import numpy as np
import os

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def array2raster(array, rasterin, rasterout):
    # Data from the original file
    [cols, rows] = array.shape
    rasterIn = gdal.Open(rasterin)
    trans = rasterIn.GetGeoTransform()
    proj = rasterIn.GetProjection()

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

def resizeRaster(floodraster, newfloodraster):

    commandline = "gdalwarp -tr 0.000138439040640 -0.000138469003690 {floodraster} {newfloodraster}".format(floodraster=floodraster, newfloodraster=newfloodraster)
    os.system(commandline)

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def siteSuitabilityAnalysis(floodingmap, urbanbuffer, agribuffer, waterbuffer, urban, water, agri, natural):

    flooding = gdal.Open(floodingmap)
    urban_b = gdal.Open(urbanbuffer)
    agri_b = gdal.Open(agribuffer)
    water_b = gdal.Open(waterbuffer)
    urban_r = gdal.Open(urban)
    water_r = gdal.Open(water)
    agri_r = gdal.Open(agri)
    natural_r = gdal.Open(natural)

    floodArray = flooding.GetRasterBand(1).ReadAsArray()
    urbanArray = urban_r.GetRasterBand(1).ReadAsArray()
    waterArray = water_r.GetRasterBand(1).ReadAsArray()
    agriArray = agri_r.GetRasterBand(1).ReadAsArray()
    naturalArray = natural_r.GetRasterBand(1).ReadAsArray()
    urbanBufferArray = urban_b.GetRasterBand(1).ReadAsArray()
    agriBufferArray = agri_b.GetRasterBand(1).ReadAsArray()
    waterBufferArray = water_b.GetRasterBand(1).ReadAsArray()

    greenInfrastructureSiting = np.zeros((floodArray.shape[0], floodArray.shape[1]), np.float32)

    i = 0
    while i < greenInfrastructureSiting.shape[0]:
        j = 0
        while j < greenInfrastructureSiting.shape[1]:
            # LULC IDs
                # 1 = URBAN
                # 2 = FOREST
                # 3 = WATER
                # 4 = AGRICULTURAL

            # Agricultural areas are developable
            # if agriArray[i][j] == 1:
            #     greenInfrastructureSiting[i][j] = 1

            # Forest areas are developable
            # if naturalArray[i][j] == 1:
            #     greenInfrastructureSiting[i][j] = 1

            # Flooding Areas have priority
            if floodArray[i][j] != 0:
                greenInfrastructureSiting[i][j] += floodArray[i][j]

            # Urban buffers have priority
            #if urbanBufferArray[i][j] != 0:
            #    greenInfrastructureSiting[i][j] += .5

            # Water buffers have priority
            #if waterBufferArray[i][j] != 0:
            #    greenInfrastructureSiting[i][j] += .5

            # Agricultural buffers have priority
            # if agriBufferArray[i][j] != 0:
            #     greenInfrastructureSiting[i][j] += .25

            # Urban areas are non-developable
            if urbanArray[i][j] == 1:
                greenInfrastructureSiting[i][j] = 0

            # Water areas are non-developable
            if waterArray[i][j] == 1:
                greenInfrastructureSiting[i][j] = 0

            j += 1
        i += 1

    array2raster(greenInfrastructureSiting, floodingmap, "greeninfrastructure_suitableland.TIF")

    return greenInfrastructureSiting


########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def pathCreation():
    return 'not finished yet'


########################################################################################################################
#                                                                                                                      #
#                                                        __main___                                                     #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    commandprompt = raw_input('type 1 to resize a raster and 2 to perform a site suitability analysis: ')

    if int(commandprompt) == 1:
        resizeRaster(raw_input('type in flooding map file: '), raw_input('type in land use map file: '))
    else:
        maindirectory = 'data'
        os.chdir(maindirectory)
        floodmap = 'flood.TIF'
        urbanbuffer = 'urbanbuffer.TIF'
        agribuffer = 'agri.TIF'
        waterbuffer = 'waterbuffer.TIF'
        urban = 'urban.TIF'
        water = 'water.TIF'
        natural = 'natural.TIF'
        agri = 'agri.TIF'
        siteSuitabilityAnalysis(floodmap, urbanbuffer, agribuffer, waterbuffer, urban, water, agri, natural)