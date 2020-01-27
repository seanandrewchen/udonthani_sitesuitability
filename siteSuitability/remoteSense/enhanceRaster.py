########################################################################################################################
#                                                                                                                      #
#                                                Load Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import os
#from pymasker import landsatmasker, confidence

########################################################################################################################
#                                                                                                                      #
#                                                   enhanceRaster                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def pansharpen(filein, panchromatic, fileout):
        os.system('gdal_pansharpen.py ' + panchromatic + ' ' + filein + ' ' + fileout)


#def cloudMask(bqa_band):
    #masker = landsatmasker(bqa_band)
    #mask = masker.getcloudmask(confidence.high, cirrus=True, cumulative=True)
    #masker.savetif(mask, bqa_band.split()[0] + '_mask.TIF')


########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    pansharpen(raw_input('type in file in name: '), raw_input('type in panchromatic image name: '), raw_input('type in file out name: '))
    #cloudMask(raw_input('type in bqa band file: '))


