import bpy
import os
import sys

# .\blender.exe --python C:\Users\srita\Desktop\3dify_task\duplicate\main.py

def selectObject(names):
        
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
        
    print("Args: ", sys.argv)
    # Select and delete all objects to start with a clean space
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Import the source object and shift it to x=-1
    src_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/duplicate/source.fbx'
    bpy.ops.import_scene.fbx( filepath = src_FBXfilePath )
    selected_obj = bpy.context.active_object
    selected_obj.location[0] = -2
    
    # Import the target object
    tar_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/duplicate/target.fbx'
    bpy.ops.import_scene.fbx( filepath = tar_FBXfilePath )
    
    print("Active : ", bpy.context.active_object)
    print(bpy.context.space_data)
    
    # Maintains target object in a list
    target_objects = bpy.context.selected_objects
    act = bpy.context.active_object
    print("Active: ", act)
    
    # Creating a duplicate Armature
    selectObject(["Armature"])
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(2, 0, 0)})
    armature = bpy.context.scene.objects["Armature.001"]

    export_objects_names = ["Armature.001"]
    # Loop over every target objects(selected objects)
    for obj in target_objects:

        if obj != act:
            obj.location[0] = 0
            export_objects_names.append(obj.name)
            # Sets the obj accessible to bpy.ops adds data transfer and armature modifier
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_add(type='DATA_TRANSFER')
            bpy.ops.object.modifier_add(type='ARMATURE')
            
            # Obtain and set the source object for data transfer using naming convention
            name = obj.name.split('.')[0]
            src_ob = bpy.context.scene.objects[name]
            bpy.context.object.modifiers["DataTransfer"].object = src_ob

            # Set required parameters and Generate Data Layers
            bpy.context.object.modifiers["DataTransfer"].use_vert_data = True
            bpy.context.object.modifiers["DataTransfer"].data_types_verts = {'VGROUP_WEIGHTS'}
            bpy.context.object.modifiers["DataTransfer"].vert_mapping = 'TOPOLOGY'
            bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
            
            # Sets parent of the object as armature and restores the object position
            obj.parent = armature
            obj.matrix_parent_inverse = armature.matrix_world.inverted()
            bpy.context.object.modifiers["Armature"].object = armature
            
    bpy.context.view_layer.objects.active = act
    print(export_objects_names)
    
    selectObject(export_objects_names)

    export_path = 'C:/Users/srita/Desktop/3dify_task/duplicate/final.fbx'
    bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True, object_types={'MESH', 'ARMATURE'}, path_mode='COPY', embed_textures= True, global_scale=1, add_leaf_bones=False)