import cv2
import numpy as np

def selectRange(image):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color = np.array((128, 128, 128))

    def on_scale(new_value):
        pass

    def on_mouse(event, x, y, flags, userdata):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        color[:] = img_hsv[y, x, :]

    cv2.namedWindow("RangeSelector")
    cv2.setMouseCallback("RangeSelector", on_mouse)
    cv2.createTrackbar("H", "RangeSelector", 255, 255, on_scale)
    cv2.createTrackbar("S", "RangeSelector", 255, 255, on_scale)
    cv2.createTrackbar("V", "RangeSelector", 255, 255, on_scale)

    cv2.imshow("RangeSelector", image)
    while True:
        threshold = np.array((cv2.getTrackbarPos("H", "RangeSelector"),
                                cv2.getTrackbarPos("S", "RangeSelector"),
                                cv2.getTrackbarPos("V", "RangeSelector")))
        low = np.maximum(color - threshold, np.array((0, 0, 0)))
        high = np.minimum(color + threshold, np.array((255, 255, 255)))
        
        thresh_img = cv2.inRange(img_hsv, low, high)
        cv2.imshow("RangeSelector", cv2.bitwise_and(image, image,
                                                    mask=thresh_img))
        
        k = cv2.waitKey(10)
        if k == 27:
            print('ESC')
            cv2.destroyWindow("RangeSelector")
            break        
        if cv2.getWindowProperty('RangeSelector',cv2.WND_PROP_VISIBLE) < 1:
            cv2.destroyWindow("RangeSelector")       
            break  

    return (low, high)

if __name__ == "__main__":
    img = cv2.imread("background.png")
    high, low = selectRange(img)
    print(high, low)