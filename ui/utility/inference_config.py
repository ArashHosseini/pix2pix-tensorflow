'''
Created on Dec 2, 2017

@author: flyn
'''
import os
_dir = os.path.dirname(__file__)

model = os.path.join(_dir, "facades_sandbox/export")
output_file = os.path.join(_dir, "facades_sandbox/output_dir/output_inference.png")
tmp_file = os.path.join(_dir, "facades_sandbox/input_dir/image.png")
maps_model = os.path.join(_dir, "maps_sandbox/export")
output_maps_file = os.path.join(_dir, "maps_sandbox/output_dir/start_map.png")
maps_init_ouput = output_resize_maps_file = os.path.join(_dir, "maps_sandbox/output_dir/resize_output_inference.png")
maps_tmp_file = os.path.join(_dir, "maps_sandbox/input_dir/image.png")
maps_init_file = os.path.join(_dir, "maps_sandbox/init_image/start_map.jpg")


face_model = os.path.join(_dir, "cloud_sandbox/export")#"cloud_sandbox/reexport")#face_sandbox/merkel_obama_sandbox")#merkel_obama_sandbox

face_dict = {"mouth_":(255,255,255)}

"""
face_dict = {"mouth_":(82,149,14),
              "nose": (24,28,122),
              "left_eye": (24,122,118),
              "right_eye":(126,75,126),
              "right_eye_br":(180,57,59),
              "left_eye_br":(17,119,172),
              "face":(165,32,135),
              "delete":(0,0,0)}

"""
    
buttons_dict = {"Wall": (13,61,251),
                "Door": (165,0,0),
                "Window": (0,117,255),
                "W.Sill": (104,248,152),
                "W.Head": (29,255,221),
                "Shutter": (238,237,40),
                "Balcony": (184,255,56),
                "Trim": (255,146,4),
                "Cornice": (255,68,1),
                "Column": (246,0,1),
                "Entrance": (0,201,255)}


maps_buttons_dict = {"Street": (255, 255, 255),
                     "Block": (230, 230, 225),
                     "Grass": (205, 220, 175),
                     "Buildings": (245, 240, 235)}

