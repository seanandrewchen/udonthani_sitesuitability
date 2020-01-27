########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from osgeo import ogr
import os

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def convert2UTM(shapefile):
    utmzone = 48
    shapefileout = shapefile.split('.')[0] + '_UTM.shp'
    command_line = 'ogr2ogr -t_srs "+proj=utm +zone={utmzone} +datum=NAD83 +units=m" {outfile} {infile} '.format(
        utmzone=utmzone, outfile=shapefileout, infile=shapefile)
    os.system(command_line)
    return shapefileout

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def createBuffer(shapefileIn, bufferDistance):

    #Create buffer shapefile output file name
    outputBuffer = shapefileIn.split('.')[0] + '_buffer.shp'
    print outputBuffer

    #Convert input shapefile to UTM so that units are in meters
    utmShapefile = convert2UTM(shapefileIn)
    print utmShapefile

    #Open shapefile, get layer, and get driver information
    inputShape = ogr.Open(utmShapefile)
    inputLayer = inputShape.GetLayer()
    shapeDriver = ogr.GetDriverByName('ESRI Shapefile')
    spatialRef = inputLayer.GetSpatialRef()
    print spatialRef

    #Create new buffer shapefile and then create new layer for buffer
    outputBufferShape = shapeDriver.CreateDataSource(outputBuffer)
    bufferLayer = outputBufferShape.CreateLayer(outputBuffer, spatialRef, geom_type=ogr.wkbPolygon)
    featureDefinition = bufferLayer.GetLayerDefn()
    newSpatialRef = bufferLayer.GetSpatialRef()
    print newSpatialRef

    #Create new field for buffer shapefile and layer
    newField = ogr.FieldDefn('id', ogr.OFTInteger)
    bufferLayer.CreateField(newField)

    #Loop through each feature in input layer and add buffer as new feature in buffer layer as well as set ID value
    for feature in inputLayer:
        geometryInput = feature.GetGeometryRef()
        geometryBuffer = geometryInput.Buffer(float(bufferDistance))

        outFeature = ogr.Feature(featureDefinition)
        outFeature.SetGeometry(geometryBuffer)
        outFeature.SetField('id', 1)

        bufferLayer.CreateFeature(outFeature)

    return outputBuffer

########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == "__main__":
    inputShapefile = raw_input('type in input shapefile: ')
    bufferDistance = raw_input('type in buffer distance: ')

    createBuffer(inputShapefile, bufferDistance)