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
    print(1)
    packet, senderAddress = serverSocket.recvfrom(1000)
    print(2)
    print(senderAddress)
    print(3)
    serverSocket.sendto(packet, senderAddress)
    print(4)
    pass


"""
Don't touch the code below
"""
if  __name__ == '__main__':
    server()


