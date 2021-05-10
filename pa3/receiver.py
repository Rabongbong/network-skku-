import sys
import socket
import time
from logHandler import logHandler

def fileReceiver():
  #print('receiver program starts...')
  serverPort = 10080
  receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  receiverSocket.bind(('', serverPort))
  receiverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)
  dstFilename=""  
    
  logProc = logHandler()

  #########################
  #Write your Code here
  logProc.startLogging("testRecvLogFile.txt")
  receivePacket={}           #receive packet
  cumulativeACK=-1           #ACK
  lastPacket = None
  start_time = time.time()

  while True:
    packet, senderAddress = receiverSocket.recvfrom(1400)

    flag, file_name, packetNumber, body = packetParsing(packet)

    if not dstFilename: 
      dstFilename = file_name
      writefile = open(dstFilename, 'wb')
        
    logProc.writePkt(packetNumber, "received")

    # If receive packet is last packet
    if flag == '1':
      lastPacket = packetNumber


    if packetNumber == cumulativeACK + 1:
      cumulativeACK +=1
      writefile.write(body)

      while True:
        if cumulativeACK +1 not in receivePacket.keys():
          break
        cumulativeACK+=1
        writefile.write(receivePacket[cumulativeACK])

        del receivePacket[cumulativeACK]

    elif packetNumber > cumulativeACK + 1:
      receivePacket[packetNumber]=body

    receiverSocket.sendto(str(cumulativeACK).encode(), senderAddress)
    logProc.writeAck(cumulativeACK, "sent")

    # if receive last packet
    if cumulativeACK == lastPacket:
      throughput = (lastPacket+1)/(time.time()-start_time)
      logProc.writeEnd(throughput)
      break
  
  receiverSocket.close()
  writefile.close()

#########################
# Parsing packet data to flag, fileName, packetNumber, body
def packetParsing(packet):
    flag = packet[:1].decode()  
    fileName = packet[1:50].decode().split('\0')[0]
    packetNumber = int(packet[50:100].decode())
    body = packet[100:]
    return flag, fileName, packetNumber, body

if __name__=='__main__':
    fileReceiver()
