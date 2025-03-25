import cv2 # OpenCV library, must be installed in python

camera = cv2.VideoCapture(0) # Access default webcam
# video_size = (640,480) #480P
# camera.set(cv2.CAP_PROP_FRAME_WIDTH,video_size[0]);
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT,video_size[1]);

# create display window
cv2.namedWindow("Output", cv2.WINDOW_NORMAL)

print('Entering loop')
while True:
    (success, frame) = camera.read() # Read a camera image
    
    if success:
        cv2.imshow("Output", frame) # Display only if a frame is available
    
    # Press q while the window is selected to exit
    key = cv2.waitKey(1)
    if key == ord('q'):
        break    

# Release resources    
cv2.destroyAllWindows()
print('Complete')
