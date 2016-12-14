# Written By Zachary Taylor
# December 14th, 2016
# Locker System for Gobble 2 Go 

#!/usr/bin/env/ pyhton

import RPi.GPIO as GPIO
import sys, socket
import json

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Arrays for managing LEDs
numbers = [0, 1, 2, 3, 4, 5, 6, 7]
redL =   [2, 17, 14, 24, 11, 13, 16,  8]
greenL = [3, 27, 15, 23,  5, 19, 20,  7]
blueL =  [4, 22, 18, 25,  6, 26, 21, 12]
#LED Pinout
for count in numbers:
    GPIO.setup(redL[count], GPIO.OUT)
    GPIO.setup(greenL[count], GPIO.OUT)
    GPIO.setup(blueL[count], GPIO.OUT)

# Arrays for managing Displays
locker = ['Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty']
redPart = [0, 0, 0, 0, 0, 0, 0, 0]
greenPart = [0, 0, 0, 0, 0, 0, 0, 0]
bluePart = [0, 0, 0, 0, 0, 0, 0, 0]

# Arrays for managing Orders
name = ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
item = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
time = ['12:00', '12:00', '12:00', '12:00', '12:00', '12:00', '12:00', '12:00']

##### GUIDE FOR COMMAND / TERMINAL INPUT #####
print("\n\t    Welcome to the Gobble 2 Go Locker System!")
print("-----------------------------------------------------------------")
print("\tLED Codes: Green-Empty, Yellow-Public, Red-Private\n")
print("\t\tGobble 2 Go System Command Key:")
print("    Summary-Storage:\tLists capacity status of each locker")
print("    Summary-Info:\tLists order information of each locker")
print("    Update:\t\tUpdates the status of any locker")
print("    Drop-Off:\t\tEnters order information of drop-off locker")
print("    Pick-Up:\t\tRemoves order information of picked-up locker")
print("    Receive:\t\tAdds new order to the system from server")
print("-----------------------------------------------------------------\n")

# Socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect(('172.30.63.244',2001))
size = 1024


# Main While Loop
while True:

    #LED Part
    for count in numbers:
        if(locker[count] == 'Empty'):
            # Green - Go - Empty
            redPart[count] = 1
            greenPart[count] = 0
            bluePart[count] = 1
        elif(locker[count] == 'Full-Private'):
            # Red - Stop - Private
            redPart[count] = 0
            greenPart[count] = 1
            bluePart[count] = 1
        elif(locker[count] == 'Full-Public'):
            # Yellow - Maybe - Public
            redPart[count] = 0
            greenPart[count] = 0
            bluePart[count] = 1
    # Display LED Values
    for count in numbers:
        GPIO.output(redL[count], redPart[count]) # R
        GPIO.output(greenL[count], greenPart[count]) # G
        GPIO.output(blueL[count], bluePart[count]) # B
        
    #Command Prompting    
    command = input("Enter Command: ")
    # Summary of Storage
    if(command == 'Summary-Storage'):
        print("-----Storage-----")
        for count in numbers:
            print("Locker %s: %s" % ((count+1),locker[count]))
    # Summary of Orders
    elif(command == 'Summary-Info'):
        print("------Info------")
        for count in numbers:
            if(locker[count] == 'Empty'):
                print("Locker %s: %s" % ((count+1),locker[count]))
            else :
                print("Locker %s:\tName: %s\tItem: %s\tTime: %s" %((count+1),name[count],item[count],time[count]))
      # Updating Lockers  
    elif(command == 'Update'):
        lockerNum = int(input("Locker #: "))
        if(lockerNum >= 1 and lockerNum <= 8) :
            lockerStatus = input("Locker Status: ")
            # To Empty Locker
            if(lockerStatus == 'Empty'):
                name[lockerNum-1] = 'None'
                item[lockerNum-1] = 'NA'
                time[lockerNum-1] = '12:00'
                locker[lockerNum-1] = 'Empty'
                s.send(str(lockerNum-1).encode())
                print("Updated: Locker %d to %s" % (lockerNum, lockerStatus))
            # To Update Food Info
            elif(lockerStatus == 'Private') :
                name[lockerNum-1] = input("Name: ")
                item[lockerNum-1] = input("Item: ")
                time[lockerNum-1] = input("Time: ")
                locker[lockerNum-1] = 'Full-Private'
                print("Updated: Locker %d to %s" % (lockerNum, lockerStatus))
            # To Update Food to Public
            elif(lockerStatus == 'Public') :
                name[lockerNum-1] = 'Public'
                item[lockerNum-1] = item[lockerNum-1]
                time[lockerNum-1] = time[lockerNum-1]
                locker[lockerNum-1] = 'Full-Public'
                print("Updated: Locker %d to %s" % (lockerNum, lockerStatus))
            else :
                print("Invalid Status: %s!" % lockerStatus)
        else :
            print("Invalid Locker #: %s!" % lockerNum)

    # To Pick-Up / Withdraw Food 
    elif(command == 'Pick-Up'):
        lockerNum = int(input("Locker #: "))
        if(lockerNum >= 1 and lockerNum <= 8) :
            name[lockerNum-1] = 'None'
            item[lockerNum-1] = 'NA'
            time[lockerNum-1] = '12:00'
            locker[lockerNum-1] = 'Empty'
            s.send(str(lockerNum-1).encode())
            print("Cleared Locker %s!" % lockerNum)
        else :
            print("Invalid Locker #: %s!" % lockerNum)

    # To Receive New Orders From Server
    elif(command == 'Receive'):
        inDataJson = s.recv(size)
        print('Adding Order!')
        inData = json.loads(inDataJson.decode())
        print(inData)
        inName = inData['name']
        print(inName)
        inItem = inData['rest']
        print(inItem)
        inTime = inData['time']
        print(inTime)
        inLocker = inData['idnum']
        print(inLocker)
        
        locker[int(inLocker)] = 'Full-Private'
        name[int(inLocker)] = inName
        item[int(inLocker)] = inItem
        time[int(inLocker)] = inTime
        
    else :
        print("Invalid Command!")

