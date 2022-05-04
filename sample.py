import sys

# Function to read from an obj file

def read_obj(path):

    file = open(path,'r')
    str_Array = file.readlines()

    vertices = []
    faces = []
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
            face = []
            for word in str:  
                if word != 'f':
                    face.append(int(word))
            faces.append(face)

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
    return vertices, faces, vertex_normals, parameter_space_vertices, lines

# Function to construct sentences

def CreateSentence(values):
    
    sentence = ' '.join([str(value) for value in values])
    return sentence
    

# Function to write to an obj file

def write_obj(path, vertices, faces, vertex_normals, parameter_space_vertices, lines):
    
    file = open(path,'w')

    if len(vertices) > 0:
        sentences = []
        for item in vertices:
            sentence = 'v '
            sentence += CreateSentence(item)
            sentence += '\n'
            sentences.append(sentence)
        file.writelines(sentences)

    if len(faces) > 0:
        sentences = []
        for item in faces:
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
vertices, faces, vertex_normals, parameter_space_vertices, lines = read_obj(read_path)
write_obj(write_path, vertices, faces, vertex_normals, parameter_space_vertices, lines)