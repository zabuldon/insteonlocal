import requests, time, pprint, logging, logging.handlers, sys, json
from collections import OrderedDict

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

# Todo:
# error handling
# linking devices
# scene management
# double tap scenes
# switch on updates/broadcasts

class Hub(object):
    def __init__(self, ip, username, password, port="25105", logfile="/tmp/insteonlocal.log", consoleLog = False):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

        json_cats = open('device_categories.json')
        json_cats_str = json_cats.read()
        self.deviceCategories = json.loads(json_cats_str)

        json_models = open('device_models.json')
        json_models_str = json_models.read()
        self.deviceModels = json.loads(json_models_str)

        self.hubUrl = 'http://' + self.ip + ':' + self.port

        # Standard command (not extended)
        self.StdFlag = "0F"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(logfile, mode='a')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s] ' +
                     '(%(filename)s:%(lineno)s) %(message)s',
    				datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

        if (consoleLog):
            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)


    ## Convert numeric brightness percentage into hex for insteon
    def brightnessToHex(self, level):
        levelInt = int(level)
        newInt = int((levelInt * 255)/100)
        newLevel = format(newInt, '02X')
        self.logger.debug("brightnessToHex: {} to {}".format(level, str(newLevel)))
        return str(newLevel)


    ## Send raw command via post
    def postDirectCommand(self, commandUrl):
        self.logger.info("postDirectCommand: {}".format(commandUrl))
        return requests.post(commandUrl,
            auth=requests.auth.HTTPBasicAuth(self.username, self.password))


    ## Send raw comment via get
    def getDirectCommand(self, commandUrl):
        self.logger.info("getDirectCommand: {}".format(commandUrl))
        return requests.get(commandUrl,
            auth=requests.auth.HTTPBasicAuth(self.username, self.password))


    # Wrapper to send posted direct command and get response
    # level 0 to 100
    def directCommand(self, deviceId, command, command2):
        self.logger.info("directCommand: Device {} Command {} Command 2 {}".format(deviceId, command, command2))
        deviceId = deviceId.upper()
        commandUrl = (self.hubUrl + '/3?' + "0262"
                    + deviceId + self.StdFlag
                    + command + command2 + "=I=3")
        return self.postDirectCommand(commandUrl)


    # Direct hub command
    def directCommandHub(self, command):
        self.logger.info("directCommandHub: Command {}".format(command))
        commandUrl = (self.hubUrl + '/3?' + command + "=I=3")
        return self.postDirectCommand(commandUrl)


    # Wrapper for short-form commands (doesn't need device id or flags byte)
    # For group commands
    def directCommandShort(self, command):
        self.logger.info("directCommandShort: Command {}".format(command))
        commandUrl = (self.hubUrl + '/3?' + command + "=I=0")
        return self.postDirectCommand(commandUrl)


    # Get a list of all currently linked devices
    def getLinked(self):
        linkedDevices = {}
        self.logger.info("\ngetLinked")

        #todo instead of sleep, create loop to keep checking buffer
        self.directCommandHub("0269")
        time.sleep(1)
        status = self.getBufferStatus()
        if (status['linkedDev'] == "000000"):
            self.logger.info("getLinked: No devices linked")
            return linkedDevices

        if status['linkedDev'] not in linkedDevices:
            devInfo = self.idRequest(status['linkedDev'])

            devCat = devInfo.get("response2Cat", "")
            devSubCat = devInfo.get("response2Subcat", "")
            devCatRec = self.getDeviceCategory(devCat)
            if devCatRec and "name" in devCatRec:
                devCatName = devCatRec["name"]
                devCatType = devCatRec["type"]
            else:
                devCatName = "Unknown"
                devCatType = "unknown"
            linkedDevModel = self.getDeviceModel(devCat, devSubCat)

            if "name" in linkedDevModel:
                devModelName = linkedDevModel["name"]
            else:
                devModelName = "unknown"

            if "sku" in linkedDevModel:
                devSku = linkedDevModel["sku"]
            else:
                devSku = "unknown"

            self.logger.info("getLinked: Got first device: {} group {} cat type {} cat name {} dev model name {}".format(status['linkedDev'], status['linkedGroupNum'], devCatType, devCatName, devModelName))
            linkedDev = status['linkedDev']
            linkedDevices[linkedDev] = {
                'catName': devCatName,
                'catType': devCatType,
                'modelName' : devModelName,
                'cat': devCat,
                'subCat': devSubCat,
                'sku': devSku,
                'group': []
            }
        linkedGroupNum = status['linkedGroupNum']
        linkedDevices[linkedDev]['group'].append(linkedGroupNum)

        while (status['success']):
            self.directCommandHub("026A")
            time.sleep(1)
            status = self.getBufferStatus()
            if (status['linkedDev'] != "000000"):
                if status['linkedDev'] not in linkedDevices:
                    devInfo = self.idRequest(status['linkedDev'])
                    devCat = devInfo.get("response2Cat", "")
                    devSubCat = devInfo.get("response2Subcat", "")
                    devCatRec = self.getDeviceCategory(devCat)
                    if devCatRec and "name" in devCatRec:
                        devCatName = devCatRec["name"]
                        devCatType = devCatRec["type"]
                    else:
                        devCatName = "Unknown"
                        devCatType = "unknown"

                    linkedDevModel = self.getDeviceModel(devCat, devSubCat)
                    if "name" in linkedDevModel:
                        devModelName = linkedDevModel["name"]
                    else:
                        devModelName = "unknown"

                    if "sku" in linkedDevModel:
                        devSku = linkedDevModel["sku"]
                    else:
                        devSku = "unknown"
                    self.logger.info("getLinked: Got |device| {} |group| {} |cat type| {} |cat name| {} |dev model name| {}".format(status['linkedDev'], status['linkedGroupNum'], devCatType, devCatName, devModelName))
                linkedDev = status['linkedDev']
                if linkedDev not in linkedDevices:
                    linkedDevices[linkedDev] = {
                        'catName': devCatName,
                        'catType': devCatType,
                        'modelName' : devModelName,
                        'cat': devCat,
                        'subCat': devSubCat,
                        'sku': devSku,
                        'group': []
                    }
                linkedGroupNum = status['linkedGroupNum']
                linkedDevices[linkedDev]['group'].append(linkedGroupNum)

        self.logger.info("getLinked: Final device list: {}".format(pprint.pformat(linkedDevices)))
        return linkedDevices


    # Given the category id, return name and type for the category
    def getDeviceCategory(self, cat):
        if cat in self.deviceCategories:
            return self.deviceCategories[cat]
        else:
            return False


    # Return the model name given cat/subcat or product key
    def getDeviceModel(self, cat, subCat, key=''):
        if cat + ":" + subCat in self.deviceModels:
            return self.deviceModels[cat + ":" + subCat]
        else:
            for k,v in self.deviceModels.items():
                if "key" in v:
                    if v["key"] == key:
                        return v
            return False


    # Get the device for the ID. ID request can return device type (cat/subcat), firmware ver, etc.
    # cat is status['response2Cat'], sub cat is status['response2Subcat']
    def idRequest(self, deviceId):
        self.logger.info("\nidRequest for device {}".format(deviceId))
        deviceId = deviceId.upper()

        self.directCommand(deviceId, "10", "00")

        time.sleep(2)

        status = self.getBufferStatus()

        return status

    # Do a separate query to get device status. This can tell if device is on/off, lighting level, etc.
    # status['responseCmd2'] is lighting level
    # responseCmd1 contains All-Link Database delta
    # if returnLED = 0. returns light level in responseCmd2
    # if returnLED = 1, returns LED Bit Flags in responseCmd1

    def getDeviceStatus(self, deviceId, returnLED=0):
        self.logger.info("\ngetDeviceStatus for device {}".format(deviceId))
        deviceId = deviceId.upper()

        if (returnLED == 1):
            level = "01"
        else:
            level = "00"
        self.directCommand(deviceId, "19", level)

        time.sleep(2)

        status = self.getBufferStatus()

        return status


    # Main method to read from buffer
    def getBufferStatus(self):
        commandUrl = self.hubUrl + '/buffstatus.xml'
        self.logger.info("getBufferStatus: {}".format(commandUrl))

        response = self.getDirectCommand(commandUrl)
        responseText = response.text
        responseText = responseText.replace('<response><BS>', '')
        responseText = responseText.replace('</BS></response>', '')

        responseStatus = OrderedDict()

        responseType = responseText[0:4]

        self.logger.info("getBufferStatus: Got Response type {} text of {}".format(responseType, responseText))

        if (responseType == '0250'):
            self.logger.info("Response type 0250 standard message")
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['responseType']     = responseText[0:4]
            responseStatus['responseDevice']   = responseText[4:10]
            responseStatus['responseHub']      = responseText[10:16]
            responseStatus['responseFlag']     = responseText[16:17] # 2 for ack
            responseStatus['responseHopCt']    = responseText[17:18] # hop count F, B, 7, or 3
            responseStatus['responseCmd1']     = responseText[18:20] # cmd 1
            responseStatus['responseCmd2']     = responseText[20:22] # brightness, etc.
        elif (responseType == '0251'):
            # TODO
            self.logger.error("Not implemented handling 0251 extended message")
        elif (responseType == '0252'):
            self.logger.error("Not implemented handling 0252 X10 message received")
        elif (responseType == '0253'):
            # TODO test
            self.logger.info("Response type 0253 All Linking Completed")
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['sendResponseType'] = responseText[0:4] # direct vs scene,
            # imType = 00 responder 01 controller FF link deleted
            responseStatus['imType']           = responseText[4:6]
            responseStatus['groupId']          = responseText[6:8]
            responseStatus['responseDevice']   = responseText[8:14]
            responseStatus['deviceCat']        = responseText[14:16]
            responseStatus['deviceSubcat']     = responseText[16:18]
            responseStatus['firmware']         = responseText[18:20]

        elif (responseType == '0254'):
            # TODO
            self.logger.error("Not implemented handling 0254 Button Event Report")
            # next byte:
            # 02 set button tapped
            # 03 set button held
            # 04 set button released after hold
            # 12 button 2 tapped
            # 13 button 2 held
            # 14 button 2 released after hold
            # 22 button 3 tapped
            # 23 button 3 held
            # 24 button 3 released after hold
        elif (responseType == '0255'):
            # TODO
            self.logger.error("Not implemented handling 0255 User Reset - user pushed and held SET button on power up")
        elif (responseType == '0256'):
            # TODO
            self.logger.error("Not implemented handling 0256 All-link cleanup failure")
        elif (responseType == '0257'):
            # TODO
            self.logger.error("Not implemented handling 0257 All-link record response")
        elif (responseType == '0258'):
            # TODO
            self.logger.error("Not implemented handling 0258 All-link cleanup status report")
        elif (responseType == '0259'):
            # TODO
            self.logger.error("Not implemented handling 0259 database record found")
        elif (responseType == '0261'):
            # scene response
            self.logger.info("Response type 0261 scene response")
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['responseType']     = responseText[0:4]
            responseStatus['groupNum']         = responseText[4:6]
            responseStatus['groupCmd']         = responseText[6:8] # 11 for on
            responseStatus['groupCmdArg']      = responseText[8:10] # ????
            responseStatus['ackorNak']         = responseText[10:12]

        elif (responseType == '0262'):
            self.logger.info("Response type 0262 (cmd sent from host) extended msg received {}".format(responseText[18:22]))
            # Pass through command to PLM
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['sendResponseType'] = responseText[0:4] # direct vs scene,
            responseStatus['sendDevice']       = responseText[4:10]
            responseStatus['sendCmdFlag']      = responseText[10:12] # std vs extended
            responseStatus['sendCmd']          = responseText[12:14]
            responseStatus['sendCmdArg']       = responseText[14:16]
            responseStatus['ackorNak']         = responseText[16:18] # 06 ok 15 error
            responseStatus['responseType']     = responseText[18:22]
            responseStatus['responseDevice']   = responseText[22:28]
            responseStatus['responseHub']      = responseText[28:34]
            responseStatus['responseFlag']     = responseText[34:35] # 2 for ack
            responseStatus['responseHopCt']    = responseText[35:36] # hop count F, B, 7, or 3
            responseStatus['responseCmd1']     = responseText[36:38] # database delta
            responseStatus['responseCmd2']     = responseText[38:40] # brightness, etc.

            if ((len(responseText) > 40) and (responseText[40:44] != "0000") and (responseText[0:44] != "")):
                # we have another message - like id response
                responseStatus['response2Type']     = responseText[40:44]
                responseStatus['response2Device']   = responseText[44:50]
                responseStatus['response2Cat']      = responseText[50:52]
                responseStatus['response2Subcat']   = responseText[52:54]
                responseStatus['response2Firmware'] = responseText[54:56]
                responseStatus['response2Flag']     = responseText[56:57]
                responseStatus['response2HopCt']    = responseText[57:58]
                responseStatus['response2Cmd1']     = responseText[58:60]
                responseStatus['response2Cmd2']     = responseText[60:62]

        elif (responseType == '0264'):
            responseStatus['responseType'] = responseText[0:4]
            responseStatus['imType']       = responseText[4:6] # 00 IM is responder, 01 is controller, 03 im is either, FF link deleted
            responseStatus['groupId']      = responseText[6:8]

        elif (responseType == '0265'):
            # Hub responds to cancel all linking
            responseStatus['responseType'] = responseText[0:4]
            responseStatus['ack']          = responseText[4:6] # 06

        elif ((responseType == '0269') or (responseType == '026A')):
            # Response from getting devices from hub
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['sendCmd']          = responseText[0:4] # 0269
            responseStatus['ackorNak']         = responseText[4:6] # 06 ack 15 nak or empty
            responseStatus['responseCmd']      = responseText[6:10] # 0257 all link record response
            responseStatus['responseFlags']    = responseText[10:12] # 00-FF is controller...bitted for in use, master/slave, etc. See p44 of INSTEON Hub Developers Guide 20130618
            responseStatus['linkedGroupNum']   = responseText[12:14]
            responseStatus['linkedDev']        = responseText[14:20]
            responseStatus['linkedData1']     = responseText[20:22] # 01 dimmer
            responseStatus['linkedData2']  = responseText[22:24] # varies by device type
            responseStatus['linkedData3'] = responseText[24:26] # varies by device type

        if ((not responseText) or (responseText == 0) or (responseType == "0000")):
            responseStatus['error'] = True
            responseStatus['success'] = False
            responseStatus['message'] = 'Empty buffer'
        elif (responseStatus.get('ackorNak', '') == '06'):
            responseStatus['success'] = True
            responseStatus['error'] = False
        elif (responseStatus.get('ackorNak', '') == '15'):
            responseStatus['success'] = False
            responseStatus['error'] = True
            responseStatus['message'] = 'Device returned nak'
        elif (responseStatus.get('responseFlag', '') == '2'):
            responseStatus['success'] = True
            responseStatus['error'] = False

        self.logger.info("getBufferStatus: Received response of: {}".format(pprint.pformat(responseStatus)))

        # Best to clear it after reading it. It overwrites the buffer left
        # to right but doesn't clear out old chars past what it wrote. Last
        # two bytes tell where it stopped writing
        self.clearBuffer()
        return responseStatus


    ## Check if last command succeeded  by checking buffer
    def checkSuccess(self, deviceId, level):
        deviceId = deviceId.upper()

        self.logger.info('checkSuccess: for device {} level {}'.format(deviceId, level))

        time.sleep(2)
        status = self.getBufferStatus()
        statusDevice = status.get("responseDevice", "")
        statusCmdArg = status.get("responseCmd2", "")
        statusSuccess = status.get("success", False)
        #self.logger.info('checkSuccess: Got status {}'.format(pprint.pformat(status)))
        self.logger.info('checkSuccess: Response device {} cmd {}'.format(statusDevice, statusCmdArg))
        if ((statusDevice == deviceId) and statusSuccess
            and (statusCmdArg == self.brightnessToHex(level))):
            self.logger.info('checkSuccess: Switch command was successful')
            return True
        else:
            self.logger.error('checkSuccess: Switch command failed')
            self.logger.info('checkSuccess: Device compare {} to {}'.format(deviceId, statusDevice))
            self.logger.info('checkSuccess: Level compare {} to {}'.format(self.brightnessToHex(level), statusCmdArg))
            return False


    ## Clear the hub buffer
    def clearBuffer(self):
        commandUrl = self.hubUrl + '/1?XB=M=1'
        response = self.postDirectCommand(commandUrl)
        self.logger.info("clearBuffer: {}".format(response))
        return response



   ## @TODO IN DEVELOPMENT
   ### TODO listen for linked page 35 http://cache.insteon.com/developer/2242-222dev-062013-en.pdf
   ## Begin all linking
   # linkType:
   #  00 as responder/slave
   #  01 as controller/master
   #  03 as controller with im initiates all linking or as responder when another device initiates all linking
   #  FF deletes the all link
    def startAllLinking(self, linkType):
        self.logger.info("\nstartAllLinking for type " + linkType)
        self.directCommandHub('0264' + linkType)
       # TODO: read response
        #    Byte Value Meaning
        #1 0x02 Echoed Start of IM Command
        #2 0x64 Echoed IM Command Number
        #3 <Code> Echoed <Code>
        #4 <ALL-Link Group> Echoed <ALL-Link Group>
        #5 <ACK/NAK> 0x06 (ACK) if the IM executed the Command correctly
        #0x15 (NAK) if an error occurred


    def cancelAllLinking(self):
        self.logger.info("\ncancelAllLinking")
        self.directCommandHub('0265')
        ## TODO read response
            # 0x02 echoed start of command
            # 0x65 echoed im command
            # ack 06 or nak 15


    def group(self, groupId):
        groupObj = Group(self, groupId)
        return groupObj

    def dimmer(self, deviceId):
        dimmerObj = Dimmer(self, deviceId)
        return dimmerObj

    def switch(self, deviceId):
        switchObj = Switch(self, deviceId)
        return switchObj



