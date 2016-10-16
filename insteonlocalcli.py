#!/Users/mlong/hassdev/bin/python3.5
import time
from InsteonLocal import InsteonLocal
#import InsteonLocal
insteonLocal = InsteonLocal('192.168.1.160', 'Monaster', 'dtix6Fqs', '25105', '/tmp/insteonlocal.log', True)

#insteonLocal.lightOn('39f972', 100)

#insteonLocal.lightOn('42902e', 100)
#insteonLocal.lightOff('42902e', 100)

#insteonLocal.lightOn('42902e', 5, 1)
#time.sleep(3)
#insteonLocal.getBufferStatus()
#time.sleep(3)
#insteonLocal.lightOff('42902e', 100, 0)

#insteonLocal.getDeviceStatus('42902e')

insteonLocal.lightOff('42902e', 0)

insteonLocal.getLinked()

insteonLocal.idRequest('42902e')
