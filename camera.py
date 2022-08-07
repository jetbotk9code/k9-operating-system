# TopTechBoy.com
# AI on the Jetson Nano LESSON 33:
# Introduction to Face Detection with OpenCV

import cv2
import numpy as np
import time
import datetime
import argparse
from graphics import *
import config as cf


def setup_camera(cam_type='onboard', dispW=640, dispH=480, flip=0):
    the_result = ""

    if cam_type == 'onboard':
    # Open the device at the ID 0
        camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=640, height=720, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink drop=1'

    elif cam_type == 'web':
        cam=cv2.VideoCapture(1)

    # Check whether user selected camera is opened successfully.
    try:
        cam = cv2.VideoCapture(camSet)

        # To set the resolution
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, dispW)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, dispH)
    except:
        the_result = "Could not open camera"

    return the_result, cam


def setup_window(image, name):
    cv2.imshow(name, image)
    time.sleep(3)
    cv2.moveWindow(name, 0, 0)


def load_image(file_name):
    image = cv2.imread(file_name)

    return image


def process_camera_frame(back_g, cam, fps):
    offset = np.array((57,33))
    try:
        ret, camera_frame = cam.read()

        if cf.take_photo == True:

            if cf.elapsed > 0 and cf.elapsed < 18:
                camera_frame = draw_text(camera_frame, (320, 200), '3', scale=3, color=cf.red_color)

            elif cf.elapsed > 20 and cf.elapsed < 38:
                camera_frame = draw_text(camera_frame, (320, 200), '2', scale=3, color=cf.red_color)

            elif cf.elapsed > 40 and cf.elapsed < 54:
                camera_frame = draw_text(camera_frame, (320, 200), '1', scale=3, color=cf.red_color)

            # flash white box
            if cf.elapsed > 55 and cf.elapsed < 59:
                cv2.rectangle(camera_frame, (0,0), (640,400), (255,255,255), -1)

            if cf.elapsed > 60:
                grab_frame(camera_frame)
                cf.elapsed = 0
            cf.elapsed += 1
           
        # Using cv2.putText() method
        clock_text = str(datetime.datetime.now().strftime("%a %b %d, %Y - %-I:%M %p"))  # Time Date
        back_g = cv2.rectangle(back_g,(727,471),(984,484),(0,0,0),-1)
        back_g = draw_text(back_g, (730, 483), clock_text, scale=.5, color=cf.white_color)

        back_g = cv2.rectangle(back_g,(700,159),(933,192),(170,170,170),-1)
        back_g = draw_text(back_g, (720, 188), cf.face_button_text, scale=.75, color=cf.black_color)
        back_g = cv2.rectangle(back_g,(700,202),(933,235),(170,170,170),-1)
        back_g = draw_text(back_g, (720, 231), cf.fps_button_text, scale=.75, color=cf.black_color)
        back_g = cv2.rectangle(back_g,(700,245),(933,278),(170,170,170),-1)
        back_g = draw_text(back_g, (720, 274), cf.color_mode_button_text, scale=.75, color=cf.black_color)

        if cf.face_detection:
            # convert color frame to gray scale
            gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)

            faces = cf.face_cascade.detectMultiScale(gray, 1.3, 5)
            if faces is not None:
                for (x,y,w,h) in faces:
                    cv2.rectangle(camera_frame, (x,y), (x+w,y+h),(0,0,255, 5))

        if not cf.color_mode:
            pass
            # camera_frame=cv2.cvtColor(camera_frame,cv2.COLOR_BGR2GRAY)

        if cf.show_fps:
            # red background panel for fps display
            cv2.rectangle(camera_frame, (0,0), (100,40), cf.red_color, -1)
            cv2.putText(camera_frame, str(fps)+":fps", (0,25), cf.my_font, .75, cf.black_color, 2)
            cf.start_fps_time = time.time()

        # video added to image code
        back_g[offset[0]:offset[0] + camera_frame.shape[0],offset[1]:offset[1] + camera_frame.shape[1]] = camera_frame
    except:
        print("Can not read camera.")
     
    return back_g


def loop_stream(back_g, cam, name):
    check_time_avr = 0.0
    check_time = 0.0
    clock_org = (730, 483)
    ref_point = []

    while cf.camera_loop:
        if cf.show_fps:
            check_time = time.time() - cf.start_fps_time
            check_time_avr = (0.9 * check_time) + (0.1 * check_time_avr)
            # Round off for display
            fps = round(1 / check_time_avr, 1)

        my_frame = process_camera_frame(back_g, cam, fps)
        cv2.imshow(name, my_frame)

        if cv2.waitKey(1) == ord('q'):
            cf.camera_loop = False


def draw_text(image, loc, text, color=cf.white_color, scale=1):
    thickness = 1
    new_image = cv2.putText(image, text, loc, cf.my_font, scale, color, thickness, cv2.LINE_AA)
    
    return new_image


def grab_frame(frame):
    save_location = cf.attach_dir_send + "/jetbot_camera_" + str(datetime.datetime.now()) + ".jpg"
    cv2.imwrite(save_location, frame)
    print("Captered Photo")
    cf.take_photo = False


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if clicked_rect(cf.menu_box, Point(x, y)):
            cf.camera_loop = False

        elif clicked_rect(cf.capture_box, Point(x, y)):
            cf.take_photo = True
        elif clicked_rect(cf.detect_box, Point(x, y)):
            if cf.face_detection == True:
                cf.face_detection = False
                cf.face_button_text = "Turn Detection On"
            else:
                cf.face_detection = True
                cf.face_button_text = "Turn Detection OFF"
        elif clicked_rect(cf.fps_display_box, Point(x, y)):
            if cf.show_fps == True:
                cf.show_fps = False
                cf.fps_button_text = "Show FPS"
            else:
                cf.show_fps = True
                cf.fps_button_text = "Hide FPS"
        elif clicked_rect(cf.color_mode_box, Point(x, y)):
            if cf.color_mode == True:
                cf.color_mode = False
                cf.color_mode_button_text = "Full Color"
            else:
                cf.color_mode = True
                cf.color_mode_button_text = "Grey Scale"


def clicked_rect(test_rect, the_click):
    result = False
    if test_rect.p1.x < the_click.x < test_rect.p2.x:
        if test_rect.p1.y < the_click.y < test_rect.p2.y:
            result = True
    return result


def clean_up(cam):
    cam.release()
    cv2.destroyAllWindows()


# ============================== Main =============================
if __name__ == "__main__":
    print("opencv ver:" + cv2.__version__)

    error, my_camera = setup_camera(dispW=640, dispH=400)
    if error == "":
        bg_image = load_image('ui/K9 Systems Monitor_Camera.png')
        setup_window(bg_image, 'K-9 Camera')
        cv2.setMouseCallback('K-9 Camera', on_mouse)

        loop_stream(bg_image, my_camera, 'K-9 Camera')

        clean_up(my_camera)
    else:
        print(error)

# 3264 x 2464 FR = 21.000000
# 3264 x 1848 FR = 28.000001
# 1920 x 1080 FR = 29.999999
# 1640 x 1232 FR = 29.999999
# 1280 x 720 FR = 59.999999
# 1280 x 720 FR = 120.000005

