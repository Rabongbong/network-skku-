import sys
import socket
import os
import time
from logHandler import logHandler

# RTT time
avgRTT = 1.0
devRTT = 0.1

# Window size
window_size = None

# Receiver ip
dest = None

# File name in header
header_fn = None

# Sender socket
senderSocket = None

# save time for each packet
timeBuffer = {}

# save packet 
packetBuffer= {}

##############################

# padding packet number 
def paddingNumber(n):
    s = str(n)
    if len(s) > 50:
        return
    return '0' * (50 - len(s)) + s

# padding packet Filename
def paddingFilename(s):
    if len(s) > 49:
        return
    return s + '\0' * (49 - len(s))

# Read data for each packet
def fileRead(f, seq):
    f.seek(seq*1300)
    r = f.read(1300)
    return r

# Send packet to receiver (header size:100(filename:49 + serialnumber:50 + flag:1) + body size:1300)
def sendPacket(f, seq, last_packet):

    # Make packet number for header
    packetN = ('0' * (50 - len(str(seq))) + str(seq)).encode()
    # header_pn = paddingNumber(seq).encode()

    # Make body of packet
    body = fileRead(f, seq)

    # if the packet is the last packet, flag is set to O
    if seq == last_packet:
        header_flag = "1"

    else:
        header_flag = "0"

    # Send packet
    senderSocket.sendto(header_flag.encode() + header_fn + packetN + body, dest)

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
def fileSender(srcFilename, dstFilename, last_packet, windowSize, ds):

    # Use global variable
    global header_fn
    global window_size
    global dest
    global senderSocket

    # File discriptor
    f = open(srcFilename, 'rb')
    logProc = logHandler()
    logProc.startLogging("testSendLogFile.txt")


    # Assign variables to global variable
    header_fn = paddingFilename(dstFilename).encode()
    window_size = windowSize
    availableWindow = window_size
    dest = ds
    serialN = -1
    lastNumber = last_packet
    checkduplicated = 0

    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    timeOut = 1.0 # initial value: 1 second
    senderSocket.settimeout(timeOut)

    start_time = time.time()

    # Send packets as much as available window size
    while availableWindow > 0:
        packetNumber = serialN + 1 + window_size - availableWindow
        if packetNumber > lastNumber:
            break

        sendPacket(f, packetNumber, lastNumber)
        logProc.writePkt(packetNumber, 'sent')
        availableWindow -= 1

    # After receive ack from receiver
    while True:
        try:
            ack, receiver = senderSocket.recvfrom(100)
            
        except socket.timeout:

            lt = round(timeBuffer[serialN+1] - start_time, 3)
            sendPacket(f, serialN + 1, lastNumber)
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
                    sendPacket(f, serialN + 1, lastNumber)
                    logProc.writePkt(serialN, '3 duplicated ACKs')
                    logProc.writePkt(serialN+1, 'retransmitted')
                    checkduplicated = 0
            
            if ack == lastNumber:
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
                    packetNumber = serialN + 1 + window_size - availableWindow
                    if packetNumber > lastNumber:
                        break

                    sendPacket(f, packetNumber, lastNumber)
                    logProc.writePkt(packetNumber, 'sent')
                    availableWindow -= 1

            elif ack == serialN:
                if checkduplicated == 3:
                    sendPacket(f, serialN + 1, lastNumber)
                    logProc.writePkt(serialN, '3 duplicated ACKs')
                    logProc.writePkt(serialN+1, 'retransmitted')
                    checkduplicated = 0

    senderSocket.close()
    endtime = time.time()

    throughput = (lastNumber + 1) / (endtime - start_time)
    logProc.writeEnd(throughput, avgRTT*1000)

    f.close()

if __name__=='__main__':

    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name
    
    dest = (recvAddr, 10080)
    
    # calculate last_packet
    last_packet = os.stat(srcFilename).st_size // 1300

    fileSender(srcFilename, dstFilename, last_packet, windowSize, dest)



