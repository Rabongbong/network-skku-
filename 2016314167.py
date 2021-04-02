import socket
import os
import threading


def socket_programming():

  while True:
    msg = connectionSocket.recv(1024).decode()
    print(msg)
    filename = msg.split()[1].split('/')[1]
    print(filename)
    httpResHeader=''
    if not msg:
      print('bye')
      lock.release()
      break

    if(os.path.isfile(filename)):
      filetype = filename.split('.')[1]
      if(filetype=='html'):
        file = open(filename, 'rt', encoding='utf8')
        sendData = file.read()
        file.close()
        httpResHeader += 'HTTP/1.1 200 OK\r\n'
        httpResHeader += 'connection: keep-alive\r\n'
        httpResHeader += 'content-type: text/html; charset=utf-8\r\n'
        httpResHeader += '\r\n'
        httpResHeader +=sendData
        connectionSocket.send(httpResHeader.encode())
        #connectionSocket.close()
      else:
        file = open(filename, 'rb')
        sendData = file.read()
        file.close()
        httpResHeader += 'HTTP/1.1 200 OK\r\n'
        httpResHeader += 'connection: keep-alive\r\n'
        httpResHeader += 'content-type: text/html; charset=utf-8\r\n'
        httpResHeader += '\r\n'
        httpResHeader += sendData
        connectionSocket.send(httpResHeader.encode())
        # connectionSocket.close()
    else:
      httpResHeader += 'HTTP/1.1 404 Not Found\r\n'
      httpResHeader += 'connection: keep-alive\r\n'
      httpResHeader += 'content-type: text/html; charset=utf-8\r\n'
      httpResHeader += '\r\n'
      httpResHeader += '404 Not Found'
      connectionSocket.send(httpResHeader.encode())
      # connectionSocket.close()
  # lock.release()


if __name__ == "__main__":
  lock = threading.Lock()
  serverPort = 10080
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serverSocket.bind(('', serverPort))
  serverSocket.listen(5)
  while True:
    connectionSocket, addr = serverSocket.accept()
    # lock.acquire()
    t = threading.Thread(target=socket_programming)
    t.start()
  connectionSocket.close()