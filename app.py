import cv2
import mediapipe as mp
import pyautogui
import time
import math
import subprocess

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.7)

sensitivity = 10
alpha = 0.5
click_cooldown = 0.5
fist_threshold = 0.35
open_threshold = 0.65

cursor_x, cursor_y = screen_w // 2, screen_h // 2
velocity_x, velocity_y = 0, 0
prev_hand_x, prev_hand_y = None, None
last_click_time = 0
last_launch_time = 0

high_five_was_active = False
three_fingers_was_active = False
alt_pressed = False

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def draw_landmarks(frame, hand_landmarks):
    connections = mp_hands.HAND_CONNECTIONS
    landmark_drawing_spec = mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
    connection_drawing_spec = mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
    mp.solutions.drawing_utils.draw_landmarks(
        frame,
        hand_landmarks,
        connections,
        landmark_drawing_spec,
        connection_drawing_spec)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    active = False
    click = False
    high_five_active = False
    three_fingers_active = False

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            draw_landmarks(frame, handLms)
            
            lm_list = [(id, int(lm.x * w), int(lm.y * h)) for id, lm in enumerate(handLms.landmark)]
            
            wrist = next(item for item in lm_list if item[0] == 0)[1:]
            thumb_tip = next(item for item in lm_list if item[0] == 4)[1:]
            index_tip = next(item for item in lm_list if item[0] == 8)[1:]
            middle_tip = next(item for item in lm_list if item[0] == 12)[1:]
            ring_tip = next(item for item in lm_list if item[0] == 16)[1:]
            pinky_tip = next(item for item in lm_list if item[0] == 20)[1:]
            
            mcp_joints = [item[1:] for item in lm_list if item[0] in [1, 5, 9, 13, 17]]
            palm_center = (
                sum(p[0] for p in mcp_joints + [wrist]) // (len(mcp_joints) + 1),
                sum(p[1] for p in mcp_joints + [wrist]) // (len(mcp_joints) + 1)
            )
            
            middle_mcp = next(item for item in lm_list if item[0] == 9)[1:]
            palm_size = calculate_distance(wrist, middle_mcp)
            
            thumb_dist = calculate_distance(thumb_tip, palm_center)
            index_dist = calculate_distance(index_tip, palm_center)
            middle_dist = calculate_distance(middle_tip, palm_center)
            ring_dist = calculate_distance(ring_tip, palm_center)
            pinky_dist = calculate_distance(pinky_tip, palm_center)
            
            thumb_norm = thumb_dist / palm_size
            index_norm = index_dist / palm_size
            middle_norm = middle_dist / palm_size
            ring_norm = ring_dist / palm_size
            pinky_norm = pinky_dist / palm_size
            
            fingers_closed = (index_norm < fist_threshold and 
                              middle_norm < fist_threshold and 
                              ring_norm < fist_threshold and 
                              pinky_norm < fist_threshold)
            
            three_fingers_active = (index_norm > open_threshold and 
                                    middle_norm > open_threshold and 
                                    ring_norm > open_threshold and 
                                    pinky_norm < fist_threshold and 
                                    thumb_norm < fist_threshold * 1.5)
            
            current_time = time.time()
            if three_fingers_active and not three_fingers_was_active and current_time - last_launch_time > 10:
                subprocess.Popen(["C:\\Riot Games\\Riot Client\\RiotClientServices.exe", "--launch-product=league_of_legends", "--launch-patchline=live"])
                last_launch_time = current_time
            three_fingers_was_active = three_fingers_active

            high_five_active = (thumb_norm > fist_threshold * 2 and 
                                index_norm > fist_threshold * 2 and 
                                middle_norm > fist_threshold * 2 and 
                                ring_norm > fist_threshold * 2 and 
                                pinky_norm > fist_threshold * 2)

            if high_five_active and not high_five_was_active:
                if current_time - last_click_time > click_cooldown:
                    click = True
                    last_click_time = current_time
            high_five_was_active = high_five_active

            thumb_open = thumb_norm > open_threshold
            thumb_closed = thumb_norm < fist_threshold

            if fingers_closed and thumb_open and not alt_pressed:
                pyautogui.keyDown('alt')
                pyautogui.press('tab')
                alt_pressed = True

            if alt_pressed:
                if pinky_norm > open_threshold:
                    pyautogui.press('tab')
                    time.sleep(0.2)
                
                if thumb_closed:
                    pyautogui.keyUp('alt')
                    alt_pressed = False

            if (index_norm > fist_threshold * 1.5 and 
                not (middle_norm > fist_threshold * 1.5 or 
                     ring_norm > fist_threshold * 1.5 or 
                     pinky_norm > fist_threshold * 1.5)):
                active = True
                if prev_hand_x is None:
                    prev_hand_x, prev_hand_y = index_tip

                dx = index_tip[0] - prev_hand_x
                dy = index_tip[1] - prev_hand_y

                velocity_x = alpha * (dx * sensitivity) + (1 - alpha) * velocity_x
                velocity_y = alpha * (dy * sensitivity) + (1 - alpha) * velocity_y

                prev_hand_x, prev_hand_y = index_tip
            else:
                active = False
                prev_hand_x, prev_hand_y = None, None

    if active:
        cursor_x += velocity_x
        cursor_y += velocity_y
        cursor_x = max(0, min(screen_w - 1, cursor_x))
        cursor_y = max(0, min(screen_h - 1, cursor_y))
        pyautogui.moveRel(velocity_x, velocity_y)
    else:
        velocity_x, velocity_y = 0, 0

    if click:
        pyautogui.click()

    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        if alt_pressed:
            pyautogui.keyUp('alt')
        break

cap.release()
cv2.destroyAllWindows()