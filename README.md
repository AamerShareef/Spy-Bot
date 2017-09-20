# Spy-Bot: A Cloud Pentesting Approach
The Spy-Bot is a robot based on a Raspberry-Pi, which can navigate and perform wireless penetration testing over the cloud. The Spy-Bot works with a Spy-Bot framework, which constitutes the source code and files needed to perform wireless penetration testing objectives. 

The SpyBot framework provides a convenient approach to perform RED-TEAM exercises aimed to perform penetration tests on wireless networks in a particular region. The framework contains remote admin scripts used by a remote admin (Admin WorkSpace) and Spy-Bot scripts used on the Raspbery-Pi (SpyBot Workspace) to perform remote wireless penetration testing over cloud. 

The Spy-Bot framework contains tools developed and designed to gather geographical information regarding wireless access points, detect wifi signal leakage by plotting geo-coordinates of a wireless AP packets on google maps and perform several other attack objectives. The Spy-Bot framework sets up a database which stores information related to the wireless pentests and audits performed using the Spy-Bot. 

This wireless pentest framework is designed specifically to work efficiently with a raspberry-pi. The source files for performing wireless penetration testing objectives (present in the SpyBot Workspace) can also be used on a standalone individual system that runs Kali Linux or a similiar distro. The source codes have been designed and tested to work with a TP-Link WN-722N ( use SpyBotmian.py in the master branch ) and ALFA cards ( check SpyBotMain_alfa.py to work with other cards and alfa cards). 

OBJECTIVES of the SPYBOT:
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





