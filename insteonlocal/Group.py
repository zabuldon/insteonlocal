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


### Group Lighting Functions - note, groups cannot be dimmed. They can be linked in dimmed mode.
### Valid group id 1-255 (decimal)
class Group():

    def __init__(self, hub, groupId):
        self.groupId = groupId
        self.hub = hub
        self.logger = hub.logger

    # Turn group on
    def on(self):
        self.logger.info("\ngroupOn: group {}".format(self.groupId))
        self.sceneCommand('11')

        #sleep(2)
        #status = self.hub.getBufferStatus()

        #success = self.checkSuccess(deviceId, '11', self.hub.brightnessToHex(level))
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOn: Group turned on successfully")
        #else:
        #    self.logger.error("groupOn: Group did not turn on")


    # Turn group off
    def off(self):
        self.logger.info("\ngroupOff: group {}".format(self.groupId))
        self.sceneCommand('13')

        #sleep(2)
        #status = self.hub.getBufferStatus()
        #success = self.checkSuccess(deviceId, '13', self.hub.brightnessToHex(level))
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOff: Group turned off successfully")
        #else:
        #    self.logger.error("groupOff: Group did not turn off")


    # Wrapper to send posted scene command and get response
    def sceneCommand(self, command):
        self.logger.info("sceneCommand: Group {} Command {}".format(self.groupId, command))
        commandUrl = self.hub.hubUrl + '/0?' + command + self.groupId + "=I=0"
        return self.hub.postDirectCommand(commandUrl)


    # Enter linking mode for a group
    # Press and hold button on device after sending this command
    def enterLinkMode(self):
        self.logger.info("\nenterLinkMode Group {}".format(self.groupId));
        self.sceneCommand('09')
        # should send http://0.0.0.0/0?0901=I=0

        ## TODO check return status
        status = self.hub.getBufferStatus()
        return status


    # Enter unlinking mode for a group
    def enterUnlinkMode(self):
        self.logger.info("\nenterUnlinkMode Group {}".format(self.groupId));
        self.sceneCommand('0A')
        # should send http://0.0.0.0/0?0A01=I=0

        ## TODO check return status
        status = self.hub.getBufferStatus()
        return status


    # Cancel linking or unlinking mode
    def cancelLinkUnlinkMode(self):
        self.logger.info("\ncancelLinkUnlinkMode");
        self.sceneCommand('08')
        # should send http://0.0.0.0/0?08=I=0

        ## TODO check return status
        status = self.hub.getBufferStatus()
        return status
