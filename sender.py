import sys
import socket
import os
import time
from logHandler import logHandler

# RTT time
avgRTT = 1.0
devRTT = 0.1


# Receiver ip
dest = None

# File name(dstFilename)
sendFileName = None

senderSocket = None

# save time for each packet
timeBuffer = {}

# save packet 
packetBuffer= {}

##############################

# Read data for each packet
def fileRead(f, seq):
    f.seek(seq*1300)
    r = f.read(1300)
    return r

# Send packet to receiver (header size:100(filename:49 + serialnumber:50 + flag:1) + body size:1300)
def sendPacket(f, seq, lastPacket):

    #flag for lastPacket
    if seq == lastPacket:
        flag = "1"
    else:
        flag = "0"

    # Make packet number 
    packetN = ('0' * (50 - len(str(seq))) + str(seq)).encode()

    # Make body of packet
    body = fileRead(f, seq)

    # Send packet
    senderSocket.sendto(flag.encode() + sendFileName + packetN + body, dest)

    # Store Transmission time
    timeBuffer[seq] = time.time()

# Calculate timeout by rtt
def calTimeout(sampleRTT):
    global avgRTT
    global devRTT
    a = 0.125
    b = 0.25
    
    avgRTT = (1 - a) * avgRTT + a * sampleRTT
    devRTT = (1 - b) * devRTT + b * abs(sampleRTT - avgRTT) 
    return avgRTT + 4 * devRTT

# Sender function
def fileSender(srcFilename, dstFilename, lastPacket, windowSize, ds):


    global sendFileName
    global dest
    global senderSocket

    readFile = open(srcFilename, 'rb')
    logProc = logHandler()
    logProc.startLogging("testSendLogFile.txt")

    #########################
    
    #Write your Code here
    
    sendFileName = (dstFilename + '\0' * (49 - len(dstFilename))).encode()
    availableWindow = windowSize
    dest = ds
    serialN = -1
    checkduplicated = 0

    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    timeOut = 1.0 # initial value: 1 second
    senderSocket.settimeout(timeOut)

    start_time = time.time()

    # 초기에 windowSize 만큼 패킷을 보낸다.
    while availableWindow > 0:
        packetNumber = serialN + 1 + windowSize - availableWindow
        if packetNumber > lastPacket:
            break

        sendPacket(readFile, packetNumber, lastPacket)
        logProc.writePkt(packetNumber, 'sent')
        availableWindow -= 1

    # After receive ack from receiver
    while True:
        try:
            ack, receiver = senderSocket.recvfrom(100)
            
        except socket.timeout:

            lt = round(timeBuffer[serialN+1] - start_time, 3)
            sendPacket(f, serialN + 1, lastPacket)
            logProc.writePkt(serialN+1, "timeout since " + str(lt)  + " (timeout value " + str(round(timeOut, 3)) +")")
            logProc.writePkt(serialN+1, 'retransmitted')
            checkduplicated = 0
            
        else:
            ack = int(ack.decode())
            logProc.writeAck(ack, 'received')

            try:
                sampleRTT = time.time() - timeBuffer[ack] 
                timeOut = calTimeout(sampleRTT)
                senderSocket.settimeout(timeOut)

            except KeyError:
                # check duplicated key
                checkduplicated = checkduplicated + 1
                if checkduplicated == 2:
                    sendPacket(readFile, serialN + 1, lastPacket)
                    logProc.writePkt(serialN, '3 duplicated ACKs')
                    logProc.writePkt(serialN+1, 'retransmitted')
                    checkduplicated = 0
            
            if ack == lastPacket:
                break

            elif ack > serialN:
                checkduplicated = 0
                key_list = list(timeBuffer.keys())
                for key in key_list:
                    if key <= ack:
                        del timeBuffer[key]
                availableWindow = ack - serialN
                serialN = ack

                while availableWindow > 0:
                    packetNumber = serialN + 1 + windowSize - availableWindow
                    if packetNumber > lastPacket:
                        break

                    sendPacket(readFile, packetNumber, lastPacket)
                    logProc.writePkt(packetNumber, 'sent')
                    availableWindow -= 1

            elif ack == serialN:
                if checkduplicated == 3:
                    sendPacket(readFile, serialN + 1, lastPacket)
                    logProc.writePkt(serialN, '3 duplicated ACKs')
                    logProc.writePkt(serialN+1, 'retransmitted')
                    checkduplicated = 0

    senderSocket.close()
    endtime = time.time()

    throughput = (lastPacket + 1) / (endtime - start_time)
    logProc.writeEnd(throughput, avgRTT*1000)

    readFile.close()

if __name__=='__main__':

    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name
    serverPort = 10080

    dest = (recvAddr, serverPort)
    # calculate lastPacket
    lastPacket = os.stat(srcFilename).st_size // 1300

    fileSender(srcFilename, dstFilename, lastPacket, windowSize, dest)



