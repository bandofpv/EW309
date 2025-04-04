from ultralytics import YOLO
import datetime
import os

"""
This script takes the output of EW309_YoloPrep.py and trains Ultralytics
YOLO DNN v8 or v11. User must select model size and version. If you have already
trained a yolo model, you may start training using it as the basis (a significant)
time saver!

Recommend running with the default 3 eepochs the first time to verify that the
date input/output works. Once completed, increase epochs up to 150 and run again.
More epochs increases model performance at the expense of more training time.

This script can be modified if you have an NVIDIA GPU to significantly reduce training
time.

Usage: EW309_YoloTrainingCPU.py

Requires: pip install ultralytics
          pip install datetime

"""

# Model Size: uncomment the model size you desire, set the variables as desired
#             inference speed (FPS) performance improves with smaller models
# ModelSize = 'Nano'
ModelSize = 'Small'
# ModelSize = 'Medium'
# ModelSize = 'Large'
# ModelSize = 'Extra Large'

# Yolo Version
# yolo_version = '8'
yolo_version = '11'

# Prior trained model:
#prior_model = ''
prior_model = 'yolo_100.pt'

# Epochs: select a larger number to improve the model performance, 150 is a good
#         starting value
total_number_of_epochs = 100

# Image Size: Must be a multiple of 32 (2^5), YOLOv8 assumes square images,
#             640x640 pixels is the default size, newer versions support rectangular images
image_size = 640

# Path to data: Point to the directory where the data.yaml and train/validate
#               directories are located 
path_to_my_data = r'/home/bandofpv/EW309/DATASET'

# -----------------------------------------------
if prior_model:
    my_weights_filename = prior_model
elif yolo_version == '8':
    if ModelSize == 'Nano':
        my_weights_filename = 'yolov8n.pt'
    if ModelSize == 'Small':
        my_weights_filename = 'yolov8s.pt'
    if ModelSize == 'Medium':
        my_weights_filename = 'yolov8m.pt'
    if ModelSize == 'Large':
        my_weights_filename = 'yolov8l.pt'
    if ModelSize == 'Extra Large':
        my_weights_filename = 'yolov8x.pt'
elif yolo_version == '11':
    if ModelSize == 'Nano':
        my_weights_filename = 'yolo11n.pt'
    if ModelSize == 'Small':
        my_weights_filename = 'yolo11s.pt'
    if ModelSize == 'Medium':
        my_weights_filename = 'yolo11m.pt'
    if ModelSize == 'Large':
        my_weights_filename = 'yolo11l.pt'
    if ModelSize == 'Extra Large':
        my_weights_filename = 'yolo11x.pt'
else:
    print('Error with weights')
    exit()

print(my_weights_filename)
model = YOLO(my_weights_filename)

now = datetime.datetime.now()
results_folder = os.path.join(path_to_my_data,f'YOLO_Output_{now.month}_{now.day}_{now.hour}{now.minute}')
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
    
results=model.train(data=os.path.join(path_to_my_data,'data.yaml'),epochs=total_number_of_epochs,imgsz=image_size,patience=0,project=results_folder,device=0,plots=True)
path = model.export(format="onnx")

name,ext=os.path.splitext(os.path.basename(my_weights_filename))
print(name)
new_weights_name = name + f'_{now.month}_{now.day}_{now.hour}{now.minute}'
path_to_models = os.path.join(results_folder,r'train/weights')
path_to_pt = os.path.join(path_to_models,'best.pt')
pt_with_path = os.path.join(path_to_models,new_weights_name+'.pt')
path_to_onnx = os.path.join(path_to_models,'best.onnx')
onnx_with_path = os.path.join(path_to_models,new_weights_name+'.onnx')
os.rename(path_to_pt,pt_with_path)
os.rename(path_to_onnx,onnx_with_path)
