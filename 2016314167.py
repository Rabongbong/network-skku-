import socket
import os
import threading


def socket_programming(connectionSocket):

  while True:
    msg = connectionSocket.recv(1024).decode()
    print(msg)
    if not msg:
      print('bye')
      connectionSocket.close()
      break

    filename = msg.split()[1].split('/')[1]
    httpResHeader=''

    if(os.path.isfile(filename)):
      filetype = filename.split('.')[1]
      if(filetype=='html'):
        file = open(filename, 'rb')
        sendData = file.read()
        # print(sendData)
        file.close()
        httpResHeader += 'HTTP/1.1 200 OK\r\n'
        httpResHeader += 'keep-alive: 120\r\n'
        httpResHeader += 'connection: keep-alive\r\n'
        httpResHeader += 'content-type: text/html; charset=utf-8\r\n'
        httpResHeader += '\r\n'
        data = httpResHeader.encode()
        data += sendData
        connectionSocket.send(data)
        #connectionSocket.close()
      else:
        print(filetype)
        print(filename)
        file = open(filename, 'rb')
        sendData = file.read()
        file.close()
        httpResHeader += 'HTTP/1.1 200 OK\r\n'
        httpResHeader += 'keep-alive: 120\r\n'
        httpResHeader += 'connection: keep-alive\r\n'
        httpResHeader += 'content-type: image/png; charset=utf-8\r\n'
        # httpResHeader += 'content-length: %s\r\n' %len(sendData)
        httpResHeader += '\r\n'
        data = httpResHeader.encode()
        data += sendData
        connectionSocket.send(data)
        # connectionSocket.send()
        # connectionSocket.close()
    else:
      httpResHeader += 'HTTP/1.1 404 Not Found\r\n'
      httpResHeader += 'keep-alive: 120\r\n'
      httpResHeader += 'connection: keep-alive\r\n'
      httpResHeader += 'content-type: text/html; charset=utf-8\r\n'
      httpResHeader += '\r\n'
      httpResHeader += '404 Not Found'
      connectionSocket.send(httpResHeader.encode())
      # connectionSocket.close()
  # lock.release()


if __name__ == "__main__":
  # lock = threading.Lock()
  serverPort = 10080
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serverSocket.bind(('', serverPort))
  serverSocket.listen(5)
  while True:
    connectionSocket, addr = serverSocket.accept()
    # lock.acquire()
    t=threading.Thread(target=socket_programming, args=(connectionSocket,))
    t.start()