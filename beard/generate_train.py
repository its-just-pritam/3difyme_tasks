import sys
import os
import cv2 as cv

images_folder_path = 'new_Stock'
dir_files = os.listdir(images_folder_path)
print(dir_files)

for files in dir_files:

    img_name = files.split('.')[0]
    if not os.path.isdir(images_folder_path + '/' + img_name + '/'):
        os.mkdir(images_folder_path + '/' + img_name)
    
    if files.split('.')[-1] == 'jpg' or files.split('.')[-1] == 'png':
        img = cv.imread(images_folder_path + '/' + files)
        img = cv.resize(img, (1024, 1024))

        cv.imwrite(images_folder_path + '/' + img_name + '/' + '_face_cropped_0.png', img)