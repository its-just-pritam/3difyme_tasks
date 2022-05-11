import cv2 as cv
import matplotlib.path as mplPath
import numpy as np

# Function returns True if a point lies inside or on the rectangle

def inside_rectangle(P, rect):

    if P[0] >= rect[0] and P[0] <= rect[2] and P[1] >= rect[1] and P[1] <= rect[3]:
        return True
    else:
        return False

# Function draws Delauany triangle on an image

def draw_delauany(image, subdiv, poly_path):

    triangles = subdiv.getTriangleList()
    rect = (0,0,image.shape[0], image.shape[1])
    new_triangles = []

    for T in triangles:
        P1 = (int(T[0]), int(T[1]))
        P2 = (int(T[2]), int(T[3]))
        P3 = (int(T[4]), int(T[5]))

        Cx = (P1[0] + P2[0] + P3[0]) // 3
        Cy = (P1[1] + P2[1] + P3[1]) // 3

        if inside_rectangle(P1, rect) and inside_rectangle(P1, rect) and inside_rectangle(P1, rect) and poly_path.contains_point((Cx, Cy)):
            new_triangles.append([P1, P2, P3])
            cv.line(image, P1, P2, (255,0,255), thickness=1)
            cv.line(image, P2, P3, (255,0,255), thickness=1)
            cv.line(image, P3, P1, (255,0,255), thickness=1)

    return new_triangles

# Main function of the module

def triangulation(points, image):

    rect = (0,0,image.shape[0], image.shape[1])
    subdiv = cv.Subdiv2D(rect)

    polygon_points = []
    for P in points:
        polygon_points.append([P[0], P[1]])
        subdiv.insert(P)
        cv.circle(image, P, 2, (0,0,255), thickness=2)

    poly_path = mplPath.Path(np.array(polygon_points))
    triangles = draw_delauany(image, subdiv, poly_path)
    cv.imshow('Triangulated Image', image)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return triangles