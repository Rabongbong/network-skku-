import sys
import socket
from logHandler import logHandler
import threading

def findNumber(receivePacket):
  for i in range(0, 100):
    if receivePacket[i] == 48:
      return i


def sendACK(receiverSocket):
  global ACK
	global receiveACK
  receiverSocket.sendto(ACK.encode(), senderAddress)
  lock.acquire()
  logProc.writeAck(ACK, "sent")
  lock.release()


def fileReceiver():
  # print('receiver program starts...')
  logProc = logHandler()
  throughput = 0.0

  #########################
  serverPort = 10080
  receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  receiverSocket.bind(('', serverPort))

  ACK=0                		#ACK
  receiveACK={}           #receiveACK
	filename=''

  t = threading.Thread(target=sendACK, args=(receiverSocket))

  logProc.startLogging("testRecvLogFile.txt")

  while True:
    if ACK==0:
      message, senderAddress = receiverSocket.recvfrom(1400)
      index = findNumber(message)
      filename = message[:index].decode()
      print(filename)
      writeFile = open(filename, 'wb')
      writeFile.write(message[index:])
      lock.acquire()
      logProc.writePkt(message[index].decode(), "received")
      lock.release()
			ACK+=1
		else:
  		message, senderAddress = receiverSocket.recvfrom(1400)
			writeFile.write(message[1:])
			lock.acquire()
      logProc.writePkt(message[0].decode(), "received")
      lock.release()
			ACK+=1
    
		# logProc.writeEnd(throughput)
  
    #Write your Code here
    #########################


if __name__=='__main__':
    lock = threading.Lock()
    fileReceiver()
