'''
Created on Dec 2, 2017

@author: flyn
'''
# windows temporary fix
import sys, os
sys.path.append("%s/utility" %os.getcwd())

import numpy as np
import multiprocessing as mp
import tensorflow as tf
import json
import base64
import ctypes
import inference_config
import time
import socket

def check_maya_connection(host, port, logger):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientsocket.connect((host, port))
    except socket.error as e:
        logger.info("maya connection failed!!!")
        logger.debug("maya connection failed!!! {0}".format(e))
        return 
    else:
        return True
    


def process_handler(mode,
                    logger):
    live_process = []
    manager = mp.Manager()
    lifetime_end = manager.Value(ctypes.c_char_p, False)
    input_image_queue, output_image_queue = [mp.Queue() for _ in range(2)]
    img_cap_process = mp.Process(target=local_inference,
                                 args=(input_image_queue,
                                       output_image_queue,
                                       lifetime_end,
                                       mode,
                                       logger,))
    
    live_process.append(img_cap_process)
    logger.debug("starting local inference process")
    img_cap_process.start()
    
    return input_image_queue, output_image_queue, live_process, lifetime_end

def local_inference(input_image_queue,
                    output_image_queue,
                    lifetime_end,
                    mode,
                    logger,
                    *args):
    
    logger.info("local inference started")
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    with tf.Session(config=config) as sess:
        logger.debug("local inference session started with {0}".format(mode))
        if mode == "facades":
            output_file = inference_config.output_file
            model = inference_config.model
        else:
            model = inference_config.maps_model
            output_file = inference_config.output_maps_file 
        saver = tf.train.import_meta_graph(model + "/export.meta")
        saver.restore(sess, model + "/export")
        
        input_vars = json.loads(tf.get_collection("inputs")[0].decode('utf-8'))
        output_vars = json.loads(tf.get_collection("outputs")[0].decode('utf-8'))
        
        _input = tf.get_default_graph().get_tensor_by_name(input_vars["input"])
        output = tf.get_default_graph().get_tensor_by_name(output_vars["output"])
        while True:
            if not input_image_queue.empty():
                start = time.time()
                input_file = input_image_queue.get()
                logger.debug("local inference get {0}".format(input_file))
                # if input_file:
                with open(input_file, "rb") as f:
                    input_data = f.read()
        
                input_instance = dict(_input=base64.urlsafe_b64encode(input_data).decode("ascii"), key="0")
                input_instance = json.loads(json.dumps(input_instance))
        
                input_value = np.array(input_instance["_input"])
                output_value = sess.run(output, feed_dict={_input: np.expand_dims(input_value, axis=0)})[0]
        
                output_instance = dict(output=output_value.decode("ascii"), key="0")
            
                b64data = output_instance["output"]
                b64data += "=" * (-len(b64data) % 4)
                output_data = base64.urlsafe_b64decode(b64data.encode("ascii"))
                            
                with open(output_file, "wb") as f:
                    logger.debug("local inference open file {0}".format(output_file))
                    f.write(output_data)
                
                
                output_image_queue.put(output_file)
                logger.debug("local inference sent {0}".format(output_file))
                logger.info(time.time() - start)
    
            if lifetime_end.value:
                logger.debug("exiting local inference")
                break
