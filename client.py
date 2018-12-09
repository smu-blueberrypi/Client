#client socket programming
import os
import sys
import socket
import threading
from video import test
from video import main
from video import object_detection_yolo
from operator import eq
from pyautogui import press
from queue import Queue
import time
import gps
import json
#import sysv_ipc

HOST = "118.217.34.116" #Server Ip Address
PORT = 9000
checkStream = False

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

lat = None
lng = None
alt = None

print("wait server")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("connect Success")

q = Queue()
tmp = None

def sendingMsg():
  global tmp
  global q
  global lat, lng, alt
  while True:
    search =  object_detection_yolo.getSearchObj()
    '''
    if not q.empty():
      imgByte = q.get()
      data = imgByte
      print(type(data))
      #data = bytes(data, "utf-8")
      s.send(data)
    '''
    if not eq(search,None) and not eq(search, tmp):
      
      print("접근!!")
      j1 = {'object':search,'lat':lat,'lon':lng,'alt':alt}
      data = json.dumps(j1)
      print(data)
      #data = search
      data = bytes(data, "utf-8")
      s.send(data)
      tmp = search # data only one send check 
      object_detection_yolo.setSearchObj()   
    
  s.close()

def gettingMsg():
  global checkStream
  global q
  while True:
    data = s.recv(1024)
    data = str(data).split("b'", 1)[1].rsplit("'",1)[0]
    print(data)
    
    if eq(data,"test"):
      test.TestTCP()
    if eq(data,"runVideo"):
      if checkStream:
        os.system('kill -9 `ps -ef | grep /home/pi/class/project/NodeMedia* | awk "{print $2}"`')
      th_yolo = threading.Thread(target = object_detection_yolo.ObjectDetection_YOLO, args=(q,))
      th_yolo.start()
      #threading._start_new_thread(object_detection_yolo.ObjectDetection_YOLO,())
      #threading._start_new_thread(main.SearchObject,())
    if eq(data,"stopVideo"):
      press('q')
      time.sleep(1)
      checkStream = True
      os.system('~/class/project/NodeMediaDevice/raspipublisher -w 1280 -h 720 -b 1000000 -t 0 -vf -hf -o rtmp://118.217.34.116/live/s &')
  s.close()

#threading._start_new_thread(sendingMsg,())
#threading._start_new_thread(gettingMsg,())
th_sendMsg = threading.Thread(target = sendingMsg, args=())
th_getMsg = threading.Thread(target = gettingMsg, args=())

th_sendMsg.start()
th_getMsg.start()


while True:


  try:
    report = session.next()
        
    if report['class'] == 'TPV':
      if hasattr(report, 'lat'):
        lat = report.lat
      if hasattr(report, 'lon'):
        lng = report.lon
      if hasattr(report, 'alt'):
        alt = report.alt
  except KeyError:
    pass
  except KeyboardInterrupt:
    quit()
  except StopIteration:
    session = None
      

