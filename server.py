#server.py

import sys
import socket
import threading
from operator import eq


users = {}
num = 0
#Server to RaspberryPi(Camera)
HOST = '0.0.0.0' # All Port Connectting open
PORT = 9000
justOneStartPi = True

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP, Ipv4 setting
s.bind((HOST, PORT)) #binding everyone and Port 9000
s.listen(1) #wait
th_getMsg_1 = None
th_getMsg_2 = None
g_pi_data = None

class ThreadStart():

  def threading():
    global justOneStartPi
    print("-----thread start-----")
    #th_sendMsg.start()
    if justOneStartPi:
      th_getMsg_1.start()
      justOneStartPi = False


    th_getMsg_2.start()

  def checking(num):
    if num > 1:
      print("start Socket Connectting")
      ThreadStart.threading()



print("waitting client")

def conSocket():
  global num
  global th_getMsg_1, th_getMsg_2
  while True:
    conn, addr = s.accept()
    users[num] = (conn, addr)
    num = num+1
    if num == 1 :
      th_getMsg_1 = threading.Thread(target = gettingMsg_1, args=(conn,))
    elif num == 2 :
      th_getMsg_2 = threading.Thread(target = gettingMsg_2, args=(conn,))

    print('TCP Connect by', addr) # Check Connecting
    ThreadStart.checking(num)
   
th_conSocket = threading._start_new_thread(conSocket,())

def sendingMsg():
  print("-----connect mobile to drone------")
  global g_pi_data
  while True:
    chose = input("insert 1: Drone, 2: Mobile")
    
    if eq(chose,'1'):
      data = input("Insert message send to Drone")
      data = data.encode("utf-8")
      users[0][0].send(data) #first connect client
    elif eq(chose,'2'):
      data = input("Insert message send to Mobile : ")
      data = data+"\r\n"
      data = data.encode("utf-8")
      users[1][0].send(data) #Second connect client
    else :
      print("Please Check number\n------------------------------")

    if not eq(g_pi_data, None):
      print('inside sendMsg show data = ',g_pi_data)

  users[0][0].close()
  users[1][0].close()

def deliverMsg(who, data):
  global g_pi_data
  if eq(who,"mobile"): # mobile send to drone Message
    data = data.encode("utf-8")
    users[0][0].send(data) # first connect client(drone)
  
  elif eq(who,"drone"):
    data = data+"\r\n"
    data = data.encode("utf-8")
    users[1][0].send(data)

 
def gettingMsg_1(conn): #drone
  global g_pi_data
  while True:
    data = conn.recv(10000)
    if not data:
      break
    else:
      data = str(data).split("b'", 1)[1].rsplit("'",1)[0] # delete b'
      deliverMsg("drone",data)
      print(data)

     
  conn.close()


def gettingMsg_2(conn): #mobile
  global num
  while True:

    if num==1:
      print('num ==1 and break')
      break

    data = conn.recv(1024)
    
    if not data:
      break
    else:
      data = str(data).split("b'", 1)[1].rsplit("'",1)[0] # delete b'
      data = data[:-2] #delete \n
      
      if eq(data,"detach"):
        print("get detach")
        num = num -1;
      else:
        deliverMsg("mobile",data)
        print(data)
     
  conn.close()

th_sendMsg = threading.Thread(target = sendingMsg, args=())


#th_sendMsg = threading._start_new_thread(sendingMsg,())
#th_getMsg = threading._start_new_thread(gettingMsg,())


while True:
  pass



