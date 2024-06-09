import numpy as np
from keras.models import load_model
import os
from PIL import Image
 

class cnn_model_eval():
    def __init__(self, model_path, image_path, labels, user_folder_path):
        self.model_path = model_path
        self.image_path = image_path
        self.user_folder_path = user_folder_path
        self.labels = labels
        
    def get_model_input_size(self):
        model = load_model(self.model_path,  compile=False)
        inputs = model.input_shape
        clean_outputs = tuple(inputs[1:3])  # We only need the first two dimensions
        return clean_outputs

    def resize_img(self):
        image = Image.open(self.image_path)
        # Check if the image is grayscale, if so, convert it to RGB
        if image.mode == 'L':
            image = image.convert('RGB')
        
        size = cnn_model_eval.get_model_input_size(self)

        resized = image.resize(size)  # Resize directly to the desired input size
        resized = np.array(resized)  # Convert to numpy array

        resized = Image.fromarray(resized)
        
        # Convert to RGB mode
        resized = resized.convert('RGB')
        
        # Print the converted image mode
        print("Converted image mode:", resized.mode)
        
        # Save the image to check separately
        resized_img_path = os.path.join(self.user_folder_path, "output_image.jpg")
        resized.save(resized_img_path)
        
        resized.close()
        image.close()
        return resized_img_path

    def model_prediction(self):
        
        img = Image.open(cnn_model_eval.resize_img(self))
        model = load_model(self.model_path)
        
        preprocessed_image = np.array(img) / 255.0

        preds = model.predict(np.expand_dims(preprocessed_image, axis=0))

        preds_class = np.argmax(preds)

        preds_label = self.labels[preds_class]
        Confidence = preds[0][preds_class]
        img.close()
        return Confidence, preds_label

def get_labels(model_path):
    model = load_model(model_path)
    output = model.output_shape
    num_of_classes = output[1]
    
    return num_of_classes
    
        

