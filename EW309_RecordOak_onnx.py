# Requires OAK camera attached with USB3 cable and trained YOLO model
# depthai API vailable at: https://docs.luxonis.com/projects/api/en/latest/
# EW309 Computer Vision, P. Frontera, March 2024

import cv2
import depthai as dai
import datetime 
import os

import yolo # Adds class to perform NN detection/display

# onnx model and yaml file file
path_to_model = r"C:\Users\m260477\Desktop\EW309\yolo.onnx" # path to .onnx weights
path_to_yaml = r"C:\Users\m260477\Desktop\EW309\data.yaml" # path to data.yaml file used to train the model 
conf_thres = 0.15 # classification confidence threshold, 0.0-1.0
iou_thres = 0.15 # iou threshold, 0.0-1.0

# Flag to toggle video recording
record = False # Use True to record; use False for no recording

# Set up window
windowName = 'OAK-1 Live Stream'
windowSize = (1920, 1080) # Maintain aspect ratio (16:9) 

# Create pipeline    
pipeline = dai.Pipeline()

# Define source and output 
camRgb = pipeline.createColorCamera()
xoutRgb = pipeline.createXLinkOut()

# Camera Properties
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P) # THE_1080_P
camRgb.setPreviewSize(camRgb.getVideoSize()) # must match resolution, max 4K
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
camRgb.setFps(30)

xoutRgb.setStreamName("rgb")

# Linking
camRgb.preview.link(xoutRgb.input)

# Verify OAK connected, access OAK information
try:
    print(f'Product Name: {dai.Device(pipeline).getProductName()}')
    print(f'Connected Camera(s): {dai.Device(pipeline).getConnectedCameraFeatures()}')
except:
    print('OAK Camera not connected.')
    exit()

# Start pipeline
with dai.Device(pipeline) as device:
    # Get camera information 
    calibData = device.readCalibration()
    M_row1, M_row2, M_row3  = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A,640,480)
    fov = calibData.getFov(dai.CameraBoardSocket.CAM_A)
    print('Camera Intrinsic Matrix:')
    print(f'{M_row1}')
    print(f'{M_row2}')
    print(f'{M_row3}')
    print(f'Camera Horizontal FOV: {fov} deg \n')
    print('')
    
    # Queues        
    qRgb = device.getOutputQueue("rgb", 1, False) # Non-blocking

    # Create video writer
    vidSize = camRgb.getVideoSize() # Video (height, width)
 
    if record:
        # Set up folder path, assumes google drive mounted to PC
        VID_FOLDER = r"G:\My Drive\Videos"
        if not os.path.exists(VID_FOLDER):
            os.makedirs(VID_FOLDER)
        # Generate path/filename
        now = datetime.datetime.now().strftime('%m_%d_%H%M%S')
        filename = os.path.join(VID_FOLDER,'OAKvid_'+now+'.avi')
        # Create videowriter object, outputs .avi file
        out = cv2.VideoWriter(filename, cv2.VideoWriter.fourcc(*'MJPG'), 30, vidSize)

    # Create output window
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName, int(vidSize[0]/2), int(vidSize[1]/2))  # resize to half output size

    # Instantiate YOLOv11 object
    detect=yolo.YOLOv8_11(path_to_model,path_to_yaml,[],conf_thres,iou_thres)

    print('Entering loop')
    
    while True:
        inRgb = qRgb.get() 

        if inRgb is not None:

            # Get frame
            frame = inRgb.getCvFrame()

            # Perform inference
            detect.input_image = frame
            out_img = detect.CPUinference()
            
            if detect.nn:
                print("\n")
                for item in detect.nn:
                    print(f'{item}')
            
            # Display 
            cv2.imshow(windowName, out_img)

            # Write video
            if record:
                out.write(out_img)          

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    # Release resources    
    cv2.destroyAllWindows()
    if record:
        out.release()
        print(f"Video is located at: {filename}")
    print('Complete')