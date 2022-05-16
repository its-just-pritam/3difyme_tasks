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
    src_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/pose/source.fbx'
    src_obj = bpy.ops.import_scene.fbx( filepath = src_FBXfilePath )
    selected_obj = bpy.context.active_object
    selected_obj.location[0] = 0
    
    # Import the target object
    tar_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/pose/target.fbx'
    tar_obj = bpy.ops.import_scene.fbx( filepath = tar_FBXfilePath)
    
    # Import the camera
    cam_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/pose/camera.fbx'
    cam_obj = bpy.ops.import_scene.fbx( filepath = cam_FBXfilePath )
    
    # Import the light
    lit_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/pose/light.fbx'
    lit_obj = bpy.ops.import_scene.fbx( filepath = lit_FBXfilePath )

    print([x.name for x in bpy.data.objects])
    source_armature = bpy.data.objects['Armature']
    target_armature = bpy.data.objects['Armature.001']
    
    bpy.ops.object.mode_set( mode = 'POSE' )
    
    for bones in target_armature.pose.bones:
        
        boneToSelect = bones.bone
        bpy.context.object.data.bones.active = boneToSelect
        boneToSelect.select = True
        
        bcr = bones.constraints.new('COPY_ROTATION')
        bcr.target = bpy.data.objects["Armature"]
        bcr.subtarget = bones.name
        bpy.ops.constraint.apply(constraint="Copy Rotation", owner='BONE')
        
        bcl = bones.constraints.new('COPY_LOCATION')
        bcl.target = bpy.data.objects["Armature"]
        bcl.subtarget = bones.name
        bpy.ops.constraint.apply(constraint="Copy Location", owner='BONE')
    
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    export_obj_names = []
    for x in bpy.data.objects:
        if x != source_armature:
            export_obj_names.append(x.name)
            
    print(export_obj_names)
    selectObject(export_obj_names)

    export_path = 'C:/Users/srita/Desktop/3dify_task/pose/final.fbx'
    bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True, object_types={'MESH', 'ARMATURE'}, path_mode='COPY', embed_textures= True, global_scale=1, add_leaf_bones=False)
