# AugmentData.py

import albumentations as A
import cv2
import os
from tqdm import tqdm

"""
This script augments images/Yolo annotation txt files for
training Ultralytics YOLO DNN. User must provide path to the folder
where the images/annotation txt files are located, and modify the desired
augmentation techniques.

Be sure to review A.Compose section of code as this is the portion where you
will define the applied augmentations. Parameters can be modified and
additional available augmentation techniques can be inserted in this section.
Details of available augmentations can be found at
https://albumentations.ai/docs/api_reference/augmentations/

Augmented images/annotation txt files are placed into the original directory.

Requires: pip install albumentations
          pip install opencv-python
          pip install tqdm
          
"""

num_augment=2 # Number of desired additional augmented images, must be int greater than 1
input_dir=r'/home/bandofpv/EW309/DATASET/train'

# --------------------------------------------

# Verify user inputs
if os.path.exists(input_dir):
    pass
else:
    print('User entered directory does not exist.')
    exit()

if isinstance(num_augment,int) and num_augment > 1:
    pass
else:
    print('Desired number of augmentations is invalid.')
    exit()
    
# Locate image files
image_files = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
if len(image_files) < 1:
    print('Images not found. Ensure that you specified the folder path where your images/annotation files are located.')
    exit()
else:
    print(f'Augmenting training set x{num_augment}.\n')

# Augment all images specified number 
for image_file in tqdm(image_files, desc="Augmenting images"):
    filename=image_file
    image_filename = os.path.splitext(filename)[0]
    image_extension = os.path.splitext(filename)[1]

    image=cv2.imread(os.path.join(input_dir,filename))
    class_labels=[]
    bboxes=[]
    if os.path.exists(os.path.join(input_dir, image_filename+'.txt')):
        with open(os.path.join(input_dir, image_filename+'.txt')) as f:
            for line in f:
                line = line.strip().split()
                if line and len(line) == 5:
                    class_labels.append(line[0])
                    bboxes.append([float(x) for x in line[1:5]])

    for n in range(num_augment):
        # Desired augmentation transforms are inserted in A.Compose
        transform = A.Compose([
            A.BBoxSafeRandomCrop(erosion_rate=0.1, p=0.8),
            #A.RandomBrightnessContrast(p=0.5),
            A.ColorJitter(brightness=0.6, contrast=0.2, saturation=0.2, hue=0, p=0.8)
        ], bbox_params=A.BboxParams(format='yolo', min_visibility=0.3, label_fields=['class_labels']))
        transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)

        if len(class_labels)>0:
            with open(os.path.join(input_dir, image_filename+f'_a{n}.txt'),'w') as f:
                for i in range(len(transformed['class_labels'])):
                    annotation_list=[transformed['class_labels'][i]]+[str(x) for x in transformed['bboxes'][i]]
                    annotations=' '.join(annotation_list)
                    f.write(f'{annotations}\n')
        cv2.imwrite(os.path.join(input_dir, image_filename+f'_a{n}'+image_extension),transformed['image'])
