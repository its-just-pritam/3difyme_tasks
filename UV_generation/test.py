from uv_map import UV_Map
import cv2 as cv

final_img = UV_Map('tshirt1.jpg', 'input1.txt', 'output1.txt')
cv.imwrite('tshirt1_transformed.jpg', final_img)