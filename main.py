import cv2
import glob
import time
from emailing import send_email

video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
count = 1

while True:
    status = 0
    check, frame = video.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau

    # return the difference between first frame and new frame
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # transforms all pixels above 60 to 255, to make them white
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]

    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # check the edges of the new objects
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # in case the contour area is small, don't highlight it
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0) , 3)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    # append 0 in case we're not drawing a rectangle
    # append 1 in case we're drawing a rectangle
    status_list.append(status)

    # get the last 2 items of the status_list
    status_list = status_list[-2:]

    # only  send the email when an object enters and leaves the frame
    if status_list[0] == 1 and status_list == 0:
        send_email()

    cv2.imshow("Video", frame)

    key = cv2.waitKey(1)

    if key == ord("q"):
        break

video.release()