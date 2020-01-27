########################################################################################################################
#                                                                                                                      #
#                                                     Libraries                                                        #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from osgeo import gdal, gdal_array
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors
import osr

########################################################################################################################
#                                                                                                                      #
#                                                  ARRAY TO RASTER                                                     #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def array2raster(array, rasterin, rasterout):
    # Data from the original file
    [cols, rows] = array.shape
    trans = rasterin.GetGeoTransform()
    proj = rasterin.GetProjection()

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
#                                                   RANDOMFOREST                                                       #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def randomforestSupervisedClassify(classifying_raster, roi_raster):

    ####################################################################################################################
    #                                      READ IN RASTER AND ROI IMAGES                                               #
    ####################################################################################################################
    img_ds = gdal.Open(classifying_raster, gdal.GA_ReadOnly)
    roi_ds = gdal.Open(roi_raster, gdal.GA_ReadOnly)
    img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount),
                   gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))
    for b in range(img.shape[2]):
        img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()
    roi = roi_ds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
    ####################################################################################################################



    ####################################################################################################################
    #                                           TRAINING DATA INFORMATION                                              #
    ####################################################################################################################
    # Find how many non-zero entries we have -- i.e. how many training data samples?
    n_samples = sum(roi > 0)
    print('We have {n} samples'.format(n=n_samples))

    # What are our classification labels?
    labels = np.unique(roi[roi > 0])
    print('The training data include {n} classes: {classes}'.format(n=labels.size,
                                                                    classes=labels))
    ####################################################################################################################



    ####################################################################################################################
    #                                                 PAIR Y WITH X                                                    #
    ####################################################################################################################
    #          We will need a "X" matrix containing our features, and a "y" array containing our labels                #
    #                                      These will have n_samples rows                                              #
    ####################################################################################################################
    X = img[roi > 0, :]  # include 8th band, which is Fmask, for now
    y = roi[roi > 0]

    print('Our X matrix is sized: {sz}'.format(sz=X.shape))
    print('Our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                                        MASKING HIGH ALTITUDE CIRRUS CLOUDS                                       #
    ####################################################################################################################
    # Mask out clouds, cloud shadows, and snow using Fmask
    #clear = X[:, 7] #<= 1

    #X = X[clear, :7]  # we can ditch the Fmask band now
    #y = y[clear]

    #print('After masking, our X matrix is sized: {sz}'.format(sz=X.shape))
    #print('After masking, our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                               CREATE CLASSIFIER MODEL AND FIT TO TRAINING DATA                                   #
    ####################################################################################################################
    # Initialize our model with 50 trees
    rf = RandomForestClassifier(n_estimators=50, oob_score=True)

    # Fit our model to training data
    rf.fit(X, y)

    # To save memory delete variables no longer being used
    del roi
    del n_samples, labels
    del roi_ds, img_ds

    ####################################################################################################################



    ####################################################################################################################
    #                                          RANDOM FOREST DIAGNOSTICS                                               #
    ####################################################################################################################
    print('Our OOB prediction of accuracy is: {oob}%'.format(oob=rf.oob_score_ * 100))
    bands = ['a', 'b', 'c']

    for b, imp in zip(bands, rf.feature_importances_):
        print('Band {b} importance: {imp}'.format(b=b, imp=imp))

    # Setup a dataframe -- just like R
    df = pd.DataFrame()
    df['truth'] = y
    df['predict'] = rf.predict(X)

    # Cross-tabulate predictions
    print(pd.crosstab(df['truth'], df['predict'], margins=True))
    ####################################################################################################################



    ####################################################################################################################
    #                                      PREDICT THE REST OF THE IMAGE                                               #
    ####################################################################################################################
    # Take our full image, ignore the Fmask band, and reshape into long array for classification
    new_shape = (img.shape[0] * img.shape[1], img.shape[2])

    img_as_array = img[:, :, :].reshape(new_shape)
    print('Reshaped from {o} to {n}'.format(o=img.shape,
                                            n=img_as_array.shape))

    # To save memory delete variables no longer being used
    del X, y

    # Now predict for each pixel
    class_prediction = rf.predict(img_as_array)

    # Reshape our classification map
    class_prediction = class_prediction.reshape(img[:, :, 0].shape)
    ####################################################################################################################


    ####################################################################################################################
    #                                                    RASTERIZE                                                     #
    ####################################################################################################################
    def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):

        cols = array.shape[1]
        rows = array.shape[0]
        originX = rasterOrigin[0]
        originY = rasterOrigin[1]

        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()

    rastero = [102.547625999999994, 17.576460999999998]
    pixelwd = [0.000138439040640, -0.000138469003690]
    array2raster(classifying_raster.split('.')[0] + '_classified.TIF', rastero, pixelwd[0], pixelwd[1], class_prediction)

    del class_prediction
    ####################################################################################################################


