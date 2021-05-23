import sys
from time import sleep
import socket

serverPort = 10080

def server():
    """
    Write your code!!!
    """
    allClient={}
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    packet, senderAddress = receiverSocket.recvfrom(100)
    print(packet.decode())
    print(senderAddress)
    pass


"""
Don't touch the code below
"""
if  __name__ == '__main__':
    server()


