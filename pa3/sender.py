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

    resHeader=''
    resHeader += dstFilename
    resHeader += str(i)
    sendfile = open(srcFilename, 'rb')
    fileData = sendfile.read(1400-len(resHeader))
    sendfile.close()
    sendData = resHeader.encode()
    sendData += fileData
    senderSocket.sendto(sendData, (recvAddr, serverPort))
    windowSize = windowSize-1



    newMsg, recvAddr= senderSocket.recvfrom(1400)
    # print(newMsg.decode())
    #senderSocket.close()
    #Write your Code here
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
