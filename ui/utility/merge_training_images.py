'''
Created on Dec 4, 2017

@author: flyn
'''

from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2
import os
import logging.config
from utility import inference_utility, inference_config
import time


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="path to input images dir")
ap.add_argument("-a", "--alpha", required=True,
    help="path to input images alpha dir")
ap.add_argument("-o", "--output", required=True,
    help="path to merged output dir")
args = vars(ap.parse_args())

image_dir = args["image"]
alpha_dir = args["alpha"]
output_dir = args["output"]

images = iter(os.listdir(image_dir))
alphas = iter(os.listdir(alpha_dir))

end_reached = 0
n = 0

while not end_reached:
    try:
        color_image = cv2.imread(os.path.join(image_dir,next(images)))
        alpha = cv2.imread(os.path.join(alpha_dir,next(alphas)))

        image = np.concatenate((color_image, alpha), axis=1)
        resized = cv2.resize(image, (2048, 1024))
        cv2.imwrite(os.path.join(output_dir, "cloud_{0}.jpg".format(str(n))), resized)
        n += 1
    except StopIteration:
        end_reached = True