########################################################################################################################
#                                                                                                                      #
#                                                GRADIENT BOOSTING                                                     #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def gradientboostingSupervisedClassify(classifying_raster, roi_raster):

    ####################################################################################################################
    #                                      READ IN RASTER AND ROI IMAGES                                               #
    ####################################################################################################################
    img_ds = gdal.Open(classifying_raster, gdal.GA_ReadOnly)
    roi_ds = gdal.Open(roi_raster, gdal.GA_ReadOnly)
    img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount),
                   gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))
    for b in range(img.shape[2]):
        img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()
    roi = roi_ds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
    ####################################################################################################################



    ####################################################################################################################
    #                                           TRAINING DATA INFORMATION                                              #
    ####################################################################################################################
    # Find how many non-zero entries we have -- i.e. how many training data samples?
    n_samples = sum(roi > 0)
    print('We have {n} samples'.format(n=n_samples))

    # What are our classification labels?
    labels = np.unique(roi[roi > 0])
    print('The training data include {n} classes: {classes}'.format(n=labels.size,
                                                                    classes=labels))
    ####################################################################################################################



    ####################################################################################################################
    #                                                 PAIR Y WITH X                                                    #
    ####################################################################################################################
    #          We will need a "X" matrix containing our features, and a "y" array containing our labels                #
    #                                      These will have n_samples rows                                              #
    ####################################################################################################################
    X = img[roi > 0, :]  # include 8th band, which is Fmask, for now
    y = roi[roi > 0]

    print('Our X matrix is sized: {sz}'.format(sz=X.shape))
    print('Our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                                        MASKING HIGH ALTITUDE CIRRUS CLOUDS                                       #
    ####################################################################################################################
    # Mask out clouds, cloud shadows, and snow using Fmask
    #clear = X[:, 7] #<= 1

    #X = X[clear, :7]  # we can ditch the Fmask band now
    #y = y[clear]

    #print('After masking, our X matrix is sized: {sz}'.format(sz=X.shape))
    #print('After masking, our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                               CREATE CLASSIFIER MODEL AND FIT TO TRAINING DATA                                   #
    ####################################################################################################################
    # Initialize our model with 50 trees
    rf = GradientBoostingClassifier(n_estimators=300, min_samples_leaf=1, min_samples_split=4, max_depth=4, max_features = 'auto', learning_rate = 0.8, subsample = 1, random_state = None, warm_start = True)
    # Fit our model to training data
    rf.fit(X, y)

    # To save memory delete variables no longer being used
    del roi
    del n_samples, labels
    del img_ds, roi_ds

    ####################################################################################################################



    ####################################################################################################################
    #                                               DIAGNOSTICS                                                        #
    ####################################################################################################################
    bands = [7, 6, 4]
    for b, imp in zip(bands, rf.feature_importances_):
        print('Band {b} importance: {imp}'.format(b=b, imp=imp))

    # Setup a dataframe -- just like R
    df = pd.DataFrame()
    df['truth'] = y
    df['predict'] = rf.predict(X)

    # Cross-tabulate predictions
    print(pd.crosstab(df['truth'], df['predict'], margins=True))
    ####################################################################################################################



    ####################################################################################################################
    #                                      PREDICT THE REST OF THE IMAGE                                               #
    ####################################################################################################################
    # Take our full image, ignore the Fmask band, and reshape into long array for classification
    new_shape = (img.shape[0] * img.shape[1], img.shape[2])

    img_as_array = img[:, :, :].reshape(new_shape)
    print('Reshaped from {o} to {n}'.format(o=img.shape,
                                            n=img_as_array.shape))

    # To save memory delete variables no longer being used
    del X, y

    # Now predict for each pixel
    class_prediction = rf.predict(img_as_array)

    # Reshape our classification map
    class_prediction = class_prediction.reshape(img[:, :, 0].shape)
    ####################################################################################################################



    ####################################################################################################################
    #                                             VISUALIZE AND PLOT                                                   #
    ####################################################################################################################

    n = class_prediction.max()
    # Next setup a colormap for our map
    colorsd = dict((
        (0, (0, 0, 0, 255)),  # Nodata
        (1, (0, 242, 28, 28)),  # Urban
        (2, (0, 38, 229, 76)),  # Forest
        (3, (0, 10, 48, 235)),  # Water
        (4, (0, 38, 229, 76)),  # Agriculture
    ))
    # Put 0 - 255 as float 0 - 1
    for k in colorsd:
        v = colorsd[k]
        _v = [_v / 255.0 for _v in v]
        colorsd[k] = _v

    index_colors = [colorsd[key] if key in colorsd else
                    (255, 255, 255, 0) for key in range(1, n + 1)]
    cmap = matplotlib.colors.ListedColormap(index_colors, 'Classification', n)

    plt.imshow(class_prediction, cmap=cmap, interpolation='none')
    plt.show()
    ####################################################################################################################



    ####################################################################################################################
    #                                                    RASTERIZE                                                     #
    ####################################################################################################################
    def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):

        cols = array.shape[1]
        rows = array.shape[0]
        originX = rasterOrigin[0]
        originY = rasterOrigin[1]

        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()

    rastero = [102.547625999999994, 17.576460999999998]
    pixelwd = [0.000138439040640, -0.000138469003690]
    array2raster(classifying_raster.split('.')[0] + '_classified.TIF', rastero, pixelwd[0], pixelwd[1], class_prediction)

    del class_prediction
    ####################################################################################################################


