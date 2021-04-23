import socket
import os
import threading


def socket_programming(connectSocket):

  while True:
    msg = connectSocket.recv(2048).decode()
    connectFlag=True  

    if not msg:
      connectSocket.close()
      break

    if 'Connection' in msg:
      if 'keep-alive' in  msg:
        connectFlag=True
      elif 'close' in msg:
        connectFlag=False

    filename = msg.split()[1].split('/')[1]
    httpResHeader=''

    if(os.path.isfile(filename)):
      filetype = filename.split('.')[1]
      if(filetype=='html'):
        file = open(filename, 'rb')
        sendData = file.read()
        file.close()
        httpResHeader += 'HTTP/1.1 200 OK\r\n'
        httpResHeader += 'Connection: Keep-Alive\r\n'
        httpResHeader += 'Content-Type: text/html; charset=utf-8\r\n'
        httpResHeader += 'Content-Length: %d\r\n' %os.path.getsize(filename)
        httpResHeader += '\r\n'
        data = httpResHeader.encode()
        data += sendData
        connectSocket.send(data)
        if not connectFlag:
          connectSocket.close()
      else:
        file = open(filename, 'rb')
        sendData = file.read()
        file.close()
        httpResHeader += 'HTTP/1.1 200 OK\r\n'
        httpResHeader += 'Connection: Keep-Alive\r\n'
        httpResHeader += 'Content-Type: image/%s; charset=utf-8\r\n' %filetype
        httpResHeader += 'Content-Length: %d\r\n' %os.path.getsize(filename)
        httpResHeader += '\r\n'
        data = httpResHeader.encode()
        data += sendData
        connectSocket.send(data)
        if not connectFlag:
          connectSocket.close()
    else:
      error = '404 Not Found'    
      httpResHeader += 'HTTP/1.1 404 Not Found\r\n'
      httpResHeader += 'Connection: Keep-Alive\r\n'
      httpResHeader += 'Content-Type: text/html; charset=utf-8\r\n'
      httpResHeader += 'Content-Length: %d\r\n' %len(error.encode())
      httpResHeader += '\r\n'
      data = httpResHeader.encode()
      data += error.encode()
      connectSocket.send(data)
      if not connectFlag:
        connectSocket.close()


if __name__ == "__main__":
  serverPort = 10080
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serverSocket.bind(('', serverPort))
  serverSocket.listen(5)
  while True:    
    connectionSocket, addr = serverSocket.accept()
    t=threading.Thread(target=socket_programming, args=(connectionSocket,))
    t.start()