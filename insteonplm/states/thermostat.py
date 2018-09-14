"""Thermostat states."""
import logging
from abc import abstractmethod

from insteonplm.constants import (
    COMMAND_EXTENDED_GET_SET_0X2E_0X00,
    # COMMAND_THERMOSTAT_TEMPERATURE_UP_0X68_NONE,
    # COMMAND_THERMOSTAT_TEMPERATURE_DOWN_0X69_NONE,
    COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
    COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04,
    COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05,
    COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06,
    COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07,
    COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08,
    COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09,
    COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02,
    COMMAND_THERMOSTAT_SET_COOL_SETPOINT_0X6C_NONE,
    COMMAND_THERMOSTAT_SET_HEAT_SETPOINT_0X6D_NONE,
    COMMAND_THERMOSTAT_TEMPERATURE_STATUS_0X6E_NONE,
    COMMAND_THERMOSTAT_HUMIDITY_STATUS_0X6F_NONE,
    COMMAND_THERMOSTAT_MODE_STATUS_0X70_NONE,
    COMMAND_THERMOSTAT_COOL_SET_POINT_STATUS_0X71_NONE,
    COMMAND_THERMOSTAT_HEAT_SET_POINT_STATUS_0X72_NONE,
    MESSAGE_TYPE_DIRECT_MESSAGE,
    MESSAGE_TYPE_DIRECT_MESSAGE_ACK,
    ThermostatMode)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.extendedSend import ExtendedSend
from insteonplm.messages.extendedReceive import ExtendedReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.messages.userdata import Userdata
from insteonplm.states import State

_LOGGER = logging.getLogger(__name__)


class Temperature(State):
    """A state representing a temperature sensor."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Temperature state."""
        super(Temperature, self).__init__(address, statename, group,
                                          send_message_method,
                                          message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def _send_status_request(self):
        _LOGGER.debug("Sending status request")
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x00)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        _LOGGER.debug("Received temperature status update")
        self._update_subscribers(msg.cmd2 / 2)

    def _temp_received(self, msg):
        _LOGGER.debug("Received temperature value update")
        self._update_subscribers(msg.cmd2 / 2)

    @abstractmethod
    def _register_messages(self):
        pass

    @abstractmethod
    def _ext_status_received(self, msg):
        pass

class Humidity(State):
    """A state representing a humidity sensor."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(Humidity, self).__init__(
            address, statename, group, send_message_method,
            message_callbacks, defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x20)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        _LOGGER.debug("Received humidity status")
        self._update_subscribers(msg.cmd2)

    def _humidity_received(self, msg):
        _LOGGER.debug("Received humidity value")
        self._update_subscribers(msg.cmd2)

    @abstractmethod
    def _register_messages(self):
        pass

    @abstractmethod
    def _ext_status_received(self, msg):
        pass

class SystemMode(State):
    """A state representing the thermostat mode."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(SystemMode, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def set(self, mode):
        """Set the thermostat mode.

        Mode optons:
            OFF = 0x00,
            HEAT = 0x01,
            COOL = 0x02,
            AUTO = 0x03,
            FAN_AUTO = 0x04,
            FAN_ALWAYS_ON = 0x8
        """
        new_mode = None
        if mode == ThermostatMode.OFF:
            new_mode = COMMAND_THERMOSTAT_CONTROL_OFF_ALL_0X6B_0X09
        elif mode == ThermostatMode.HEAT:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_HEAT_0X6B_0X04
        elif mode == ThermostatMode.COOL:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_COOL_0X6B_0X05
        elif mode == ThermostatMode.AUTO:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_AUTO_0X6B_0X06
        if new_mode:
            msg = ExtendedSend(address=self._address,
                               commandtuple=new_mode,
                               userdata=Userdata())
            msg.set_checksum()
            self._send_method(msg, self._mode_change_ack)

    def _mode_change_ack(self, msg):
        set_mode = msg.cmd2
        mode = None
        if set_mode == 0x04:
            mode = ThermostatMode.HEAT
        elif set_mode == 0x05:
            mode = ThermostatMode.COOL
        elif set_mode in [0x06, 0x0a]:
            mode = ThermostatMode.AUTO
        elif set_mode == 0x09:
            mode = ThermostatMode.OFF
        if mode:
            self._update_subscribers(mode)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        _LOGGER.info("mode standard status received")
        self._update_subscribers(ThermostatMode(msg.cmd2))

    @abstractmethod
    def _ext_status_received(self, msg):
        pass

    @abstractmethod
    def _register_messages(self):
        pass


