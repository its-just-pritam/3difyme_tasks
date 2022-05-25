'''
RUN COMMAND:
python classification.py train_images test_images checkpoints.txt
'''

import cv2 as cv
from skimage.feature import graycomatrix, graycoprops
import sys
import os
from read import read_obj
from sklearn import preprocessing
import pandas as pd
from sklearn import svm
import pickle
from sklearn.metrics import confusion_matrix

PATCH_SIZE = 32
GLCM_DIST = 5
RESIZE = 512


'''
From an image, obtain a set of patches as per checkpoints

INPUT:

1. Input image
2. Checkpoints
3. Input obj file

OUTPUT:

1. Patches corresponding to the input image
'''

def obtain_patches_from_image(train_img, checkpoints, train_obj):

    # Resize and convert image to gray scale
    train_img = cv.resize(train_img, (RESIZE, RESIZE))
    train_img = cv.cvtColor(train_img, cv.COLOR_BGR2GRAY)

    # Obtain lists of obj parameters
    vertices, faces, textures, vertex_normals, parameter_space_vertices, lines = read_obj(train_obj)

    # Create and populate the vertices of each triangle in a list
    triangles = []
    for F in faces['vt']:

        V1 = (int(textures[F[0]-1][0] * train_img.shape[1]), int((1-textures[F[0]-1][1]) * train_img.shape[0]))
        V2 = (int(textures[F[1]-1][0] * train_img.shape[1]), int((1-textures[F[1]-1][1]) * train_img.shape[0]))
        V3 = (int(textures[F[2]-1][0] * train_img.shape[1]), int((1-textures[F[2]-1][1]) * train_img.shape[0]))
        triangles.append([V1, V2, V3])

    # Obtain the co-ordinates of faces and bears patches
    beard_locations = []
    for i in range(len(checkpoints)):
            
        index = int(checkpoints[i])
        x1 = ( triangles[index][0][0] + triangles[index][1][0] + triangles[index][2][0] ) // 3
        y1 = ( triangles[index][0][1] + triangles[index][1][1] + triangles[index][2][1] ) // 3 
        x2 = ( triangles[index+1][0][0] + triangles[index+1][1][0] + triangles[index+1][2][0] ) // 3
        y2 = ( triangles[index+1][0][1] + triangles[index+1][1][1] + triangles[index+1][2][1] ) // 3
            
        beard_locations.append((y1,x1))
        beard_locations.append((y2,x2))

    # Create and populate the patches of each checkpoint in a list
    beard_patches = []
    for loc in beard_locations:
        beard_patches.append(train_img[loc[0]:loc[0] + PATCH_SIZE, loc[1]:loc[1] + PATCH_SIZE])

    return beard_patches


'''
From a list of image paths, obtain patches and classsification labels.

INPUT:

1. <training_data_directory>
2. A list containing <individual_directory>
3. Checkpoints

OUTPUT:

1. A list of classsification labels
2. A list of patches corresponding to each image
3. A list of images
'''

def obtain_patches_and_labels(images_folder_path, images_folder_list, checkpoints):

    _patches = []
    _labels = []
    _images = []

    for directory_path in images_folder_list:

        dir_files = os.listdir(images_folder_path + '/' + directory_path)
        train_obj_path = ''
        train_img_path = ''

        # Obtain the train_obj_path and train_img_path.
        if dir_files[0].split('.')[-1] == 'obj':
            train_obj_path = dir_files[0]
            train_img_path = dir_files[1]
        else:
            train_obj_path = dir_files[1]
            train_img_path = dir_files[0]
        
        # Obtain the label from image path
        label = train_img_path.split('.')[0].split('_')[-1]
        print(directory_path, label)

        train_img = cv.imread(images_folder_path + '/' + directory_path + '/' + train_img_path)
        file = open(train_obj_path,'r')
        input_obj = file.readlines()
        file.close()

        # Obtain patches for the image
        beard_patches = obtain_patches_from_image(train_img, checkpoints, input_obj)

        _images.append(train_img)
        _patches.append(beard_patches)
        _labels.append(label)

    return _labels, _patches, _images


