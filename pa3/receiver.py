import sys
import socket
from logHandler import logHandler
import time

def findNumber(receivePacket):
  for i in range(0, 100):
    if receivePacket[i] == 48:
      return i


def sendACK(receiverSocket):
  global ACK
	global receiveACK
  receiverSocket.sendto(ACK.encode(), senderAddress)

  logProc.writeAck(ACK, "sent")

#(header size:100(filename:49 + serialnumber:50 + flag:1) + body size:1300)
def parsePacket(packet):
  filename = packet[:49].decode().split('\0')[0]
  serialNumber = packet[49:99].decode()
  flag = packet[99:100].decode()
  body = packet[100:]
  return filename, serialNumber, flag, body


def fileReceiver():
  # print('receiver program starts...')
  logProc = logHandler()
  throughput = 0.0


  #########################
  serverPort = 10080
  receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  receiverSocket.bind(('', serverPort))

  start_time = time.time()
  ACK=0                		#ACK
  receiveACK={}           #receiveACK
  dstFilename=""          # destination filename

  logProc.startLogging("testRecvLogFile.txt")

  while True:
    message, senderAddress = receiverSocket.recvfrom(1400)
    filename, serialNumber, flag, body = parsePacket(message)

    if not dstFilename:
      dstFilename = filename


    if flag == '1':


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
  fileReceiver()
