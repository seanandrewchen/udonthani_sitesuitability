########################################################################################################################
#                                                                                                                      #
#                                                  Import Library                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import os
import subprocess
import re

########################################################################################################################
#                                                                                                                      #
#                                                  Define Functions                                                    #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def clipNreprojectDirectory(directoryname, mask):
    #get the bounding box coordinates
    line = 'ogrinfo -al {shape} | grep Extent'.format(shape=mask)
    maskextent = subprocess.check_output(line, shell=True)
    non_decimal = re.compile(r'[^\d.\s]+')
    maskextent = non_decimal.sub('', maskextent)
    maskextent = maskextent.split()

    #reproject
    listoffiles = os.listdir(directoryname)
    pathname = str(directoryname + '/prepared')
    os.mkdir(pathname, 0755)
    for file in listoffiles:
        command_string = 'gdalwarp {img_in} {img_out} -t_srs "+proj=longlat +ellps=WGS84"'.format(img_in=directoryname + '/' + file, img_out=directoryname + '/' + 'prepared' + '/' + file)
        os.system(command_string)

    #clip
    listoffiles2 =os.listdir(directoryname + '/prepared')
    os.mkdir(directoryname + '/prepared/clipped', 0755)
    for file in listoffiles2:
        command_string2 = 'gdalwarp -te {bb1} {bb2} {bb3} {bb4} {img_in} {img_out} -of GTiff'.format(
            bb1=maskextent[0], bb2=maskextent[1], bb3=maskextent[2], bb4=maskextent[3], img_in=directoryname + '/prepared/' + file,
            img_out=directoryname + '/prepared/' + 'clipped/' + file)
        os.system(command_string2)


########################################################################################################################
#                                                                                                                      #
#                                                       __main__                                                       #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    directory = raw_input('type directory name: ')
    mask = raw_input('type mask file name: ')
    clipNreprojectDirectory(directory, mask)

