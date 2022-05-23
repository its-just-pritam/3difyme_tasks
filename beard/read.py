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