import cv2
from operator import eq
import sys
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
from multiprocessing import Queue
from multiprocessing import Process
import time




class SearchObject():

  def exit_model(self):
    print("exit_exit")
    sys.exit(1)

  def id_class_name(self,class_id, classes):
    for key, value in classes.items():
      if class_id == key:
        return value

  #add file
  def classify_frame(self, model, inputQueue, outputQueue):
    while True:
      if not inputQueue.empty():
        frame = inputQueue.get()
        frame = cv2.resize(frame, (300,300))
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True)
        model.setInput(blob)
        detections = model.forward()
        outputQueue.put(detections)


  
 
  def __init__(self):
    print("deep learning model")
  
    # Pretrained classes in the model
    classNames = {0: 'background', 1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle',
                  5: 'airplane', 6: 'bus', 7: 'train', 8: 'truck', 9: 'boat',
                  10: 'traffic light', 11: 'fire hydrant', 13: 'stop sign',
                  14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
                  18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
                  24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
                  32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
                  37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
                  41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
                  46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
                  51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
                  56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
                  61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
                  67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
                  75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
                  80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
                  86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}


  
    COLORS = np.random.uniform(0,255, size=(len(classNames),3))
    #loding model
    model = cv2.dnn.readNetFromTensorflow('./video/models/frozen_inference_graph.pb',
                                        './video/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')

    inputQueue = Queue(maxsize=1)
    outputQueue = Queue(maxsize=1)
    detections = None

    print("session 1 start")
    p = Process(target=self.classify_frame, args=(model, inputQueue, outputQueue,))
    p.daemon = True
    p.start()

    print("session 2 start")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()

    while True:
      frame = vs.read()
      frame = imutils.resize(frame, width=400)
      (fH, fW) = frame.shape[:2] # (300, 400)
      if inputQueue.empty():
        inputQueue.put(frame)

      if not outputQueue.empty():
        detections = outputQueue.get()
      if detections is not None:
        for value in np.arange(0, detections.shape[2]):
          i = value
          confidence = detections[0,0,i,2]
          #print("confidence = ",confidence)
          if confidence < .7:
             continue
          class_id = detections[0,0,i,1]
          class_name = self.id_class_name(class_id, classNames)
          print(str(str(class_id) + " " + str(detections[0,0,i,2]) + " " + class_name))
          idx = int(detections[0, 0, i, 1])
          dims = np.array([fW, fH, fW, fH])
          box = detections[0, 0, i, 3:7] * dims
          (startX, startY, endX, endY) = box.astype("int")
          label = "{}: {:.2f}%".format(classNames[idx], confidence * 100)
          cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
          y = startY -15 if startY -15 > 15 else startY +15
          cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

      cv2.imshow("Frame", frame)
      key = cv2.waitKey(1) & 0xFF

      if key ==ord("q"):
        print("Stop people Search Model")
        break

      fps.update()

    fps.stop()
    cv2.destroyAllWindows()
    vs.stop() 
