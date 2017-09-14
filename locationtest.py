#!/usr/bin/python
import googlemaps
try:
	gmaps=googlemaps.Client(key='AIzaSyDV2Ys57bk8fMuFfTflNlsfcgyc-XUnPGo')
except:
	print "[*] Google API Key retriev failed"
