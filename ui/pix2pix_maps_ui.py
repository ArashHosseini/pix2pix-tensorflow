'''
Created on Dec 4, 2017

@author: flyn
'''
import cv2
import argparse
import numpy as np
from utility import inference_utility, inference_config
import threading
import socket
import os
import json
import logging.config


logging.config.fileConfig('{0}/utility/_logging/pixi_logging.conf'.format(os.path.abspath(os.path.dirname(__file__))))
logger= logging.getLogger('pix2pix')

support = ["maps", "facades"]

class Pix2Pix_Maps(threading.Thread):
    def __init__(self, segment = [], inference_mode = "maps", interval=0.09, *args):
        self.inference_mode = inference_mode 
        self.tmp_ = inference_config.maps_tmp_file if self.inference_mode == "maps" else inference_config.tmp_file
        self.buttons_dict = inference_config.maps_buttons_dict if self.inference_mode == "maps" else inference_config.buttons_dict
        self.color_positions = {}
        self.segment = segment
        self.min = 0
        self.max = 0
        self.resized_inf_img = []
        self.rect_endpoint_tmp = []
        self.rect_bbox = []
        self.drawing = False
        self.drawing_area = [(-1000, 45), (508, 1000)]
        self.funcs = []
        self.interval = interval
        
        self.img = np.zeros((553, 1024, 3), np.uint8)
        self.draw_map_curves_in_maya = True
        self.host = 'localhost'
        self.port = 7002
        self.warm_up = False
        self.output_label = "connected to maya"

        self.set_inference_mode()

    def set_inference_mode(self, *args):
        if self.inference_mode == "maps":
            if self.draw_map_curves_in_maya:
                if inference_utility.check_maya_connection(self.host,
                                                            self.port,
                                                            logger):
                
                    self.init_map_in_maya(host=self.host, port=self.port)
                else:
                    self.output_label = " maya connection failed!"

            self.mode = False
            self.col = inference_config.maps_buttons_dict["Grass"][::-1]
            self.map_img = cv2.imread(inference_config.maps_init_file)
            self.map_out = cv2.imread(inference_config.output_maps_file)
            self.img[41:553, 0:512] = self.map_img
            self.img[41:553, 512:1024] = cv2.resize(self.map_out, (512, 512))
            self.img[0:41, 513:1024] = (0,0,0)
            cv2.rectangle(self.img, (0, 0), (512, 40), (128, 128, 128), -1)

            self.box_size = (128, 30)
            self.brush_size = 5
        elif self.inference_mode == "facades":
            self.mode = True
            self.col = (0,0,255)
            self.img[:] = (13,61,251)[::-1]
            cv2.rectangle(self.img, (0, 0), (512, 40), (255,255,255), -1)
            self.box_size = (47,30)
            
        cv2.putText(self.img, "OUTPUT", (550, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
        cv2.putText(self.img, self.output_label, (750, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))


    def setup_draw_btn_line(self, *args):
        for k, (button_text, button_color) in enumerate(self.buttons_dict.items()):

            button_color = button_color[::-1]
            first_point = (((k + 1) * self.box_size[0]), 0)
            second_point = (k * self.box_size[0], self.box_size[1])
            self.color_positions[button_color] = [first_point, second_point]
            cv2.rectangle(self.img, first_point, second_point, button_color, -1)
            cv2.putText(self.img, button_text, (((k + 1) * self.box_size[0]) - self.box_size[0], self.box_size[1] + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, self.col)


    def send_to_process(self, *args):
        if not self.warm_up:
            logger.info("Warm up, take a while....")
            self.warm_up = not self.warm_up
        resized_image = cv2.resize(self.img[41:553, 0:512], (256, 256))
        cv2.imwrite(self.tmp_, resized_image)
        while self.post.empty():
            self.post.put(self.tmp_)
            logger.debug("main sent {0}".format(self.tmp_))
            return
        
    def get_from_process(self, resize=True, *args):
        while not self.get.empty():
            inference = self.get.get()
            logger.debug("main get {0}".format(inference))
            inference_read = cv2.imread(inference)
            self.resized_inf_img = cv2.resize(inference_read, (512, 512))
            
    def beat(self, *args):
        if self.inference_mode == "maps":
            self.get_from_process()
        self.heart()
            
    def heart(self, *args):
        self.send_to_process()
        if self.drawing:
            threading.Timer(float(self.interval), self.beat).start()

    def init_map_in_maya(self, host='localhost', port=7002):
        logger.debug("init_map_in_maya")
        script_dir = (os.path.join(os.path.join(os.getcwd(), "utility"), "maps_sandbox"))        
        curves_data = json.load(open(script_dir + "/init_map.json"))

        maya_cmd = "import sys; sys.path.append('%s');" %script_dir
        maya_cmd += "import init_map; reload(init_map); init_map.init_map_in_maya(%s)"%curves_data

        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, port))
        clientsocket.send(maya_cmd.encode('utf-8'))
        logger.debug("sent init map to maya")

    def draw_curve_in_maya(self, curve_points, host='localhost', port=7002):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, port))
        clientsocket.send(("cmds.curve(p=%s)"%str(curve_points)).encode('utf-8'))
        logger.debug("sent curve to maya")
        
    def draw_rectangle(self, event, x, y, flags, param):
        self.x = x
        self.y = y
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing_points = []
            self.start_point = (x,0,y)
            self.rect_endpoint_tmp = []
            
            for color, position in self.color_positions.items():

                if self.x in range(position[1][0], position[0][0]) and self.y in range(position[0][1], position[1][1]):
                    self.col = color
                    current_selection = (list(self.buttons_dict.keys())[list(self.buttons_dict.values()).index(self.col[::-1])])
                    logger.info('Switched to {0}'.format(current_selection))
                    break

            if self.x in range(self.drawing_area[0][0], self.drawing_area[1][0]) and self.y in range(self.drawing_area[0][1], self.drawing_area[1][1]):
                self.rect_bbox = [(x, y)]
                self.drawing = True
                
            if not self.heart in self.funcs:
                self.funcs.append(self.heart)
                self.heart()

        elif event == cv2.EVENT_LBUTTONUP:
            # self.end_point = (x,0,y)
            
            if self.drawing_area[0][0] < self.x < self.drawing_area[1][0] and self.drawing_area[0][1] < self.y < self.drawing_area[1][1]:

                self.rect_bbox.append((self.x, self.y))
                self.drawing = False
            
                p_1, p_2 = self.rect_bbox

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
                if self.heart in self.funcs:
                    self.funcs.remove(self.heart)
                #self.draw_curve_in_maya(self.drawing_points, host=self.host, port=self.port)


        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
                if not self.heart in self.funcs:
                    self.funcs.append(self.heart)
                    self.heart()
                if self.drawing_area[0][0] < x < self.drawing_area[1][0] and self.drawing_area[0][1] < y < self.drawing_area[1][1]:
                    self.drawing_points.append((x,0,y))
                    if self.inference_mode == "facades":
                        self.rect_endpoint_tmp = [(x, y)]
                    else:
                        cv2.circle(self.img, (x, y), self.brush_size, self.col, -1)
                        cv2.imshow('pix2pix', self.img)
    
    def set_min(self, value,*args):
        self.min = value
    
    def set_max(self, value, *args):
        self.max = value
                            
    def draw_run(self, *args):
        img = self.img.copy()
        cv2.namedWindow('pix2pix')
        cv2.imshow('pix2pix', self.img)       
        cv2.setMouseCallback('pix2pix', self.draw_rectangle)
        
        self.post, self.get, self.pool, self.killer = inference_utility.process_handler( 
                                                                                        self.inference_mode,
                                                                                        logger
                                                                                        )
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if len(self.resized_inf_img):
                self.img[41:553, 512:1024] = cv2.resize(self.resized_inf_img, (512, 512))
                cv2.imshow('pix2pix', self.img)

            elif self.drawing and self.rect_endpoint_tmp:
                rect_cpy = self.img.copy()
                start_point = self.rect_bbox[0]
                end_point_tmp = self.rect_endpoint_tmp[0]
                if self.mode:
                    cv2.rectangle(rect_cpy, start_point, end_point_tmp, color=self.col, thickness=-1)
                else:
                    rect_cpy = self.img.copy()
                    cv2.circle(rect_cpy, (self.x, self.y), self.brush_size, self.col, -1)
                
                cv2.imshow('pix2pix', rect_cpy)
        
        
            if key == ord('q'):
                self.killer.value = True
                for _process in self.pool:
                    logger.info("exiting {0}".format(_process))
                    logger.debug("kill local inference process")
                    _process.join()
                break
            
            if self.inference_mode == "maps":
                if key == ord('m'):
                    self.mode = not self.mode
                    
            if not self.drawing:
                if self.inference_mode == "facades":
                    self.get_from_process()
        
            if key == ord('+'):
                logger.debug("up scale brush size")
                self.brush_size += 1
        
            if key == ord('-'):
                logger.debug("down scale brush size")
                self.brush_size -= 1

        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pix2Pix Inference Module')
    parser.add_argument('-m', '--mode',
                        action="store",
                        dest='inference_mode',
                        help='select inference mode, default is maps',
                        default="maps")
    parser.add_argument('-s', '--segment',
                        dest='segment',
                        help='segement detection like street, block, grass and buildings',
                        default="street",
                        nargs='+')
    parser.add_argument('-i', '--interval',
                        action="store",
                        dest='interval',
                        help='heartbeat interval',
                        default=0.06)
    parser.add_argument('-v',
                        action="store",
                        dest='verbose',
                        help="0:Error, 1:Warning, 2:INFO*(default), 3:debug",
                        default=2,
                        type=int)
    results = parser.parse_args()
    
    level = {0:logging.ERROR,
             1:logging.WARNING,
             2:logging.INFO,
             3:logging.DEBUG}
    
    logger.setLevel(level[results.verbose])

    if not results.inference_mode in support:
        raise Exception("{0} not supported yet".format(results.inference_mode))
    _inference_mode = results.inference_mode

    draw = Pix2Pix_Maps(results.segment,
                        _inference_mode,
                        results.interval)
    draw.setup_draw_btn_line()
    draw.draw_run()

