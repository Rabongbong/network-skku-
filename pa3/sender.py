import sys
import socket
from logHandler import logHandler
import time


def fileSender(recvAddr, windowSize, srcFilename, dstFilename):

  logProc = logHandler()
  throughput = 0.0
  avgRTT = 10.0

  ##########################
  serverPort = 10080  #port
  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
  serialNumber=0
  sendBuffer={}    # 파일에서 읽어오는 내용은 list에 저장
  checkACK={}      # check ACK is arrived or not
  checkTime={}     # check time(packet)
  flag=1           # 파일을 다 읽었는지 여부 표시
  ACK=-1           # ACK  

  logProc.startLogging("testSendLogFile.txt")
  sendfile = open(srcFilename, 'rb')
  resHeader=''
  senderSocket.settimeout(1.0)


  # 초기에 packet 보내기
  while windowSize!=0:
    if serialNumber == 0:
      resHeader += dstFilename
      resHeader += str(serialNumber)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      sendBuffer[serialNumber]=sendData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
      logProc.writePkt(serialNumber, 'sent')
      windowSize -= 1
      serialNumber += 1

    else:
      resHeader += str(serialNumber)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      sendBuffer[serialNumber]=sendData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
      logProc.writePkt(serialNumber, 'sent')
      windowSize -= 1
      serialNumber += 1


  while True:
    try:
      newMsg, recvAddr = senderSocket.recvfrom(1400)

    except timeout:
      senderSocket.sendto(sendBuffer[ACK+1], (recvAddr, serverPort))
      logProc.writePkt(serialNumber, 'retransmitted')

    else:
      ACK =  newMsg.decode()
      logProc.writeAck(ACK, 'received')
      for i in range(0, ACK):
        del sendBuffer[i]


    if serialNumber == 0:
      resHeader += dstFilename
      resHeader += str(serialNumber)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      sendBuffer[serialNumber]=sendData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
      logProc.writePkt(serialNumber, 'sent')
      windowSize -= 1
      serialNumber += 1

      else:
        resHeader += str(serialNumber)
        fileData = sendfile.read(1400-len(resHeader))
        sendData = resHeader.encode()
        sendData += fileData
        sendBuffer[serialNumber]=sendData
        senderSocket.sendto(sendData, (recvAddr, serverPort))
        lock.acquire()
        logProc.writePkt(serialNumber, 'sent')
        windowSize -= 1
        serialNumber += 1
        lock.release()

      if fileData =="":
        flag=0
        sendfile.close()
        break
    
    if flag ==0:
      break

  sendfile.close();
  logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':

  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
  fileSender(recvAddr, windowSize, srcFilename, dstFilename)
