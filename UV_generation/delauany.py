import cv2 as cv

# Function returns True if a point lies inside or on the rectangle

def inside_rectangle(P, rect):

    if P[0] >= rect[0] and P[0] <= rect[2] and P[1] >= rect[1] and P[1] <= rect[3]:
        return True
    else:
        return False

# Function draws Delauany triangle on an image

def draw_delauany(image, subdiv):

    triangles = subdiv.getTriangleList()
    rect = (0,0,image.shape[0], image.shape[1])

    for T in triangles:
        P1 = (int(T[0]), int(T[1]))
        P2 = (int(T[2]), int(T[3]))
        P3 = (int(T[4]), int(T[5]))

        if inside_rectangle(P1, rect) and inside_rectangle(P1, rect) and inside_rectangle(P1, rect):
            cv.line(image, P1, P2, (255,255,255), thickness=1)
            cv.line(image, P2, P3, (255,255,255), thickness=1)
            cv.line(image, P3, P1, (255,255,255), thickness=1)

# Main function of the module

def triangulation(points, image, img_path):

    img_path += '_triangulated.jpg'
    rect = (0,0,image.shape[0], image.shape[1])
    subdiv = cv.Subdiv2D(rect)

    for P in points:
        subdiv.insert(P)
        cv.circle(image, P, 2, (0,0,255), thickness=2)

    draw_delauany(image, subdiv)
    cv.imwrite(img_path, image)
    cv.imshow('Delauany Image', image)
    cv.waitKey(3000)