import bpy
import os
import sys

# .\blender.exe --python C:\Users\srita\Desktop\3dify_task\duplicate\main.py

def SelectObject(names):
        
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    for name in names:
        # Get the object
        ob = bpy.context.scene.objects[name]
    
        # Make the target the active object 
        bpy.context.view_layer.objects.active = ob
    
        # Select the target object
        ob.select_set(True)
        
        

if __name__=="__main__":

    # Enter the OBJECT mode
#    bpy.ops.object.mode_set( mode = 'OBJECT' )
    # Select and delete all objects to start with a clean space
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Import the source object and shift it to x=-1
    src_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/uvfix/new_uvs.obj'
    src_obj = bpy.ops.import_scene.obj( filepath = src_FBXfilePath )
    reference_obj = bpy.context.selected_objects[0]
    reference_obj_name = reference_obj.name
    print('Src: ', reference_obj_name)
    
    src_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/uvfix/clothes.obj'
    src_obj = bpy.ops.import_scene.obj( filepath = src_FBXfilePath )
    main_obj = bpy.context.selected_objects[1]
    lower_clothing_name = bpy.context.selected_objects[0].name
    main_obj_name = main_obj.name
    print('Tar: ', main_obj_name)
    
    SelectObject([main_obj_name])
    bpy.ops.mesh.uv_texture_remove()
    
    SelectObject([main_obj_name, reference_obj_name])
    bpy.ops.object.join_uvs()
    
    # Select objects supposed to be exported
    SelectObject([lower_clothing_name, main_obj_name])

    # Export selected objects
    export_path = 'C:/Users/srita/Desktop/3dify_task/uvfix/final.obj'
    bpy.ops.export_scene.obj(filepath=export_path, use_selection=True, path_mode='COPY', global_scale=1)
    