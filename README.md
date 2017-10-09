# Spy-Bot: A Cloud Pentesting Approach
Sit back in your room and pentest wireless networks anywhere in the world over cloud! 

The Spy-Bot is a robot based on a Raspberry-Pi build using Python, which can navigate and perform wireless penetration testing over the cloud. The Spy-Bot works with a Spy-Bot framework, which constitutes the source code and files needed to perform wireless penetration testing objectives using Python Scripts.

![ScreenShot](/Screenshots_Git/Screenshot03.png)

![ScreenShot](/Screenshots_Git/Screenshot01.JPG)

![ScreenShot](/Screenshots_Git/Screenshot02.JPG)

The SpyBot framework provides a convenient approach to perform RED-TEAM exercises aimed to perform penetration tests on wireless networks in a particular region. The framework contains remote admin scripts used by a remote admin (Admin WorkSpace) and Spy-Bot scripts used on the Raspbery-Pi (SpyBot Workspace) to perform remote wireless penetration testing over cloud. 

The Spy-Bot framework contains tools developed and designed to gather geographical information regarding wireless access points, detect wifi signal leakage by plotting geo-coordinates of a wireless AP packets on google maps and perform several other attack objectives. The Spy-Bot framework sets up a database which stores information related to the wireless pentests and audits performed using the Spy-Bot. 

This wireless pentest framework is designed specifically to work efficiently with a raspberry-pi. The source files for performing wireless penetration testing objectives (present in the SpyBot Workspace) can also be used on a standalone individual system that runs Kali Linux or a similiar distro. The source codes have been designed and tested to work with a TP-Link WN-722N ( use SpyBotmian.py in the master branch ) and ALFA cards ( check SpyBotMain_alfa.py to work with other cards and alfa cards). 

