import sys
import socket
from logHandler import logHandler
import os
import time

###### Global variables #######
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

# Is the last packet sent
is_last_packet_sent = False

# Last transmit time
last_transmit_time = None

# Single start time 
start_time = None

# Packet size
packet_size = 1400

# Header size 
header_size = 200



# Transmitted time per packet
transmitted_time = {}

# Body size
body_size = packet_size - header_size
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
    f.seek(seq*body_size)
    r = f.read(body_size)
    return r

# Send packet to receiver
def sendPacket(f, seq, last_packet):
    global is_last_packet_sent

    # Make packet number for header
    header_pn = paddingNumber(seq).encode()

    # Make body of packet
    body = fileRead(f, seq)


    # if the packet is the last packet, flag is set to O
    if seq == last_packet:
        header_flag = "1"
        is_last_packet_sent = True

    else:
        header_flag = "0"

    # Send packet
    senderSocket.sendto(header_flag.encode() + header_fn + header_pn + body, dest)

    # Store Transmission time
    transmitted_time[seq] = time.time()

# Calculate timeout by rtt
def calculateTimeout(sampleRTT):
    global avgRTT
    global devRTT
    
    a = 0.125
    b = 0.25
    
    avgRTT = (1 - a) * avgRTT + a * sampleRTT
    devRTT = (1 - b) * devRTT + b * abs(sampleRTT - avgRTT) 
    
    return avgRTT + 4 * devRTT

# Sender function
def fileSender(srcFilename, dstFilename, last_packet, windowSize):

    # Use global variable
    global header_fn
    global window_size
    global dest
    global is_last_packet_sent
    global senderSocket
    global start_time
    global last_transmit_time

    # File discriptor
    f = open(srcFilename, 'rb')
    logProc.startLogging("testSendLogFile.txt")

  
    header_fn = paddingFilename(dstFilename).encode()
    window_size = windowSize
    sendWindow = window_size
    serialNumber = -1
    last_number = last_packet
    checkDuplicated = 0

    senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    to = 1.0 # initial value = 1 second
    senderSocket.settimeout(to)

    start_time = time.time()

    # Send packets as much as available window size
    while sendWindow > 0:
        packet_number = serialNumber + 1 + window_size - sendWindow
        if packet_number > last_number:
            break

        sendPacket(f, packet_number, last_number)
        log_time = transmitted_time[packet_number] - start_time

        logProc.writePkt(packet_number, 'sent')

        sendWindow -= 1

    # After receive ack from receiver
    while True:
        try:
            ack, receiver = senderSocket.recvfrom(100)
            
        except timeout:

            lt = round(transmitted_time[serialNumber+1] - start_time, 3)
            sendPacket(f, serialNumber + 1, last_number)

            log_time = transmitted_time[serialNumber + 1] - start_time
            event = "timeout since " + str(lt)  + " (timeout value " + str(round(to, 3)) +")"
            logProc.writePkt(serialNumber+1, event)
            logProc.writePkt(serialNumber+1, 'retransmitted')
            checkDuplicated = 0

        except ConnectionResetError:
            print('client is not running')
            break
            
        else:
            ack = int(ack.decode())
            arrived_time = time.time()
            log_time = arrived_time - start_time
            logProc.writeAck(ack, 'received')


            # ack receive -> adjust timeout value
            try:
                sampleRTT = time.time() - transmitted_time[ack] 
                to = calculateTimeout(sampleRTT)
                senderSocket.settimeout(to)

            except KeyError:
                # duplicated key
                checkDuplicated = checkDuplicated + 1
                if checkDuplicated == 2:
                    sendPacket(f, serialNumber + 1, last_number)
                    logProc.writePkt(serialNumber, '3 duplicated ACKs')
                    logProc.writePkt(serialNumber+1, 'retransmitted')

                    checkDuplicated = 0
            
            if ack == last_number:
                break

            elif ack > serialNumber:
                checkDuplicated = 0
                key_list = list(transmitted_time.keys())
                for key in key_list:
                    if key <= ack:
                        del transmitted_time[key]
                sendWindow = ack - serialNumber
                serialNumber = ack

                while sendWindow > 0:
                    packet_number = serialNumber + 1 + window_size - sendWindow
                    if packet_number > last_number:
                        break

                    sendPacket(f, packet_number, last_number)
                    logProc.writePkt(packet_number, 'sent')

                    sendWindow -= 1


            elif ack == serialNumber:
                if checkDuplicated == 3:
                  sendPacket(f, serialNumber + 1, last_number)
                  logProc.writePkt(serialNumber, '3 duplicated ACKs')
                  logProc.writePkt(serialNumber+1, 'retransmitted')
                  checkDuplicated = 0

                else:
                    last_transmit_time = transmitted_time[ack + 1]

    senderSocket.close()
    endtime = time.time()

    throughput = (last_number + 1) / (endtime - start_time)
    logProc.writeEnd(throughput, avgRTT)

    f.close()


if __name__=='__main__':

  recvAddr = sys.argv[1]  #receiver IP address
  windowSize = int(sys.argv[2])   #window size
  srcFilename = sys.argv[3]   #source file name
  dstFilename = sys.argv[4]   #result file name
    

  last_packet = os.stat(srcFilename).st_size // 1300

  fileSender(srcFilename, dstFilename, last_packet, windowSize, dest)


