# RUN COMMAND
# python main.py face.png face.obj facial_hair_full.txt checkpoints.txt models/SVM

import sys
import os
import cv2 as cv
import math
import numpy as np
from read import read_obj
from sklearn.cluster import KMeans
import pickle
from classification import obtain_patches_from_image, feature_extractor

CLUSTER_SIZE = 3

def visualize_Dominant_colors(cluster, C_centroids):

    C_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (C_hist, _) = np.histogram(cluster.labels_, bins = C_labels)
    C_hist = C_hist.astype("float")
    C_hist /= C_hist.sum()
    img_colors = ([(percent, color) for (percent, color) in zip(C_hist, C_centroids)])

    return img_colors


def findColor(src_img):

    src_image_RGB = cv.cvtColor(src_img, cv.COLOR_BGR2RGB)
    reshape_img = src_image_RGB.reshape((src_image_RGB.shape[0] * src_image_RGB.shape[1], 3))
    KM_cluster = KMeans(n_clusters=CLUSTER_SIZE).fit(reshape_img)
    
    image_colors = visualize_Dominant_colors(KM_cluster, KM_cluster.cluster_centers_)

    return image_colors


def color_difference(C1, C2):

    dx = (C1[0] - C2[0])**2
    dy = (C1[1] - C2[1])**2
    dz = (C1[2] - C2[2])**2

    ratio = (dx + dy + dz) / (C2[0]**2 + C2[1]**2 + C2[2]**2)

    return math.sqrt(ratio)


def beard_mask_builder(src_obj_path, src_img_path, facial_hair_txt):

    src_img = cv.imread(src_img_path)
    OG_size = src_img.shape

    vertices, faces, textures, vertex_normals, parameter_space_vertices, lines = read_obj(src_obj_path)
    blank = np.zeros((src_img.shape[0], src_img.shape[1], 3), dtype = np.uint8)
    white = [1, 1, 1]

    triangles = []
    for F in faces['vt']:

        V1 = (int(textures[F[0]-1][0] * src_img.shape[1]), int((1-textures[F[0]-1][1]) * src_img.shape[0]))
        V2 = (int(textures[F[1]-1][0] * src_img.shape[1]), int((1-textures[F[1]-1][1]) * src_img.shape[0]))
        V3 = (int(textures[F[2]-1][0] * src_img.shape[1]), int((1-textures[F[2]-1][1]) * src_img.shape[0]))
        triangles.append([V1, V2, V3])

    facial_hair = open(facial_hair_txt, "r").read()
    facial_hair = list(facial_hair.split('\n'))
    list_of_beard_triangles = []
    
    for hair in facial_hair:
        list_of_beard_triangles.append(int(hair))
        list_of_beard_triangles.append(int(hair)+1)

    for index in  list_of_beard_triangles:

        T = triangles[index]
        tri = np.float32([[[T[0][0], T[0][1]], [T[1][0], T[1][1]], [T[2][0], T[2][1]]]])
        rect = cv.boundingRect(tri)
        src_img_Cropped = src_img[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
        # src_img_Cropped_small = cv.resize(src_img_Cropped, (64, 64))
            
        # image_colors = findColor(src_img_Cropped)
        # dom_color = max(image_colors,key=lambda item:item[0])[1]
        # color_diff = color_difference(dom_color, ref_color)

        tri_Cropped = []
        for i in range(0, 3):
            tri_Cropped.append(((tri[0][i][0] - rect[0]),(tri[0][i][1] - rect[1])))

        # beard_region = int(color_diff * 255) * np.ones((src_img_Cropped.shape[0], src_img_Cropped.shape[1], 3), np.uint8)
        mask = np.zeros((rect[3], rect[2], 3), dtype = np.float32)
        cv.fillConvexPoly(mask, np.int32(tri_Cropped), white, 16, 0)

        src_img_Cropped = src_img_Cropped * mask

        blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] = blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] * ( white - mask )
        blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] = blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] + src_img_Cropped

    # blank = cv.blur(blank, (10, 10))
    blank = cv.resize(blank, (OG_size[1], OG_size[0]))
    return blank


if __name__ == '__main__':

    src_img_path = sys.argv[1]
    src_obj_path = sys.argv[2]
    facial_hair_txt = sys.argv[3]
    checkpoints_path = sys.argv[4]
    ML_model_path = sys.argv[5]

    final_img_path = os.path.splitext(src_img_path)[0]
    final_img_path = final_img_path + 'beard' + '.png'

    src_img = cv.imread(src_img_path)
    checkpoints = open(checkpoints_path, "r").read()
    checkpoints = list(checkpoints.split('\n'))
    print(checkpoints)

    ML_model = pickle.load(open(ML_model_path, 'rb'))
    patches = obtain_patches_from_image(src_img, checkpoints, src_obj_path)
    X_test_for_ML = feature_extractor([patches])

    print(X_test_for_ML)
    y_pred = ML_model.predict(X_test_for_ML)
    print(y_pred)

    if y_pred[0] == 1:

        final_image_beard = beard_mask_builder(src_obj_path, src_img_path, facial_hair_txt)
        cv.imwrite(final_img_path, final_image_beard)
        cv.imshow('Full Beard Mask', final_image_beard)
        cv.waitKey(0)
        cv.destroyAllWindows()


# Change to grayscale
# Two outputs:
# Beard Triangles
# All Triangles

# Add new faces for beard
# Generate a metric with values 0/1
# 0: Edge beard
# 1: Full beard
# Check out GLCM