# OBJECTIVES OF THE SPY-BOT:
### 1. Deploying the Spy-Bot:
- Remotely connecting to the Spy-Bot using Python. ( Using Yaler Services https://yaler.net/. Setup the Yaler services on the raspberry-pi for auto start by checking out the official documentation on the Yaler website. Place your yaler files in the Admin Workspace)
- Remotely controlling and navigating the Spy-Bot using Python. ( Run the navigation.py on the raspberry-pi )

### 2. Testing Attacks against WPA/WPA2/WPA-Enterprise Networks ( Objectives done using SpyBotMain.py and SpyBotMain_alfa.py)
- Passively Deauthenticate connected clients to an AP using Python & Scapy.
- Detect WPS status of APs.
- Force Handshake Capturing while Deauthenticating using Python & Scapy.
- GPU accelerated PSK cracking using Pyrit using custom Wordlists. ( Place your Wordlists in the Admin Workspace Directory. Check out the basic layout figures to setup the Admin Workspace  )
### 3. Testing Attacks against WEP Networks
- Passively Deauthenticate connected clients to an AP using Python & Scapy.
- Collect AP data packets using Python & Scapy.
- Acquire WEP Network Key.
### 4. Testing Attacks against Authentication Protocols 
- Using Python to leverage vulnerabilities in EAP-LEAP/PEAP/TTLS/MD5 to obtain challenge & response pairs during misconfigured authentications.
- Using ASLEAP, EAPMD5PASS and custom wordlists to perform dictionary brute-forcing to acquire weak passwords used by clients.
### 5. Dynamically Hosting Rogue AP’s for victim clients 
Using Python and hostapd to:
- Hosting a rogue AP (Open networks or WPA-Enterprise Networks) based on the Access points in a region or creating a custom AP.
- Dynamically selecting and hosting the Strongest AP in a region.
- Hosting a rogue AP based on selection of available APs. 
- Hosting Rogue APs in karma mode.

# INSTALLATION
### 1.Setting up the CLOUD System/Command&Control Center
- The remote system/C2C System is used to connect & control the Spy-Bot remotely over the internet.
- Place the contents of the Admin_Workspace onto the system that you wish to use as a Remote System.
- If you are SSHing into the Spy-Bot remotely using Yaler, make sure to add the Yaler relay node in the admin.py.
- The remote system must have aircrack-ng, optirun, bumblebeed and pyrit installed.
- The remote system must be running a suitable OS such as Kali Linux. (Tested on Parrot OS).
### 2. Setting up the Spy-Bot
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

```
chmod a+x SpyBotMain.py
```

```
./Spybotmain.py <wireless-interface name>
```

example: ./Spybotmain.py wlan0

2. Run the admin.py (as root) if performing objectives remotely.

```
chmod a+x admin.py
```

```
./admin.py
```

3. Run navigation.py to control the motors of the Spy-Bot
Use the arrow keys of 'a','s','d','w' to control directions. Press space key to stop.

```
chmod a+x navigation.py
```

```
./navigation.py
```

# Screenshots
#### 1. Connecting to the SpyBot. 

![ScreenShot](/Screenshots_Git/Screenshot04.tmp)

On the cloud/C2C system, execute the admin.py script (sudo/root) present in the admin_workspace directory. The admin.py allows you to connect to the SpyBot over YALER, launch GPU password attacks on pcap files and retrieves any handshake files, rogua AP login detail files etc captured by the SpyBot and stores it in the admin_workspace.
NOTE: root@localhost is the default remote login prompt given to you by Yaler services, if you configure the yaler services properly for the remote connection.

#### 2. Running the spybotmain.py

![ScreenShot](/Screenshots_Git/Screenshot07.png)

Once you login to the SpyBot using the admin.py script on the cloud server/remote control system, launch the spybotmain.py in the spybot_workspace directory. The spybotmain.py runs on the raspberry-pi (Spy-Bot) to perform wireless penetration testing objectives.

#### 3. Controlling the SpyBot remotely & war-driving over cloud

![ScreenShot](/Screenshots_Git/Screenshot08.jpg)

Launch the navigation.py on the SpyBot in the spybot_workspace to control and navigate the spybot. Configure a VNC camera access if needed ( Check Yaler.net for further details ). 
The terminal 1 shows the admin.py on the C2C system.
The terminal 2 shows the output for the navigation.py (present in the spybot_workspace on the remote rpi) controlling the motors on the remote Spy-Bot.
The terminal 3 shows the output of spybotmain.py when a network scan is initiated.  It shows a list of available wireless networks, channel numbers, etc. 
The 'coordinates' show the last seen location where an access point is detected. The 'location' field provides description of the coordinates using google APIs.
All the collected information about the networks is stored in a database _spybot.db_ on the SpyBot which can later be retreived at the end of a wireless recon operation.

#### 4. Mapping access points last seen locations on a map

![ScreenShot](/Screenshots_Git/Screenshot09.tmp)

The last seen coordinates of the access points are mapped to a google map template and is stored as a html file.
Move the cursor over the blue points to show information about the Access point name, signal strength and encryption used.

#### 5. Scanning for client probes

![ScreenShot](/Screenshots_Git/Screenshot15.png)

Launch the client probe scanner using the spybotmain.py to recon the access points which are searched by network devices in the region.
When a network device wants to connect to a known saved wireless network, it sends out probes to search for the networks it knows. This information can be used to set up rogue access points.

#### 6. Rogue access points and obtaining challenge-response pairs for WPA2-Enterprise networks

![ScreenShot](/Screenshots_Git/Screenshot15.png)

Launch the rogue ap launcher in the spybotmain.py to create rogue access points:
- dynamically by selecting the strongest/weakest access point.
- by defining a custom rogue access point
- hosting rogue access points in karma mode.

wait for victims to connect and enter credentials.(works in WPA-enterprise networks that allow authentication without certificate validation )
Launch ASLEAP functions using the admin.py AFTER retreiving the remote files from the remote spybot onto the c2c/cloud server.

![ScreenShot](/Screenshots_Git/Screenshot11.tmp)


#### 7. Deauth selective/all clients and force a WPA handshake

![ScreenShot](/Screenshots_Git/Screenshot13.png)

Launch the wpa handshake capture in the spybotmain.py to sniff for EAPOL messages.


![ScreenShot](/Screenshots_Git/Screenshot14.png)

Launch the deauth launcher in the spybotmain.py to deauthenticate all the clients or to select multiple clients to deauthenticate the clients. 

#### 8. Transfer captured handshakes, mapped APs, spybot.db to the C2C server

![ScreenShot](/Screenshots_Git/Screenshot 16.png)

Prepare files to send in the spybotmain.py file. Retrieve the files using the admin.py.
View the contents of the spybot.db database using a suitable database viewer (like firefox SQL plugin)

![ScreenShot](/Screenshots_Git/Screenshot16a.png)

![ScreenShot](/Screenshots_Git/Screenshot16b.png)

Networks and client probes found &  collected during the recon by the spybot are stored in the _spybot.db_ database.

### 9. GPU crack the handshake using pyrit 

![ScreenShot](/Screenshots_Git/Screenshot 11b.png)

Launch the GPU password attack using the admin.py on the cloud server after retreiving the sniffed handhshakes from the SpyBot.

Similiar operations for cracking WEP networks is also provided by the framework.
# LICENSE 

MIT License

Copyright (c) 2017 Aamer Shareef

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


