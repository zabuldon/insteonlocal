#import pprint
#from time import sleep

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

class Group():
    """Group lighting functios. Note: groups cannot be dimmed. They can be
    linked in dimmed mode. Valid group id 1-255 (decimal)"""
    def __init__(self, hub, group_id):
        self.group_id = group_id
        self.hub = hub
        self.logger = hub.logger

    def on(self):
        """Turn group on"""
        self.logger.info("\ngroupOn: group %s", self.group_id)
        self.scene_command('11')

        #sleep(2)
        #status = self.hub.get_buffer_status()

        #success = self.check_success(device_id, '11', self.hub.brightness_to_hex(level))
        ### Todo - probably can't check this way, need to do a clean up and
        # check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOn: Group turned on successfully")
        #else:
        #    self.logger.error("groupOn: Group did not turn on")


    def off(self):
        """Turn group off"""
        self.logger.info("\ngroupOff: group %s", self.group_id)
        self.scene_command('13')

        #sleep(2)
        #status = self.hub.get_buffer_status()
        #success = self.checkSuccess(device_id, '13', self.hub.brightness_to_hex(level))
        ### Todo - probably can't check this way, need to do a clean up and
        # check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOff: Group turned off successfully")
        #else:
        #    self.logger.error("groupOff: Group did not turn off")


    def scene_command(self, command):
        """Wrapper to send posted scene command and get response"""
        self.logger.info("scene_command: Group %s Command %s", self.group_id, command)
        command_url = self.hub.hub_url + '/0?' + command + self.group_id + "=I=0"
        return self.hub.post_direct_command(command_url)


    def enter_link_mode(self):
        """Enter linking mode for a group. Press and hold button on device
        after sending this command"""
        self.logger.info("enter_link_mode Group %s", self.group_id)
        self.scene_command('09')
        # should send http://0.0.0.0/0?0901=I=0

        ## TODO check return status
        status = self.hub.get_buffer_status()
        return status


    def enter_unlink_mode(self):
        """Enter unlinking mode for a group"""
        self.logger.info("enter_unlink_mode Group %s", self.group_id)
        self.scene_command('0A')
        # should send http://0.0.0.0/0?0A01=I=0

        ## TODO check return status
        status = self.hub.get_buffer_status()
        return status


    def cancel_link_unlink_mode(self):
        """Cancel linking or unlinking mode"""
        self.logger.info("cancel_link_unlink_mode")
        self.scene_command('08')
        # should send http://0.0.0.0/0?08=I=0

        ## TODO check return status
        status = self.hub.get_buffer_status()
        return status
