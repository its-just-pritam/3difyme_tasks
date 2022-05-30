'''
RUN COMMAND
python main.py new_uvs.obj clothes.obj
'''

import io
import sys
from obj_helpers import read_obj, write_obj


def read_obj_with_groups(path):

    obj_containers = []
    mtl_file = None
    obj_entry = {
                'name': '',
                'mtl': '',
                'vertices': [],
                'faces': [],
                'uv': [],
                'v_offset': 0,
                'uv_offset': 0
            }

    for line in io.open(path).readlines():

        line = line.strip()

        if(line.startswith("mtllib")):
            _, mtl_file = line.split(" ")

        if(line.startswith("o ")):

            prev_v_offset = obj_entry['v_offset']
            prev_vert_len = len(obj_entry['vertices'])
            prev_uv_offset = obj_entry['uv_offset']
            prev_uv_len = len(obj_entry['uv'])

            if len(obj_entry['name']) > 0:
                obj_containers.append(obj_entry)
                obj_entry = {
                    'name': '',
                    'mtl': '',
                    'vertices': [],
                    'faces': [],
                    'uv': [],
                    'v_offset': 0,
                    'uv_offset': 0
                }

            obj_name = line.split(" ")[1:][0].split(".")[0]
            obj_entry['name'] = obj_name
            obj_entry['v_offset'] = prev_v_offset + prev_vert_len
            obj_entry['uv_offset'] = prev_uv_offset + prev_uv_len

        if(line.startswith("usemtl")):
            _, obj_entry['mtl'] = line.split(" ")

        # Pick lines starting with v_ 
        if(line.startswith("v ")):
            vertex = [ float(x) for x in line.split(" ")[1:]]
            obj_entry['vertices'].append(vertex)

        # Pick lines starting with vt_ 
        if(line.startswith("vt ")):
            vertex = [ float(x) for x in line.split(" ")[1:]]
            obj_entry['uv'].append(vertex)
        
        # Pick lines starting with f_ 
        if(line.startswith("f ")):
            face_vertex = [ int(x.split("/")[0]) for x in line.split(" ")[1:]]
            face_uv = [ int(x.split("/")[1]) for x in line.split(" ")[1:]]
            obj_entry['faces'].append([face_vertex, face_uv])

    obj_containers.append(obj_entry)

    return (obj_containers, mtl_file)



def copy_obj_vertices(src_obj_containers, tar_obj_containers, obj_name):

    data = []

    for index in range(len(src_obj_containers)):
        if src_obj_containers[index]['name'] == obj_name:
            data = src_obj_containers[index]['vertices']
            break

    for index in range(len(tar_obj_containers)):
        if tar_obj_containers[index]['name'] == obj_name:
            tar_obj_containers[index]['vertices'] = data
            break
    
    return tar_obj_containers



def copy_obj_uv(src_obj_containers, tar_obj_containers, obj_name):

    data = []

    for index in range(len(src_obj_containers)):
        if src_obj_containers[index]['name'] == obj_name:
            data = src_obj_containers[index]['uv']
            break

    for index in range(len(tar_obj_containers)):
        if tar_obj_containers[index]['name'] == obj_name:
            tar_obj_containers[index]['uv'] = data
            break
    
    return tar_obj_containers



def copy_obj_faces(src_obj_containers, tar_obj_containers, obj_name):

    data = []

    for index in range(len(src_obj_containers)):
        if src_obj_containers[index]['name'] == obj_name:

            for i in range(len(data)):
                for j in range(len(data[i])):
                    for k in range(len(data[i][j])):
                        if j == 0:
                            data[i][j][k] -= src_obj_containers[index]['v_offset']
                        elif j == 1:
                            data[i][j][k] -= src_obj_containers[index]['uv_offset']


            data = src_obj_containers[index]['faces']
            break
    
    for index in range(len(tar_obj_containers)):
        if tar_obj_containers[index]['name'] == obj_name:
            
            for i in range(len(data)):
                for j in range(len(data[i])):
                    for k in range(len(data[i][j])):
                        if j == 0:
                            data[i][j][k] += tar_obj_containers[index]['v_offset']
                        elif j == 1:
                            data[i][j][k] += tar_obj_containers[index]['uv_offset']

            tar_obj_containers[index]['faces'] = data
            break
    
    return tar_obj_containers


if __name__ == '__main__':

    path1 = sys.argv[1]
    path2 = sys.argv[2]
    obj_containers1, mtl_file1, = read_obj_with_groups(path1)

    print('Src: ', mtl_file1)
    for obj_entry in obj_containers1:
        print(obj_entry['name'])
        print(obj_entry['mtl'])
        print(len(obj_entry['vertices']), len(obj_entry['uv']), len(obj_entry['faces']))
        print(obj_entry['v_offset'])
        print(obj_entry['uv_offset'])

    obj_containers2, mtl_file2 = read_obj_with_groups(path2)

    print('\nTar: ', mtl_file2)
    for obj_entry in obj_containers2:
        print(obj_entry['name'])
        print(obj_entry['mtl'])
        print(len(obj_entry['vertices']), len(obj_entry['uv']), len(obj_entry['faces']))
        print(obj_entry['v_offset'])
        print(obj_entry['uv_offset'])

    obj_containers2 = copy_obj_vertices(obj_containers1, obj_containers2, 'upper_clothing')
    obj_containers2 = copy_obj_uv(obj_containers1, obj_containers2, 'upper_clothing')
    obj_containers2 = copy_obj_faces(obj_containers1, obj_containers2, 'upper_clothing')

    print('\nNew Tar: ', mtl_file2)
    for obj_entry in obj_containers2:
        print(obj_entry['name'])
        print(obj_entry['mtl'])
        print(len(obj_entry['vertices']), len(obj_entry['uv']), len(obj_entry['faces']))
        print(obj_entry['v_offset'])
        print(obj_entry['uv_offset'])

    write_path = 'fixed_uv.obj'
    mode = 'w'

    for obj_entry in obj_containers2:

        write_obj(write_path, obj_entry['vertices'], uv=obj_entry['uv'], faces=obj_entry['faces'], mtl_file=mtl_file2, mtl_name=obj_entry['mtl'], smooth=True, file_mode=mode, obj_name=obj_entry['name'])
        mode = 'a'
        mtl_file2 = None