########################################################################################################################
#                                                                                                                      #
#                                                    ADA BOOSTING                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def adaboostingSupervisedClassify(classifying_raster, roi_raster):

    ####################################################################################################################
    #                                      READ IN RASTER AND ROI IMAGES                                               #
    ####################################################################################################################
    img_ds = gdal.Open(classifying_raster, gdal.GA_ReadOnly)
    roi_ds = gdal.Open(roi_raster, gdal.GA_ReadOnly)
    img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount),
                   gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))
    for b in range(img.shape[2]):
        img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()
    roi = roi_ds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
    ####################################################################################################################



    ####################################################################################################################
    #                                           TRAINING DATA INFORMATION                                              #
    ####################################################################################################################
    # Find how many non-zero entries we have -- i.e. how many training data samples?
    n_samples = sum(roi > 0)
    print('We have {n} samples'.format(n=n_samples))

    # What are our classification labels?
    labels = np.unique(roi[roi > 0])
    print('The training data include {n} classes: {classes}'.format(n=labels.size,
                                                                    classes=labels))
    ####################################################################################################################



    ####################################################################################################################
    #                                                 PAIR Y WITH X                                                    #
    ####################################################################################################################
    #          We will need a "X" matrix containing our features, and a "y" array containing our labels                #
    #                                      These will have n_samples rows                                              #
    ####################################################################################################################
    X = img[roi > 0, :]  # include 8th band, which is Fmask, for now
    y = roi[roi > 0]

    print('Our X matrix is sized: {sz}'.format(sz=X.shape))
    print('Our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                                        MASKING HIGH ALTITUDE CIRRUS CLOUDS                                       #
    ####################################################################################################################
    # Mask out clouds, cloud shadows, and snow using Fmask
    # clear = X[:, 7] #<= 1

    # X = X[clear, :7]  # we can ditch the Fmask band now
    # y = y[clear]

    # print('After masking, our X matrix is sized: {sz}'.format(sz=X.shape))
    # print('After masking, our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                               CREATE CLASSIFIER MODEL AND FIT TO TRAINING DATA                                   #
    ####################################################################################################################
    # Initialize our model with 50 trees
    rf = AdaBoostClassifier(n_estimators=100)

    # Fit our model to training data
    rf.fit(X, y)

    # To save memory delete variables no longer being used
    del roi
    del n_samples, labels
    del img_ds, roi_ds

    ####################################################################################################################



    ####################################################################################################################
    #                                               DIAGNOSTICS                                                        #
    ####################################################################################################################
    bands = [7, 6, 4]
    for b, imp in zip(bands, rf.feature_importances_):
        print('Band {b} importance: {imp}'.format(b=b, imp=imp))

    # Setup a dataframe -- just like R
    df = pd.DataFrame()
    df['truth'] = y
    df['predict'] = rf.predict(X)

    # Cross-tabulate predictions
    print(pd.crosstab(df['truth'], df['predict'], margins=True))
    ####################################################################################################################



    ####################################################################################################################
    #                                      PREDICT THE REST OF THE IMAGE                                               #
    ####################################################################################################################
    # Take our full image, ignore the Fmask band, and reshape into long array for classification
    new_shape = (img.shape[0] * img.shape[1], img.shape[2])

    img_as_array = img[:, :, :].reshape(new_shape)
    print('Reshaped from {o} to {n}'.format(o=img.shape,
                                            n=img_as_array.shape))

    # To save memory delete variables no longer being used
    del X, y

    # Now predict for each pixel
    class_prediction = rf.predict(img_as_array)

    # Reshape our classification map
    class_prediction = class_prediction.reshape(img[:, :, 0].shape)
    ####################################################################################################################



    ####################################################################################################################
    #                                             VISUALIZE AND PLOT                                                   #
    ####################################################################################################################

    n = class_prediction.max()
    # Next setup a colormap for our map
    colorsd = dict((
        (0, (0, 0, 0, 255)),  # Nodata
        (1, (0, 242, 28, 28)),  # Urban
        (2, (0, 38, 229, 76)),  # Forest
        (3, (0, 10, 48, 235)),  # Water
        (4, (0, 38, 229, 76)),  # Agriculture
    ))
    # Put 0 - 255 as float 0 - 1
    for k in colorsd:
        v = colorsd[k]
        _v = [_v / 255.0 for _v in v]
        colorsd[k] = _v

    index_colors = [colorsd[key] if key in colorsd else
                    (255, 255, 255, 0) for key in range(1, n + 1)]
    cmap = matplotlib.colors.ListedColormap(index_colors, 'Classification', n)

    plt.imshow(class_prediction, cmap=cmap, interpolation='none')
    plt.show()

    ####################################################################################################################



    ####################################################################################################################
    #                                                    RASTERIZE                                                     #
    ####################################################################################################################
    def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):

        cols = array.shape[1]
        rows = array.shape[0]
        originX = rasterOrigin[0]
        originY = rasterOrigin[1]

        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()

    rastero = [102.547625999999994, 17.576460999999998]
    pixelwd = [0.000138439040640, -0.000138469003690]
    array2raster(classifying_raster.split('.')[0] + '_classified.TIF', rastero, pixelwd[0], pixelwd[1], class_prediction)


    del class_prediction
    ####################################################################################################################


