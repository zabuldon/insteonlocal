import pprint, logging, logging.handlers, json, requests, pkg_resources
from collections import OrderedDict
from time import sleep
from io import StringIO
from sys import stdout

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

class Switch():

    def __init__(self, hub, deviceId):
        self.deviceId = deviceId
        self.hub = hub
        self.logger = hub.logger


   ## @TODO IN DEVELOPMENT
   ### TODO listen for linked page 35 http://cache.insteon.com/developer/2242-222dev-062013-en.pdf
   ## Begin all linking
   # linkType:
   #  00 as responder/slave
   #  01 as controller/master
   #  03 as controller with im initiates all linking or as responder when another device initiates all linking
   #  FF deletes the all link
    def startAllLinking(self, linkType, groupId):
        self.logger.info("\nstartAllLinking for device {} type {} group {}".format(self.deviceId, linkType, groupId))
        self.hub.directCommand(self.deviceId, '02', '64' + linkType + groupId)
       # TODO: read response
        #    Byte Value Meaning
        #1 0x02 Echoed Start of IM Command
        #2 0x64 Echoed IM Command Number
        #3 <Code> Echoed <Code>
        #4 <ALL-Link Group> Echoed <ALL-Link Group>
        #5 <ACK/NAK> 0x06 (ACK) if the IM executed the Command correctly
        #0x15 (NAK) if an error occurred

    def cancelAllLinking(self):
        self.logger.info("\ncancelAllLinking for device {}".format(self.deviceId))
        self.hub.directCommand(self.deviceId, '02', '65')


    def status(self, returnLED = 0):
        status = self.hub.getDeviceStatus(self.deviceId, returnLED)
        self.logger.info("\nDimmer {} status: {}".format(self.deviceId, pprint.pformat(status)))
        return status


    ## Turn Switch On
    def on(self):
        self.logger.info("\nSwitch {} on".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '11', 'FF')

        success = self.hub.checkSuccess(self.deviceId, '11', 'FF')

        if (success):
            self.logger.info("Switch {} on: Switch turned on successfully".format(self.deviceId))
        else:
            self.logger.error("Switch {} on: Switch did not turn on".format(self.deviceId))

        return success


    ## Turn Switch Off
    def off(self):
        self.logger.info("\nSwitch {} off".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '13', 'FF')

        success = self.hub.checkSuccess(self.deviceId, '13', 'FF')

        if (success):
            self.logger.info("Switch {} off: Switch turned off successfully".format(self.deviceId))
        else:
            self.logger.error("Switch {} off: Switch did not turn off".format(self.deviceId))

        return success


    ## Make switch beep
    ## Not all devices suppot this
    def beep(self):
        self.logger.info("\nSwitch() beep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '30', '00')

        success = self.hub.checkSuccess(self.deviceId, '30', '00')
