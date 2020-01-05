from naoqi import ALProxy, ALModule
import time
import numpy as np
import cv2

from TowerOfHanoi.GameState import GameState
import yaml


# lookup table to reduce the colorspace of the detected image
bins = 32 # 4-bit colorspace
lut = np.round(np.linspace(0, bins, 256))
lut = np.round(lut / bins * 255).astype(np.uint8)

# config to determine on which pole a is

class USRHanoiGameState(ALModule):
    """ A module to detect the current gamestate in a game
    of Tower of Hanoi between the NAO and a human.

    """
    def __init__(self, name, config):
        ALModule.__init__(self, name)
        
        self.name = name
        self.tts = ALProxy("ALTextToSpeech")
        self.camera = ALProxy("ALVideoDevice")
        self.memory = ALProxy("ALMemory")
        self.posture = ALProxy("ALRobotPosture")

        # this could be potentially dangerous if other modules use the camera in parallel
        # turn of all the automatically adjusting camera parameters
        self.camera.setParameter(0, 11, 0) #auto-exposure
        self.camera.setParameter(0, 12, 0) #auto-WB
        
        # set some camera parameters manually
        exposure = config["camera"]["exposure"]
        exposure_in_ms = int(round(exposure*1000))
        self.camera.setParameter(0, 17, exposure_in_ms)

        wb = config["camera"]["whitebalance"]
        self.camera.setParameter(0, 33, wb) # white-balance
        gain = config["camera"]["gain"]
        self.camera.setParameter(0, 6, gain) # Gain / ISO

        resolution = 2 # kVGA (640x480px)
        colorSpace = 9 # native camera format (save FPS from conversion)
        fps = 15
        self.handle_id = self.camera.subscribeCamera(self.name+"1", 0, resolution, colorSpace, fps)

        background_frame = self.camera.getImageRemote(self.handle_id)
        background_bgr = self.raw_to_bgr(background_frame)
        self.background_hsv = cv2.cvtColor(background_bgr, cv2.COLOR_BGR2HSV)

        cv2.startWindowThread()
        cv2.namedWindow("preview")

        self.config = config
        self.mask = np.zeros((480,640), dtype=np.bool)
        
        # create a mask to only track within bounding boxes
        for name in ["start", "middle", "finish"]:
            x, y, w, h = config["poles"][name]
            self.mask[y:(y+h),x:(x+w)] = 1

    def __enter__(self):
        return self

    def __exit__(self, exec_type, ethresholdsvalue, traceback):
        # this could be potentiallythresholdsgerous if other modules use the camera, too
        self.camera.setAllParametersToDefault(0)
        self.camera.unsubscribe(self.handle_id)

    def get_gamestate(self):
        if not self.posture._isRobotInPosture("USRLookAtTower", 0.02, 0.02)[0]:
            self.posture.goToPosture("USRLookAtTower", 1.0)

        # state = GameState()
        state = self.detect_disks()

        print("The current gamestate is:" + str(state.array))
        return state

    def detect_disks(self):
        # frame from naoqi into opencv friendly format
        img_frame = self.camera.getImageRemote(self.handle_id)
        frame_bgr = self.raw_to_bgr(img_frame)
        frame_bgr = self.preprocess_image(frame_bgr)

        # HSV image for color robustness
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        
        # substract background to reduce false detections
        # mask = cv2.inRange(np.abs(frame_hsv - self.background_hsv), np.array([1, 1, 0]), np.array([255, 255, 255]))
        # mask = np.ones_like(frame_hsv)[:,:,0]
        mask = self.mask

        game_state = GameState(5)
        for disk_name in game_state.disk_names:
            cont, cX, cY = self.find_contour(frame_hsv, disk_name, mask)

            # find the name of the pole
            position = (cX, cY)
            for pole_name in game_state.pole_names:
                if pole_name == "None":
                    continue

                x, y, w, h = self.config["poles"][pole_name]
                pos_in_rect = position - np.array((x,y))
                if 0 < pos_in_rect[0] < w and 0 < pos_in_rect[1] < h:
                    break
            else:
                pole_name = "None"

            # # draw detection in image
            color = self.config["disks"][disk_name]["color"]
            cv2.drawContours(frame_bgr, cont, -1, color, 2)
            cv2.circle(frame_bgr, (cX, cY), 8, (0, 0, 0), -1)
            cv2.circle(frame_bgr, (cX, cY), 5, color, -1)

            game_state.move(disk_name, pole_name)
        
        cv2.imshow("preview", frame_bgr)
        cv2.waitKey(1)

        return game_state

    def preprocess_image(self, frame_bgr):
        # linear quantization of image
        b = cv2.LUT(frame_bgr[:, :, 0], lut)
        g = cv2.LUT(frame_bgr[:, :, 1], lut)
        r = cv2.LUT(frame_bgr[:, :, 2], lut)
        frame_bgr = np.stack((b, g, r), axis=2)

        # reduce noise from high ISO
        frame_bgr = cv2.medianBlur(frame_bgr, 3)

        return frame_bgr

    def find_contour(self, image, disk_name, background_mask):
        low = np.array(self.config["disks"][disk_name]["low"])
        high = np.array(self.config["disks"][disk_name]["high"])
        mask = cv2.inRange(image, low, high)
        mask = cv2.erode(mask, np.ones([3, 3]))
        mask = cv2.dilate(mask, np.ones([15, 15]))
        mask = mask & background_mask

        
        contours = None
        contours, _ = cv2.findContours(mask, 0, cv2.CHAIN_APPROX_SIMPLE)

        try:
            M = cv2.moments(mask, True)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        except ZeroDivisionError:
            cX = 0
            cY = 0

        return contours, cX, cY

    def raw_to_bgr(self, img_frame):
        img_width = img_frame[0]
        img_height = img_frame[1]
        img_raw = img_frame[6]

        U  = img_raw[0::4]
        Y1 = img_raw[1::4]
        V  = img_raw[2::4]
        Y2 = img_raw[3::4]
        
        UV = np.empty((img_height*img_width), dtype=np.uint8)
        YY = np.empty((img_height*img_width), dtype=np.uint8)
        
        UV[0::2] = np.fromstring(U,  dtype=np.uint8)
        UV[1::2] = np.fromstring(V,  dtype=np.uint8)
        YY[0::2] = np.fromstring(Y1, dtype=np.uint8)
        YY[1::2] = np.fromstring(Y2, dtype=np.uint8)
        
        UV = UV.reshape((img_height, img_width))
        YY = YY.reshape((img_height, img_width))

        uyvy = cv2.merge([YY, UV])
        frame_bgr  = cv2.cvtColor(uyvy, cv2.COLOR_YUV2BGR_UYVY)

        return frame_bgr


if __name__ == "__main__":
    foo = USRHanoiGameState("USRHanoiGameState")
    foo.configure()