class FanMode(State):
    """A state representing the thermostat fan mode."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(FanMode, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def set(self, mode):
        """Set the thermostat mode.

        Mode optons:
            OFF = 0x00,
            HEAT = 0x01,
            COOL = 0x02,
            AUTO = 0x03,
            FAN_AUTO = 0x04,
            FAN_ALWAYS_ON = 0x8
        """
        if mode == ThermostatMode.FAN_AUTO:
            new_mode = COMMAND_THERMOSTAT_CONTROL_OFF_FAN_0X6B_0X08
        elif mode == ThermostatMode.FAN_ALWAYS_ON:
            new_mode = COMMAND_THERMOSTAT_CONTROL_ON_FAN_0X6B_0X07
        if new_mode:
            msg = ExtendedSend(address=self._address,
                               commandtuple=new_mode,
                               userdata=Userdata())
            msg.set_checksum()
            self._send_method(msg, self._mode_change_ack)

    def _mode_change_ack(self, msg):
        set_mode = msg.cmd2
        mode = None
        if set_mode == 0x07:
            mode = ThermostatMode.FAN_ALWAYS_ON
        elif set_mode == 0x08:
            mode = ThermostatMode.FAN_AUTO
        elif set_mode == 0x09:
            mode = ThermostatMode.OFF
        elif self.value == ThermostatMode.OFF:
            mode = ThermostatMode.FAN_AUTO
        if mode:
            self._update_subscribers(mode)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_CONTROL_GET_MODE_0X6B_0X02)
        self._send_method(msg, self._status_received)

    def _status_received(self, msg):
        _LOGGER.debug("Fan standard status message received")
        self._update_subscribers(ThermostatMode(msg.cmd2))

    @abstractmethod
    def _ext_status_received(self, msg):
        pass

    @abstractmethod
    def _register_messages(self):
        pass



class CoolSetPoint(State):
    """A state to manage the cool set point."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the Humidity state."""
        super(CoolSetPoint, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def set(self, val):
        """Set the cool set point."""
        msg = ExtendedSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_SET_COOL_SETPOINT_0X6C_NONE,
            cmd2=int(val * 2),
            userdata=Userdata())
        msg.set_checksum()
        self._send_method(msg, self._set_cool_point_ack)

    def _set_cool_point_ack(self, msg):
        _LOGGER.debug("Cooling setpoint standard received")
        self._update_subscribers(msg.cmd2 / 2)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x20)
        self._send_method(msg, self._status_message_received)

    def _status_message_received(self, msg):
        _LOGGER.debug("Cooling standard status received")
        self._update_subscribers(msg.cmd2 / 2)

    @abstractmethod
    def _register_messages(self):
        pass

    @abstractmethod
    def _ext_status_received(self, msg):
        pass


class HeatSetPoint(State):
    """A state to manage the cool set point."""

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue=None):
        """Init the HeatSetPoint state."""
        super(HeatSetPoint, self).__init__(
            address, statename, group, send_message_method, message_callbacks,
            defaultvalue)

        self._updatemethod = self._send_status_request

        self._register_messages()

    def set(self, val):
        """Set the heat set point."""
        msg = ExtendedSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_SET_HEAT_SETPOINT_0X6D_NONE,
            cmd2=int(val * 2),
            userdata=Userdata())
        msg.set_checksum()
        self._send_method(msg, self._set_heat_point_ack)

    def _set_heat_point_ack(self, msg):
        self._update_subscribers(msg.cmd2)

    def _send_status_request(self):
        msg = StandardSend(
            address=self._address,
            commandtuple=COMMAND_THERMOSTAT_GET_ZONE_INFORMATION_0X6A_NONE,
            cmd2=0x20)
        self._send_method(msg, self._status_message_received)

    def _status_message_received(self, msg):
        _LOGGER.debug("Heating standard status received")
        self._update_subscribers(msg.cmd2 / 2)

    @abstractmethod
    def _register_messages(self):
        pass

    @abstractmethod
    def _ext_status_received(self, msg):
        pass
