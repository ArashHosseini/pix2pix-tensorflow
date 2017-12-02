#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np

rect_temp = []
rect_bbox = []
drawing = False
col = (0,0,255)

img = np.zeros((553,512,3), np.uint8)
img[:] = (13,61,251)[::-1]

drawing_area = [(-1000,40), (1000, 1000)]
cv2.rectangle(img, (0, 0), (512, 40), (255,255,255), -1)

box_size = (47,30)

# color buttons
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

color_positions = {}

for k,v in enumerate(buttons_dict.items()):

    button_color = v[1][::-1]
    button_text = v[0]

    first_point = (((k+1)*box_size[0]), 0)
    second_point = (k*box_size[0], box_size[1])
    color_positions[button_color] = [first_point, second_point]
    
    cv2.rectangle(img, first_point, second_point, button_color, -1)
    cv2.putText(img, button_text, (((k+1)*box_size[0]) - box_size[0], box_size[1]+8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,0,0))

def draw_rectangle(event, x, y, flags, param):
    
        global rect_bbox, rect_temp, drawing, col
    
        if event == cv2.EVENT_LBUTTONDOWN:
            rect_temp = []
            
            for color, position in color_positions.items():

                if x in range(position[1][0], position[0][0]) and y in range(position[0][1], position[1][1]):
                    col = color
                    current_selection = (list(buttons_dict.keys())[list(buttons_dict.values()).index(col[::-1])])
                    print('Switched to {0}'.format(current_selection))
                    break

            if x in range(drawing_area[0][0], drawing_area[1][0]) and y in range(drawing_area[0][1], drawing_area[1][1]):
                rect_bbox = [(x, y)]
                drawing = True

        elif event == cv2.EVENT_LBUTTONUP:

            if drawing_area[0][0] < x < drawing_area[1][0] and drawing_area[0][1] < y < drawing_area[1][1]:

                rect_bbox.append((x, y))
                drawing = False
            
                p_1, p_2 = rect_bbox

                cv2.rectangle(img, p_1, p_2, color=col,thickness=-1)
                cv2.imshow('pix2pix', img)

                p_1x, p_1y = p_1
                p_2x, p_2y = p_2

                lx = min(p_1x, p_2x)
                ty = min(p_1y, p_2y)
                rx = max(p_1x, p_2x)
                by = max(p_1y, p_2y)
            
                if (lx, ty) != (rx, by):
                    bbox = [lx, ty, rx, by]
                   
                # print ("Drawing Done") #callback when drawing is done

        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            if drawing_area[0][0] < x < drawing_area[1][0] and drawing_area[0][1] < y < drawing_area[1][1]:
                rect_temp = [(x, y)]

img_copy = img.copy()
cv2.namedWindow('pix2pix')
cv2.setMouseCallback('pix2pix', draw_rectangle)

while True:

    if not drawing:
        cv2.imshow('pix2pix', img)

    elif drawing and rect_temp:
        rect_cpy = img.copy()
        start_point = rect_bbox[0]
        end_point_tmp = rect_temp[0]
        cv2.rectangle(rect_cpy, start_point, end_point_tmp, color=col, thickness=-1)
        cv2.imshow('pix2pix', rect_cpy)

        # print ("Drawing") #callback during drawing

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        resized_image = cv2.resize(img[41:553, 0:512], (256, 256))
        cv2.imwrite("image.jpg", resized_image)
        print ("Image saved!, go for tensorflow")


cv2.destroyAllWindows()