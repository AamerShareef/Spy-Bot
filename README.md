# Spy-Bot: A Cloud Pentesting Approach
The Spy-Bot is a robot based on a Raspberry-Pi build using Python, which can navigate and perform wireless penetration testing over the cloud. The Spy-Bot works with a Spy-Bot framework, which constitutes the source code and files needed to perform wireless penetration testing objectives using Python Scripts.

The SpyBot framework provides a convenient approach to perform RED-TEAM exercises aimed to perform penetration tests on wireless networks in a particular region. The framework contains remote admin scripts used by a remote admin (Admin WorkSpace) and Spy-Bot scripts used on the Raspbery-Pi (SpyBot Workspace) to perform remote wireless penetration testing over cloud. 

The Spy-Bot framework contains tools developed and designed to gather geographical information regarding wireless access points, detect wifi signal leakage by plotting geo-coordinates of a wireless AP packets on google maps and perform several other attack objectives. The Spy-Bot framework sets up a database which stores information related to the wireless pentests and audits performed using the Spy-Bot. 

This wireless pentest framework is designed specifically to work efficiently with a raspberry-pi. The source files for performing wireless penetration testing objectives (present in the SpyBot Workspace) can also be used on a standalone individual system that runs Kali Linux or a similiar distro. The source codes have been designed and tested to work with a TP-Link WN-722N ( use SpyBotmian.py in the master branch ) and ALFA cards ( check SpyBotMain_alfa.py to work with other cards and alfa cards). 

# OBJECTIVES OF THE SPY-BOT:
1. Deploying the Spy-Bot:
- Remotely connecting to the Spy-Bot using Python. ( Using Yaler Services https://yaler.net/. Setup the Yaler services on the raspberry-pi for auto start by checking out the official documentation on the Yaler website. Place your yaler files in the Admin Workspace)
- Remotely controlling and navigating the Spy-Bot using Python. ( Run the navigation.py on the raspberry-pi )
2. Testing Attacks against WPA/WPA2/WPA-Enterprise Networks ( Objectives done using SpyBotMain.py and SpyBotMain_alfa.py)
- Passively Deauthenticate connected clients to an AP using Python & Scapy.
- Detect WPS status of APs.
- Force Handshake Capturing while Deauthenticating using Python & Scapy.
- GPU accelerated PSK cracking using Pyrit using custom Wordlists. ( Place your Wordlists in the Admin Workspace Directory. Check out the basic layout figures to setup the Admin Workspace  )
3. Testing Attacks against WEP Networks
- Passively Deauthenticate connected clients to an AP using Python & Scapy.
- Collect AP data packets using Python & Scapy.
- Acquire WEP Network Key.
4. Testing Attacks against Authentication Protocols 
- Using Python to leverage vulnerabilities in EAP-LEAP/PEAP/TTLS/MD5 to obtain challenge & response pairs during misconfigured authentications.
- Using ASLEAP, EAPMD5PASS and custom wordlists to perform dictionary brute-forcing to acquire weak passwords used by clients.
5. Dynamically Hosting Rogue AP’s for victim clients 
Using Python and hostapd to:
- Hosting a rogue AP (Open networks or WPA-Enterprise Networks) based on the Access points in a region or creating a custom AP.
- Dynamically selecting and hosting the Strongest AP in a region.
- Hosting a rogue AP based on selection of available APs. 
- Hosting Rogue APs in karma mode.

# INSTALLATION
1.Setting up the CLOUD System/Command&Control Center
- The remote system/C2C System is used to connect & control the Spy-Bot remotely over the internet.
- Place the contents of the Admin_Workspace onto the system that you wish to use as a Remote System.
- If you are SSHing into the Spy-Bot remotely using Yaler, make sure to add the Yaler relay node in the admin.py.
- The remote system must have aircrack-ng, optirun, bumblebeed and pyrit installed.
- The remote system must be running a suitable OS such as Kali Linux. (Tested on Parrot OS).
2. Setting up the Spy-Bot
- Refer the wiki to set up the SPyBot motor controller, GPIO Connection and Circuit connections.
- Make sure you have configured the Yaler services to run on boot on the raspberry pi (if using a remote connection over the internet)
- Make sure you are using Parrot OS armhf or a similiar distro on the Raspberry pi.
- Install the pygmaps module present in the dependencies folder.
- Install scapy, click, gps, googlemaps and RPi python  modules on the Raspberry Pi (Spy-Bot).
- Create a Google geoloaction API and add it to the line  key="<insert_api_here>" in locationtest.py. Use a paid API to bypass any restrictions if needed(preferred). The script sends a API request for every packet sniffed.
- Connect a NMEA USB GPS device for retrieving geographical coordinates . (I have tested and used GlobSAT bu353, which is connected to tty0 by defualt. Change this value in gpstest.py if needed)
- Connect a suitable wireless card (Tp-Link/ALFA) to the Spybot which supports monitor-mode.
- Ensure the Spy-Bot has a internet connection at boot (Example: Like a 3g connnection. you need to preconfigure it if you are deploying the SpyBot remotely)

USE A SUITABLE DATABASE VIEWER (SUCH AS SQLITE MANAGER FIREFOX PLUGIN) TO VIEW THE CONTENTS OF THE SPYBOT.DB DATABASE.
SAMPLE FILES ARE PROVIDED.

REFER WIKI PAGE FOR MORE DETAILS & SETTING UP.

# Usage
1. The Spybotmain.py is responsible for performing the wireless pentest objectives.
It can be run on a remote command and control center, or on the Spybot.
Make the spybotmain.py as an executable and run with root privilages.

- chmod a+x SpyBotMain.py
- ./Spybotmain.py <wireless-interface name> example: ./Spybotmain.py wlan0

2. Run the admin.py (as root) if performing objectives remotely.
- chmod a+x admin.py
- ./admin.pygmaps

3. Run navigation.py to control the motors of the Spy-Bot
Use the arrow keys of 'a','s','d','w' to control directions. Press space key to stop.
- chmod a+x navigation.py
- ./navigation.py


