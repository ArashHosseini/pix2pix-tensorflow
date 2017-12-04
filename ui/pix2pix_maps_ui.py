'''
Created on Dec 4, 2017

@author: flyn
'''
import cv2
import numpy as np
from utility import inference_utility, inference_config

rect_endpoint_tmp = []
rect_bbox = []
drawing = False
mode = False
brush_size = 5
col = (205, 220, 175)[::-1]

img = np.zeros((553, 512, 3), np.uint8)
map_img = cv2.imread(inference_config.maps_init_file)
img[41:553, 0:512] = map_img

drawing_area = [(-1000, 40), (1000, 1000)]
cv2.rectangle(img, (0, 0), (512, 40), (128, 128, 128), -1)

box_size = (128, 30)

# color buttons
buttons_dict = {"Street": (255, 255, 255),
                "Block": (230, 230, 225),
                "Grass": (205, 220, 175),
                "Buildings": (245, 240, 235)}

color_positions = {}

for k, v in enumerate(buttons_dict.items()):

    button_color = v[1][::-1]
    button_text = v[0]

    first_point = (((k + 1) * box_size[0]), 0)
    second_point = (k * box_size[0], box_size[1])
    color_positions[button_color] = [first_point, second_point]
    
    cv2.rectangle(img, first_point, second_point, button_color, -1)
    cv2.putText(img, button_text, (((k + 1) * box_size[0]) - box_size[0], box_size[1] + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))


def send_to_process():
    resized_image = cv2.resize(img[41:553, 0:512], (256, 256))
    cv2.imwrite(tmp_, resized_image)
    while post.empty():
        post.put(tmp_)
        return
    
def get_from_process():
    while not get.empty():
        inference = get.get()
        inference_read = cv2.imread(inference)
        cv2.imshow('INFERENCE', inference_read)

def draw_rectangle(event, x, y, flags, param):
    
        global rect_bbox, rect_endpoint_tmp, drawing, mode, col, brush_size
    
        if event == cv2.EVENT_LBUTTONDOWN:
            rect_endpoint_tmp = []
            
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
                
                send_to_process()

                if mode:
                    cv2.rectangle(img, p_1, p_2, color=col, thickness=-1)
                    cv2.imshow('pix2pix', img)

                    p_1x, p_1y = p_1
                    p_2x, p_2y = p_2

                    lx = min(p_1x, p_2x)
                    ty = min(p_1y, p_2y)
                    rx = max(p_1x, p_2x)
                    by = max(p_1y, p_2y)
                
                    if (lx, ty) != (rx, by):
                        bbox = [lx, ty, rx, by]
                else:
                    cv2.circle(img, (x, y), brush_size, col, -1)            
                    cv2.imshow('pix2pix', img)

                # print ("Drawing Done") ################################# ARASH - callback when drawing is done

        elif event == cv2.EVENT_MOUSEMOVE and drawing:
                if drawing_area[0][0] < x < drawing_area[1][0] and drawing_area[0][1] < y < drawing_area[1][1]:
                    if mode:
                        rect_endpoint_tmp = [(x, y)]
                    else:
                        cv2.circle(img, (x, y), brush_size, col, -1)
                        cv2.imshow('pix2pix', img)

img_copy = img.copy()
cv2.namedWindow('pix2pix')
tmp_ = inference_config.maps_tmp_file
cv2.setMouseCallback('pix2pix', draw_rectangle)

post, get, pool, killer = inference_utility.process_handler("maps")

while True:

    if not drawing:
        cv2.imshow('pix2pix', img)

    elif drawing and rect_endpoint_tmp:
        rect_cpy = img.copy()
        start_point = rect_bbox[0]
        end_point_tmp = rect_endpoint_tmp[0]
        if mode:
            cv2.rectangle(rect_cpy, start_point, end_point_tmp, color=col, thickness=-1)
            cv2.imshow('pix2pix', rect_cpy)
        else:
            rect_cpy = img.copy()
            cv2.circle(rect_cpy, (x, y), brush_size, col, -1)            
            cv2.imshow('pix2pix', rect_cpy)

            # print ("Drawing") ################################# ARASH - callback during drawing

    key = cv2.waitKey(1) & 0xFF
    get_from_process()

    if key == ord('q'):
        break

    if key == ord('m'):
        mode = not mode

    if key == ord('+'):
        brush_size += 1

    if key == ord('-'):
        brush_size -= 1

    if key == ord('s'):
        resized_image = cv2.resize(img[41:553, 0:512], (256, 256))
        cv2.imwrite("image.jpg", resized_image)
        print ("Image saved!, go for tensorflow")


cv2.destroyAllWindows()
