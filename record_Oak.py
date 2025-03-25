# Requires OAK camera attached with USB3 cable
# depthai API vailable at: https://docs.luxonis.com/projects/api/en/latest/
# EW309 Computer Vision, P. Frontera, March 2024
# 

import cv2
import depthai as dai
import datetime 
import os

# Flag to toggle video recording
record = True # Use True to record; use False for no recording

# Set up window
windowName = 'OAK-1 Live Stream'

# Create pipeline    
pipeline = dai.Pipeline()

# Define source and output 
camRgb = pipeline.createColorCamera()
xoutRgb = pipeline.createXLinkOut()

# Camera Properties
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P) #THE_1080_P)
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
    M_row1, M_row2, M_row3  = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A)
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
    size = camRgb.getVideoSize() # Video (height, width)
 
    if record:
        # Set up folder path
        VID_FOLDER = r"C:\Users\m260477\Videos"
        if not os.path.exists(VID_FOLDER):
            os.makedirs(VID_FOLDER)
        # Generate path/filename
        now = datetime.datetime.now().strftime('%m_%d_%H%M%S')
        filename = os.path.join(VID_FOLDER,'OAKvid_'+now+'.avi')
        # Create videowriter object, outputs .avi file
        out = cv2.VideoWriter(filename, cv2.VideoWriter.fourcc(*'MJPG'), 30, size)

    # Create output window
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName, int(size[0]/2), int(size[1]/2))  # resize to half output size
    
    print('Entering loop')
    
    while True:
        inRgb = qRgb.get() 

        if inRgb is not None:

            # Get frame
            frame = inRgb.getCvFrame()
            
            # Draw crosshairs
            cv2.line(frame, (0, int(size[1]/2)), (size[0],int(size[1]/2)), (0, 255, 0), 3)
            cv2.line(frame, (int(size[0]/2), 0), (int(size[0]/2),size[1]), (0, 255, 0), 3)
            
            # Display 
            cv2.imshow(windowName, frame)

            # Write video
            if record:
                out.write(frame)          

        key = cv2.waitKey(1)
        if key == ord('q') or cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1:
            break
        
    # Release resources    
    cv2.destroyAllWindows()
    if record:
        out.release()
        print(f"Video is located at: {filename}")
    print('Complete')