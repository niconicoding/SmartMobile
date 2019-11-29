# USAGE
#python3 smartmobile.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel


# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from gpiozero import Buzzer
from time import sleep

import numpy as np
import argparse
import imutils
import cv2
import serial
import datetime
import os
import telepot
import time

import RPi.GPIO as GPIO

#텔레그램 봇 토큰과 봇 생성
os.system('sudo rfcomm release 0')
time.sleep(3)
os.system('sudo rfcomm bind rfcomm0 BLUETOOTH ID')
my_token = 'TELEGRAM BOT TOKEN'
bot = telepot.Bot(my_token)

telegram_id = 'TELEGRAM ID'

bot.sendMessage(chat_id = telegram_id, text = "!! system is changed !!")


#경고 메세지
msg_face = '뒤집힘 경고'
msg_object = '관심영역 경고'

#GPIO input/output 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#부저 생성
buzzer = Buzzer(3)

#현재 시간을 초로 계산하여 반환
def total():
  now = datetime.datetime.now()
  nowTuple = now.timetuple()
  total_sec = nowTuple.tm_sec +(nowTuple.tm_min*60) + (nowTuple.tm_hour*3600) + (nowTuple.tm_mday * 3600 * 24) + (nowTuple.tm_mon * 3600 * 24 * nowTuple.tm_mday) + (nowTuple.tm_year * 3600 * 24 * 365.25)

  return int(total_sec)


# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-p", "--prototxt", required=True,
#	help="path to Caffe 'deploy' prototxt file")
#ap.add_argument("-m", "--model", required=True,
#	help="path to Caffe pre-trained model")
#ap.add_argument("-c", "--confidence", type=float, default=0.2,
#	help="minimum probability to filter weak detections")
#ap.add_argument("-u", "--movidius", type=bool, default=0,
#	help="boolean indicating if the Movidius should be used")
#args = vars(ap.parse_args())



# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class

IGNORE = set(["background", "aeroplane", "bicycle", "bird", "boat",
         "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
         "dog", "horse", "motorbike", "pottedplant", "sheep",
         "sofa", "train", "tvmonitor"])


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
##------edited      COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))



# load our serialized model from disk
print("[INFO] loading model...")
people_net = cv2.dnn.readNetFromCaffe("/home/pi/infant_accident_prevention_system_development/MobileNetSSD_deploy.prototxt","/home/pi/infant_accident_prevention_system_development/MobileNetSSD_deploy.caffemodel")
face_net = cv2.dnn.readNetFromCaffe("/home/pi/infant_accident_prevention_system_development/deploy.prototxt.txt","/home/pi/infant_accident_prevention_system_development/res10_300x300_ssd_iter_140000.caffemodel") 

fps = FPS().start()
#vs = VideoStream(src=2).start()
#USE WebCam

frame = 0

# specify the target device as the Myriad processor on the NCS
people_net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter

#----------------------------------------------------------------------------------------
#print("[INFO] starting video stream...")


#vs = VideoStream(usePiCamera=True).start()
vs = cv2.VideoCapture(2, cv2.CAP_V4L)

#time.sleep(2.0)
#fps = FPS().start()


def total():
    now = datetime.datetime.now()
    nowTuple = now.timetuple()
    total_sec = nowTuple.tm_sec +(nowTuple.tm_min*60) + (nowTuple.tm_hour*3600) + (nowTuple.tm_mday * 3600 * 24) + (nowTuple.tm_mon * 3600 * 24 * nowTuple.tm_mday) + (nowTuple.tm_year * 3600 * 24 * 365.25)

    return int(total_sec)

def imgprocessing_people():
    # loop over the frames from the video stream
    global frame
    global people_net
    global fps
    global vs
    global CLASSES
    global count
    global buzzer

    global serial

    global msg_face
    global msg_object
    global bot
    global telegram_id

    ROI_EVENT_FLAG = False
    ROI_EVENT_START_TIME = 0
    ROI_EVENT_START_TIME_FLAG = False


    FACE_EVENT_FLAG = False
    FACE_EVENT_START_TIME = 0
    FACE_EVENT_START_TIME_FLAG = False

    # loop over the frames from the video stream
    bluetoothSerial = serial.Serial("/dev/rfcomm0", baudrate=9600)

#    face_num = 0
    while True:
        if GPIO.input(17) == 0:
            print("reset!")
            ROI_EVENT_FLAG = False
            ROI_EVENT_START_TIME_FLAG = False
            FACE_EVENT_START_TIME_FLAG = False
            buzzer.off()

	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
        ret, frame = vs.read()
        #print('ret', ret)
        #print('frame', frame)

        #frame = imutils.resize(frame, width=800)
	# grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
