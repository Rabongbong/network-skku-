import sys
import socket
from logHandler import logHandler
import threading


def receiveACK(senderSocket):
  global windowSize
  global checkAck
  newMsg, recvAddr= senderSocket.recvfrom(1400)
  
  lock.acquire()
  logProc.writeAck(newMsg.decode(), 'received')
  lock.release()
  


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
  flag=1           # 파일을 다 읽었는지 여부 표시
  

  # ACK 처리하는 소켓
  t = threading.Thread(target=receiveACK, args=(senderSocket))
  t.start()


  while True:
    sendfile = open(srcFilename, 'rb')

    while windowSize !=0:
      resHeader=''
      logProc.startLogging("testSendLogFile.txt")

      if serialNumber == 0:
        resHeader += dstFilename
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
      # logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':
  lock = threading.Lock()
  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
  fileSender(recvAddr, windowSize, srcFilename, dstFilename)
