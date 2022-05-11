import cv2 as cv
import numpy as np
from delauany import triangulation

# Function reads and returns control points from a file

def read_controlPoints(path):

    file = open(path,'r')
    str_Array = file.readlines()
    points = []

    for str in str_Array:

        str = str.replace('\n', '')
        str = str.split(' ')
        points.append((float(str[0]), float(str[1])))

    return points

# Function to generate an UV Mapping from source to target image (main function)

def UV_Map(src_img_path, source_path, target_path):

    src_img = cv.imread(src_img_path)
    source_points = read_controlPoints(source_path)
    target_points = read_controlPoints(target_path)

    source_image_points = []
    source_points_index = {}
    count = 0
    for P in source_points:
        x = int(src_img.shape[1] * P[0])
        y = int(src_img.shape[0] * P[1])
        source_image_points.append((x,y))

        key = str(x) + '_' + str(y)
        source_points_index[key] = count
        count += 1

    blank = np.zeros((1024, 1024, 3), dtype='uint8')
    target_image_points = []
    for P in target_points:
        x = int(blank.shape[1] * P[0])
        y = int(blank.shape[0] * P[1])
        target_image_points.append((x,y))

    img_copy = src_img.copy()
    source_triangles = triangulation(source_image_points, src_img)

    for T in source_triangles:

        img2 = 255 * np.ones(img_copy.shape, dtype = img_copy.dtype)
        V1 = str(T[0][0]) + '_' + str(T[0][1])
        V2 = str(T[1][0]) + '_' + str(T[1][1])
        V3 = str(T[2][0]) + '_' + str(T[2][1])

        tri_1 = np.float32([[[T[0][0], T[0][1]], [T[1][0], T[1][1]], [T[2][0], T[2][1]]]])
        
        p1 = source_points_index[V1]
        p2 = source_points_index[V2]
        p3 = source_points_index[V3]
        tri_2 = np.float32([[[target_image_points[p1][0], target_image_points[p1][1]],
        [target_image_points[p2][0], target_image_points[p2][1]],
        [target_image_points[p3][0], target_image_points[p3][1]]]])

        r1 = cv.boundingRect(tri_1)
        r2 = cv.boundingRect(tri_2)

        tri1Cropped = []
        tri2Cropped = []
            
        for i in range(0, 3):
            tri1Cropped.append(((tri_1[0][i][0] - r1[0]),(tri_1[0][i][1] - r1[1])))
            tri2Cropped.append(((tri_2[0][i][0] - r2[0]),(tri_2[0][i][1] - r2[1])))

        img1Cropped = img_copy[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
        matrix = cv.getAffineTransform(np.float32(tri1Cropped), np.float32(tri2Cropped))
        img2Cropped = cv.warpAffine( img1Cropped, matrix, (r2[2], r2[3]), None, flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REFLECT_101 )

        white = [1, 1, 1]
        mask = np.zeros((r2[3], r2[2], 3), dtype = np.float32)
        cv.fillConvexPoly(mask, np.int32(tri2Cropped), white, 16, 0)
        img2Cropped = img2Cropped * mask

        blank[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = blank[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ( white - mask )
        blank[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = blank[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Cropped

    cv.imshow('Final Image', blank)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return blank