########################################################################################################################
#                                                                                                                      #
#                                                      EXTRA TREES                                                     #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

def extratreesSupervisedClassify(classifying_raster, roi_raster):

    ####################################################################################################################
    #                                      READ IN RASTER AND ROI IMAGES                                               #
    ####################################################################################################################
    img_ds = gdal.Open(classifying_raster, gdal.GA_ReadOnly)
    roi_ds = gdal.Open(roi_raster, gdal.GA_ReadOnly)
    img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount),
                   gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))
    for b in range(img.shape[2]):
        img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()
    roi = roi_ds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
    ####################################################################################################################



    ####################################################################################################################
    #                                           TRAINING DATA INFORMATION                                              #
    ####################################################################################################################
    # Find how many non-zero entries we have -- i.e. how many training data samples?
    n_samples = sum(roi > 0)
    print('We have {n} samples'.format(n=n_samples))

    # What are our classification labels?
    labels = np.unique(roi[roi > 0])
    print('The training data include {n} classes: {classes}'.format(n=labels.size,
                                                                    classes=labels))
    ####################################################################################################################



    ####################################################################################################################
    #                                                 PAIR Y WITH X                                                    #
    ####################################################################################################################
    #          We will need a "X" matrix containing our features, and a "y" array containing our labels                #
    #                                      These will have n_samples rows                                              #
    ####################################################################################################################
    X = img[roi > 0, :]  # include 8th band, which is Fmask, for now
    y = roi[roi > 0]

    print('Our X matrix is sized: {sz}'.format(sz=X.shape))
    print('Our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                                        MASKING HIGH ALTITUDE CIRRUS CLOUDS                                       #
    ####################################################################################################################
    # Mask out clouds, cloud shadows, and snow using Fmask
    #clear = X[:, 7] #<= 1

    #X = X[clear, :7]  # we can ditch the Fmask band now
    #y = y[clear]

    #print('After masking, our X matrix is sized: {sz}'.format(sz=X.shape))
    #print('After masking, our y array is sized: {sz}'.format(sz=y.shape))
    ####################################################################################################################



    ####################################################################################################################
    #                               CREATE CLASSIFIER MODEL AND FIT TO TRAINING DATA                                   #
    ####################################################################################################################
    # Initialize our model with 50 trees
    rf = ExtraTreesClassifier(n_estimators=100, max_depth=None, min_samples_split=1, random_state=0)

    # Fit our model to training data
    rf.fit(X, y)

    # To save memory delete variables no longer being used
    del roi
    del n_samples, labels
    del img_ds, roi_ds

    ####################################################################################################################



    ####################################################################################################################
    #                                          RANDOM FOREST DIAGNOSTICS                                               #
    ####################################################################################################################
    bands = [7, 6, 4]
    for b, imp in zip(bands, rf.feature_importances_):
        print('Band {b} importance: {imp}'.format(b=b, imp=imp))

    # Setup a dataframe -- just like R
    df = pd.DataFrame()
    df['truth'] = y
    df['predict'] = rf.predict(X)

    # Cross-tabulate predictions
    print(pd.crosstab(df['truth'], df['predict'], margins=True))
    ####################################################################################################################



    ####################################################################################################################
    #                                      PREDICT THE REST OF THE IMAGE                                               #
    ####################################################################################################################
    # Take our full image, ignore the Fmask band, and reshape into long array for classification
    new_shape = (img.shape[0] * img.shape[1], img.shape[2])

    img_as_array = img[:, :, :].reshape(new_shape)
    print('Reshaped from {o} to {n}'.format(o=img.shape,
                                            n=img_as_array.shape))

    # To save memory delete variables no longer being used
    del X, y

    # Now predict for each pixel
    class_prediction = rf.predict(img_as_array)

    # Reshape our classification map
    class_prediction = class_prediction.reshape(img[:, :, 0].shape)
    ####################################################################################################################



    ####################################################################################################################
    #                                             VISUALIZE AND PLOT                                                   #
    ####################################################################################################################

    n = class_prediction.max()
    # Next setup a colormap for our map
    colorsd = dict((
        (0, (0, 0, 0, 255)),  # Nodata
        (1, (0, 242, 28, 28)),  # Urban
        (2, (0, 38, 229, 76)),  # Forest
        (3, (0, 10, 48, 235)),  # Water
        (4, (0, 38, 229, 76)),  # Agriculture
    ))
    # Put 0 - 255 as float 0 - 1
    for k in colorsd:
        v = colorsd[k]
        _v = [_v / 255.0 for _v in v]
        colorsd[k] = _v

    index_colors = [colorsd[key] if key in colorsd else
                    (255, 255, 255, 0) for key in range(1, n + 1)]
    cmap = matplotlib.colors.ListedColormap(index_colors, 'Classification', n)

    plt.imshow(class_prediction, cmap=cmap, interpolation='none')
    plt.show()
    ####################################################################################################################



    ####################################################################################################################
    #                                                    RASTERIZE                                                     #
    ####################################################################################################################
    def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):

        cols = array.shape[1]
        rows = array.shape[0]
        originX = rasterOrigin[0]
        originY = rasterOrigin[1]

        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()

    rastero = [102.547625999999994, 17.576460999999998]
    pixelwd = [0.000138439040640, -0.000138469003690]
    array2raster(classifying_raster.split('.')[0] + '_classified.TIF', rastero, pixelwd[0], pixelwd[1], class_prediction)

    del class_prediction
    ####################################################################################################################


########################################################################################################################
#                                                                                                                      #
#                                                    __main__                                                          #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

if __name__ == '__main__':
    classifyingraster = raw_input('Please type in the raster file name to be classified: ')
    roiraster = raw_input('Please type in the ROI raster file name: ')

    whichmethod = raw_input('Please choose a Ensemble Learning method. Enter 1 for Random Forest, 2 for Gradient Boosting, 3 for ADA Boosting or 4 for Extra Trees: ')

    if int(whichmethod) == 1:
        randomforestSupervisedClassify(classifyingraster, roiraster)
    elif int(whichmethod) == 2:
        gradientboostingSupervisedClassify(classifyingraster, roiraster)
    elif int(whichmethod) == 3:
        adaboostingSupervisedClassify(classifyingraster, roiraster)
    elif int(whichmethod) == 4:
        extratreesSupervisedClassify(classifyingraster, roiraster)
