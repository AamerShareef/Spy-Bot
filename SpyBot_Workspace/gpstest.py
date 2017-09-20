#!/usr/bin/python
from gps import *
import time,threading
import multiprocessing
global gpsd
import os
os.system("gpsd /dev/ttyUSB0")
time.sleep(1)
def handle(gpsd):
	
	try:	
		#global gpsd
	#	gpsd.next()
	#	while (gpsd.fix.latitude==0.0):
	#		gpsd.next()
	#		gpsd.next()
	#		gpsd.next()
		while True:
			gpsd.next()
			
	except:
		print "[*] GPS Device Not Found!"
		time.sleep(10)

gpsd=gps(mode=WATCH_ENABLE)
gpsthread=threading.Thread(target=handle,args=(gpsd,))
gpsthread.setDaemon(True)
gpsthread.start()
time.sleep(2)
#try:
#	while True:
#		print gpsd.fix.latitude,',',gpsd.fix.longitude
#		time.sleep(0.4)
#except KeyboardInterrupt:
#	print "Exiting"
#	gpsthread.running=False
#	print "Done Exiting"
#	sys.exit(0) #Thread stops when the main program exits

	
