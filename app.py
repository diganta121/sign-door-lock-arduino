import numpy as np
import time
import cv2
import mediapipe as mp
import serial

COM_PORT = "COM3"
BAUD_RATE = 9600
finger_passwd = [0, 0, 1, 1]  # password for lock

locked = False
prev = False

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

finger_tips = [8, 12, 16, 20]
thumb_tip = 4
thumb_status = False


def draw_circle(tip, lm_list, state=False):
    x, y = int(lm_list[tip].x * w), int(lm_list[tip].y * h)

    if state == True:
        cv2.circle(img, (x, y), 15, (255, 0, 0), cv2.FILLED)
    elif state == False:
        cv2.circle(img, (x, y), 15, (0, 255, 0), cv2.FILLED)


def finger_count(lm_list):
    global finger_tips
    finger_fold_status = []

    for tip in finger_tips:
        # getting the landmark tip position and drawing blue circle
        # writing condition to check if finger is folded i.e checking if finger tip starting value is smaller than finger starting position which is inner landmark. for index finger
        # if finger folded changing color to green

        state = lm_list[tip - 3].y < lm_list[tip].y

        draw_circle(tip, lm_list, state=state)

        if state:
            finger_fold_status.append(True)
        else:
            finger_fold_status.append(False)
    return finger_fold_status


def trigger_lock(ser):
    if locked:
        print("LOCKED")
        # ser.write(b"0")
        time.sleep(0.1)


def trigger_unlock(ser):
    if locked:
        print("UNLOCKED")
        # ser.write(b"1")
        time.sleep(1)


def trigger_sign(finger_status, ser):
    # check if the correct sign is done
    # put ring finger down to take screenshot
    global locked
    if finger_status == finger_passwd:
        trigger_unlock(ser)
        locked = False
    else:
        trigger_lock(ser)
        locked = True


while True:
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    h, w, c = img.shape
    results = hands.process(img)
    # check if hand is detected
    try:
        ser = serial.Serial("COM3", 9600, timeout=0.1)
    except:
        print("Serial port not found")

    if results.multi_hand_landmarks:
        for hand_landmark in results.multi_hand_landmarks:
            # accessing the landmarks by their position
            lm_list = []
            for id, lm in enumerate(hand_landmark.landmark):
                lm_list.append(lm)

            # array to hold true or false if finger is folded

            finger_fold_status = finger_count(lm_list)

            trigger_sign(finger_fold_status, "ser")
            print(finger_fold_status, locked)

            mp_draw.draw_landmarks(
                img,
                hand_landmark,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec((0, 0, 255), 2, 2),
                mp_draw.DrawingSpec((0, 255, 0), 4, 2),
            )
    else:
        # if no hand is detected then unlock the lock
        if locked:
            trigger_lock("ser")
        else:
            trigger_unlock("ser")
    cv2.imshow("hand tracking", img)
    key = cv2.waitKey(1)
    if key == 32:
        break

cv2.destroyAllWindows()
