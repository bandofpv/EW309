# camera.py

import os
import cv2
import datetime
import threading
import depthai as dai

class Camera:
    def __init__(self, fps, record):
        self.fps = fps
        self.record = record
        
        self.windowName = 'OAK-1 Video Stream'

        # Create pipeline    
        self.pipeline = dai.Pipeline() 
        self.camRgb = self.pipeline.createColorCamera()
        xoutRgb = self.pipeline.createXLinkOut()

        # Camera Properties
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P) # THE_1080_P)
        self.camRgb.setPreviewSize(self.camRgb.getVideoSize()) # must match resolution, max 4K
        self.camRgb.setInterleaved(False)
        self.camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        self.camRgb.setFps(self.fps)
        
        # Preview Link
        xoutRgb.setStreamName("rgb")
        self.camRgb.preview.link(xoutRgb.input)
        
        # Get Video Output Size
        self.video_size = self.camRgb.getVideoSize() # Video (height, width)

        # Initialze Video Recorder
        if self.record:
            self.init_recorder()
            
        # Verify OAK connected, access OAK information
        try:
            print(f'Connected Camera: {dai.Device(self.pipeline).getProductName()}')
#             print(f'Connected Camera(s): {dai.Device(self.pipeline).getConnectedCameraFeatures()}')
        except:
            print('OAK Camera not connected.')
            exit()
        
        # Print Camera Intrinsics
        self.get_camera_info()
        
        # Create threading event for taking snapshots
        self.snapshot_event = threading.Event()
    
    def get_camera_info(self):
        # Start pipeline
        with dai.Device(self.pipeline) as device:
            # Get camera information 
            calibData = device.readCalibration()
            M_row1, M_row2, M_row3  = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A)
            fov = calibData.getFov(dai.CameraBoardSocket.CAM_A)
            print('Camera Intrinsic Matrix:')
            print(f'{M_row1}')
            print(f'{M_row2}')
            print(f'{M_row3}')
            print(f'Camera Horizontal FOV: {fov} deg')
            
    def init_recorder(self):
        # Set up folder path
        VID_FOLDER = r"C:\Users\m260477\Videos"
        if not os.path.exists(VID_FOLDER):
            os.makedirs(VID_FOLDER)
        now = datetime.datetime.now().strftime('%m_%d_%H%M%S')
        self.filename = os.path.join(VID_FOLDER,'OAKvid_'+now+'.avi')
        
        # Create videowriter object, outputs .avi file
        self.video_out = cv2.VideoWriter(self.filename, cv2.VideoWriter.fourcc(*'MJPG'), self.fps, self.video_size)
            
    def stream_video(self):
        # Start pipeline
        with dai.Device(self.pipeline) as device:
            # Queues Video Feed        
            qRgb = device.getOutputQueue("rgb", 1, False) # Non-blocking

            # Create output window
            cv2.namedWindow(self.windowName, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.windowName, int(self.video_size[0]/2), int(self.video_size[1]/2))  # resize to half output size
            
            print("Starting Video Stream")
            
            while True:
                inRgb = qRgb.get() 

                if inRgb is not None:

                    # Get self.frame
                    self.frame = inRgb.getCvFrame()
                    
                    # Draw crosshairs
                    cv2.line(self.frame, (0, int(self.video_size[1]/2)), (self.video_size[0],int(self.video_size[1]/2)), (0, 255, 0), 3)
                    cv2.line(self.frame, (int(self.video_size[0]/2), 0), (int(self.video_size[0]/2),self.video_size[1]), (0, 255, 0), 3)
                    
                    # Display 
                    cv2.imshow(self.windowName, self.frame)

                    # Write video
                    if self.record:
                        self.video_out.write(self.frame)
                        
#                     # Snapshot window 
#                     if cv2.waitKey(1) == ord('p'):
#                         self.grab_snapshot()
                     
                    # Snapshot window  
                    if self.snapshot_event.is_set():
                        self.grab_snapshot()
                        self.snapshot_event.clear()  # reset threading event

                if cv2.getWindowProperty(self.windowName, cv2.WND_PROP_VISIBLE) < 1:
                    break
                
            # Release resources    
            cv2.destroyAllWindows()
            if self.record:
                self.video_out.release()
                print(f"Video is located at: {self.filename}")
            print("Ending Video Stream")
    
    def grab_snapshot(self):
        image_window_name = f"Snapshot {datetime.datetime.now().strftime('%m_%d_%H%M%S')}"
        cv2.namedWindow(image_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(image_window_name, int(self.video_size[0]/2), int(self.video_size[1]/2)) 
        cv2.imshow(image_window_name, self.frame)