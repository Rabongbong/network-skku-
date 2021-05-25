import sys
import time
import socket
import threading

serverPort = 10080
# save allClient's information
allClient={}

# save time for all clients
connectTime={}

#server Socket
serverSocket = None

#lock
lock = None


def address(value):
    ip = value.split(":")[0]
    port = value.split(":")[1]

    return (ip, int(port))


def check_alive():

    global serverSocket
    global connectTime
    global lock
    item =""
    lock.acquire()
    for key, value in connectTime.items():
        if (time.time() - value) > 30:
            disappear(key)
            item=key
    lock.release()

    if item!="":
        del connectTime[item]


def disappear(client):
    
    global allClient
    global serverSocket
    global connectTime
    global lock

    ip = allClient[client].split(":")[0]
    port = allClient[client].split(":")[1]
    info = ip +":" + str(port)
    print(client + " is disappeared \t\t" + info)
    del allClient[client]
    for key, value in allClient.items():
        data = ("1:" + client).encode()
        serverSocket.sendto(data, address(value))


def register_client(packet, senderAddress):

    global allClient
    global connectTime
    global serverSocket
    global lock

    clientInfo = packet.decode().split(":")[1]
    localIp = packet.decode().split(":")[2]
    localPort = packet.decode().split(":")[3]
    connectTime[clientInfo]=time.time()
    ip = senderAddress[0]
    port = str(senderAddress[1])
    info = ip +":" + port
    print(clientInfo + "\t\t" + info)
    allClient[clientInfo]= info + ":" + localIp + ":" + localPort

    for key, value in allClient.items():
        data = ("0:" + clientInfo + ":").encode()
        data+= allClient[clientInfo].encode()
        serverSocket.sendto(data, address(value))
    for key, value in allClient.items():
        data = ("0:" + key + ":").encode()
        data+= value.encode()
        serverSocket.sendto(data, senderAddress)


def unregister_client(packet, senderAddress):

    global allClient
    global serverSocket
    global connectTime
    global lock

    clientInfo = packet.decode().split(":")[1]
    ip = senderAddress[0]
    port = str(senderAddress[1])
    info = ip +":" + port
    print(clientInfo + "  is deregistered\t\t" + info)
    del allClient[clientInfo]
    lock.acquire()
    del connectTime[clientInfo]
    lock.release()
    for key, value in allClient.items():
        data = ("1:" + clientInfo).encode()
        serverSocket.sendto(data, address(value))


def keep_alive(packet):

    global connectTime
    global lock

    clientInfo = packet.decode().split(":")[1]
    connectTime[clientInfo]=time.time()


def server():
    """
    Write your code!!!
    """
    global allClient
    global connectTime
    global serverSocket
    global lock

    lock = threading.Lock()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    while True:
        packet, senderAddress = serverSocket.recvfrom(100)
        flag = packet.decode().split(":")[0]
        print(packet.decode())

        if flag == "0":      # register new client
           register_client(packet, senderAddress)

        elif flag == "1":    # deregister client
            unregister_client(packet, senderAddress)

        elif flag == "3":    # keep_alive
            keep_alive(packet)

        check_alive()

"""
Don't touch the code below
"""
if  __name__ == '__main__':
    server()