### Group Lighting Functions - note, groups cannot be dimmed. They can be linked in dimmed mode.
class Group():

    def __init__(self, hub, groupId):
        self.groupId = groupId.zfill(2)
        self.hub = hub
        self.logger = hub.logger

    # Turn group on
    def on(self):
        self.logger.info("\ngroupOn: group {}".format(self.groupId))
        self.sceneCommand('11')

        #time.sleep(2)
        #status = self.hub.getBufferStatus()

        #success = self.checkSuccess(deviceId, level)
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOn: Group turned on successfully")
        #else:
        #    self.logger.error("groupOn: Group did not turn on")


    # Turn group off
    def off(self):
        self.logger.info("\ngroupOff: group {}".format(self.groupId))
        self.sceneCommand('13')

        #time.sleep(2)
        #status = self.hub.getBufferStatus()
        #success = self.checkSuccess(deviceId, level)
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
    ## @TODO UNTESTED - IN DEVELOPMENT
    def enterLinkMode(self):
        self.logger.info("\nenterLinkMode Group {}".format(self.groupId));
        self.sceneCommand('09')
        # should send http://0.0.0.0/0?0901=I=0

        ## TODO check return status
        status = self.hub.getBufferStatus()
        return status


    # Enter unlinking mode for a group
    ## @TODO UNTESTED - IN DEVELOPMENT
    def enterUnlinkMode(self,):
        self.logger.info("\nenterUnlinkMode Group {}".format(self.groupId));
        self.sceneCommand('0A')
        # should send http://0.0.0.0/0?0A01=I=0

        ## TODO check return status
        status = self.hub.getBufferStatus()
        return status


    # Cancel linking or unlinking mode
    ## @TODO UNTESTED - IN DEVELOPMENT
    def cancelLinkUnlinkMode(self):
        self.logger.info("\ncancelLinkUnlinkMode");
        self.sceneCommand('08')
        # should send http://0.0.0.0/0?08=I=0

        ## TODO check return status
        status = self.hub.getBufferStatus()
        return status



