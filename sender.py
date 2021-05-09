import sys
import socket
import os
import time
from logHandler import logHandler


# RTT time
avgRTT = 1.0
devRTT = 0.1

# Sender socket
senderSocket = None

# save time for each packet
timeBuffer = {}

# File name in header
sendFileName = None


# Read data for each packet
def fileRead(f, seq):
    f.seek(seq*1300)
    r = f.read(1300)
    return r

# Send packet to receiver
def sendPacket(f, seq, last_packet, receiver):

    sendHeader=''
    global sendFileName
    # Make flag for last packet
    if seq == last_packet:
        header_flag = "1"
    else:
        header_flag = "0"
    sendHeader+=header_flag

    # Make filename
    sendFile= '\0' * (49 - len(sendFileName))
    sendHeader+=sendFile  
    
    # Make packet number
    packetNumber = '0' * (50 - len(str(seq))) + str(seq)
    sendHeader+=packetNumber   

    # Make body of packet
    body = fileRead(f, seq)

    senderSocket.sendto(sendHeader.encode()+ body, receiver)
    timeBuffer[seq] = time.time()

# Calculate timeout 
def calculateTimeout(sampleRTT):
    global avgRTT
    global devRTT
    
    a = 0.125
    b = 0.25
    
    avgRTT = (1 - a) * avgRTT + a * sampleRTT
    devRTT = (1 - b) * devRTT + b * abs(sampleRTT - avgRTT) 
    
    return avgRTT + 4 * devRTT


# FILE Sender function
def fileSender(recvAddr, srcFilename, dstFilename, last_packet, windowSize):

    global sendFileName
    global senderSocket

    logProc = logHandler()
    # File discriptor
    f = open(srcFilename, 'rb')
    logProc.startLogging("testSendLogFile.txt")

    # Assign variables to global variable
    serverPort = 10080
    sendFileName = dstFilename
    window_size = windowSize
    available_window = window_size
    receiver = (recvAddr, serverPort)
    seq_base = -1
    last_number = last_packet
    duplicated = 0

    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    timeout = 1.0 # initial value = 1 second
    senderSocket.settimeout(timeout)

    start_time = time.time()

    # Send packets as much as available window size
    while available_window > 0:
        packet_number = seq_base + 1 + window_size - available_window
        if packet_number > last_number:
            break

        sendPacket(f, packet_number, last_number, receiver)
        logProc.writePkt(packet_number, 'sent')

        available_window -= 1

    # After receive ack from receiver
    while True:
        try:
            ack, receiver = senderSocket.recvfrom(100)
            
        except socket.timeout:

            lt = round(timeBuffer[seq_base+1] - start_time, 3)
            sendPacket(f, seq_base + 1, last_number, receiver)

            event = "timeout since " + str(lt)  + " (timeout value " + str(round(timeout, 3)) +")"
            logProc.writePkt(seq_base+1, event)
            logProc.writePkt(seq_base+1, 'retransmitted')
            duplicated = 0

        except ConnectionResetError:
            print('client is not running')
            break
            
        else:
            ack = int(ack.decode())
            logProc.writeAck(ack, 'received')


            # ack receive -> adjust timeout value
            try:
                sampleRTT = time.time() - timeBuffer[ack] 
                timeout = calculateTimeout(sampleRTT)
                senderSocket.settimeout(timeout)

            except KeyError:
                # duplicated key
                duplicated = duplicated + 1
                if duplicated == 2:
                    sendPacket(f, seq_base + 1, last_number, receiver)
                    logProc.writePkt(seq_base, '3 duplicated ACKs')
                    logProc.writePkt(seq_base+1, 'retransmitted')
                    duplicated = 0
            
            if ack == last_number:
                break

            elif ack > seq_base:
                duplicated = 0
                key_list = list(timeBuffer.keys())
                for key in key_list:
                    if key <= ack:
                        del timeBuffer[key]
                available_window = ack - seq_base
                seq_base = ack

                while available_window > 0:
                    packet_number = seq_base + 1 + window_size - available_window
                    if packet_number > last_number:
                        break
                    sendPacket(f, packet_number, last_number, receiver)
                    logProc.writePkt(packet_number, 'sent')

                    available_window -= 1


            elif ack == seq_base:
                if duplicated == 3:
                    sendPacket(f, seq_base + 1, last_number, receiver)
                    logProc.writePkt(seq_base, '3 duplicated ACKs')
                    logProc.writePkt(seq_base+1, 'retransmitted')
                    duplicated = 0


    senderSocket.close()
    endtime = time.time()

    throughput = (last_number + 1) / (endtime - start_time)
    logProc.writeEnd(throughput, avgRTT*1000)

    f.close()



if __name__=='__main__':
    
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name
    
    last_packet = os.stat(srcFilename).st_size // 1300

    # Call sender function
    fileSender(recvAddr, srcFilename, dstFilename, last_packet, windowSize)

