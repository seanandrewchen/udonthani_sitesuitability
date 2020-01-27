########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import os
from lulcClassification import supervisedClassification_ensemble, dimensionalityReduction

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def pca():
    maindirectory = str(raw_input('type in directory name of images to be reduced: '))
    os.chdir(maindirectory)
    print maindirectory
    filelist = os.listdir(os.curdir)

    for file in filelist:
        print file
        dimensionalityReduction.pcaRaster(file)

def classify(maindirectory, roiraster):
    os.chdir(maindirectory)

    print maindirectory
    print roiraster

    filelist = os.listdir(os.curdir)

    for file in filelist:
        if os.path.isdir(file):
            continue
        print file
        supervisedClassification_ensemble.randomforestSupervisedClassify(file, roiraster)



########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    listofdirectories = raw_input('type in list of directories: ').split()
    print listofdirectories
    roiraster = raw_input('type in roi raster: ')

    for directory in listofdirectories:
        classify(directory, roiraster)



