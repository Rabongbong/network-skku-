import sys
import socket
from logHandler import logHandler

def fileSender(recvAddr, windowSize, srcFilename, dstFilename):

  logProc = logHandler()
  throughput = 0.0
  avgRTT = 10.0
  ##########################
  i=0
  serverPort = 10080  #port
  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
  while True:
    sendfile = open(srcFilename, 'rb')
    if i==0:
      resHeader=''
      resHeader += dstFilename
      resHeader += str(i)
      fileData = sendfile.read(1400-len(resHeader))
      sendData = resHeader.encode()
      sendData += fileData
      senderSocket.sendto(sendData, (recvAddr, serverPort))
			logProc.writePkt(i, 'sent')
      windowSize = windowSize-1
			i=i+1
		else:
  		fileData = sendfile.read(1400)
  		while fileData!= "":
  			
        
    newMsg, recvAddr= senderSocket.recvfrom(1400)
    logProc.startLogging("testSendLogFile.txt")
    logProc.writePkt(0, newMsg.decode())
    logProc.writeAck(1, "Like this")
    logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':
  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
  fileSender(recvAddr, windowSize, srcFilename, dstFilename)
