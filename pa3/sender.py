import sys
import socket
from logHandler import logHandler

def fileSender():
    
    logProc = logHandler()
    
    throughput = 0.0
    avgRTT = 10.0
    ##########################

    serverPort = 10080  #port
    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # resHeader=''
    # sendfile = open(srcFilename, 'rb')
    # sendData = sendfile.read(1400)
    # sendfile.close()
    # resHeader += dstFilename
    # print(1)
    sendData = "Hello"
    senderSocket.sendto(sendData.encode(), (recvAddr, serverPort))
    
    newMsg, recvAddr= senderSocket.recvfrom(1024)
    print(newMsg.decode())
    #senderSocket.close()
    #Write your Code here
    # logProc.startLogging("testSendLogFile.txt")
    
    # logProc.writePkt(0, "Use your log file Processor")
    # logProc.writeAck(1, "Like this")
    # logProc.writeEnd(throughput, avgRTT)
    ##########################


if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name

    fileSender()
