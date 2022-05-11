"""
written by whitney constantine, for managing the importing of textures

you can import in a folder of blend files with materials, or texture files themselves. If you wish 
to import in texture files, please package the textures into individual folders

eg: if you have a wood texture, put all the wood texture files into one folder.

-Most of the textures this script supports come from Polyhaven.com, a free resource for textures
model and HDRIs. Please support them if you have the means! The amount of content they provide for free
is absolutely amazing.
"""


import bpy
import sys
import os
from enum import Enum

"""
This script can import in textures via either:

    -blender 
    -folders with textures
    
"""

class texture_import_menu(bpy.types.menu):
    bl_idname = "OBJECT_MT_select_submenu"
    bl_label = "select"

#mode of importing in assets
class import_mode(Enum):
    blender = 1
    files = 2
    
class Texture:
    def __init__(self, texture_path):
        
        #check if texture has normal map, ao, diff, etc
        self.normal_map = False
        self.diffuse = False
        self.ao = False
        self.height = False
        self.rough = False
        
        self.path = texture_path
        self.name = os.path.split(texture_path)[-1]

        images = []
        for file in os.listdir(texture_path):
            
            if os.path.isdir(os.path.join(texture_path, file)):
                path = os.path.join(texture_path, file)
                
                for img in os.listdir(path):
                    images.append(os.path.join(path, img))
            else:
                images.append(os.path.join(texture_path, file))

        for img in images:
            if not "rough_ao" in img and "ao" in img:
                self.ao = True
                self.ao_path = img
            
            if "normal" in img or "_nor_" in img:
                self.normal_map = True
                self.normal_path = img
                
            if "_disp_" in img or "displacement" in img or "height" in img:
                self.height = True
                self.height_path = img
                
            if "diffuse" in img or "_diff_" in img or "albedo" in img:
                self.diffuse = True
                self.diffuse_path = img
                print(self.diffuse_path)
                
            if not "_rough_ao" in img and "_rough_" in img or "roughness" in img:
                self.rough = True
                self.rough_path = img
                
            if not "rough_ao" in img and "ao" in img:
                self.ao = True
                self.ao_path = img
            
        print("all images for {} found".format(self.path))
        print("------------")
            
            
mode = import_mode
import_folder = r"D:\textures"
import_mode = mode.files


if import_mode == mode.blender:
    # handle blender assets
    print("handle blender assets")
    
    for file in os.listdir(import_folder):
        if file.endswith(".blend"):
            
            path = os.path.join(import_folder,file)
            print(path)
            
            with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.materials = data_from.materials
                
                for mat in data_to.materials:
                    if mat is not None:
                        print(" imported : ", mat)
                    
elif import_mode == mode.files:
    # hand files mode
    print("Handle files")
    
    # find all directories that house textures
    texture_folders = []
    for file in os.listdir(import_folder):
        if os.path.isdir(os.path.join(import_folder, file)):
            texture_folders.append(os.path.join(import_folder, file))
    
    textures = []
    for fld in texture_folders:
        tex = Texture(fld)
        textures.append(tex)


    for texture in textures:
        # create a material, and assign and link all relevant textures.
            
        material = bpy.data.materials.new(name=texture.name)
        material.use_nodes = True
        
        
        node_tree = material.node_tree
        nodes = material.node_tree.nodes
        
        shader = nodes["Principled BSDF"]
        
        texture_coord = nodes.new("ShaderNodeTexCoord")
        texture_coord.location = (-1300, 400)
        
        mapping = nodes.new("ShaderNodeMapping")
        mapping.location = (-1100, 400)
        node_tree.links.new(texture_coord.outputs["UV"], mapping.inputs["Vector"])
        
        if texture.diffuse == True:
            diff = nodes.new("ShaderNodeTexImage")
            diff.location = (-700, 300)
            diff_img = bpy.data.images.load(texture.diffuse_path)
            diff.image = diff_img
            
            
            
            node_tree.links.new(mapping.outputs["Vector"], diff.inputs["Vector"])
            
            #if we have an ao texture, create a mix node and combine the two textures
            if texture.ao == True:
                ao = nodes.new("ShaderNodeTexImage")
                ao.location = (-700, 300)
                ao_img = bpy.data.images.load(texture.ao_path)
                ao.image = ao_img
                ao.location = (-700, 600)
                
                node_tree.links.new(mapping.outputs["Vector"], ao.inputs["Vector"])
                
                # create a mix, and link the ao and diffuse together, use a multiply:
                mix = nodes.new("ShaderNodeMixRGB")
                mix.location = (-300, 260)
                mix.blend_type = "MULTIPLY"
                mix.inputs[0].default_value = 1
                node_tree.links.new(diff.outputs["Color"], mix.inputs["Color1"])
                node_tree.links.new(ao.outputs["Color"], mix.inputs["Color2"])
                
                node_tree.links.new(mix.outputs["Color"], shader.inputs["Base Color"])
                
            else:
                node_tree.links.new(diff.outputs["Color"], shader.inputs["Base Color"])
        
            
        if texture.normal_map == True:
            
            normal = nodes.new("ShaderNodeTexImage")
            normal.location = (-700, -500)
            normal_img = bpy.data.images.load(texture.normal_path)
            normal.image = normal_img
            
            
            node_tree.links.new(mapping.outputs["Vector"], normal.inputs["Vector"])
            
            normal_map = nodes.new("ShaderNodeNormalMap")
            normal_map.location = (-300, -500)
            
            
            node_tree.links.new(normal.outputs["Color"], normal_map.inputs["Color"])
            node_tree.links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
            
        if texture.rough == True:
            
            rough = nodes.new("ShaderNodeTexImage")
            rough.location = (-700, -100)
            rough_img = bpy.data.images.load(texture.rough_path)
            rough.image = rough_img
            
            node_tree.links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
            node_tree.links.new(rough.outputs["Color"], shader.inputs["Roughness"])
            
            
        print("material created for: {} ".format(texture.name))
        

def register():
    bpy.utils.register_class(ObjectMoveX)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    bpy.utils.unregister_class(ObjectMoveX)


if __name__ == "__main__":
    register()