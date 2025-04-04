import cv2
import datetime
import os
import json
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm

"""
This script prepares images/AnyLabeling JSON annotation files for
training Ultralytics YOLO DNN. User must modify the class_labels to
match those selected in AnyLabeling, provide path to the folder where
the images/JSON files are located, and specify the percentage of
images to set aside for validation.

Script built from https://github.com/ultralytics/JSON2YOLO.git

Usage: EW309_YoloPrep.py

Requires: pip install opencv-python
          pip install json
          pip install shutil
          pip install scikit-learn
          pip install tqdm

"""


# Define the class labels, should match those used when you labeled images for training
class_labels = {"orange": 0, "red": 1, "yellow": 2} # {"Name1": Label#,"Name2": Label2#,...,"Namen": Labeln#}

# Define the input directory and ensure that output directories do not already exist
input_dir = r'/home/bandofpv/EW309/DATASET' # Replace with your directory

# Default output directory for use with other EW309 scripts
output_dir = r'/home/bandofpv/EW309/DATASET' # Replace with your directory

# --------------------------------------------

# Determine if old train/validate data exists in folder and move it to another directory
train_dir = os.path.join(output_dir, 'train')
validate_dir = os.path.join(output_dir, 'valid')
data_yaml = os.path.join(output_dir, 'data.yaml')
if (os.path.exists(train_dir) and os.path.isdir(train_dir)) or (os.path.exists(validate_dir) and os.path.isdir(validate_dir)):
    new_dir_name = 'Prior_data'
    counter=1
    while os.path.exists(new_dir_name):
        new_dir_name = f"Prior_data_{counter}"
        counter += 1
    os.makedirs(new_dir_name)
    if os.path.exists(train_dir):
        shutil.move(train_dir,os.path.join(input_dir,new_dir_name))
    if os.path.exists(validate_dir):
        shutil.move(validate_dir,os.path.join(input_dir,new_dir_name))
    # Move data.yaml only if existing train and/or validate directories exist
    if (os.path.exists(data_yaml) and os.path.isfile(data_yaml)):
        shutil.move(data_yaml,os.path.join(input_dir,new_dir_name))
    
# Define the train-validate split
split_ratio = 0.2 # 20% of the data will go to the validation set

# Specify YOLO input image size
yolo_size =  []# Should be multiple of 32 for faster processing, px
if not yolo_size or (yolo_size%32 != 0):
    yolo_size = 640 # Default YOLO image size, px 

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Create train and validate directories
os.makedirs(train_dir, exist_ok=True)

if split_ratio > 0:
    os.makedirs(validate_dir, exist_ok=True)

# Locate image/json files
image_files = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
if len(image_files) < 1:
    print('Images not found. Ensure that you specified the folder path where your images/files are located.')
    exit()
else:
    print('Preparing images/files for Yolo.')

if split_ratio > 0:
    train_images, validate_images = train_test_split(image_files, test_size=split_ratio)
else:
    train_images = image_files
json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

# Copy all images to train and validate directories, resize if required
for image_file in tqdm(image_files, desc="Copying images"):
    current_output_dir = train_dir if image_file in train_images else validate_dir
    shutil.copy(os.path.join(input_dir, image_file), current_output_dir)
    img = cv2.imread(os.path.join(current_output_dir, image_file))
    # Resize image as square, if required
    if img.shape[:2] != (yolo_size,yolo_size):
        resized_img = cv2.resize(img,(yolo_size,yolo_size))
        cv2.imwrite(os.path.join(current_output_dir, image_file),resized_img)

# Use tqdm for progress bar
for filename in tqdm(json_files, desc="Converting annotations"):
    with open(os.path.join(input_dir, filename)) as f:
        data = json.load(f)

    image_filename = filename.replace('.json', '')
    if any(os.path.isfile(os.path.join(input_dir, image_filename + ext)) for ext in ['.jpg', '.png', '.jpeg']):
        if image_filename + '.jpg' in train_images or image_filename + '.png' in train_images or image_filename + '.jpeg' in train_images:
            current_output_dir = train_dir
        else:
            current_output_dir = validate_dir

        with open(os.path.join(current_output_dir, filename.replace('.json', '.txt')), 'w') as out_file:
            for shape in data['shapes']:
                class_label = shape['label']
                if class_label in class_labels:
                    x1, y1 = shape['points'][0]
                    x2, y2 = shape['points'][1]

                    dw = 1. / data['imageWidth']
                    dh = 1. / data['imageHeight']
                    w = x2 - x1
                    h = y2 - y1
                    x = x1 + (w / 2)
                    y = y1 + (h / 2)

                    x *= dw
                    w *= dw
                    y *= dh
                    h *= dh

                    out_file.write(f"{class_labels[class_label]} {x} {y} {w} {h}\n")

# Produce the yolo data.yaml file
with open(os.path.join(input_dir,'data.yaml'), "w") as f:
    f.write(f'train: {train_dir}\n') # {os.path.join(train_dir)}
    f.write(f'val: {validate_dir}\n') # {os.path.join(validate_dir)}
    f.write(f'nc: {len(class_labels.keys())}\n')
    f.write(f'names: [\'')
    f.write('\',\n        \''.join(class_labels.keys()))
    f.write('\'\n]')

print("Conversion and split completed successfully!")
