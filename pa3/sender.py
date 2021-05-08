import sys
import socket
from logHandler import logHandler
import time
import os

avgRTT = 1.0
devRTT = 0.1

def calculateTimeout(sampleRTT):
    global avgRTT
    global devRTT
    
    a = 0.125
    b = 0.25

    avgRTT = (1 - a) * avgRTT + a * sampleRTT
    devRTT = (1 - b) * devRTT + b * abs(sampleRTT - avgRTT) 
    
    return avgRTT + 4 * devRTT

def fileSender(recvAddr, windowSize, srcFilename, dstFilename):

  logProc = logHandler()
  throughput = 0.0
  lastSerialNumber = os.stat(srcFilename).st_size // 1300

  ##########################
  serverPort = 10080  #port
  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
  serialNumber=0
  sendBuffer={}    # 파일에서 읽어오는 내용은 list에 저장
  checkACK={}      # check ACK is arrived or not
  timeBuffer={}    # store time for drop
  flag=0           # 마지막 패킷인지 확인 (마지막 패킷:1)
  ack=0            # ack #
  duplicateFlag =0 # check duplicate
  timeOut = 1.0

  logProc.startLogging("testSendLogFile.txt")
  sendfile = open(srcFilename, 'rb')
  resHeader=''
  senderSocket.settimeout(timeOut)

  start_time = time.time()

  # 초기에 packet 보내기(header size:100(filename:49 + serialnumber:50 + flag:1) + body size:1300)
  while windowSize!=0:
    resHeader += dstFilename
    resHeader += '\0' * (49-len(dstFilename))
    resHeader += '0' * (50-len(str(serialNumber)))
    resHeader += str(serialNumber)
    resHeader += str(flag)
    fileData = sendfile.read(1300)
    sendData = resHeader.encode()
    sendData += fileData
    sendBuffer[serialNumber]=sendData  #store data
    senderSocket.sendto(sendData, (recvAddr, serverPort))
    timeBuffer[serialNumber]=time.time()  # store time
    logProc.writePkt(serialNumber, 'sent')
    windowSize -= 1
    serialNumber += 1

  while True:
    try:
      newMsg, recvAddr = senderSocket.recvfrom(1400)

    except timeout:

      outTime = round(timeBuffer[ack]-start_time, 3)
      senderSocket.sendto(sendBuffer[ack], (recvAddr, serverPort))

      logProc.writePkt(ack, 'timeout since ' + str(outTime) + '(time out value ' + str(round(timeOut, 3)) + ')')
      logProc.writePkt(ack, 'retransmitted')
      duplicateFlag=0


    else:
      ACK = newMsg.decode()
      logProc.writeAck(ACK, 'received')

      try:
        sampleRTT = time.time()-timeBuffer[ACK]
        timeOut =calculateTimeout(sampleRTT)
        senderSocket.settimeout(timeOut)

      if ACK == lastSerialNumber:
        break

      elif ACK == ack:
        if duplicateFlag==3:
          senderSocket.sendto(sendBuffer[ACK+1], (recvAddr, serverPort))
          logProc.writePkt(serialNumber, '3 duplicated ACKs')
          logProc.writePkt(serialNumber+1, 'retransmitted')
          duplicateFlag=0

      elif ACK > ack:
        duplicateFlag=0
        for i in range(0, ACK):
          if i in sendBuffer.keys():
            del sendBuffer[i]

        for i in range(0, ACK):
          if i in timeBuffer.keys():
            del timeBuffer[i]

        sendWindowSize = ACK - ack
        ack = ACK

        while sendWindowSize!=0:
          resHeader += dstFilename
          resHeader += '\0' * (49-len(dstFilename))
          resHeader += '0' * (50-len(str(serialNumber)))
          resHeader += str(serialNumber)
          resHeader += str(flag)
          fileData = sendfile.read(1300)
          sendData = resHeader.encode()
          sendData += fileData
          sendBuffer[serialNumber]=sendData
          senderSocket.sendto(sendData, (recvAddr, serverPort))
          logProc.writePkt(serialNumber, 'sent')
          windowSize -= 1
          serialNumber += 1

  senderSocket.close()
  endtime = time.time()
  sendfile.close()

  throughput = serialNumber /(endtime- start_time)
  logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':

  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
  fileSender(recvAddr, windowSize, srcFilename, dstFilename)
