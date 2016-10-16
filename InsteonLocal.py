#from urllib import urlencode
import requests, time, pprint, logging, logging.handlers, sys

# todo
# move switch to its own class?
# error handling
# buffer handling - handle broadcasts?
# device list
# linking
# scenes
# sprinkler
# pool
# leak detector
# thermostats
# sensor open/close
# sensor hidden door
# sensor motion
# sensor leak (leak detector)
# smoke bridge
# io module
# ceiling fan
# micro dimmer
# on/off micro
# open/close micro
# ballast dimmer
# dimmer in-line
# mini remote
# outlets
# garage controller
# other devices
# allow setting operating flags (program lock, led off, beeper off)

class InsteonLocal(object):

    def __init__(self, ip, username, password, port="25105", logfile="/tmp/insteonlocal.log", consoleLog = False):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

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
    def directCommand(self, deviceId, command, level):
        self.logger.info("directCommand: Device {} Command {} Level {}".format(deviceId, command, level))
        deviceId = deviceId.upper()
        levelHex = self.brightnessToHex(level)
        commandUrl = (self.hubUrl + '/3?' + "0262"
                    + deviceId + self.StdFlag
                    + command + levelHex + "=I=3")
        return self.postDirectCommand(commandUrl)


    # Wrapper to send posted scene command and get response
    def sceneCommand(self, groupNum, command):
        self.logger.info("sceneCommand: Group {} Command {}".format(groupNum, command))
 #       levelHex = self.brightnessToHex(level)
        commandUrl = self.hubUrl + '/0?' + command + groupNum + "=I=0"
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


    def getLinked(self):
        linkedDevices = {}

        #todo instead of sleep, create loop to keep checking buffer
        self.directCommandHub("0269")
        time.sleep(1)
        status = self.getBufferStatus()
        if (status['linkedDev'] == "000000"):
            self.logger.info("getLinked: No devices linked")
            return linkedDevices
        self.logger.info("getLinked: Got first device: {} group {}".format(status['linkedDev'], status['linkedGroupNum']))
        linkedDevices[status['linkedGroupNum']] = status['linkedDev']

        while (status['success']):
            self.directCommandHub("026A")
            time.sleep(1)
            status = self.getBufferStatus()
            if (status['linkedDev'] != "000000"):
                self.logger.info("getLinked: Got device: {} group {}".format(status['linkedDev'], status['linkedGroupNum']))
                linkedDevices[status['linkedGroupNum']] = status['linkedDev']

        self.logger.info("getLinked: Final device list: {}".format(pprint.pformat(linkedDevices)))
        return linkedDevices


    # Get the device for the ID
    def idRequest(self, deviceId):
        self.logger.info("idRequest for device {}".format(deviceId))
        deviceId = deviceId.upper()

        self.directCommand(deviceId, "10", "00")

        time.sleep(2)

        self.getBufferStatus()


    # Do a separate query to get device status
    def getDeviceStatus(self, deviceId):
        self.logger.info("getDeviceStatus for device {}".format(deviceId))
        deviceId = deviceId.upper()

        self.directCommand(deviceId, "19", "00")

        time.sleep(2)

        self.getBufferStatus()


    # Main method to read from buffer
    def getBufferStatus(self):
        commandUrl = self.hubUrl + '/buffstatus.xml'
        self.logger.info("getBufferStatus: {}".format(commandUrl))

        response = self.getDirectCommand(commandUrl)
        responseText = response.text
        responseText = responseText.replace('<response><BS>', '')
        responseText = responseText.replace('</BS></response>', '')

        responseType = responseText[0:4];

        if (responseType == '0262'):
            # Pass through command to PLM
            responseStatus = {
                'error':            True,
                'success':          False,
                'message':          '',
                'sendCmdType':      responseText[0:4], # direct vs scene,
                'sendDevice':       responseText[4:10],
                'sendCmdFlag':      responseText[10:12], # std vs extended
                'sendCmd':          responseText[12:14],
                'sendCmdArg':       responseText[14:16],
                'ackorNak':         responseText[16:18], # 06 ok 15 error
                'responseCmdStart': responseText[18:20],
                'responseType':     responseText[20:22],
                'responseDevice':   responseText[22:28],
                'responseHub':      responseText[28:34],
                'responseFlag':     responseText[34:35], # 2 for ack
                'responseHopCt':    responseText[35:36], # hop count F, B, 7, or 3
                'responseCmd1':     responseText[36:38], # database delta
                'responseCmd2':     responseText[38:40] # brightness, etc.
            }
        elif ((responseType == '0269') or (responseType == '026A')):
                # Response from getting devices from hub
            responseStatus = {
                'error':            True,
                'success':          False,
                'message':          '',
                'sendCmd':          responseText[0:4], # 0269
                'ackorNak':         responseText[4:6], # 06 ack 15 nak or empty
                'responseCmd':      responseText[6:10], # 0257 all link record response
                'responseFlags':    responseText[10:12], # 00-FF is controller...bitted for in use, master/slave, etc. See p44 of INSTEON Hub Developers Guide 20130618
                'linkedGroupNum':   responseText[12:14],
                'linkedDev':        responseText[14:20],
                'linkedDevCat':     responseText[20:22], # 01 dimmer
                'linkedDevSubcat':  responseText[22:24], # varies by device type
                'linkedDevFirmVer': responseText[24:26], # varies by device type
            }

        if (not responseText) or (responseText == 0):
            responseStatus['error'] = True
            responseStatus['success'] = False
            responseStatus['message'] = 'Empty buffer'
        elif (responseStatus['ackorNak'] == '06'):
            responseStatus['success'] = True
            responseStatus['error'] = False
        elif (responseStatus['ackorNak'] == '15'):
            responseStatus['success'] = False
            responseStatus['error'] = True
            responseStatus['message'] = 'Device returned nak'

        self.logger.info("getBufferStatus: Got Response text of {}".format(responseText))
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
        self.logger.info('checkSuccess: Got status {}'.format(pprint.pformat(status)))
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



