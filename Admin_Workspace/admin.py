#!/usr/bin/python
import subprocess,os,time,sys,click
dev=open(os.devnull,'wb')
def connect_to_workspace():
    try:
        print "[*] Connecting to SpyBot....Make sure the SpyBot is ONLINE!"
        os.chdir("./YalerTunnel")
        # dev=open(os.devnull,'wb')
        print "[*] Starting Yaler Services..."
        subprocess.Popen("java YalerTunnel client 127.0.0.1:10022 try.yaler.io:80 gsiot-3jpy-p0d6",shell=True,stdout=dev,stderr=dev)
        print "[*] Yaler Services Started."
        os.chdir("../")
        print "[*] Launching Terminal.."
        cmd="\"ssh root@localhost -p 10022 -o ServerAliveInterval=5\""
        # cmd2="\"ping google.com\"" #Testing purposes
        term="gnome-terminal -e "+cmd+" --geometry=120x25"
        subprocess.Popen(term,shell=True,stderr=dev,stdout=dev)
        while True:
            print "[*] Press 1 to launch another terminal/Retry"
            print "[*] Press 2 to return to main menu"
            ch=click.getchar()
            if ch=='1':
                print "[*] Launching Terminal.."
                subprocess.Popen(term,shell=True)
            elif ch=='2':
                print "[*] Returning to main menu"
                break
            else:
                print "[*] Enter a valid choice! "
                continue
        return
    except:
        print "[*] Oops something went wrong when connecting to SpyBot!"
        return
def pcap_gpu_bruteforce():
    def display_dict():
        global path
        print "[*] Displaying available lists of wordlists!"
        filelist=[]
        for root, dirs, files in os.walk("./Wordlists"):
            for name in files:
                path=os.path.join(root,name)
                if os.path.isfile(path):
                    filelist.append(path)
        cnt=1
        for i in filelist:
            print "[%d] %s"%(cnt,i)
            cnt+=1
        raw_input("[*] Press Enter!")
        print cnt
        print "[*] Select a wordlist to use: [1]-[%d] or Press [0] to enter a custom path"%(cnt-1)
        while True:
            ch=raw_input()
            ch=int(ch)
            if ch not in range(0,cnt):
                print "[*] Enter a valid input!"
                continue
            elif ch==0:
                print "[*] Enter Path to wordlist to use:"
                path=raw_input()
                break
            else:
                path=filelist[ch-1]
                break
        return
    def pyrit_launch():
        print "[*] Starting Pyrit and optirun"
        subprocess.Popen("service bumblebeed restart",shell=True,stderr=dev)
        cmd="optirun pyrit -r "+pcap+" -i "+path+" attack_passthrough"
        print cmd
        time.sleep(1)
        os.system(cmd)
        return
    try:
        print " Enter a Choice : [1] WEP Pcap [2] WPA Pcap "
        ch=click.getchar()
        if ch == '1':
            print "[*] Provide a PCAP file: [1] Auto-Select from Retrieved Directory [2] Enter Path to pcap"
            while True:
                ch=click.getchar()
                if ch=='1':
                    pcap="./Retrieved/Captures/wep_data"
                    break
                elif ch=='2':
                    print "[*] Enter a valid path.."
                    pcap=raw_input().strip()
                else:
                    print "[*] Enter a valid choice"
                    continue
            print "[*] Launching Aircrack-ng"
            cmd="aircrack-ng "+pcap
            os.system(cmd)


        elif ch=='2':
            print "[*] Provide a PCAP file: [1] Auto-Select from Retrieved Directory [2] Enter Path to pcap"
            while True:
                ch=click.getchar()
                if ch=='1':
                    pcap="./Retrieved/Captures/wpa_cap"
                    break
                elif ch=='2':
                    print "[*] Enter a valid path.."
                    pcap=raw_input().strip()
                else:
                    print "[*] Enter a valid choice"
                    continue
            display_dict()
            print "[*] PCAP Selected: %s \n[*] Path Selected: %s"%(pcap,path)
            raw_input("Press Enter!")
            pyrit_launch()

            while True:
                print "[*] Do you want to use a different wordlist? [y]/[n]"
                ch=click.getchar()
                if ch=='y':
                    display_dict()
                    pyrit_launch()
                elif ch=='n':
                    break
                else:
                    print "[*] Enter a valid option!"
                    continue
            print "[*] Returning to main! "
            return
    except KeyboardInterrupt:
        raw_input("Keyboard interrupt! press enter")
        return
