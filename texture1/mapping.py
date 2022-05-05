# NOTE: To execute this program, use the following command format
# >>>> python mapping.py <input file> <output file> <image>

import sys
import cv2 as cv

# Function to read from an obj file

def read_obj(path):

    file = open(path,'r')
    str_Array = file.readlines()

    vertices = []
    faces = {
        'v': [],
        'vt': []
    }
    textures = []
    vertex_normals = []
    parameter_space_vertices = []
    lines = []

    for str in str_Array:

        str = str.replace('\n', '')
        str = str.split(' ')

        if str[0] == 'v':
            vertex = []
            for word in str:
                if word != 'v':
                    vertex.append(float(word))
            vertices.append(vertex)

        elif str[0] == 'f':
            face_vertices = []
            face_texture = []
            for word in str:  
                if word != 'f':
                    values = list(word.split('/'))
                    face_vertices.append(int(values[0]))
                    if len(values) >= 2:
                        face_texture.append(int(values[1]))
            faces['v'].append(face_vertices)
            faces['vt'].append(face_texture)

        elif str[0] == 'vt':
            texture = []
            for word in str: 
                if word != 'vt':
                    texture.append(float(word))
            textures.append(texture)

        elif str[0] == 'vn':
            vertex_normal = []
            for word in str:  
                if word != 'vn':
                    vertex_normal.append(float(word))
            vertex_normals.append(vertex_normal)

        elif str[0] == 'vp':
            parameter_space_vertice = []
            for word in str:  
                if word != 'vp':
                    parameter_space_vertice.append(float(word))
            parameter_space_vertices.append(parameter_space_vertice)

        elif str[0] == 'l':
            line = []
            for word in str:
                if word != 'l':
                    line.append(int(word))
            lines.append(line)
    
    file.close()
    return vertices, faces, textures, vertex_normals, parameter_space_vertices, lines


# Function to construct sentences

def CreateSentence(values):
    
    sentence = ' '.join([str(value) for value in values])
    return sentence
    

# Function to write to an obj file

def write_obj(path, vertices, faces, textures, vertex_normals, parameter_space_vertices, lines):
    
    file = open(path,'w')

    if len(vertices) > 0:
        sentences = []
        for item in vertices:
            sentence = 'v '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    if len(textures) > 0:
        sentences = []
        for item in textures:
            sentence = 'vt '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    if len(faces['v']) > 0:

        combined = faces['v']
        if len(faces['vt']) > 0:
            for i in range(len(faces['vt'])):
                for j in range(len(faces['vt'][i])):
                    combined[i][j] = str(combined[i][j]) + '/' + str(faces['vt'][i][j])

        sentences = []
        for item in combined:
            sentence = 'f '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    if len(vertex_normals) > 0:
        sentences = []
        for item in vertex_normals:
            sentence = 'vn '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    if len(parameter_space_vertices) > 0:
        sentences = []
        for item in parameter_space_vertices:
            sentence = 'vp '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    if len(lines) > 0:
        sentences = []
        for item in lines:
            sentence = 'l '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    file.close()


# Base instructions

read_path = sys.argv[1]
write_path = sys.argv[2]
img_path = sys.argv[3]
vertices, faces, textures, vertex_normals, parameter_space_vertices, lines = read_obj(read_path)
write_obj(write_path, vertices, faces, textures, vertex_normals, parameter_space_vertices, lines)

img = cv.imread(img_path)

for dot in textures:
    x = img.shape[1]*dot[0]
    y = img.shape[0]*(1-dot[1])
    cv.circle(img, (int(x),int(y)), 2, (0,0,255), thickness=2)

for vt in faces['vt']:
    for i in range(len(vt)):
        for j in range(i):
            if vt[i] != vt[j]:
                #print(vt[i], vt[j])
                x1 = textures[vt[i]-1][0]*img.shape[1]
                y1 = (1-textures[vt[i]-1][1])*img.shape[0]
                x2 = textures[vt[j]-1][0]*img.shape[1]
                y2 = (1-textures[vt[j]-1][1])*img.shape[0]
                cv.line(img, (int(x1),int(y1)), (int(x2),int(y2)), (255,255,255), thickness=1)

#cv.circle(img, (int(img.shape[1]*textures[dot][0]),int(img.shape[0]*textures[dot][1])), 2, (0,0,255), thickness=2)
cv.imwrite('messi_texture.png', img)
cv.imshow('Messi', img)
cv.waitKey(2000)