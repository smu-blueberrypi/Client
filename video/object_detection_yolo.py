# This code is written at BigVision LLC. It is based on the OpenCV project. It is subject to the license terms in the LICENSE file found in this distribution and at http://opencv.org/license.html

# Usage example:  python3 object_detection_yolo.py --video=run.mp4
#                 python3 object_detection_yolo.py --image=bird.jpg

import cv2 as cv
from operator import eq
import argparse
import sys
import numpy as np
import os.path
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
from multiprocessing import Queue
from multiprocessing import Process
#import sysv_ipc #shared Memory
import time
import base64
from PIL import Image
from io import BytesIO

#Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold
inpWidth = 320 #416     #Width of network's input image
inpHeight = 320 #416     #Height of network's input image

# Load names of classes
classesFile = "./video/coco.names";
#classesFile = "custom.names";
classes = None
searchObj = None
imageByte = "basic"

with open(classesFile, 'rt') as f:
  classes = f.read().rstrip('\n').split('\n')

def getSearchObj():
  return searchObj

def setSearchObj():
  global searchObj
  searchObj = None

#memory = sysv_ipc.Sharedmemory(aaaa,[flags=0_CREAT, [mode = 0600, [size = 0, [read_only = false]]]])

class ObjectDetection_YOLO():

  def __init__(self,q):
    global imageByte

    # Give the configuration and weight files for the model and load the network using them.
    modelConfiguration = "./video/yolov3-tiny.cfg";
    modelWeights = "./video/yolov3-tiny.weights";
    #modelWeights = "yolov3-tiny_obj_41600.weights";

    net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    inputQueue = Queue(maxsize=1)
    outputQueue = Queue(maxsize=1)
    detections = None

    p = Process(target=self.classify_frame, args=(net, inputQueue, outputQueue,))
    p.daemon = True
    p.start()

    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()

    while True:
   
      frame = vs.read()
      frame = imutils.resize(frame, width=400)
      (fH, fW) = frame.shape[:2]

    
      if inputQueue.empty():
        inputQueue.put(frame)

      if not outputQueue.empty():
        detections = outputQueue.get()
      if detections is not None:
        # Remove the bounding boxes with low confidence
        self.postprocess(frame, detections)
      cv.imshow("Frame",frame)
      key = cv.waitKey(1) & 0xFF
      '''
      #1205
      buffered = BytesIO()
      img = Image.fromarray(frame, 'RGB')
      size = (100, 100)
      img.thumbnail(size)
      img.save(buffered, format="jpeg")

      imageByte = base64.b64encode(buffered.getvalue())
      if q.empty():
        q.put(imageByte)
      #1205 finish
      '''
      if key == ord("q"):
        print("Stop people Search Model")
        break
  
    fps.update()

    fps.stop()
    cv.destroyAllWindows()
    vs.stop()



  # Get the names of the output layers
  def getOutputsNames(self,net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]



  # Giyeon Custom Multi-Processing
  def classify_frame(self, net, inputQueue, outputQueue):
    while True:
      if not inputQueue.empty():
        frame = inputQueue.get()
        frame = cv.resize(frame, (300, 300))
        blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)
        net.setInput(blob)
        detections = net.forward(self.getOutputsNames(net))    
        outputQueue.put(detections)

  # Draw the predicted bounding box
  def drawPred(self, frame ,classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
    label = '%.2f' % conf
        
    global classes

    # Get the label for the class name and its confidence
    if classes:
      assert(classId < len(classes))
        
      label = '%s:%s' % (classes[classId], label)
      
      peopleSearch = classes[classId]
      if eq(peopleSearch, "person") :
        label = '%s-%s' % ("sos", label)
        peopleSearch = "sos"
        #Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine), (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 1)
        self.sendClient(frame, label)    

  def sendClient(self, frame, label):
    global searchObj
    searchObj = label
    print("Search = ",label)

    
    #memory.write(label) #Write shared memory

  # Remove the bounding boxes with low confidence using non-maxima suppression
  def postprocess(self, frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
      for detection in out:
        scores = detection[5:]
        classId = np.argmax(scores)
        confidence = scores[classId]
        if confidence > confThreshold:
          center_x = int(detection[0] * frameWidth)
          center_y = int(detection[1] * frameHeight)
          width = int(detection[2] * frameWidth)
          height = int(detection[3] * frameHeight)
          left = int(center_x - width / 2)
          top = int(center_y - height / 2)
          classIds.append(classId)
          confidences.append(float(confidence))
          boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
      i = i[0]
      box = boxes[i]
      left = box[0]
      top = box[1]
      width = box[2]
      height = box[3]
      self.drawPred(frame, classIds[i], confidences[i], left, top, left + width, top + height)

    #cv.imshow(winName, frame)
 
