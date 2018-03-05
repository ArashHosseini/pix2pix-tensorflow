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
import inference_utility, inference_config
import time


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="path to input images dir")
ap.add_argument("-a", "--alpha", required=True,
    help="path to input images alpha dir")
ap.add_argument("-o", "--output", required=True,
    help="path to merged output dir")
ap.add_argument("-s", "--seq", required=False,
    help="path to merged output dir")
ap.add_argument("-p", "--prefix", required=True,
    help="path to merged output dir")
args = vars(ap.parse_args())

image_dir = args["image"]
alpha_dir = args["alpha"]
output_dir = args["output"]

images = iter(sorted(os.listdir(image_dir)))

if args["seq"]:
    alpha_dir = os.path.dirname(alpha_dir)
    alphas = iter(os.listdir(alpha_dir))
    alphas = iter(sorted([a for a in alphas if "color" in a]))
else:
    alphas = iter(sorted(os.listdir(alpha_dir)))

end_reached = 0
n = 464
while not end_reached:
    try:
        print ("-------------------------------------------")
        print (">>>>>", os.path.join(image_dir,next(images)))
        print (">>>>>", os.path.join(alpha_dir,next(alphas)))

        color_image = cv2.imread(os.path.join(image_dir,next(images)))
        alpha = cv2.imread(os.path.join(alpha_dir,next(alphas)))


        crop_img = color_image[0:1024,512:1024+512].copy()
        crop_alpha = alpha[0:1024,512:1024+512].copy()

        image = np.concatenate((crop_img, crop_alpha), axis=1)
        resized = cv2.resize(image, (2048, 1024))
        cv2.imwrite(os.path.join(output_dir, "{1}_{0}.jpg".format(str(n), args["prefix"])), resized)
        n += 1
    except StopIteration:
        end_reached = True