# camera.py
 
import os
import cv2
import yolo
import math
import datetime
import threading
import depthai as dai

class Camera:
    def __init__(self, distance_to_target, target_color, x_bias, y_bias, fps, record, conf_thres=0.15, iou_thres=0.15):
        self.distance_to_target = distance_to_target
        self.target_color = target_color
        self.x_bias = x_bias
        self.y_bias = y_bias
        self.fps = fps
        self.record = record
        
        # onnx model, yaml, and video file paths
        self.path_to_model = r"C:\Users\m260477\Desktop\EW309\yolo.onnx" # path to .onnx weights
        self.path_to_yaml = r"C:\Users\m260477\Desktop\EW309\data.yaml" # path to data.yaml file used to train the model
        self.video_path = r"C:\Users\m260477\Videos"

        # Thresholds
        self.conf_thres = conf_thres # classification confidence threshold, 0.0-1.0
        self.iou_thres = iou_thres # iou threshold, 0.0-1.0

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
        self.video_size = self.camRgb.getVideoSize() # Video (width, height)

        # Initialze Video Recorder
        if self.record:
            self.init_recorder()
         
        # Verify OAK connected, access OAK information
        try:
            print(f'Connected Camera: {dai.Device(self.pipeline).getProductName()}')
        except:
            print('OAK Camera not connected.')
            exit()

        # Get Camera Intrinsics
        self.M_row1 = self.M_row2 = self.M_row3 = 0
        self.get_camera_info()

        # Create threading event for taking snapshots
        self.snapshot_event = threading.Event()
        
        # Store center point of detected targets
        self.targets = 0
        
    # Pulls camera intrinsics
    def get_camera_info(self):
        # Start pipeline
        with dai.Device(self.pipeline) as device:
            # Get camera information 
            calibData = device.readCalibration()
            self.M_row1, self.M_row2, self.M_row3 = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A,self.video_size[0],self.video_size[1])
            fov = calibData.getFov(dai.CameraBoardSocket.CAM_A)
            print('Camera Intrinsic Matrix:')
            print(f'{self.M_row1}')
            print(f'{self.M_row2}')
            print(f'{self.M_row3}')
            print(f'Camera Horizontal FOV: {fov} deg')
    
    # Initilize video recorder
    def init_recorder(self):
        if not os.path.exists(self.video_path):
            os.makedirs(self.video_path)
        now = datetime.datetime.now().strftime('%m_%d_%H%M%S')
        self.filename = os.path.join(self.video_path,'OAKvid_'+now+'.avi')

        # Create videowriter object, outputs .avi file
        self.video_out = cv2.VideoWriter(self.filename, cv2.VideoWriter.fourcc(*'MJPG'), self.fps, self.video_size)
    
    # Stream video output with detections
    def stream_video(self):
        # Start pipeline
        with dai.Device(self.pipeline) as device:
            # Queues Video Feed        
            qRgb = device.getOutputQueue("rgb", 1, False) # Non-blocking

            # Create output window
            cv2.namedWindow(self.windowName, cv2.WINDOW_NORMAL)
