########################################################################################################################
#                                                                                                                      #
#                                                  Libraries                                                           #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from remoteSense import prepRaster, stackRaster, enhanceRaster
import os
import shutil

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def processNprepRasters(main_directory, mask, list_file_bases, band_1, band_2, band_3):
    # raster prep (clip and reproject)
    prepRaster.clipNreprojectDirectory(main_directory, mask)
    os.chdir(main_directory + '/prepared/clipped')

    # stack and enhance raster bands
    os.mkdir('stacked')
    os.mkdir('stacked/pansharpened')
    for base in list_file_bases:
        stackRaster.fullStack(base)
        stackRaster.stackBands(base, band_1, band_2, band_3)
        enhanceRaster.pansharpen(base + '_fullstacked.TIF', base + '_B8.TIF', base + '_fullstacked_pansharpened.TIF')
        enhanceRaster.pansharpen(base + '_B' + band_1 + band_2 + band_3 + '.TIF', base + '_B8.TIF',
                                 base + '_B' + band_1 + band_2 + band_3 + '_pansharpened.TIF')
        shutil.move(base + '_fullstacked.TIF', 'stacked')
        shutil.move(base + '_B' + band_1 + band_2 + band_3 + '.TIF', 'stacked')
        shutil.move(base + '_fullstacked_pansharpened.TIF', 'stacked/pansharpened')
        shutil.move(base + '_B' + band_1 + band_2 + band_3 + '_pansharpened.TIF', 'stacked/pansharpened')

def stackBands(main_directory, list_file_bases, band_1, band_2, band_3):

    os.chdir(main_directory)
    for base in list_file_bases:
        stackRaster.stackBands(base, band_1, band_2, band_3)

def pansharpenRaster(main_directory, list_file_bases, band_1, band_2, band_3):

    os.chdir(main_directory)
    for base in list_file_bases:
        enhanceRaster.pansharpen(base + '_B' + band_1 + band_2 + band_3 + '.TIF', base + '_B8.TIF', base + '_B' + band_1 + band_2 + band_3 + '_pansharpened.TIF')


########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    whichprocess = raw_input('type 1 to entirely process a directory. type 2 to stack three bands of your choosing. type 3 to pansharpen a directory: ')

    if whichprocess == str(1):
        main_directory = raw_input('type main directory name: ')
        mask = raw_input('type in mask file name: ')
        list_file_bases = raw_input('type file base names: ').split()
        band_1 = raw_input('type in first band for band combination: ')
        band_2 = raw_input('type in second band for band combination: ')
        band_3 = raw_input('type in third band for band combination: ')
        processNprepRasters(main_directory, mask, list_file_bases, band_1, band_2, band_3)
    elif whichprocess == str(2):
        main_directory = raw_input('type main directory name: ')
        list_file_bases = raw_input('type file base names: ').split()
        band_1 = raw_input('type in first band for band combination: ')
        band_2 = raw_input('type in second band for band combination: ')
        band_3 = raw_input('type in third band for band combination: ')
        stackBands(main_directory, list_file_bases, band_1, band_2, band_3)
    elif whichprocess == str(3):
        main_directory = raw_input('type main directory name: ')
        list_file_bases = raw_input('type file base names: ').split()
        band_1 = raw_input('type in first band for band combination: ')
        band_2 = raw_input('type in second band for band combination: ')
        band_3 = raw_input('type in third band for band combination: ')
        pansharpenRaster(main_directory, list_file_bases, band_1, band_2, band_3)






