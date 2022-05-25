'''
RUN COMMAND:
python main.py test_images facial_hair_full.txt checkpoints.txt models/SVM
'''

import sys
import os
import cv2 as cv
import numpy as np
import pickle
import ckwrap
from classification import obtain_patches_from_image, feature_extractor
from read import read_obj


'''
Applies mask to beard region

INPUT:

1. Image of beard region

OUTPUT:

1. beard_mask
'''

def get_facial_hair_mask(colored_face_mat):

    mat = cv.resize(colored_face_mat, (256, 256))
    
    mat = mat & np.stack((mat[..., 3],) * 4, axis=-1)
    gray = cv.cvtColor(mat, cv.COLOR_BGR2GRAY)

    # Choose only opaque pixels
    opaque = mat[..., 3] > 127
    opaque_idx = np.where(opaque)
    opaque_pixels = gray[opaque_idx]
    vectors = opaque_pixels.reshape(-1)

    km = ckwrap.ckmeans(vectors, 2)
    cluster_mask = np.zeros((256, 256), dtype=np.uint8)
    cluster_mask[opaque_idx] = km.labels
    cluster_mask *= 255
    cluster_mask = cv.bitwise_not(cluster_mask)

    # Erode the edges
    opaque_mask = opaque.astype(np.uint8)*255
    
    # Ignore transparent values 
    cluster_mask = cluster_mask & opaque_mask

    # Make it 4 channels and resize to original
    cluster_mask_full = np.stack((cluster_mask,) * 4, axis=-1)
    cluster_mask_full = cv.resize(cluster_mask_full, colored_face_mat.shape[:2])

    cluster_mask_full = cv.blur(cluster_mask_full, (15, 15))

    return cluster_mask_full.astype(np.uint8)


'''
Reduces the image to the beard region

INPUT:

1. Input obj file
2. Input image
3. A lsit of beard triangles

OUTPUT:

1. Image of beard region
'''

def beard_region_builder(src_obj, src_img, list_of_beard_triangles):

    OG_size = src_img.shape

    # Obtain lists of obj parameters
    vertices, faces, textures, vertex_normals, parameter_space_vertices, lines = read_obj(src_obj)

    # Create a blank image
    blank = np.zeros((src_img.shape[0], src_img.shape[1], 3), dtype = np.uint8)
    white = [1, 1, 1]

    # Create and populate the vertices of each triangle in a list
    triangles = []
    for F in faces['vt']:

        V1 = (int(textures[F[0]-1][0] * src_img.shape[1]), int((1-textures[F[0]-1][1]) * src_img.shape[0]))
        V2 = (int(textures[F[1]-1][0] * src_img.shape[1]), int((1-textures[F[1]-1][1]) * src_img.shape[0]))
        V3 = (int(textures[F[2]-1][0] * src_img.shape[1]), int((1-textures[F[2]-1][1]) * src_img.shape[0]))
        triangles.append([V1, V2, V3])
    
    for index in  list_of_beard_triangles:

        T = triangles[index]

        # Obtain the bounding rectangle of each triangle
        tri = np.float32([[[T[0][0], T[0][1]], [T[1][0], T[1][1]], [T[2][0], T[2][1]]]])
        rect = cv.boundingRect(tri)
        src_img_Cropped = src_img[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]

        # Obtain the mask of beard region for each traingle using the bounding rectangle
        tri_Cropped = []
        for i in range(0, 3):
            tri_Cropped.append(((tri[0][i][0] - rect[0]),(tri[0][i][1] - rect[1])))

        mask = np.zeros((rect[3], rect[2], 3), dtype = np.float32)
        cv.fillConvexPoly(mask, np.int32(tri_Cropped), white, 16, 0)

        # Apply mask of beard region on source cropped image
        src_img_Cropped = src_img_Cropped * mask

        blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] = blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] * ( white - mask )
        blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] = blank[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] + src_img_Cropped

    blank = cv.resize(blank, (OG_size[1], OG_size[0]))
    return blank


'''
Detects beard in an image and applies mask accoedingly

INPUT:

1. Input image
2. Input obj file
3. A lsit of beard triangles
4. Checkpoints
5. ML model

OUTPUT:

1. beard_flag
2. beard_mask
'''

