########################################################################################################################
#                                                                                                                      #
#                                                    Libraries                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import gdalnumeric
from osgeo import gdal_array
import numpy as np
import os
import shutil

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def changeDetection(image1, image2, outputname):

    ar1 = gdalnumeric.LoadFile(image1).astype(np.int8)
    ar2 = gdalnumeric.LoadFile(image2)[1].astype(np.int8)

    diff = ar2 - ar1

    classes = np.histogram(diff, bins=5)[1]

    lut = [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,255,0], [255,0,0]]
    start = 1

    rgb = np.zeros((3, diff.shape[0], diff.shape[1],), np.int8)
    for i in range(len(classes)):
        mask = np.logical_and(start <= diff, diff <= classes[i])
        for j in range(len(lut[i])):
            rgb[j] = np.choose(mask, (rgb[j], lut[i][j]))
        start = classes[i] + 1

    gdal_array.SaveArray(rgb, outputname, format="GTiff")

def seriesChangeDetection():
    directory = raw_input('type in name of directory: ')
    listfiles = os.listdir(directory)
    numberfiles = len(listfiles)
    os.mkdir('changedetection')

    i = 0
    while i < numberfiles:
        changeDetection(listfiles[i], listfiles[i+1], 'changedetection_' + str(i) + '.TIF')
        shutil.move('changedetection_' + str(i) + '.TIF', 'changedetection')
        i = i + 1

    os.chdir('changedetection')
    allfiles = os.listdir('changedetection')
    os.system(('gdal_merge.py studyarea_changedetection.tif {files}').format(files=allfiles))



########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    seriesChangeDetection()