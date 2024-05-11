import numpy as np
import pandas as pd
import tensorflow as tf
from keras.utils import load_img
from keras.models import Sequential,load_model
import matplotlib.pyplot as plt
import os
from PIL import Image
 

class cnn_model():
    def __init__(self, model_path, image_path, labels):
        self.model_path = model_path
        self.image_path = image_path
        self.labels = labels
        
    def get_model_input_size(self):
        model = load_model(self.model_path)
        inputs = model.input.shape
        clean_outputs = tuple(inputs[1:3])  # We only need the first two dimensions
        return clean_outputs

    def resize_img(self):
        image = Image.open(self.image_path).convert('L')  # Convert image to grayscale
        size = cnn_model.get_model_input_size(self)
        resized = image.resize(size)  # Resize directly to the desired input size
        resized = np.expand_dims(resized, axis=-1)  # Add grayscale channel
        resized = np.tile(resized, (1, 1, 3))  # Convert to RGB by repeating grayscale channel
        resized = Image.fromarray(resized)
        resized.save(self.image_path)
        image.close()


    def model_evaluation(self):
        model = load_model(self.model_path)
        val_loss, val_acc = model.evaluate()
        
        return val_loss, val_acc



    def model_prediction(self):
        cnn_model.resize_img(self)
        img = Image.open(self.image_path)
        model = load_model(self.model_path)
        
        preprocessed_image = np.array(img) / 255.0

        preds = model.predict(np.expand_dims(preprocessed_image, axis=0))

        preds_class = np.argmax(preds)

        preds_label = self.labels[preds_class]
        Confidence = preds[0][preds_class]
        return Confidence, preds_label

def get_labels(model_path):
    model = load_model(model_path)
    output = model.output.shape
    num_of_classes = output[1]
    
    return num_of_classes
    
        

