#!/Users/mlong/hassdev/bin/python3.5
import time,requests,sys
import pprint
from insteonlocal.Hub import Hub
import config
import logging
from sys import stdout

## To being, create a file called config.py containing:
#username = "hub's username"
#password = "hub's password"
# or comment out the import config and manually specify below

try:
    FORMAT = '[%(asctime)s] (%(filename)s:%(lineno)s) %(message)s'
    #logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename='/tmp/insteonlocal.log')
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    logger = logging.getLogger('')

    # create hub object
    hub = Hub(
        '192.168.1.160', 
        config.username, 
        config.password, 
        '25105', #port 
        10, #timeout
        logger
    )
    buffer = hub.getBufferStatus()
except requests.exceptions.RequestException as e:
   if hub.http_code == 401:
       print("Unauthorized...check user/pass for hub\n")
       sys.exit(1)
   else:
       print(e)
       sys.exit(1)

#hub.getLinked()

#insteonLocal.idRequest('42902e')

#insteonLocal.getDeviceStatus('42902e')

#modelInfo = insteonLocal.getDeviceCategory("00")
#if ("name" in modelInfo):
#    print("Got name of " + modelInfo["name"])
#pprint.pprint(modelInfo)

# Dimmer example
#dimmer1 = hub.dimmer('42902e')
#dimmer1.beep()
#dimmer1.on(25)
#dimmer1.status(0)
#dimmer1.status(1)
#dimmer1.brightenStep()
#dimmer1.brightenStep()
#dimmer1.brightenStep()
#dimmer1.brightenStep()
#dimmer1.dimStep()
#dimmer1.dimStep()
#dimmer1.dimStep()
#dimmer1.changeLevel(75)
#dimmer1.offInstant()
#dimmer1.onSaved()
#dimmer1.on(75)
#dimmer1.startChange('down')
#time.sleep(1)
#dimmer1.stopChange()
#time.sleep(2)
#dimmer1.on(10)
#dimmer1.startChange('up')
#time.sleep(1)
#dimmer1.stopChange()
#time.sleep(2)
#dimmer1.offInstant()
#time.sleep(1)
#dimmer1.off()

# Get list of linked devices
#devices = hub.getLinked()
#pprint.pprint(devices)

# Group example
#group2 = hub.group("2")
#group2.on()
#time.sleep(1)
#group2.off()

switch1 = hub.switch('40565b')
#switch1.on()
switch1.beep()
#switch1.beep()
#switch1.beep()
#switch1.off()

# switch join new group 03
#group3 = hub.group("03")
##group3.enterLinkMode()
#hub.startAllLinking("01", group3.groupId) #controller
#switch1 = hub.switch('40565b')
#switch1.startAllLinking("00", group3.groupId) #responder
##    b.directCommand("40565b", "01", group3.groupId)
#time.sleep(2)
hub.getBufferStatus()
##group3.cancelLinkUnlinkMode()

#hub.getLinked()