def challege_response_bruteforce():
    def display_dict():
        global path
        print "[*] Displaying available lists of wordlists!"
        filelist=[]
        for root, dirs, files in os.walk("./Wordlists"):
            for name in files:
                path=os.path.join(root,name)
                if os.path.isfile(path):
                    filelist.append(path)
        cnt=1
        for i in filelist:
            print "[%d] %s"%(cnt,i)
            cnt+=1
        raw_input("[*] Press Enter!")
        print cnt
        print "[*] Select a wordlist to use: [1]-[%d] or Press [0] to enter a custom path"%(cnt-1)
        while True:
            ch=raw_input()
            ch=int(ch)
            if ch not in range(0,cnt):
                print "[*] Enter a valid input!"
                continue
            elif ch==0:
                print "[*] Enter Path to wordlist to use:"
                path=raw_input()
                break
            else:
                path=filelist[ch-1]
                break
        return
    def dict_attack():
        cmd="%s -C %s -R %s"%(option,challenge,response)
        if option=='eapmd5pass':
            cmd=cmd+" -w %s"%(path)
        elif option=="asleap":
            cmd=cmd+" -W %s"%(path)
        print "[*] Launching dictionary bruteforce..."
        os.system(cmd)
        return
    try:

        print "[*] This function is used to attack MSCHAPv2 protocol used by EAP-MD5 & PEAP/TTLS networks \n [*] "
        print "[*] Enter Challenge:"
        challenge=raw_input()
        print "[*] Enter Response:"
        response=raw_input()
        print "[*] Choose MSCHAPv2 Attack method: [1] Use ASLEAP [2] Use EAPMD5PASS"
        while True:
            ch=click.getchar()
            if ch=='1':
                option="asleap"
                break
            elif ch=='2':
                option="eapmd5pass"
                break
            else:
                print "[*] Enter a valid option!"
                continue
        print "[*] To choose a wordlist press any key!"
        raw_input()
        display_dict()
        dict_attack()
        while True:
            print "[*] Do you want to use a different wordlist? [y]/[n]"
            ch=click.getchar()
            if ch=='y':
                display_dict()
                dict_attack()
            elif ch=='n':
                break
            else:
                print "[*] Enter a valid option!"
                continue
        print "[*] Returning to main! "
        return
    except:
        print "[*] Oops something went wrong while dictionary bruteforcing! Try again! Press Enter to return to Main"
        raw_input()
        return

def file_retrieve():
    try:
        print "[*] Launching SCP, connecting over Yaler"
        cmd="scp -P 10022 root@localhost:/home/pi/Desktop/SpyBotWorkspace/ForAdmin/ForAdmin.zip ./Retrieved/"
        # cmd2="scp -P 10022 root@localhost:/home/pi/Desktop/SpyBotWorkspace/Captures/wpa_cap ./" #testing purposes
        os.system(cmd)
        print "[*] Files Retreived!"
        os.chdir("./Retrieved")
        os.system("unzip ForAdmin")
        os.system("rm ForAdmin.zip")
        print "[*] Clearing Zip files."
        os.chdir("../")
        print "[*] Returning to Main"
        return
    except:
        print "[*] Oops something went wrong while retreiving files! Try again! Press Enter to return to Main"
        raw_input()
        return
if __name__=='__main__':
    try:
        while True:
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


            Welcome Admin, To SpyBot Framework. A Remote Wireless Pentesting Framework.
            Select an option and follow the instruction to use!
            1. Connect to the SPYBOT.
            2. Perform GPU Dictionary Attack on a handshake pcap file.
            3. Perform Dictionary Attack on a Challenge/Response Pair [using asleap and md5eapass].
            4. Retrieve Files From SpyBot [Results in ForAdmin Directory].
            Press 'C' to Exit!
            """
            ch=click.getchar()
            if ch=='1':
                connect_to_workspace() #DONE-TESTED
            elif ch=='2':
                pcap_gpu_bruteforce()
            elif ch=='3':
                challege_response_bruteforce()
            elif ch=='4':
                file_retrieve()
            elif ch in ['C','c']:
                print "Bye!"
                sys.exit(0)
            else:
                print "[*] Invalid Option! Enter a valid option!"
    except KeyboardInterrupt:
        print "[*] Keyboard Interrupt Received! Exiting !"
        sys.exit(0)
