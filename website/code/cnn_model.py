import numpy as np
import pandas as pd
import tensorflow as tf
from keras.utils import load_img
from keras.models import Sequential,load_model
import matplotlib.pyplot as plt
import os
from PIL import Image
 



def get_model_input_size(model_path):
    model = load_model(model_path)
    clean_outputs = []

    inputs = model.input
    for input in inputs:
        if input != None:
            clean_outputs.append(input)
            
    return(clean_outputs)

def resize_img(image_path):
    image = Image.open(image_path)
    crop_image = image.resize()
    crop_image.save(image_path)
    

def model_evaluation(model_path):
    model = load_model(model_path)
    
    # Obtaining Loss and Accuracy on the val dataset
    val_loss, val_acc = model.evaluate()

    return val_loss, val_acc
