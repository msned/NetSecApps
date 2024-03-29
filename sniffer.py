# -*- coding: utf-8 -*-
"""
Network Scanner

@author: msned
"""

import socket
import os
import struct
from ctypes import *
import threading
import time

#host to listen on
host = "192.168.1.79"

#subnet to target
subnet = "192.168.0.0/24"

#String to check ICMP responses for
message = "Checkstop"

#sends Datagrams
def udp_sender(subnet,message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for ip in IPNetwork(subnet):
        try:
            sender.sendto(message, ("%s" % ip,65212))
        except:
            pass

#Code for IP header
class IP(Structure):
    _fields_ = [
            ("ihl", c_ubyte, 4),
            ("version", c_ubyte, 4), 
            ("tos", c_ubyte),
            ("len", c_ushort),
            ("id", c_ushort),
            ("offset", c_ushort),
            ("ttl", c_ubyte),
            ("protocol_num", c_ubyte),
            ("sum", c_ushort),
            ("src", c_ulong),
            ("dst", c_ulong)]
    
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        #map protocol constants to their name
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        
        #human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        
        #human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields_ = [
            ("type", c_ubyte),
            ("code", c_ubyte),
            ("checksum", c_ushort),
            ("unused", c_ushort),
            ("next_hop_mtu", c_ushort)]
    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)
    def __init__(self, socket_buffer):
        pass

#raw socket bound to public interface
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host,0))
#include IP headers in capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

#windows os requires IOCTL to enter promiscuous mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

#t = threading.Thread(target=udp_sender,args=(subnet,message))
#t.start()

try:
    while True:
        raw_buffer = sniffer.recvfrom(65565)[0]
        
        ip_header = IP(raw_buffer[0:20])
        
        print "Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address)
        
        if ip_header.protocol == "ICMP":
            #calc offset to ICMP packet
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]
            
            icmp_header = ICMP(buf)
            print "ICMP -> Type: %d" % (icmp_header.type, icmp_header.code)
            #if icmp_header.code == 3 and icmp_header.type == 3:
                #if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                    #if raw_buffer[len(raw_buffer) - len(message):] == message:
                       # print "Host Up: %s" % ip_header.src_address
            
except KeyboardInterrupt:
    #if Windows turn off promiscuous
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

        



