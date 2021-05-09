import sys
import socket
from logHandler import logHandler
import time


#(header size:100(filename:49 + serialnumber:50 + flag:1) + body size:1300)
def parsePacket(packet):
  filename = packet[1:50].decode().split('\0')[0]
  serialNumber = packet[50:100].decode()
  flag = packet[:1].decode()
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
  receivePacket={}           #receive packet
  dstFilename=""          # destination filename

  logProc.startLogging("testRecvLogFile.txt")

  while True:
    message, senderAddress = receiverSocket.recvfrom(1400)
    filename, serialNumber, flag, body = parsePacket(message)
    print(filename)
    print(serialNumber)
    if not dstFilename:
      dstFilename = filename
      writefile = open(dstFilename, 'wb')

    logProc.writePkt(serialNumber, "received")

    if serialNumber == ACK:
      writefile.write(body)
      ACK+=1

      while True:

        if ACK not in receivePacket.keys():
          break
        ACK +=1
        writefile.write(receivePacket[ACK])
        del receivePacket[ACK]

    elif serialNumber > ACK:
      receivePacket[serialNumber]=body

    receiverSocket.sendto(str(ACK).encode(), senderAddress)
    logProc.writeAck(serialNumber, "sent")


    # received last packet
    if flag == '1': 
      throughput = (ACK)/(time.time()-start_time)
      logProc.writeEnd(throughput)
      break
  
  receiverSocket.close()
  writefile.close()


    #Write your Code here
    #########################

if __name__=='__main__':
  fileReceiver()
