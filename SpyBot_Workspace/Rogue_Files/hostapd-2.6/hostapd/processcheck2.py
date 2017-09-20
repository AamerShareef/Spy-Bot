#!/usr/bin/python
import subprocess,time,os

def jumpto():	
	time.sleep(2)
	print "DID you receive the challenge/ response pair?"
	raw_input()
def check():
 try: 
	DN=open(os.devnull)	
	hn=subprocess.Popen(['./hostapd-wpe ./hostapd-wpe.conf'],shell=True,stdin=subprocess.PIPE,stdout=None,stderr=None)
	hn.communicate()
	print "You are here!"
	raw_input()
	print "exiting now "
	#hn.stdout.read()
 except:
    print " Exception ocured"
    jumpto()

def main():
	check()
if __name__=='__main__':
	main()

