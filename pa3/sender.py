import sys
import socket
from logHandler import logHandler

def fileSender(recvAddr, windowSize, srcFilename, dstFilename):

  logProc = logHandler()
  throughput = 0.0
  avgRTT = 10.0

  ##########################
  serverPort = 10080  #port
  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
  serialNumber=0
  sendBuffer=[]    # 파일에서 읽어오는 내용은 list에 저장
  checkACK={}      # check ACK is arrived or not 


  while True:
    sendfile = open(srcFilename, 'rb')

    while windowSize !=0:
      resHeader=''
      logProc.startLogging("testSendLogFile.txt")

      if serialNumber==0:
        resHeader += dstFilename
        resHeader += str(serialNumber)
        fileData = sendfile.read(1400-len(resHeader))
        sendData = resHeader.encode()
        sendData += fileData
        sendBuffer.append(sendData)
        senderSocket.sendto(sendData, (recvAddr, serverPort))
        logProc.writePkt(serialNumber, 'sent')
        windowSize = windowSize-1
        serialNumber = serialNumber+1

      else:
        resHeader += str(serialNumber)
        fileData = sendfile.read(1400-len(resHeader))
        sendData = resHeader.encode()
        sendData += fileData
        sendBuffer.append(sendData)
        senderSocket.sendto(sendData, (recvAddr, serverPort))
        logProc.writePkt(serialNumber, 'sent')
        windowSize = windowSize-1
        serialNumber = serialNumber+1

      if fileData =="":
        break

      newMsg, recvAddr= senderSocket.recvfrom(1400)
      logProc.writeAck(newMsg.decode(), 'received')
      windowSize=windowSize+1
      # logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':
  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
  fileSender(recvAddr, windowSize, srcFilename, dstFilename)
