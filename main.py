import cv2 as cv
import numpy as np
import os

video_path = r"C:\Users\julia\OneDrive\Documents\Physics IA\New Attempts\New Attempt Part 2\60c.MOV"
video_name = os.path.basename(video_path)  # e.g., "40c.mov"

cap = cv.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video.")
    exit()

# Create a resizable window with the video file's name.
cv.namedWindow(video_name, cv.WINDOW_NORMAL)

paused = False
current_frame = 0
# Global variable to store desired frame index from the trackbar.
trackbar_value = 0

# Get total frame count.
total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

# Base text style parameters.
font = cv.FONT_HERSHEY_SIMPLEX
base_font_scale = 1.0
base_thickness = 2
color = (0, 255, 0)  # Green

def read_and_rotate():
    """Read next frame and rotate 90° clockwise."""
    ret, f = cap.read()
    if ret:
        f = cv.rotate(f, cv.ROTATE_90_CLOCKWISE)
    return ret, f

def on_trackbar(val):
    global trackbar_value
    trackbar_value = val
    # If paused, immediately seek to the new frame.
    if paused:
        cap.set(cv.CAP_PROP_POS_FRAMES, trackbar_value)

# Create the timeline trackbar on the window with the video name.
cv.createTrackbar("Timeline", video_name, 0, total_frames - 1, on_trackbar)

# Read the first frame and get original dimensions.
ret, frame = read_and_rotate()
if not ret:
    print("Error reading first frame.")
    cap.release()
    cv.destroyAllWindows()
    exit()
else:
    current_frame = int(cap.get(cv.CAP_PROP_POS_FRAMES))
    orig_height, orig_width = frame.shape[:2]
    cv.resizeWindow(video_name, orig_width, orig_height)

while True:
    if not paused:
        ret, frame = read_and_rotate()
        if not ret:
            break
        current_frame = int(cap.get(cv.CAP_PROP_POS_FRAMES))
    # Use a short wait so keys and trackbar are polled.
    key = cv.waitKey(30 if paused else 1) & 0xFF

    # Global key: Quit.
    if key == ord('q'):
        break
    # Toggle pause/resume.
    elif key == 32:
        paused = not paused
        key = 255

    if paused:
        # If a key was pressed, process frame navigation.
        if key != 255:
            if key == ord('i'):
                # Move one frame forward.
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = int(cap.get(cv.CAP_PROP_POS_FRAMES))
                else:
                    print("No next frame available.")
            elif key == ord('u'):
                # Move one frame backward.
                new_frame = max(0, current_frame - 2)
                cap.set(cv.CAP_PROP_POS_FRAMES, new_frame)
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = new_frame + 1
                else:
                    print("No previous frame available.")
            elif key == ord('k'):
                # Move 10 frames forward.
                new_frame = current_frame + 9
                cap.set(cv.CAP_PROP_POS_FRAMES, new_frame)
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = new_frame + 1
                else:
                    print("No next frame available.")
            elif key == ord('j'):
                # Move 10 frames backward.
                new_frame = max(0, current_frame - 11)
                cap.set(cv.CAP_PROP_POS_FRAMES, new_frame)
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = new_frame + 1
                else:
                    print("No previous frame available.")
            elif key == ord('m'):
                # Move 100 frames forward.
                new_frame = current_frame + 99
                cap.set(cv.CAP_PROP_POS_FRAMES, new_frame)
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = new_frame + 1
                else:
                    print("No next frame available.")
            elif key == ord('n'):
                # Move 100 frames backward.
                new_frame = max(0, current_frame - 101)
                cap.set(cv.CAP_PROP_POS_FRAMES, new_frame)
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = new_frame + 1
                else:
                    print("No previous frame available.")
            # After processing a key, update the trackbar.
            trackbar_value = current_frame
            cv.setTrackbarPos("Timeline", video_name, current_frame)
        else:
            # If no key was pressed, check the trackbar.
            if trackbar_value != current_frame:
                cap.set(cv.CAP_PROP_POS_FRAMES, trackbar_value)
                ret, frame = read_and_rotate()
                if ret:
                    current_frame = trackbar_value
                else:
                    print("Error seeking to frame:", trackbar_value)

    # --- Create composite (letterboxed) image for display ---
    win_rect = cv.getWindowImageRect(video_name)
    if win_rect[2] > 0 and win_rect[3] > 0:
        win_w, win_h = win_rect[2], win_rect[3]
    else:
        win_w, win_h = orig_width, orig_height

    scale = min(win_w / orig_width, win_h / orig_height)
    new_w = int(orig_width * scale)
    new_h = int(orig_height * scale)
    resized_frame = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_LINEAR)

    composite = np.zeros((win_h, win_w, 3), dtype=np.uint8)
    x_offset = (win_w - new_w) // 2
    y_offset = (win_h - new_h) // 2
    composite[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_frame

    # Scale text parameters.
    scaled_font = base_font_scale * scale
    scaled_thick = max(1, int(base_thickness * scale))
    margin = int(10 * scale)

    # Overlay current frame (top-right).
    text_current = f"Frame: {current_frame}"
    (tw, th), _ = cv.getTextSize(text_current, font, scaled_font, scaled_thick)
    cv.putText(composite, text_current, (win_w - tw - margin, th + margin),
               font, scaled_font, color, scaled_thick, cv.LINE_AA)

    # Overlay total frames (top-left).
    text_total = f"Total: {total_frames}"
    (tw2, th2), _ = cv.getTextSize(text_total, font, scaled_font, scaled_thick)
    cv.putText(composite, text_total, (margin, th2 + margin),
               font, scaled_font, color, scaled_thick, cv.LINE_AA)

    cv.imshow(video_name, composite)

    # When playing, sync the trackbar.
    if not paused:
        cv.setTrackbarPos("Timeline", video_name, current_frame)

cap.release()
cv.destroyAllWindows()
