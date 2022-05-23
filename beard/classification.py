# RUN COMMAND
# python classification.py train_images test_images checkpoints.txt

import cv2 as cv
from cv2 import CMP_GE
from matplotlib import pyplot as plt
from skimage.feature import graycomatrix, graycoprops
import sys
import os
from read import read_obj
from sklearn import preprocessing
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
import pickle
from sklearn.metrics import confusion_matrix

PATCH_SIZE = 32
GLCM_DIST = 5
RESIZE = 512



def obtain_patches_from_image(train_img, checkpoints, train_obj_path):

    train_img = cv.resize(train_img, (RESIZE, RESIZE))
    train_img = cv.cvtColor(train_img, cv.COLOR_BGR2GRAY)

    vertices, faces, textures, vertex_normals, parameter_space_vertices, lines = read_obj(train_obj_path)
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

    beard_patches = []
    for loc in beard_locations:
        beard_patches.append(train_img[loc[0]:loc[0] + PATCH_SIZE, loc[1]:loc[1] + PATCH_SIZE])

    return beard_patches



def obtain_images_and_labels(images_folder_path, images_folder_list, checkpoints):

    _patches = []
    _labels = []
    _images = []

    for directory_path in images_folder_list:

        dir_files = os.listdir(images_folder_path + '/' + directory_path)
        train_obj_path = ''
        train_img_path = ''

        if dir_files[0].split('.')[-1] == 'obj':
            train_obj_path = dir_files[0]
            train_img_path = dir_files[1]
        else:
            train_obj_path = dir_files[1]
            train_img_path = dir_files[0]
        
        label = train_img_path.split('.')[0].split('_')[-1]
        print(directory_path, label)

        train_img = cv.imread(images_folder_path + '/' + directory_path + '/' + train_img_path)
        beard_patches = obtain_patches_from_image(train_img, checkpoints, images_folder_path + '/' + directory_path + '/' + train_obj_path)

        _images.append(train_img)
        _patches.append(beard_patches)
        _labels.append(label)

    return _labels, _patches, _images



def feature_extractor(dataset):

    image_dataset = pd.DataFrame()
    for patches_id in range(len(dataset)):
        patches = dataset[patches_id]
        # print(patches)
        
        df = pd.DataFrame()
        for index in range(len(patches)):

            patch = patches[index]

            GLCM = graycomatrix(patch, distances=[GLCM_DIST], angles=[0], levels=256, symmetric=True, normed=True)
            df['Energy' + str(index)] = graycoprops(GLCM, 'energy')[0]
            df['Corr' + str(index)] = graycoprops(GLCM, 'correlation')[0]
            df['Diss_sim' + str(index)] = graycoprops(GLCM, 'dissimilarity')[0]
            df['Homogen' + str(index)] = graycoprops(GLCM, 'homogeneity')[0]
            df['Contrast' + str(index)] = graycoprops(GLCM, 'contrast')[0]

        # fig = plt.figure(figsize=(10, 10))
        # ax = fig.add_subplot(3,2,1)
        # ax.imshow(train_img, cmap=plt.cm.gray, vmin=0, vmax=255)

        # ax.set_xlabel('OG Image')
        # ax.set_xticks([])
        # ax.set_yticks([])
        # ax.axis('Image')

        # for i, patch in enumerate(patches):
        #     ax = fig.add_subplot(3, len(patches), len(patches)+i+1)
        #     ax.imshow(patch, cmap=plt.cm.gray, vmin=0, vmax=255)
        #     ax.set_xlabel('Beard %d' % (i+1))

        # fig.suptitle('Gray level co-occurrence matrix features', fontsize=14, y=1.05)
        # plt.tight_layout()
        # # plt.show()
        # plt.savefig('plots/' + str(patches_id) + '.png')
            
        image_dataset = pd.concat([image_dataset, df])
        
    return image_dataset



if __name__ == '__main__':

    train_images_folder_path = sys.argv[1]
    test_images_folder_path = sys.argv[2]
    checkpoints_path = sys.argv[3]

    # Obtain the indices if triangles serving as patches
    checkpoints = open(checkpoints_path, "r").read()
    checkpoints = list(checkpoints.split('\n'))
    print(checkpoints)

    # Plot the parameters obtained along with the image marked with patches

    train_images_folder_list = os.listdir(train_images_folder_path)
    test_images_folder_list = os.listdir(test_images_folder_path)

    train_labels, train_patches, train_images = obtain_images_and_labels(train_images_folder_path, train_images_folder_list, checkpoints)
    test_labels, test_patches, test_images = obtain_images_and_labels(test_images_folder_path, test_images_folder_list, checkpoints)

    le = preprocessing.LabelEncoder()
    le.fit(test_labels)
    test_labels_encoded = le.transform(test_labels)
    le.fit(train_labels)
    train_labels_encoded = le.transform(train_labels)

    x_train, y_train, x_test, y_test = train_patches, train_labels_encoded, test_patches, test_labels_encoded

    X_train_for_ML = feature_extractor(x_train)
    X_test_for_ML = feature_extractor(x_test)
    # print(X_train_for_ML)
    X_train_for_ML.to_csv('train_data.csv')

    # km = KMeans(n_clusters=2)
    # y_predicted = km.fit_predict(X_for_ML)
    # print(y_predicted)

    if not os.path.isdir('models/'):
        os.mkdir('models')

    # ML_model = RandomForestClassifier()
    # ML_model.fit(X_train_for_ML, y_train)
    # pickle.dump(ML_model, open('models/Random_forest', 'wb'))

    ML_model = svm.SVC(decision_function_shape='ovo')
    ML_model.fit(X_train_for_ML, y_train)
    pickle.dump(ML_model, open('models/SVM', 'wb'))

    print(ML_model.score(X_test_for_ML, y_test))
    y_pred = ML_model.predict(X_test_for_ML)
    print(y_test)
    print(y_pred)

    CM = confusion_matrix(y_test, y_pred)
    print(CM)