class Switch():

    def __init__(self, hub, deviceId):
        self.deviceId = deviceId
        self.hub = hub
        self.logger = hub.logger


    def status(self, returnLED = 0):
        status = self.hub.getDeviceStatus(self.deviceId, returnLED)
        self.logger.info("\nDimmer {} status: {}".format(self.deviceId, pprint.pformat(status)))
        return status


    ## Turn light On
    def on(self):
        self.logger.info("\nSwitch {} on".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '11', 'FF')

        success = self.hub.checkSuccess(self.deviceId, 'FF')

        if (success):
            self.logger.info("Switch {} on: Light turned on successfully".format(self.deviceId))
        else:
            self.logger.error("Switch {} on: Light did not turn on".format(self.deviceId))

        return success


    ## Turn light Off
    def off(self):
        self.logger.info("\nSwitch {} off".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '13', 'FF')

        success = self.hub.checkSuccess(self.deviceId, 'FF')

        if (success):
            self.logger.info("Switch {} off: Light turned off successfully".format(self.deviceId))
        else:
            self.logger.error("Switch {} off: Light did not turn off".format(self.deviceId))

        return success


    ## Make switch beep
    ## Not all devices suppot this
    def beep(self):
        self.logger.info("\nSwitch() beep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '30', '00')

        success = self.hub.checkSuccess(self.deviceId, '00')


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

        success = self.hub.checkSuccess(self.deviceId, self.hub.brightnessToHex(level))
        if (success):
            self.logger.info("Dimmer {} on: Light turned on successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} on: Light did not turn on".format(self.deviceId))

        return success

    ## Turn light On to Saved State - using "fast"
    def onSaved(self):
        self.logger.info("\nDimmer {} onSaved".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '12', '00')

        success = self.hub.checkSuccess(self.deviceId, '00')
        if (success):
            self.logger.info("Dimmer {} onSaved: Light turned on successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} onSaved: Light did not turn on".format(self.deviceId))

        return success


    ## Turn Light Off at saved ramp rate
    def off(self):
        self.logger.info("\nDimmer {} off".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '13', '00')

        success = self.hub.checkSuccess(self.deviceId, '00')
        if (success):
            self.logger.info("Dimmer {} off: Light turned off successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} off: Light did not turn off".format(self.deviceId))

        return success


    ## Turn Light Off
    def offInstant(self):
        self.logger.info("\nDimmer {} offInstant".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '14', '00')

        success = self.hub.checkSuccess(self.deviceId, '00')
        if (success):
            self.logger.info("Dimmer {} offInstant: Light turned off successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} offInstant: Light did not turn off".format(self.deviceId))

        return success


    ## Change light level
    def changeLevel(self, level):
        self.logger.info("\nDimmer {} changeLevel: level {}".format(self.deviceId, level))

        self.hub.directCommand(self.deviceId, '21', self.hub.brightnessToHex(level))
        success = self.hub.checkSuccess(self.deviceId, self.hub.brightnessToHex(level))
        if (success):
            self.logger.info("Dimmer {} changeLevel: Light level changed successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} changeLevel: Light level was not changed".format(self.deviceId))

        return success


    ## Brighten light by one step
    def brightenStep(self):
        self.logger.info("\nDimmer {} brightenStep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '15', '00')
        success = self.hub.checkSuccess(self.deviceId, '00')
        if (success):
            self.logger.info("Dimmer {} brightenStep: Light brightened successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} brightenStep: Light brightened failure".format(self.deviceId))


    ## Dim light by one step
    def dimStep(self):
        self.logger.info("\nDimmer {} dimStep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '16', '00')
        success = self.hub.checkSuccess(self.deviceId, '00')
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

        success = self.hub.checkSuccess(self.deviceId, level)
        if (success):
            self.logger.info("Dimmer {} startChange: Light started changing successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} startChange: Light did not change".format(self.deviceId))


    ## Stop changing light level manually
    def stopChange(self):
        self.logger.info("\nDimmer {} stopChange".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '18', '00')

        status = self.hub.getBufferStatus()

        success = self.hub.checkSuccess(self.deviceId, '00')
        if (success):
            self.logger.info("Dimmer {} stopChange: Light stopped changing successfully".format(self.deviceId))
        else:
            self.logger.error("Dimmer {} stopChange: Light did not stop".format(self.deviceId))

    ## Make dimmer beep
    ## Not all devices suppot this
    def beep(self):
        self.logger.info("\nDimmer() beep".format(self.deviceId))

        self.hub.directCommand(self.deviceId, '30', '00')

        success = self.hub.checkSuccess(self.deviceId, '00')
