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
        
        
        
def DFS(source_armature, target_armature, queue):
    
    if(len(queue) == 0):
        return
    
    curr = queue.pop(len(queue)-1)
    curr_bone = target_armature.pose.bones[curr]
        
    for child in curr_bone.children:
        queue.append(child.name)
        
    DFS(source_armature, target_armature, queue)
    if curr != "mixamorig:Hips":
        src_trans_matrix = source_armature.pose.bones[curr].matrix @ source_armature.pose.bones[curr].parent.matrix.inverted_safe()
        curr_bone.matrix = src_trans_matrix @ curr_bone.parent.matrix

#    print(curr)
        

if __name__=="__main__":

    print("Args: ", sys.argv)
    # Select and delete all objects to start with a clean space
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Import the source object and shift it to x=-1
    src_FBXfilePath = 'C:/Users/srita/Desktop/3dify_task/pose/source.fbx'
    src_obj = bpy.ops.import_scene.fbx( filepath = src_FBXfilePath )
    selected_obj = bpy.context.active_object
    
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

    root = "mixamorig:Hips"
    root_bone = target_armature.pose.bones[root]
    queue = [root]
    
    print(source_armature.pose.bones["mixamorig:LeftToeBase"].matrix)
    print(target_armature.pose.bones["mixamorig:LeftToeBase"].matrix)
    print(target_armature.pose.bones["mixamorig:LeftToeBase"].matrix_basis)
        
    act_arm = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT')

    for curr in source_armature.pose.bones:
        
        if curr.name != root:
            src_trans_matrix = curr.matrix @ curr.parent.matrix.inverted_safe()
            act_arm.data.edit_bones[curr.name].matrix = src_trans_matrix @ act_arm.data.edit_bones[curr.name].parent.matrix
    
    bpy.ops.object.mode_set(mode='OBJECT')
#    DFS(source_armature, target_armature, [root])
        
    print(source_armature.pose.bones["mixamorig:LeftToeBase"].matrix)
    print(target_armature.pose.bones["mixamorig:LeftToeBase"].matrix)
    print(target_armature.pose.bones["mixamorig:LeftToeBase"].matrix_basis)
    

"""
        x-scale x-shear1 x-shear2 x-coordinate
        y-shear1 y-scale y-shear2 y-coordinate
        z-shear1 z-shear2 z-scale z-coordinate
        0 0 0 1
"""