#             cv2.resizeWindow(self.windowName, int(self.video_size[0]), int(self.video_size[1]))  # resize to output size

            # Instantiate YOLOv8 object
            detect = yolo.YOLOv8_11(self.path_to_model, self.path_to_yaml, [], self.conf_thres, self.iou_thres)
            
            print('Starting Video Stream')
         
            while True:
                inRgb = qRgb.get() 

                if inRgb is not None:
                    # Get frame
                    frame = inRgb.getCvFrame()
                    
                    # Perform inference
                    detect.input_image = frame
                    out_img = detect.CPUinference()
                    
                    if detect.nn:
                        print('\n')
                        print(*detect.nn, sep='\n')
                        self.find_targets(detect.nn)
                        
                    if self.targets:
                        print(self.targets)
                        for target in self.targets:
                            cv2.circle(out_img, (int(target[0]),int(target[1])), 4, (0, 0, 255), -1)

                    # Draw crosshairs
                    cv2.line(out_img, (0, int(self.video_size[1]/2)), (self.video_size[0],int(self.video_size[1]/2)), (0, 255, 0), 2)
                    cv2.line(out_img, (int(self.video_size[0]/2), 0), (int(self.video_size[0]/2),self.video_size[1]), (0, 255, 0), 2)
                    cv2.line(out_img, (0, int(self.M_row2[2])), (self.video_size[0],int(self.M_row2[2])), (255, 0, 0), 2)
                    cv2.line(out_img, (int(self.M_row1[2]), 0), (int(self.M_row1[2]),self.video_size[1]), (255, 0, 0), 2)

                    # Display 
                    cv2.imshow(self.windowName, out_img)

                # Write video
                if self.record:
                    self.video_out.write(out_img)
                     
                # Image window 
                if cv2.waitKey(1) == ord('p'):
                    self.grab_snapshot(out_img)
                     
                # Snapshot window  
                if self.snapshot_event.is_set():
                    self.grab_snapshot(out_img)
                    if detect.nn:
                        self.find_targets(detect.nn)
                    self.snapshot_event.clear()
                
                # Close window if x button is clicked
                if cv2.getWindowProperty(self.windowName, cv2.WND_PROP_VISIBLE) < 1:
                    break
             
            # Release resources    
            cv2.destroyAllWindows()
            if self.record:
                self.video_out.release()
                print(f"Video is located at: {self.filename}")
            print('Ending Video Stream')

    # Take snapshot from video feed
    def grab_snapshot(self, frame):
        image_window_name = f"Snapshot {datetime.datetime.now().strftime('%m_%d_%H%M%S')}"
        cv2.namedWindow(image_window_name, cv2.WINDOW_NORMAL)
#         cv2.resizeWindow(image_window_name, int(self.video_size[0]), int(self.video_size[1])) 
        cv2.imshow(image_window_name, frame)
    
    # Calculate height of targets
    def calc_height(self, y_pixels):
        f_y = self.M_row2[1]
        return (self.distance_to_target*y_pixels)/f_y
    
    # Find 5 inch (12.7 cm) targets
    def find_targets(self, detections, height=12.7, tolerance=3):
        self.targets = []

        for label, bbox, confidence in detections:
            x, y, w, h = bbox
            if label == self.target_color and abs(self.calc_height(h) - height) <= tolerance:
                center_x = x + w / 2
                center_y = y + h / 2
                self.targets.append((center_x, center_y))

        if len(self.targets) > 2:
            print("Detected more than two targets!!!")
        
    # Convert x_pixels to meters in image frame
    def x_pixels_to_si_units(self, x_pixels):
        c_x = self.M_row1[2]
        f_x = self.M_row1[0]
        return (self.distance_to_target*(x_pixels-c_x))/f_x
    
    # Convert y_pixels to meters in image frame
    def y_pixels_to_si_units(self, y_pixels):
        c_y = self.M_row2[2]
        f_y = self.M_row2[1]
        return (self.distance_to_target*(y_pixels-c_y))/-f_y
    
    # Calculate yaw and pitch angles using x, y coordinates (in meters)
    def calc_angles(self, yaw_imu, pitch_imu):
        x_pixels1 = self.x_pixels_to_si_units(self.targets[0][0])
        y_pixels1 = self.y_pixels_to_si_units(self.targets[0][1])
        yaw1 = yaw_imu + math.atan2((x_pixel1s-self.x_bias)/self.distance_to_target)
        pitch1 = pitch_imu + math.atan2((y_pixels1-self.y_bias)/self.distance_to_target)
        
        x_pixels2 = self.x_pixels_to_si_units(self.targets[1][0])
        y_pixels2 = self.y_pixels_to_si_units(self.targets[1][1])
        yaw2 = yaw_imu + math.atan2((x_pixels2-self.x_bias)/self.distance_to_target)
        pitch2 = pitch_imu + math.atan2((y_pixels2-self.y_bias)/self.distance_to_target)
        
        return yaw1, pitch1, yaw2, pitch2