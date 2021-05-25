import sys
import socket
import threading
import time

serverIP = '10.0.0.3'
serverPort = 10080
clientPort = 10081

# save allClient's information(NAT)
allClient={}

# save allClient's information(local)
allLocalClient={}

#Client Socket
clientSocket = None

# Eflag for terminate thread
Eflag=0

def socket_programming():
    global clientSocket
    global allClient
    global allLocalClient
    global Eflag

    clientSocket.settimeout(3)

    while True:
        try:
            packet, senderAddress = clientSocket.recvfrom(300)

        except socket.timeout:
            pass

        else:
            flag = packet.decode().split(":")[0]
            if flag == "0":    # register client
                name = packet.decode().split(":")[1]
                ip = packet.decode().split(":")[2]
                port = int(packet.decode().split(":")[3])
                localIp = packet.decode().split(":")[4]
                localPort = int(packet.decode().split(":")[5])
                allClient[name]=(ip, port)
                allLocalClient[name]= (localIp, localPort)
            elif flag == "1":  # deregister client
                name = packet.decode().split(":")[1]
                del allClient[name]
                del allLocalClient[name]
            elif flag == "2":
                name = packet.decode().split(":")[1]
                msg = packet.decode().split(":")[2]
                print("From " + name + " [" + msg + " ]")
        
        finally:
            if Eflag == 1:
                break


def showList():
    global allClient
    global allLocalClient
    for key, value in allClient.items():
        print(key + "\t\t" + value[0]+":"+ str(value[1]))

def exitChat(clientID):

    global Eflag

    dest = (serverIP, serverPort)
    clientSocket.sendto(("1:"+clientID).encode(), dest)
    Eflag=1
    exit()

def chat(clientID, text):
    global clientSocket
    global allClient
    Name = text.split(" ")[1]
    clientIp = allClient[Name][0]
    myIp = allClient[clientID][0]
    msg = text[6+len(Name):]
    if clientIp==myIp:
        clientSocket.sendto(("2:"+clientID + ":" +msg).encode(), allLocalClient[Name])
    else:
        clientSocket.sendto(("2:"+clientID + ":" +msg).encode(), allClient[Name])

# send for keep alive
def keep_connect(clientID):

    global clientSocket
    global Eflag
    dest = (serverIP, serverPort)
    while True:
        time.sleep(10)
        if Eflag ==1:
            break
        clientSocket.sendto(("3:"+clientID).encode(), dest)
        if Eflag ==1:
            break


def client(serverIP, serverPort, clientID):
    """
    Write your code!!!
    """
    global allClient
    global clientSocket
    global clientPort

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", clientPort))
    ip_address = s.getsockname()[0]
    s.close()

    dest = (serverIP, serverPort)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind(('', clientPort))
    clientSocket.sendto(("0:"+clientID + ":" + ip_address + ":" + str(clientPort)).encode(), dest)

    t=threading.Thread(target=socket_programming)
    t.start()

    t1=threading.Thread(target=keep_connect, args=(clientID,))
    t1.start()

    while True:
        method = input("")

        if method == "@show_list":
            showList()
        elif method == "@exit":
            exitChat(clientID)
        else:
            chat(clientID, method)

"""
Don't touch the code below!
"""
if  __name__ == '__main__':
    clientID = input("")
    client(serverIP, serverPort, clientID)