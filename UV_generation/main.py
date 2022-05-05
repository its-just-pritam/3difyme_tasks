# NOTE: To execute this program, use the following command format
# >>>> python main.py <input file> <image>

from queue import PriorityQueue
import sys
import cv2 as cv
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

#Base instructions

read_path = sys.argv[1]
img_path = sys.argv[2]
img = cv.imread(img_path)
uv_points = read_controlPoints(read_path)
# print(uv_points)

image_points = []
for P in uv_points:
    x = int(img.shape[1] * P[0])
    y = int(img.shape[0] * P[1])
    image_points.append((x,y))

# print(image_points)
triangulation(image_points, img, img_path)