def beard_detector(src_img, src_obj, list_of_beard_triangles, checkpoints, ML_model):
    
    # Obtain the list of patches for input image as per checkpoints
    patches = obtain_patches_from_image(src_img, checkpoints, src_obj)
    # Extract features from each of those patches
    X_test_for_ML = feature_extractor([patches])

    # Test features to detect beard
    y_pred = ML_model.predict(X_test_for_ML)
    print(y_pred)

    # Call this function to reduce image to beard region
    final_image_beard = beard_region_builder(src_obj, src_img, list_of_beard_triangles)

    # Set alpha=0 for beard region background
    tmp = cv.cvtColor(final_image_beard, cv.COLOR_BGR2GRAY)
    _,alpha = cv.threshold(tmp,0,255,cv.THRESH_BINARY)
    b, g, r = cv.split(final_image_beard)

    rgba = [b,g,r, alpha]
    dst = cv.merge(rgba,4)

    # Call this function to obtain mask
    segmented_image = get_facial_hair_mask(dst)

    return y_pred[0], segmented_image


'''
Parses list of images and obj files

INPUT:

1. A list of input images
2. A list of input obj files
3. A lsit of beard triangles
4. Checkpoints
5. ML model

OUTPUT:

1. A list of beard_flag
2. A list of beard_mask
'''

def beard_list_2_mask_list(input_img_list, input_obj_list, list_of_beard_triangles, checkpoints, ML_model):

    beard_flag_list = []
    beard_mask_list = []

    for index in range(len(input_img_list)):

        input_img = input_img_list[index]
        input_obj = input_obj_list[index]

        # Call this function to obtain the beard_flag and beard_mask of each image
        beard_flag, beard_mask = beard_detector(input_img, input_obj, list_of_beard_triangles, checkpoints, ML_model)
        beard_flag_list.append(beard_flag)
        beard_mask_list.append(beard_mask)

        # Uncomment the lines below to display the comparision b/w input images and it's obtained mask
        '''
        cv.resize(beard_mask, (input_img.shape[1], input_img.shape[0]))
        compare = np.hstack((input_img, beard_mask[..., :3]))
        cv.imshow('Beard', compare)
        cv.waitKey(0)
        cv.destroyAllWindows()
        '''

    return beard_flag_list, beard_mask_list


'''
Main function takes 4 arguments from command line:

1. Path of the directory containing images and obj files for training, i.e. <training_data_directory>
The directory config must follow this flow:
<training_data_directory> ___
                            |___ <individual_directory> ___
                                                           |___ <image_file>
                                                           |___ <obj_file>

2. Path to a file which contains indices of all the faces corresponding to facial hair region.

3. Path to a file contining checkpoints, i.e. indices of all those faces where beard texture is obtained.

4. Path to the ML model
'''

if __name__ == '__main__':

    images_folder_path = sys.argv[1]
    facial_hair_txt = sys.argv[2]
    checkpoints_path = sys.argv[3]
    ML_model_path = sys.argv[4]

    # Obtain a list which contains all the faces corresponding to facial hair region.
    facial_hair = open(facial_hair_txt, "r").read()
    facial_hair = list(facial_hair.split('\n'))
    list_of_beard_triangles = []
        
    for hair in facial_hair:
        list_of_beard_triangles.append(int(hair))
        list_of_beard_triangles.append(int(hair)+1)

    # Obtain a list which contains indices of all those faces where beard texture is obtained.
    checkpoints = open(checkpoints_path, "r").read()
    checkpoints = list(checkpoints.split('\n'))

    # Obtain the ML Model
    ML_model = pickle.load(open(ML_model_path, 'rb'))

    # Prepare lists containing input_img and input_obj respectively
    input_img_list = []
    input_obj_list = []

    # Obtain a list of <individual_directory> paths
    dir_folders = os.listdir(images_folder_path)

    for folder in dir_folders:

        files = os.listdir(images_folder_path + '/' + folder)
        
        # Find the img_path and obj_path individually
        img_path = ''
        obj_path = ''

        if files[0].split('.')[-1] == 'obj':
            obj_path = images_folder_path + '/' + folder + '/' + files[0]
            img_path = images_folder_path + '/' + folder + '/' + files[1]
        else:
            obj_path = images_folder_path + '/' + folder + '/' + files[1]
            img_path = images_folder_path + '/' + folder + '/' + files[0]

        # Read the input_img and input_obj
        input_img = cv.imread(img_path)
        file = open(obj_path,'r')
        input_obj = file.readlines()
        file.close()

        input_img_list.append(input_img)
        input_obj_list.append(input_obj)

    # Call this function to obtain a list of beard_flag and beard_mask respectively.
    beard_flag_list, beard_mask_list = beard_list_2_mask_list(input_img_list, input_obj_list, list_of_beard_triangles, checkpoints, ML_model)