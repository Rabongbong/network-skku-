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
    
    while True:
        packet, senderAddress = serverSocket.recvfrom(1000)
        flag = packet.decode().split(":")[0]

        if flag == "0":   #register new client
            clientInfo = packet.decode().split(":")[1]
            allClient[clientInfo]=senderAddress
            ip = senderAddress[0]
            port = str(senderAddress[1])
            info = ip +":" + port
            print(clientInfo + "\t\t" + info)

            for key, value in allClient.items():
                data = ("0:" + clientInfo + ":").encode()
                data+=info.encode()
                serverSocket.sendto(data, value)
            for key, value in allClient.items():
                data = ("0:" + key + ":").encode()
                data+= (value[0]+":").encode() + str(value[1]).encode()
                serverSocket.sendto(data, senderAddress)

        elif flag == "1":    # deregister client
            clientInfo = packet.decode().split(":")[1]
            ip = senderAddress[0]
            port = str(senderAddress[1])
            info = ip +":" + port
            print(clientInfo + "  is deregistered\t\t" + info)
            del allClient[clientInfo]
            for key, value in allClient.items():
                data = ("1:" + clientInfo).encode()
                serverSocket.sendto(data, value)
    pass


"""
Don't touch the code below
"""
if  __name__ == '__main__':
    server()


