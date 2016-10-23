#!/Users/mlong/hassdev/bin/python3.5
import time
import pprint
from insteonlocal import Hub
#from InsteonLocal.Group import Group
#from InsteonLocal.Switch import Switch
hub = Hub('192.168.1.160', 'Monaster', 'dtix6Fqs', '25105', '/tmp/insteonlocal.log', True)

#insteonLocal.getLinked()

#insteonLocal.idRequest('42902e')

#insteonLocal.getDeviceStatus('42902e')

#modelInfo = insteonLocal.getDeviceCategory("00")
#if ("name" in modelInfo):
#    print("Got name of " + modelInfo["name"])
#pprint.pprint(modelInfo)

# Dimmer example
dimmer1 = hub.dimmer('42902e')
dimmer1.on(25)
dimmer1.status(0)
dimmer1.status(1)
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
dimmer1.offInstant()
#time.sleep(1)
#dimmer1.off()

# Get list of linked devices
#devices = hub.getLinked()
#pprint.pprint(devices)
#todo

# Group example
#group2 = hub.group("2")
#group2.on()
#time.sleep(1)
#group2.off()
