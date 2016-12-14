#!/usr/bin/python3
import socket
import select
import sys
from time import time
from socket import error as socket_error
import json

host = ''
port_mobile = 2000
port_locker = 2001
backlog = 5
size = 1024

# Create and bind Mobile socket
mobile_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mobile_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mobile_socket.bind((host, port_mobile))
mobile_socket.listen(backlog)

# Create and bind Locker socket
locker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
locker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
locker_socket.bind((host, port_locker))
locker_socket.listen(backlog)

print('Server Running!')

while True:
    # Create list of available locker numbers
    sequence = list(range(0,8))

    # Accept client connections
    mobile_client, mobile_address = mobile_socket.accept()
    print('Connected to Mobile Client')
    print(mobile_address)
    
    locker_client, locker_address = locker_socket.accept()
    print('Connected to Locker Client')
    print(locker_address)

    while True:

        # Try to receive a message from somebody
        inputs = [ mobile_client, locker_client ]
        outputs = [ ]

        readable, writable, exceptional = select.select ( inputs, outputs, inputs, 15.0 )
        hadInput = 0

        for inputdata in readable:
            hadInput = 1
            data = inputdata.recv(size)
            
            if data:
                
                if (inputdata == mobile_client):
                    info = json.loads(data.decode())

                    # Parse received JSON order 
                    name = info['name']
                    email = info['email']
                    idNum = info['idnum']
                    restaurant = info['rest']
                    time = info['time']

                    print('Received Order from Mobile: ' + name + ' ' + email + ' ' + idNum + ' ' + restaurant + ' ' + time)

                    # Send the mobile Pi a locker number for their order
                    # If none available, send an error message (locker # -1 = error msg)
                    if not sequence:
                        none_avail_error = -1
                        print('No Lockers Available, About to send error: ' + str(none_avail_error))
                        mobile_client.send(str(none_avail_error).encode()) # send error 
                    else:
                        this_locker = sequence.pop() # get highest locker # in list
                        print('About to send locker number: ' + str(this_locker))
                        mobile_client.send(str(this_locker).encode()) # send locker #

                    # Send order information and locker # to locker Pi
                    info['idnum'] = (str(this_locker))
                    print('About to send to Locker -- locker number: ' + str(this_locker) + ', order information: ' + str(info))
                    
                    infoJson = json.dumps(info)
                    locker_client.send(infoJson.encode())
                    
                elif (inputdata == locker_client):
                    print('Received Data from Locker: ' + data.decode())
                    # Received a message indicating which locker is now empty and available
                    # Add that locker number back into available list
                    locker_number = int(data)
                    print('Locker #' + str(locker_number) + ' Now Available') 
                    sequence.append(locker_number)
                else :
                    print('invalid')
            #else:
                #hadInput = 1
                #print('Nothing there')

        #if (hadInput == 0):
            #print ('Timeout waiting for any message.  Restarting')
            #sys.exit(0)

#client.close()
