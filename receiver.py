import sys
from socket import *
import time


def fileReceiver():
    receiver = socket(AF_INET, SOCK_DGRAM)
    receiver.bind(('0.0.0.0', 10080))
    receiver.setsockopt(SOL_SOCKET, SO_SNDBUF, 10000000)
    file_name_cur = ""
    
    while True:
        # Get packet
        packet, sender = receiver.recvfrom(1400)

        # Get parsed packet
        flag, file_name, packet_number, bytes_to_write = packetParsing(packet)

        if not file_name_cur: # If the first packet of file is already received 
            file_name_cur = file_name
            fileReceiver = FileReceiver(file_name)
        
        fileReceiver.writePkt(packet_number, "received")

        # If the packet is the last one
        if flag == 'O':
            fileReceiver.calulateLastPacket(packet_number)

        # If the packet is in-order 
        if packet_number == fileReceiver.cumulative_ack + 1:
            fileReceiver.receiveInOrder(bytes_to_write)

        # If the packet is out-of-order
        elif packet_number > fileReceiver.cumulative_ack + 1:
            fileReceiver.receiveOutOrder(packet_number, bytes_to_write)

        # Send cumulative ack
        receiver.sendto(str(fileReceiver.cumulative_ack).encode(), sender)
        fileReceiver.writeAck(fileReceiver.cumulative_ack)

        # If receiving is done
        if fileReceiver.isComplete():
            fileReceiver.writeEnd()
            exit(0)


class FileReceiver:
    def __init__(self, fn):
        self.fd = open(fn, 'wb')        # New file
        self.cumulative_ack = -1        # cumulative_ack
        self.upcoming_packets = {}      # Upcoming packets
        self.last_packet = None         # The last packet name
        self.start_time = time.time()   # Start time of receiving certain file
        self.log = open(fn + "_receiving_log.txt", 'w') # Log file

    def calulateLastPacket(self, last_packet_number):
            self.last_packet = last_packet_number

    def receiveInOrder(self, body):
        self.cumulative_ack += 1
        self.fd.write(body)

        while True:
            # If the recieved packet is received for the first time
            if self.cumulative_ack + 1 not in self.upcoming_packets.keys():
                break

            # Update the cumulative ack
            self.cumulative_ack += 1

            # Write received data
            self.fd.write(self.upcoming_packets[self.cumulative_ack])
            
            # Remove the received packet from future packets
            del self.upcoming_packets[self.cumulative_ack]

    def receiveOutOrder(self, packet_number, body):
        self.upcoming_packets[packet_number] = body

    def isComplete(self):
        return self.cumulative_ack == self.last_packet

    # Log functions #
    def writeEnd(self):
        self.log.write('File transfer is finished.\n')
        throughput = (self.last_packet + 1) / (time.time() - self.start_time)
        self.log.write('Throughput : {:.2f} pkts/sec'.format(throughput))
        self.fd.close()
        self.log.close()

    def writePkt(self, pktNum, event):
        procTime = time.time() - self.start_time
        self.log.write('{:1.3f} pkt: {} | {}\n'.format(procTime, pktNum, event))

    def writeAck(self, ackNum):
        procTime = time.time() - self.start_time
        self.log.write('{:1.3f} ACK: {} | {}'.format(procTime, ackNum, "sent\n"))

# Parsing packet data
def packetParsing(packet):
    fl = packet[:1].decode()
    fn = packet[1:150].decode().split('\0')[0]
    pn = int(packet[150:200].decode())
    fb = packet[200:]
    return fl, fn, pn, fb

if __name__=='__main__':
    fileReceiver()
