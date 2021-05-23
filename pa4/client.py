import sys
import socket
import threading

serverIP = '10.0.0.3'
serverPort = 10080
clientPort = 10081

# save allClient's information
allClient={}

#Client Socket
clientSocket = None

#destination of server(ip, port)

def socket_programming():
    global clientSocket
    global allClient

    while True:
        packet, senderAddress = clientSocket.recvfrom(1000)
        flag = packet.decode().split(":")[0]
        if flag == "0":    # register client
            name = packet.decode().split(":")[1]
            ip = packet.decode().split(":")[2]
            port = int(packet.decode().split(":")[3])
            allClient[name]=(ip, port)
        elif flag == "1":  # deregister client
            name = packet.decode().split(":")[1]
            del allClient[name]
        elif flag == "2":
            name = packet.decode().split(":")[1]
            msg = packet.decode().split(":")[2]
            print("From " + name + " [" + msg + " ]")


def showList():
    global allClient
    for key, value in allClient.items():
        print(key + "\t\t" + value[0]+":"+ str(value[1]))


def exitChat(clientID):
    dest = (serverIP, serverPort)
    clientSocket.sendto(("1:"+clientID).encode(), dest)
    exit()


def chat(clientID, text):
    global clientSocket
    global allClient
    Name = text.split(" ")[1]
    msg = text[6+len(Name):]
    print(msg)
    print(Name)
    clientSocket.sendto(("2:"+clientID + ":" +msg).encode(), allClient[Name])


def client(serverIP, serverPort, clientID):
    """
    Write your code!!!
    """
    global allClient
    global clientSocket


    dest = (serverIP, serverPort)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.sendto(("0:"+clientID).encode(), dest)

    t=threading.Thread(target=socket_programming)
    t.start()

    while True:
        method = input("")

        if method == "@show_list":
            showList()
        elif method == "@exit":
            exitChat(clientID)
        else:
            chat(clientID, method)

    pass


"""
Don't touch the code below!
"""
if  __name__ == '__main__':
    clientID = input("")
    client(serverIP, serverPort, clientID)