'''
Extracts features from each patch given a list of patches

INPUT:

1. List of patches

OUTPUT:

1. Dataset of image features
'''

def feature_extractor(dataset):

    image_dataset = pd.DataFrame()

    for patches_id in range(len(dataset)):
        patches = dataset[patches_id]
        # print(patches)
        
        df = pd.DataFrame()
        for index in range(len(patches)):

            patch = patches[index]

            # Apply GLCM texture detection on a patch
            GLCM = graycomatrix(patch, distances=[GLCM_DIST], angles=[0], levels=256, symmetric=True, normed=True)
            df['Energy' + str(index)] = graycoprops(GLCM, 'energy')[0]
            df['Corr' + str(index)] = graycoprops(GLCM, 'correlation')[0]
            df['Diss_sim' + str(index)] = graycoprops(GLCM, 'dissimilarity')[0]
            df['Homogen' + str(index)] = graycoprops(GLCM, 'homogeneity')[0]
            df['Contrast' + str(index)] = graycoprops(GLCM, 'contrast')[0]
            
        image_dataset = pd.concat([image_dataset, df])
        
    return image_dataset


'''
Trains on an SVM classifier model and tests it

INPUT:

1. <training_data_directory>
2. <testing_data_directory>
3. Path to a file contining checkpoints, i.e. indices of all those faces where beard texture is obtained.

OUTPUT:

1. ML_model
'''

def obtain_and_test_ML_model(train_images_folder_path, test_images_folder_path, checkpoints_path):

    # Obtain the indices of triangles serving as patches
    checkpoints = open(checkpoints_path, "r").read()
    checkpoints = list(checkpoints.split('\n'))
    print(checkpoints)

    train_images_folder_list = os.listdir(train_images_folder_path)
    test_images_folder_list = os.listdir(test_images_folder_path)

    # Obtain patches and classsification labels for train and test samples
    train_labels, train_patches, train_images = obtain_patches_and_labels(train_images_folder_path, train_images_folder_list, checkpoints)
    test_labels, test_patches, test_images = obtain_patches_and_labels(test_images_folder_path, test_images_folder_list, checkpoints)

    # Transform labels as classifiaction parameters
    le = preprocessing.LabelEncoder()
    le.fit(test_labels)
    test_labels_encoded = le.transform(test_labels)
    le.fit(train_labels)
    train_labels_encoded = le.transform(train_labels)

    x_train, y_train, x_test, y_test = train_patches, train_labels_encoded, test_patches, test_labels_encoded

    # Obtain features from train and test samples
    X_train_for_ML = feature_extractor(x_train)
    X_test_for_ML = feature_extractor(x_test)

    # Create a models directory to store trained models
    if not os.path.isdir('models/'):
        os.mkdir('models')

    # Train and export the ML model.
    ML_model = svm.SVC(decision_function_shape='ovo')
    ML_model.fit(X_train_for_ML, y_train)
    pickle.dump(ML_model, open('models/SVM', 'wb'))

    # test the ML model.
    print(ML_model.score(X_test_for_ML, y_test))
    y_pred = ML_model.predict(X_test_for_ML)
    print(y_test)
    print(y_pred)

    CM = confusion_matrix(y_test, y_pred)
    print(CM)

    return ML_model


'''
Main function takes 3 arguments from command line:

1. Path of the directory containing images and obj files for training, i.e. <training_data_directory>
The directory config must follow this flow:
<training_data_directory> ___
                            |___ <individual_directory> ___
                                                           |___ <image_file>
                                                           |___ <obj_file>

2. Path of the directory containing images and obj files for testing, i.e. <testing_data_directory>
The directory config must follow this flow:
<testing_data_directory> ___
                            |___ <individual_directory> ___
                                                           |___ <image_file>
                                                           |___ <obj_file>

3. Path to a file contining checkpoints, i.e. indices of all those faces where beard texture is obtained.
'''

if __name__ == '__main__':

    train_images_folder_path = sys.argv[1]
    test_images_folder_path = sys.argv[2]
    checkpoints_path = sys.argv[3]

    ML_model = obtain_and_test_ML_model(train_images_folder_path, test_images_folder_path, checkpoints_path)
