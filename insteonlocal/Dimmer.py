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

class Dimmer():

    def __init__(self, hub, deviceId):
        self.deviceId = deviceId.upper()
        self.hub = hub
        self.logger = hub.logger


    def status(self, returnLED = 0):
        status = self.hub.getDeviceStatus(self.deviceId, returnLED)
        self.logger.info("\nDimmer {} status: {}".format(self.deviceId, pprint.pformat(status)))
        return status


    ## Turn light On at saved ramp rate
    def on(self, level):
        self.logger.info("\nDimmer {} on level {}".format(self.deviceId, level))

        self.hub.directCommand(self.deviceId, '11', self.hub.brightnessToHex(level))

        success = self.hub.checkSuccess(self.deviceId, '11', self.hub.brightnessToHex(level))
        if (success):
            self.logger.info("Dimmer {} on: Light turned on successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} on: Light did not turn on".format(self.deviceId))

        return success

    ## Turn light On to Saved State - using "fast"
    def onSaved(self):
        self.logger.info("\nDimmer {} onSaved".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '12', '00')

        success = self.hub.checkSuccess(self.deviceId, '12', '00')
        if (success):
            self.logger.info("Dimmer {} onSaved: Light turned on successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} onSaved: Light did not turn on".format(self.deviceId))

        return success


    ## Turn Light Off at saved ramp rate
    def off(self):
        self.logger.info("\nDimmer {} off".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '13', '00')

        success = self.hub.checkSuccess(self.deviceId, '13', '00')
        if (success):
            self.logger.info("Dimmer {} off: Light turned off successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} off: Light did not turn off".format(self.deviceId))

        return success


    ## Turn Light Off
    def offInstant(self):
        self.logger.info("\nDimmer {} offInstant".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '14', '00')

        success = self.hub.checkSuccess(self.deviceId, '14', '00')
        if (success):
            self.logger.info("Dimmer {} offInstant: Light turned off successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} offInstant: Light did not turn off".format(self.deviceId))

        return success


    ## Change light level
    def changeLevel(self, level):
        self.logger.info("\nDimmer {} changeLevel: level {}".format(self.deviceId, level))

        self.hub.directCommand(self.deviceId, '21', self.hub.brightnessToHex(level))
        success = self.hub.checkSuccess(self.deviceId, '21', self.hub.brightnessToHex(level))
        if (success):
            self.logger.info("Dimmer {} changeLevel: Light level changed successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} changeLevel: Light level was not changed".format(self.deviceId))

        return success


    ## Brighten light by one step
    def brightenStep(self):
        self.logger.info("\nDimmer {} brightenStep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '15', '00')
        success = self.hub.checkSuccess(self.deviceId, '15', '00')
        if (success):
            self.logger.info("Dimmer {} brightenStep: Light brightened successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} brightenStep: Light brightened failure".format(self.deviceId))


    ## Dim light by one step
    def dimStep(self):
        self.logger.info("\nDimmer {} dimStep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '16', '00')
        success = self.hub.checkSuccess(self.deviceId, '16', '00')
        if (success):
            self.logger.info("Dimmer {} dimStep: Light dimmed successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} dimStep: Light dim failure".format(self.deviceId))


    ## Start changing light level manually
    ## Direction should be 'up' or 'down'
    def startChange(self, direction):
        self.logger.info("\nDimmer {} startChange: {}".format(self.deviceId, direction))

        if (direction == 'up'):
            level = '01'
        elif (direction == 'down'):
            level = '00'
        else:
            self.logger.error("\nDimmer {} startChange: {} is invalid, use up or down".format(self.deviceId, direction))
            return False

        self.hub.directCommand(self.deviceId, '17', level)

        status = self.hub.getBufferStatus()

        success = self.hub.checkSuccess(self.deviceId, '17', self.hub.brightnessToHex(level))
        if (success):
            self.logger.info("Dimmer {} startChange: Light started changing successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} startChange: Light did not change".format(self.deviceId))


    ## Stop changing light level manually
    def stopChange(self):
        self.logger.info("\nDimmer {} stopChange".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '18', '00')

        status = self.hub.getBufferStatus()

        success = self.hub.checkSuccess(self.deviceId, '18', '00')
        if (success):
            self.logger.info("Dimmer {} stopChange: Light stopped changing successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} stopChange: Light did not stop".format(self.deviceId))

    ## Make dimmer beep
    ## Not all devices suppot this
    def beep(self):
        self.logger.info("\nDimmer() beep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '30', '00')

        success = self.hub.checkSuccess(self.deviceId, '30', '00')
