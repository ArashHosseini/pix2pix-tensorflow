'''
Created on Dec 4, 2017

@author: flyn
'''
import cv2
import argparse
import numpy as np
from utility import inference_utility, inference_config

class Pix2Pix_Draw(object):
    def __init__(self, *args):

        self.rect_endpoint_tmp = []
        self.rect_bbox = []
        self.drawing = False
        self.mode = False
        self.brush_size = 5
        self.col = (205, 220, 175)[::-1]

        self.img = np.zeros((553, 512, 3), np.uint8)
        self.map_img = cv2.imread(inference_config.maps_init_file)
        self.img[41:553, 0:512] = self.map_img

        self.drawing_area = [(-1000, 40), (1000, 1000)]
        cv2.rectangle(self.img, (0, 0), (512, 40), (128, 128, 128), -1)

        self.box_size = (128, 30)
        self.tmp_ = inference_config.maps_tmp_file# if mode == "maps" else inference_config.tmp_file
        self.buttons_dict = inference_config.maps_buttons_dict# if mode == "maps" else inference_config.buttons_dict
        self.color_positions = {}


    def setup_draw_btn_line(self, *args):
        for k, v in enumerate(self.buttons_dict.items()):
            button_color = v[1][::-1]
            button_text = v[0]

            first_point = (((k + 1) * self.box_size[0]), 0)
            second_point = (k * self.box_size[0], self.box_size[1])
            self.color_positions[button_color] = [first_point, second_point]
    
            cv2.rectangle(self.img, first_point, second_point, button_color, -1)
            cv2.putText(self.img, button_text, (((k + 1) * self.box_size[0]) - self.box_size[0], self.box_size[1] + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))


    def send_to_process(self, *args):
        resized_image = cv2.resize(self.img[41:553, 0:512], (256, 256))
        cv2.imwrite(self.tmp_, resized_image)
        while self.post.empty():
            self.post.put(self.tmp_)
            return
        
    def get_from_process(self, *args):
        while not self.get.empty():
            inference = self.get.get()
            inference_read = cv2.imread(inference)
            cv2.imshow('INFERENCE', inference_read)

    def draw_rectangle(self, event, x, y, flags, param):
        self.x = x
        self.y = y
    
        if event == cv2.EVENT_LBUTTONDOWN:
            self.rect_endpoint_tmp = []
            
            for color, position in self.color_positions.items():

                if self.x in range(position[1][0], position[0][0]) and self.y in range(position[0][1], position[1][1]):
                    self.col = color
                    current_selection = (list(self.buttons_dict.keys())[list(self.buttons_dict.values()).index(self.col[::-1])])
                    print('Switched to {0}'.format(current_selection))
                    break

            if self.x in range(self.drawing_area[0][0], self.drawing_area[1][0]) and self.y in range(self.drawing_area[0][1], self.drawing_area[1][1]):
                self.rect_bbox = [(x, y)]
                self.drawing = True

        elif event == cv2.EVENT_LBUTTONUP:

            if self.drawing_area[0][0] < self.x < self.drawing_area[1][0] and self.drawing_area[0][1] < self.y < self.drawing_area[1][1]:

                self.rect_bbox.append((self.x, self.y))
                self.drawing = False
            
                p_1, p_2 = self.rect_bbox
                
                self.send_to_process()

                if self.mode:
                    cv2.rectangle(self.img, p_1, p_2, color=self.col, thickness=-1)
                    cv2.imshow('pix2pix', self.img)

                    p_1x, p_1y = p_1
                    p_2x, p_2y = p_2

                    lx = min(p_1x, p_2x)
                    ty = min(p_1y, p_2y)
                    rx = max(p_1x, p_2x)
                    by = max(p_1y, p_2y)
                
                    if (lx, ty) != (rx, by):
                        _ = [lx, ty, rx, by]
                else:
                    cv2.circle(self.img, (self.x, self.y), self.brush_size, self.col, -1)            
                    cv2.imshow('pix2pix', self.img)

                # print ("Drawing Done") ################################# ARASH - callback when drawing is done

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
                if self.drawing_area[0][0] < x < self.drawing_area[1][0] and self.drawing_area[0][1] < y < self.drawing_area[1][1]:
                    if self.mode:
                        self.rect_endpoint_tmp = [(x, y)]
                    else:
                        cv2.circle(self.img, (x, y), self.brush_size, self.col, -1)
                        cv2.imshow('pix2pix', self.img)
                            
    def draw_run(self, *args):
        img = self.img.copy()
        cv2.namedWindow('pix2pix')
        cv2.setMouseCallback('pix2pix', self.draw_rectangle)
        
        self.post, self.get, self.pool, self.killer = inference_utility.process_handler("maps")
        
        while True:
        
            if not self.drawing:
                cv2.imshow('pix2pix', self.img)
        
            elif self.drawing and self.rect_endpoint_tmp:
                rect_cpy = self.img.copy()
                start_point = self.rect_bbox[0]
                end_point_tmp = self.rect_endpoint_tmp[0]
                if self.mode:
                    cv2.rectangle(rect_cpy, start_point, end_point_tmp, color=self.col, thickness=-1)
                    cv2.imshow('pix2pix', rect_cpy)
                else:
                    rect_cpy = self.img.copy()
                    cv2.circle(rect_cpy, (self.x, self.y), self.brush_size, self.col, -1)            
                    cv2.imshow('pix2pix', rect_cpy)
        
            key = cv2.waitKey(1) & 0xFF
            self.get_from_process()
        
            if key == ord('q'):
                self.killer.value = True
                for _process in self.pool:
                    print "killing process", _process
                    _process.join()
                break
        
            if key == ord('m'):
                self.mode = not self.mode
        
            if key == ord('+'):
                self.brush_size += 1
        
            if key == ord('-'):
                self.brush_size -= 1
        
            if key == ord('s'):
                resized_image = cv2.resize(img[41:553, 0:512], (256, 256))
                cv2.imwrite("image.jpg", resized_image)
                print ("Image saved!, go for tensorflow")

        cv2.destroyAllWindows()

if __name__ == "__main__":
    draw = Pix2Pix_Draw()
    draw.setup_draw_btn_line()
    draw.draw_run()
    

