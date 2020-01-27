########################################################################################################################
#                                                                                                                      #
#                                                    Libraries                                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from floodFunction import floodModel, greenInfrastructure, traditionalInfrastructure

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

class geoObject:
    def __init__(self, name, urbanland, openland, to_connections, from_connections, detention_options, infiltration_options ):
        self.name = name
        self.urbanland = urbanland
        self.openland = openland
        self.to_connections = to_connections
        self.from_connections = from_connections
        self.detention_options = detention_options
        self.infiltration_options = infiltration_options

    def transferFloodWaters(self):


    def receiveFloodWaters(self):


    def detainFloodWaters(self):


    def waterInfiltration(self):


    def floodLevels(self):


    def waterSupply(self):


    def economicDamages(self):


    def economicGains(self):


########################################################################################################################
#                                                                                                                      #
#                                                     main()                                                           #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def main():

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    main()
