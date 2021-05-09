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
  last_packet = None
  start_time = time.time()

  while True:
    packet, senderAddress = receiverSocket.recvfrom(1400)

    flag, file_name, packet_number, body = packetParsing(packet)

    if not dstFilename: 
      dstFilename = file_name
      writefile = open(dstFilename, 'wb')
        
    logProc.writePkt(packet_number, "received")

    # If the packet is the last one
    if flag == '1':
      last_packet = packet_number

    # If the packet is in-order 
    if packet_number == cumulativeACK + 1:
      cumulativeACK +=1
      writefile.write(body)

      while True:
        if cumulativeACK +1 not in receivePacket.keys():
          break
        cumulativeACK+=1
        writefile.write(receivePacket[cumulativeACK])

        del receivePacket[cumulativeACK]

    # If the packet is out-of-order
    elif packet_number > cumulativeACK + 1:
      receivePacket[packet_number]=body

    # Send cumulative ack
    receiverSocket.sendto(str(cumulativeACK).encode(), senderAddress)
    logProc.writeAck(cumulativeACK, "sent")

    # If receiving is done
    if cumulativeACK == last_packet:
      throughput = (last_packet+1)/(time.time()-start_time)
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
