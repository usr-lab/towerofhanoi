from naoqi import ALBroker    
from naoqi import ALProxy

import sys
import yaml
import cv2
import numpy as np

from HSVrangeSelector import selectRange

disk_names = ["orange", "yellow", "green", "blue", "purple"]
pole_names = ["start", "middle", "finish"]

config = {
    "camera": {
        "exposure":0.13,
        "whitebalance": 6500,
        "gain": 64
    },
    "poles": {
        "start":[0, 0, 0, 0],
        "middle":[0, 0, 0, 0],
        "finish":[0, 0, 0, 0]
    },
    "disks": {
        "orange":{
            "color":[38,105,233],
            "low":[0, 0, 0],
            "high":[255, 255, 255]
        },
        "yellow":{
            "color":[64,255,251],
            "low":[0, 0, 0],
            "high":[255, 255, 255]
        },
        "green":{
            "color":[28,140,42],
            "low":[0, 0, 0],
            "high":[255, 255, 255]
        },
        "blue":{
            "color":[158,124,58],
            "low":[0, 0, 0],
            "high":[255, 255, 255]
        },
        "purple":{
            "color":[128,89,124],
            "low":[0, 0, 0],
            "high":[255, 255, 255]
        },
    }
}

bins = 32 # 4-bit colorspace
lut = np.round(np.linspace(0, bins, 256))
lut = np.round(lut / bins * 255).astype(np.uint8)

def raw_to_bgr(img_frame):
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

def preprocess_image(frame_bgr):
    # linear quantization of image
    b = cv2.LUT(frame_bgr[:, :, 0], lut)
    g = cv2.LUT(frame_bgr[:, :, 1], lut)
    r = cv2.LUT(frame_bgr[:, :, 2], lut)
    frame_bgr = np.stack((b, g, r), axis=2)

    # reduce noise from high ISO
    frame_bgr = cv2.medianBlur(frame_bgr, 3)

    return frame_bgr

if __name__ == "__main__":
    # setup broker
    robot_ip = sys.argv[1]
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, 9559)

    # register all the needed proxies
    memory = ALProxy("ALMemory")
    posture = ALProxy("ALRobotPosture")
    camera = ALProxy("ALVideoDevice")

    # load custom postures
    posture._loadPostureLibraryFromName("USRTowerOfHanoi.postures")
    posture._generateCartesianMap()

    # start the camera
    resolution = 2 # kVGA (640x480px)
    colorSpace = 9 # native camera format (save FPS from conversion)
    fps = 15
    handle_id = camera.subscribeCamera("configHanoi", 0, resolution, colorSpace, fps)

    try:
        # setup the configuration
        print("Configuration of Detection Pipeline")
        posture.goToPosture("USRLookAtTower", 0.5)

        frame = camera.getImageRemote(handle_id)
        frame_bgr = raw_to_bgr(frame)
        image = preprocess_image(frame_bgr)

        for disk in disk_names:
            print("Threshold the {disk} disk".format(disk=disk))
            lower, upper = selectRange(image)
            config["disks"][disk]["low"] = lower.tolist()
            config["disks"][disk]["high"] = upper.tolist()

        for pole in pole_names:
            print("Select the {pole} pole".format(pole=pole))
            config["poles"][pole] = cv2.selectROI(image)

        with open("hanoi_config_v2.yaml", "w") as f:
            yaml.dump(config, f)
    finally:
        camera.setAllParametersToDefault(0)
        camera.unsubscribe(handle_id)