### TODO listen for linked page 35 http://cache.insteon.com/developer/2242-222dev-062013-en.pdf

   ### Group Commands

    # Enter linking mode for a group
    def enterLinkMode(self, groupNumber):
        self.logger.info("enterLinkMode for group {}".format(groupNumber));
        self.directCommandShort('09' + groupNumber)
        # should send http://0.0.0.0/0?0901=I=0

        ## TODO check return status
        status = self.getBufferStatus()
        return status


    # Enter unlinking mode for a group
    def enterUnlinkMode(self, groupNumber):
        self.logger.info("enterUnlinkMode for group {}".format(groupNumber));
        self.directCommandShort('0A' + groupNumber)
        # should send http://0.0.0.0/0?0A01=I=0

        ## TODO check return status
        status = self.getBufferStatus()
        return status


    # Cancel linking or unlinking mode
    def cancelLinkUnlinkMode(self):
        self.logger.info("cancelLinkUnlinkMode");
        self.directCommandShort('08')
        # should send http://0.0.0.0/0?08=I=0

        ## TODO check return status
        status = self.getBufferStatus()
        return status



    ## Begin all linking
    # linkType:
    #  00 as responder/slave
    #  01 as controller/master
    #  03 as controller with im initiates all linking or as responder when another device initiates all linking
    #  FF deletes the all link
    def startAllLinking(self, linkType):
        self.logger.info("startAllLinking for type " + linkType)
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
        self.logger.info("cancelAllLinking")
        self.directCommandHub('0265')
## TODO read response
    # 0x02 echoed start of command
    # 0x65 echoed im command
    # ack 06 or nak 15


    ### Group Lighting Functions - note, groups cannot be dimmed. They can be linked in dimmed mode.

    # Turn group on
    def groupOn(self, groupNum):
        self.logger.info("groupOn: group {}".format(groupNum))
        self.sceneCommand(groupNum, "11")
        success = self.checkSuccess(deviceId, level)
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        if (success):
            self.logger.info("groupOn: Group turned on successfully")
        else:
            self.logger.error("groupOn: Group did not turn on")


    # Turn group off
    def groupOff(self, groupNum):
        self.logger.info("groupOff: group {}".format(groupNum))
        self.sceneCommand(groupNum, "31")
        success = self.checkSuccess(deviceId, level)
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        if (success):
            self.logger.info("groupOff: Group turned off successfully")
        else:
            self.logger.error("groupOff: Group did not turn off")



    ### Lighting Functions


    ## Turn light On
    # fast seems to always do full brightness
    def lightOn(self, deviceId, level, fast=0):
        deviceId = deviceId.upper()

        self.logger.info("lightOn: device {} level {} fast {}".format(deviceId, level, fast))

        if fast:
            self.directCommand(deviceId, "12", level)
        else:
            self.directCommand(deviceId, "11", level)

        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightOn: Light turned on successfully")
        else:
            self.logger.error("lightOn: Light did not turn on")


    ## Turn Light Off
    # doesn't seem to be a speed difference with fast
    def lightOff(self, deviceId, fast=0):
        deviceId = deviceId.upper()

        self.logger.info("lightOff: device {} fast {}".format(deviceId, fast))

        if fast:
            self.directCommand(deviceId, "14", '00')
        else:
            self.directCommand(deviceId, "13", '00')

        success = self.checkSuccess(deviceId, '00')
        if (success):
            self.logger.info("lightOff: Light turned off successfully")
        else:
            self.logger.error("lightOff: Light did not turn off")



    ## Change light level
    def lightLevel(self, deviceId, level):
        deviceId = deviceId.upper()

        self.logger.info("lightLevel: device {} level {}".format(deviceId, level))

        self.directCommand(deviceId, "21", level)
        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightLevel: Light level changed successfully")
        else:
            self.logger.error("lightLevel: Light level was not changed")



    ## Brighten light by one step
    def lightBrightenStep(self, deviceId):
        deviceId = deviceId.upper()

        self.logger.info("lightBrightenStep: device{}".format(deviceId))

        self.directCommand(deviceId, "15", "00")
        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightBrightenStep: Light brightened successfully")
        else:
            self.logger.error("lightBrightenStep: Light brightened failure")


    ## Dim light by one step
    def lightDimStep(self, deviceId):
        deviceId = deviceId.upper()

        self.logger.info("lightDimStep: device{}".format(deviceId))

        self.directCommand(deviceId, "16", "00")
        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightDimStep: Light dimmed successfully")
        else:
            self.logger.error("lightDimStep: Light dim failure")

