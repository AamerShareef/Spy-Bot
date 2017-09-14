#!/usr/bin/python

import time,click,sys
import RPi.GPIO as GPIO

MotorA0=11		#Corresponds to IN1 signal 
MotorA1=12		#Corresponds to IN2 signal
MotorB0=15		#Corresponds to IN3 signal
MotorB1=16
A0 = False		
A1 = False
B0 = False
B1 = False
MotorAE=13
MotorBE=18
def set_motors():
	GPIO.output(MotorAE, True)
        GPIO.output(MotorBE, True)
	GPIO.output(MotorA0, A0)
        GPIO.output(MotorA1, A1)
        GPIO.output(MotorB0, B0)
        GPIO.output(MotorB1, B1)
	print "motors set!"
def init_motors():
	print "Initializing motors"
	GPIO.setmode(GPIO.BOARD)
	GPIO.cleanup()
	GPIO.setup(MotorA0,GPIO.OUT)
	GPIO.setup(MotorA1,GPIO.OUT)
	GPIO.setup(MotorAE,GPIO.OUT)
	GPIO.setup(MotorB0,GPIO.OUT)
	GPIO.setup(MotorB1,GPIO.OUT)
	GPIO.setup(MotorBE,GPIO.OUT)
	#set all motors to off 
	GPIO.output(MotorA0, A0)
	GPIO.output(MotorA1, A1)
	GPIO.output(MotorB0, B0)
	GPIO.output(MotorB1, B1)
	GPIO.output(MotorAE, False)
	GPIO.output(MotorBE, False)
	print "Initialized motors"

def stop_motors():
	print "Stopping motors"
	GPIO.output(MotorAE, False)
	GPIO.output(MotorBE, False)
	A0=False
	B0=False
	A1=False
	B1=False
	GPIO.output(MotorA0, A0)
	GPIO.output(MotorA1, A1)
	GPIO.output(MotorB0, B0)
	GPIO.output(MotorB1, B1)
	
	print "motors stopped"

def refreshGPIO():
	print "cleaning GPIO pins!"

init_motors()

while True:
    try:
	ch=click.getchar()
	if ch=='w' or ch=='\x1b[A':
		print "changing values!"
		A0=True
		B0=True
		A1=False
		B1=False
		set_motors()
		print "moving forward!"

	elif ch=='s' or ch==ch=='\x1b[B':
		print "changing values!"

		A0=False
		B0=False
		A1=True
		B1=True

		set_motors()
		print "moving backward!"

	elif ch=='d' or ch=='\x1b[C':
		print "changing values!"
		A0=True
		A1=False
		B0=False
		B1=True
		set_motors()
		print "moving right"

	elif ch=='a'or ch=='\x1b[D':

		print "changing values!"
		A0=False
		A1=True
		B0=True
		B1=False
		set_motors()
		print "moving left!"
	elif ch==' ':
		
		stop_motors()
	else : 
		print "unknown keys"
		stop_motors()
		
    except :
		print "exiting"
		stop_motors()
		refreshGPIO()
		sys.exit(0)

	
		
