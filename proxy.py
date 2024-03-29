# -*- coding: utf-8 -*-
"""
Created on Tue Jan 01 17:37:51 2019

@author: msned
"""
import sys
import socket
import threading

def server_loop(local_host,local_port,remote_host,remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((local_host, local_port))
    except:
        print "[!!] failed to listen on %s:%d" % (local_host, local_port)
              
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        print "Incoming communication from %s:%d" % (addr[0], addr[1])
        
        #make thread to talk to remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,remote_host,remote_port,receive_first))
        
        proxy_thread.start()
        
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))
    
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        
        remote_buffer = response_handler(remote_buffer)
        
        #if data to send, send it
        if len(remote_buffer):
            print "[<==] sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
        
        while True:
            local_buffer = receive_from(client_socket)
            
            if len(local_buffer):
                print "Received %d bytes from localhost." % len(local_host)
                hexdump(local_buffer)
                
                #send to reponse handler
                remote_buffer = response_handler(remote_buffer)
                
                #send response to local socket
                client_socket.send(remote_buffer)
                print "[<==] Sent to localhost."
                
            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print "No more data, closing connections"
                
                break
        
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X %-*s %s" % (i, length*(digits + 1), hexa, text))
    print b'\n'.join(result)


def receive_from(connection):
    buffer = ""
    #adjustable timeout
    connection.settimeout(2)
    
    try:
        while True:
            data = connection.recv(4096)
            
            if not data:
                break
            buffer += data
    except:
        pass
    
    return buffer


def request_handler(buffer):
    #modifications
    return buffer

def response_handler(buffer):
    #modifications
    return buffer

        
def main():
    if len(sys.argv[1:]) != 5:
        print "Usage: proxy.py [localhost] [localport] [remotehost] [remoteport] [receivefirst]"
        sys.exit(0)
    
    #set up listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    #set up remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    server_loop(local_host,local_port,remote_host,remote_port,receive_first)
    
main()