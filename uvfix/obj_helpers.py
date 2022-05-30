import io
import os


def read_obj(path):

    vertices = []
    faces = []
    uv = []
    mtl_file = None
    mtl_name = None

    for line in io.open(path).readlines():

        line = line.strip()

        if(line.startswith("mtllib")):
            _, mtl_file = line.split(" ")

        if(line.startswith("usemtl")):
            _, mtl_name = line.split(" ")

        # Pick lines starting with v_ 
        if(line.startswith("v ")):
            vertex = [ float(x) for x in line.split(" ")[1:]]
            vertices.append(vertex)

        # Pick lines starting with vt_ 
        if(line.startswith("vt ")):
            vertex = [ float(x) for x in line.split(" ")[1:]]
            uv.append(vertex)
        
        # Pick lines starting with f_ 
        if(line.startswith("f ")):
            face_vertex = [ int(x.split("/")[0]) for x in line.split(" ")[1:]]
            face_uv = [ int(x.split("/")[1]) for x in line.split(" ")[1:]]
            faces.append([face_vertex, face_uv])

    return (vertices, uv, faces, mtl_file, mtl_name)

def write_obj(path, vertices, uv=[], faces=[], mtl_file=None, mtl_name=None, smooth=True, file_mode='w', obj_name='object'):

    with io.open(path, file_mode) as fout:

        fout.write(f"o {obj_name}\n")

        if mtl_file is not None:
            fout.write(f"mtllib {mtl_file}\n")

        # Write vertices
        fout.write("\n# Vertices\n")
        for vertex in vertices:
            fout.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
        
        # Write UV
        fout.write("\n# UV\n")
        for vertex in uv:
            vertices = " ".join([f"{v}" for v in vertex])
            fout.write(f"vt {vertices}\n")

        if mtl_name:
            fout.write(f"usemtl {mtl_name}\n")

        if smooth:
            fout.write(f"s 1\n")

        # Write faces
        fout.write("\n# Faces\n")
        for face in faces:

            if len(face) > 0:
                vertices = " ".join([f"{v}/{u}" for v, u in zip(face[0], face[1])])
            else:
                vertices = " ".join([f"{v}" for v in face])

            fout.write(f"f {vertices}\n")

def write_mtl_file(path, mtl_name, texture):

    material = io.open("./base_data/materials/canonical_material.mtl").read()
    material = material.replace("__material__", mtl_name)
    material = material.replace("__texture__", texture)
    with io.open(path, "w") as fout:
        fout.write(material)

def combine_objs(target_obj_path, obj_paths=[]):

    vertex_offset = 0
    uv_offset = 0

    target_mtl_path = target_obj_path[:-4] + ".mtl"
    
    with io.open(target_obj_path, "w") as fout:
        fout.write("")

    for path in obj_paths:
        obj_name = os.path.basename(path)[:-4]
        vertices, uv, faces, mtl_file, mtl_name = read_obj(path)

        mtl_file = os.path.basename(target_mtl_path)

        if mtl_name == None:
            mtl_name = obj_name + ".material"
        
        new_faces = []
        for face_tuple in faces:

            tuple_1 = (x + vertex_offset for x in face_tuple[0])
            tuple_2 = (x + uv_offset for x in face_tuple[1])
            new_faces.append([tuple_1, tuple_2])

        write_obj(target_obj_path, vertices, uv, new_faces, mtl_file, mtl_name, smooth=True, file_mode='a', obj_name=obj_name)
        vertex_offset += len(vertices)
        uv_offset += len(uv)
    
    with io.open(target_mtl_path, "w") as fout:

        for path in obj_paths:
            mtl_path = path[:-4] + ".mtl"

            if os.path.exists(mtl_path):

                for line in io.open(mtl_path).readlines():
                    fout.write(line)
                fout.write("\n")
                
            else:
                mtl_name = os.path.basename(path)[:-4]
                fout.write(f"newmtl {mtl_name}.material\n")
                

def get_canonical_faces():
    
    # Get canonical faces
    vertices, uv, faces, *rest = read_obj("./base_data/meshes/canonical_face.obj")
    for face in faces:
        face[1] = face[0]

    return faces