#-----------------------------------------------------------------------------
        people_blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        face_blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,(300, 300), (104.0, 177.0, 123.0))
        # pass the blob through the network and obtain the detections and
	# predictions
        people_net.setInput(people_blob)
        people_detections = people_net.forward()

        face_net.setInput(face_blob)
        face_detections = face_net.forward()

        line_left_topx = 100
        line_left_topy = 50
        line_right_botx = 500
        line_right_boty = 450
        weight = 10
        cv2.rectangle(frame, (line_left_topx, line_left_topy), (line_right_botx, line_right_boty),(255,255,255), 2)

        ROI_EVENT_FLAG = True
	# loop over the detections
        for i in np.arange(0, people_detections.shape[2]):
            people_confidence = people_detections[0, 0, i, 2]
            people_idx = int(people_detections[0, 0, i, 1])
            #print(people_idx)
            #print(CLASSES[people_idx])
            if CLASSES[people_idx] in IGNORE:
                continue
            if people_confidence > 0.4:
                #people_idx = int(people_detections[0, 0, i, 1])
                #print(people_idx)
                #print(CLASSES[people_idx])
                #if CLASSES[people_idx] in IGNORE:
                #    continue

                people_box = people_detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (people_startX, people_startY, people_endX, people_endY) = people_box.astype("int")

                #영역 이탈 감지
                if people_startX < line_left_topx+weight or people_endX > line_right_botx-weight or people_startY < line_left_topy+weight or people_endY > line_right_boty-weight:
                    print('ROI WARNING')
                    ROI_EVENT_FLAG = True

                else :

                    print('ROI_safety')
                    ROI_EVENT_FLAG = False


                cv2.rectangle(frame, (people_startX, people_startY), (people_endX, people_endY),(255,0,0), 2)


        if ROI_EVENT_FLAG:    #영역 이탈한 경우

            if not ROI_EVENT_START_TIME_FLAG:    #영역 이탈 첫 발생
                ROI_EVENT_START_TIME = total()
                ROI_EVENT_START_TIME_FLAG = True

            else :     #이미 영역 이탈 발생
                diff_sec = total() - ROI_EVENT_START_TIME
                print("ROI event warning "+str(diff_sec))

                if diff_sec % 2 == 0 : #관심영역 경고 텔레그램 알림
                    bot.sendMessage(chat_id = telegram_id, text = msg_object)

                if diff_sec >= 5: #관심영역 경고가 5초이상 지속되었을 시 시간에따라 진동 혹은 부저 알림
                    #ROI_now = datetime.datetime.now()
                    #ROI_event_time = ROI_now.replace(hour=10, minute=59, second=0,microsecond=0)
                    #if ROI_now > ROI_event_time: #기준점과 시간 비교
                    #    buzzer.off()
                    #    bluetoothSerial.write(str("w").encode('utf-8'))
                    #else:
                    #    buzzer.on()
                    bluetoothSerial.write(str("w").encode('utf-8'))

        else :    #영역 이탈 정상 경우
            ROI_EVENT_START_TIME_FLAG = False



        face_num = 0

        #for i in range(0, face_detections.shape[2]):
        for i in np.arange(0, face_detections.shape[2]):
            face_confidence = face_detections[0, 0, i, 2]
            if face_confidence < 0.17:
                continue
            else:
                face_num += 1
                face_box = face_detections[0, 0, i, 3:7] * np.array([w,h,w,h])
                (face_startX, face_startY, face_endX, face_endY) = face_box.astype("int")
                #face_text = "{:.2f}%".format(face_confidence * 100)
                #face_y = face_startY - 10 if face_startY - 10 > 10 else face_startY + 10
                cv2.rectangle(frame, (face_startX, face_startY), (face_endX, face_endY),(0, 0, 255), 2)
                #cv2.putText(frame, face_text, (face_startX, face_y),cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,255),2)
        print(face_num)
        if face_num == 0:
            if not FACE_EVENT_START_TIME_FLAG:
                FACE_EVENT_START_TIME = total()
                FACE_EVENT_START_TIME_FLAG = True
            else :
                diff_sec = total() - FACE_EVENT_START_TIME
                print("FACE event warning "+str(diff_sec))
                if diff_sec % 2 == 0:
                    bot.sendMessage(chat_id = telegram_id, text = msg_face)
                if diff_sec >= 5:
                #    FACE_now = datetime.datetime.now()
                #    FACE_event_time = FACE_now.replace(hour=10, minute=59, second=0,microsecond=0)
                #    if FACE_now > FACE_event_time:
                #        buzzer.off()
                #        bluetoothSerial.write(str("w").encode('utf-8'))
                #    else:
                    buzzer.on()
        else:
            FACE_EVENT_START_TIME_FLAG = False
            if not ROI_EVENT_FLAG:
                buzzer.off()


        #cv2.putText(frame, label, (startX, y),
        #cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
        # show the output frame
        cv2.imshow("frame", frame)
        key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

	# update the FPS counter
        fps.update()

# stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    buzzer.off()

    os.system('kill -9 '+str(os.getpid()))
    #os.system("KINESIS=$(ps -a | grep kinesis_video_g |awk '{print $1}') && kill -9 $KINESIS")
    os.system('sudo rfcomm release 0')
if __name__ == '__main__':
    imgprocessing_people()
