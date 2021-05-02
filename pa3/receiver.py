import sys
import socket
from logHandler import logHandler


def findNumber(receivePacket):
    for i in range(0, 100):
        if receivePacket[i] == 48:
            return i


def fileReceiver():
    # print('receiver program starts...')
    logProc = logHandler()
    throughput = 0.0

    #########################
    serverPort = 10080
    ACK=0
    receiveACK={}

    receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiverSocket.bind(('', serverPort))
    message, senderAddress = receiverSocket.recvfrom(1400)
    index = findNumber(message)
    # print(index)
    print(message[:index].decode())
    
    # write_file = open(dstFilename, 'wb')
    # write_file.write(message.decode())
    logProc.startLogging("testRecvLogFile.txt")
    logProc.writePkt(0, message.decode())
    logProc.writeAck(1, "Like this")
    logProc.writeEnd(throughput)
    # print(message.decode())
    newMsg = message
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
    #########################


if __name__=='__main__':
    fileReceiver()
