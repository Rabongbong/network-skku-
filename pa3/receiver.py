import sys
import socket
from logHandler import logHandler

def fileReceiver():
    print('receiver program starts...')
    logProc = logHandler()
    throughput = 0.0

    #########################
    serverPort = 10080
    receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiverSocket.bind(('', serverPort))
    #print('The server is ready to receive')
    message, senderAddress = receiverSocket.recvfrom(1024)
    # print(2)
    print(message.decode())
    # write_file = open(dstFilename, 'wb')
    # write_file.write(message.decode())
    newMsg = 'hello'
    receiverSocket.sendto(newMsg.encode(), senderAddress)
    # while True:
    #     print(1)
    #     message, senderAddress = receiverSocket.recvfrom(2048)
    #     print(2)
    #     print(message)
    #     receivefile = open(dstFilename, 'wb')
    #     receivefile.write(message)
    #     newMsg = 0
    #     receiverSocket.sendto(newMsg.encode(), serverAddress)
    #     break
    #Write your Code here
    logProc.startLogging("testRecvLogFile.txt")
    logProc.writePkt(0, "Use your log file Processor")
    logProc.writeAck(1, "Like this")
    logProc.writeEnd(throughput)
    #########################


if __name__=='__main__':
    fileReceiver()
