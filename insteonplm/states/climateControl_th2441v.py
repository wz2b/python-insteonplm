from insteonplm.constants import COMMAND_THERMOSTAT_HUMIDITY_STATUS_0X6F_NONE, MESSAGE_TYPE_DIRECT_MESSAGE, \
    COMMAND_EXTENDED_GET_SET_0X2E_0X00, ThermostatMode, COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE, \
    COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04, MESSAGE_TYPE_DIRECT_MESSAGE_ACK, \
    COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05, COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06, \
    COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09, COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07, \
    COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08, COMMAND_THERMOSTAT_COOL_SET_POINT_STATUS_0X71_NONE, \
    COMMAND_THERMOSTAT_HEAT_SET_POINT_STATUS_0X72_NONE
from insteonplm.messages import StandardReceive, ExtendedReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.userdata import Userdata
from insteonplm.states.thermostat import Temperature, Humidity, SystemMode, FanMode, CoolSetPoint, HeatSetPoint


class Temperature_2441v(Temperature):

    def _register_messages(self):
        humidity_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_HUMIDITY_STATUS_0X6F_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))

        self._message_callbacks.add(humidity_msg, self._humidity_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x00,
            userdata=Userdata.template({"d1": 0x01}))
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        c_temp = msg.userdata['d10'] | (msg.userdata['d9'] << 8)
        f_temp = c_temp * .1 * 9 / 5 + 32
        self._update_subscribers(f_temp)


class SystemMode_2441v(SystemMode):


    def _register_messages(self):
        mode_status_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))
        mode_change_heat_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_cool_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_auto_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_off_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))

        self._message_callbacks.add(mode_status_msg,
                                    self._status_received)
        self._message_callbacks.add(mode_change_heat_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_cool_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_auto_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_off_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        sysmode = msg.userdata['d6']
        ext_mode = sysmode >> 4
        if ext_mode == 0:
            mode = ThermostatMode.OFF
        elif ext_mode == 1:
            mode = ThermostatMode.AUTO
        elif ext_mode == 2:
            mode = ThermostatMode.HEAT
        elif ext_mode == 3:
            mode = ThermostatMode.COOL
        self._update_subscribers(mode)

class FanMode_2441v(FanMode):

    def _register_messages(self):
        mode_status_msg = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, None))
        mode_change_fan_on_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_fan_auto_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        mode_change_off_ack = StandardReceive.template(
            commandtuple=COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE_ACK))
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))

        self._message_callbacks.add(mode_status_msg,
                                    self._status_received)
        self._message_callbacks.add(mode_change_fan_on_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_fan_auto_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(mode_change_off_ack,
                                    self._mode_change_ack)
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)


    def _ext_status_received(self, msg):
        sysmode = msg.userdata['d6']
        ext_mode = sysmode >> 4
        if ext_mode == 0:
            mode = ThermostatMode.OFF
        elif ext_mode == 1:
            mode = ThermostatMode.AUTO
        elif ext_mode == 2:
            mode = ThermostatMode.HEAT
        elif ext_mode == 3:
            mode = ThermostatMode.COOL
        self._update_subscribers(mode)

        sysmode = msg.userdata['d6']
        ext_mode = sysmode & 0x0f
        if ext_mode == 0:
            mode = ThermostatMode.FAN_AUTO
        elif ext_mode == 1:
            mode = ThermostatMode.FAN_ALWAYS_ON
        if mode:
            self._update_subscribers(mode)


class CoolSetPoint_2441v(CoolSetPoint):

    def _register_messages(self):
        cool_set_point_status = StandardReceive.template(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_COOL_SET_POINT_STATUS_0X71_NONE,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, False))
        self._message_callbacks.add(cool_set_point_status,
                                    self._status_message_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            userdata=Userdata.template({"d1": 0x01}))
        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

        def _ext_status_received(self, msg):
            cool_sp = msg.userdata['d7'] / 2
            self._update_subscribers(cool_sp)


class HeatSetPoint_2441v(HeatSetPoint):

    def _register_messages(self):
        heat_set_point_status = StandardReceive.template(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_HEAT_SET_POINT_STATUS_0X72_NONE,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, False))
        self._message_callbacks.add(heat_set_point_status,
                                    self._status_message_received)
        ext_status_recd = ExtendedReceive.template(
            commandtuple=COMMAND_EXTENDED_GET_SET_0X2E_0X00,
            cmd2=0x02,
            flags=MessageFlags.template(MESSAGE_TYPE_DIRECT_MESSAGE, True),
            userdata=Userdata.template({"d1": 0x01}))

        self._message_callbacks.add(ext_status_recd,
                                    self._ext_status_received)

    def _ext_status_received(self, msg):
        heat_sp = msg.userdata['d12'] / 2
        self._update_subscribers(heat_sp)