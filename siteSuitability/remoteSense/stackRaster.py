########################################################################################################################
#                                                                                                                      #
#                                                Load Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import rsgislib
from rsgislib import imageutils

########################################################################################################################
#                                                                                                                      #
#                                                   stackRaster                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def stackBands(basename, b1, b2, b3):
        raster_1 = basename + '_B1.TIF'
        raster_2 = basename + '_B2.TIF'
        raster_3 = basename + '_B3.TIF'
        raster_4 = basename + '_B4.TIF'
        raster_5 = basename + '_B5.TIF'
        raster_6 = basename + '_B6.TIF'
        raster_7 = basename + '_B7.TIF'
        raster_8 = basename + '_B8.TIF'
        raster_9 = basename + '_B9.TIF'
        raster_10 = basename + '_B10.TIF'
        raster_11 = basename + '_B11.TIF'

        b_1 = int(b1) - 1
        b_2 = int(b2) - 1
        b_3 = int(b3) - 1

        fullBandNamesList = ['Coastal', 'Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'Panchromatic', 'Cirrus', 'TIRS1',
                         'TIRS2']
        bandNamesList = [fullBandNamesList[b_1], fullBandNamesList[b_2], fullBandNamesList[b_3]]

        fullImageList = [raster_1, raster_2, raster_3, raster_4, raster_5, raster_6, raster_7, raster_8, raster_9,
                     raster_10, raster_11]
        imageList = [fullImageList[b_1], fullImageList[b_2], fullImageList[b_3]]

        outputName = basename + '_B' + b1 + b2 + b3 + '.TIF'
        gdalFormat = 'GTiff'
        dataType = rsgislib.TYPE_16UINT

        imageutils.stackImageBands(imageList, bandNamesList, outputName, None, 0, gdalFormat, dataType)

def fullStack(basename):
        raster_1 = basename + '_B1.TIF'
        raster_2 = basename + '_B2.TIF'
        raster_3 = basename + '_B3.TIF'
        raster_4 = basename + '_B4.TIF'
        raster_5 = basename + '_B5.TIF'
        raster_6 = basename + '_B6.TIF'
        raster_7 = basename + '_B7.TIF'
        raster_8 = basename + '_B8.TIF'
        raster_9 = basename + '_B9.TIF'
        raster_10 = basename + '_B10.TIF'
        raster_11 = basename + '_B11.TIF'

        bandNamesList = ['Coastal', 'Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'Cirrus']
        imageList = [raster_1, raster_2, raster_3, raster_4, raster_5, raster_6, raster_7, raster_9,]
        outputName = basename + '_fullstacked.TIF'
        gdalFormat = 'GTiff'
        dataType = rsgislib.TYPE_16UINT
        imageutils.stackImageBands(imageList, bandNamesList, outputName, None, 0, gdalFormat, dataType)



########################################################################################################################
#                                                                                                                      #
#                                                       main()                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def stack():
    fullStack(raw_input('type in basename: '))
    stackBands(raw_input('type in basename: '), raw_input('type in first band: '), raw_input('type in second band: '), raw_input('type in third band: '))



########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    stack()



