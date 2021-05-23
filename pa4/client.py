import sys
import socket

serverIP = '10.0.0.3'
serverPort = 10080
clientPort = 10081


def client(serverIP, serverPort, clientID):
    """
    Write your code!!!
    """
    allClient={}
    dest = (serverIP, serverPort)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.sendto(clientID.encode(), dest)
    pass


"""
Don't touch the code below!
"""
if  __name__ == '__main__':
    clientID = input("")
    client(serverIP, serverPort, clientID)


