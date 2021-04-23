#!/usr/bin/env python
import config
import socket
import time
import re
import sys
import RPi.GPIO as GPIO

# SETUP MOTOR
GPIO.setmode(GPIO.BCM)

# Set laser pin
laser = 26
GPIO.setup(laser, GPIO.OUT)
GPIO.output(laser, GPIO.LOW)

# Set all motor pins as output
StepPins = [17,22,23,24]
for pin in StepPins:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)
 
# Define advanced sequence
# as shown in manufacturers datasheet
Seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
 
StepCount = len(Seq)
StepDir = 1 # Set to 1 for clockwise
            # Set to -1 for counter-clockwise
 
# Read wait time from command line
WaitTime = 1/float(1000)
 

def spinLeft():
    StepDir = 1
    StepCounter = 0
    for i in range (250):
        #print StepCounter,
        #print Seq[StepCounter]
        for pin in range(0, 4):
            xpin = StepPins[pin]#
            if Seq[StepCounter][pin]!=0:
              # print " Enable GPIO %i" %(xpin)
              GPIO.output(xpin, True)
            else:
              GPIO.output(xpin, False)
         
        StepCounter = (StepCounter + StepDir)%8
         
        # Wait before moving on
        time.sleep(WaitTime)

def spinRight():
    StepDir = -1
    StepCounter = 0
    for i in range (250):
        #print StepCounter,
        #print Seq[StepCounter]
        for pin in range(0, 4):
            xpin = StepPins[pin]#
            if Seq[StepCounter][pin]!=0:
              # print " Enable GPIO %i" %(xpin)
              GPIO.output(xpin, True)
            else:
              GPIO.output(xpin, False)
         
        StepCounter = (StepCounter + StepDir)%8
         
        # Wait before moving on
        time.sleep(WaitTime)

# SETUP BOT
CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

# initialize bot's connection
try:
    s = socket.socket()
    s.connect((config.HOST, config.PORT))
    s.send("PASS {}\r\n".format(config.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(config.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(config.CHAN).encode("utf-8"))
    connected = True #Socket succefully connected
except Exception as e:
    print(str(e))
    connected = False #Socket failed to connect

# EXECUTE

# listen for commands
def bot_loop():
    while connected:
	response = s.recv(1024).decode("utf-8")
	if response == "PING :tmi.twitch.tv\r\n":
	    s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
	    print("Pong")
	else:
            # Parse message for command
            spl_word = "#willry1098 :"
            chat_msg = str(response.partition(spl_word)[2])
            
            print("Message: " + chat_msg)
            
            if 'left' in chat_msg:
                print("spin: left")
                spinLeft()
                chat_msg='z'

            elif 'right' in chat_msg:
                print("spin: right")
                spinRight()
                chat_msg='z'

            elif 'lon' in chat_msg:
                print("laser: on")
                GPIO.output(laser,GPIO.HIGH)
                chat_msg='z'

            elif (('lof' in chat_msg) or ('loff' in chat_msg)):
                print("laser: off")
                GPIO.output(laser,GPIO.LOW)
                chat_msg='z'
            
            elif chat_msg=='e':
                GPIO.cleanup()
                break
	time.sleep(1 / config.RATE)
	
if __name__ == "__main__":
	bot_loop()
