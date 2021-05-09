import sys
from socket import *
import os
import time
from logHandler import logHandler

###### Global variables #######
# RTT time
avg_rtt = 1.0
dev_rtt = 0.1

# Window size
window_size = None

# Receiver ip
dest = None

# File name in header
header_fn = None

# Sender socket
sender = None

# Is the last packet sent
# is_last_packet_sent = False

# Single start time 
start_time = None

# Transmitted time per packet
transmitted_time = {}


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

# Send packet to receiver
def sendPacket(f, seq, last_packet):
    # global is_last_packet_sent

    # Make packet number for header
    header_pn = paddingNumber(seq).encode()

    # Make body of packet
    body = fileRead(f, seq)


    # if the packet is the last packet, flag is set to O
    if seq == last_packet:
        header_flag = "O"
        # is_last_packet_sent = True

    else:
        header_flag = "X"

    # Send packet
    sender.sendto(header_flag.encode() + header_fn + header_pn + body, dest)

    # Store Transmission time
    transmitted_time[seq] = time.time()

# Calculate timeout by rtt
def calculateTimeout(sample_rtt):
    global avg_rtt
    global dev_rtt
    
    a = 0.125
    b = 0.25
    
    avg_rtt = (1 - a) * avg_rtt + a * sample_rtt
    dev_rtt = (1 - b) * dev_rtt + b * abs(sample_rtt - avg_rtt) 
    
    return avg_rtt + 4 * dev_rtt

# Sender function
def fileSender(recvAddr, srcFilename, dstFilename, last_packet, windowSize):

    # Use global variable
    global header_fn
    global window_size
    global dest
    # global is_last_packet_sent
    global sender
    global start_time

    logProc = logHandler()
    # File discriptor
    f = open(srcFilename, 'rb')
    logProc.startLogging("testSendLogFile.txt")
    
    dest = (recvAddr, 10080)
    # Assign variables to global variable
    header_fn = paddingFilename(dstFilename).encode()
    window_size = windowSize
    available_window = window_size
    dest = ds
    seq_base = -1
    last_number = last_packet
    duplicated = 0

    sender = socket(AF_INET, SOCK_DGRAM)
    
    to = 1.0 # initial value = 1 second
    sender.settimeout(to)

    start_time = time.time()

    # Send packets as much as available window size
    while available_window > 0:
        packet_number = seq_base + 1 + window_size - available_window
        if packet_number > last_number:
            break

        sendPacket(f, packet_number, last_number)
        log_time = transmitted_time[packet_number] - start_time

        logProc.writePkt(packet_number, 'sent')

        available_window -= 1

    # After receive ack from receiver
    while True:
        try:
            ack, receiver = sender.recvfrom(100)
            
        except timeout:

            lt = round(transmitted_time[seq_base+1] - start_time, 3)
            sendPacket(f, seq_base + 1, last_number)

            log_time = transmitted_time[seq_base + 1] - start_time
            event = "timeout since " + str(lt)  + " (timeout value " + str(round(to, 3)) +")"
            logProc.writePkt(seq_base+1, event)
            logProc.writePkt(seq_base+1, 'retransmitted')
            duplicated = 0

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
                sample_rtt = time.time() - transmitted_time[ack] 
                to = calculateTimeout(sample_rtt)
                sender.settimeout(to)

            except KeyError:
                # duplicated key
                duplicated = duplicated + 1
                if duplicated == 2:
                    sendPacket(f, seq_base + 1, last_number)
                    log_time = transmitted_time[seq_base+1] - start_time
                    logProc.writePkt(seq_base, '3 duplicated ACKs')
                    logProc.writePkt(seq_base+1, 'retransmitted')

                    duplicated = 0
            
            if ack == last_number:
                break

            elif ack > seq_base:
                duplicated = 0
                key_list = list(transmitted_time.keys())
                for key in key_list:
                    if key <= ack:
                        del transmitted_time[key]
                available_window = ack - seq_base
                seq_base = ack

                while available_window > 0:
                    packet_number = seq_base + 1 + window_size - available_window
                    if packet_number > last_number:
                        break

                    sendPacket(f, packet_number, last_number)
                    log_time = transmitted_time[packet_number] - start_time
                    logProc.writePkt(packet_number, 'sent')

                    available_window -= 1


            elif ack == seq_base:
                if duplicated == 3:
                    sendPacket(f, seq_base + 1, last_number)
                    log_time = transmitted_time[seq_base+1] - start_time
                    logProc.writePkt(seq_base, '3 duplicated ACKs')
                    logProc.writePkt(seq_base+1, 'retransmitted')
                    duplicated = 0


    sender.close()
    endtime = time.time()

    throughput = (last_number + 1) / (endtime - start_time)
    logProc.writeEnd(throughput, avg_rtt*1000)

    f.close()



if __name__=='__main__':

    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name
    
    last_packet = os.stat(srcFilename).st_size // 1300

    # Call sender function
    fileSender(recvAddr, srcFilename, dstFilename, last_packet, windowSize)

