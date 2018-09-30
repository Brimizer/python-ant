# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011, Martín Raúl Villalba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
##############################################################################

import struct

from ant.core.exceptions import MessageError
from ant.core.constants import *


def encode(self):
    raw = struct.pack('BBB',
                      MESSAGE_TX_SYNC,
                      len(self.get_payload()),
                      self.get_type())
    raw += self.get_payload()
    raw += chr(self.get_checksum())  # Converts the checksum to a single hex byte

    return raw


def decode(raw):
    if len(raw) < 5:
        raise MessageError('Could not decode (message is incomplete).')

    sync, length, type_ = struct.unpack('BBB', raw[:3])

    if sync != MESSAGE_TX_SYNC:
        raise MessageError('Could not decode (expected TX sync).')
    if length > 9:
        raise MessageError('Could not decode (payload too long).')
    if len(raw) < (length + 4):
        raise MessageError('Could not decode (message is incomplete).')

    self.set_type(type_)
    self.set_payload(raw[3:length + 3])

    if self.get_checksum() != ord(raw[length + 3]):
        raise MessageError('Could not decode (bad checksum).',
                           internal='CHECKSUM')

    return self.get_size()


def get_message_from_raw(self, raw=None):
    if raw:
        self.decode(raw)

    msg = None
    if self.type_ == MESSAGE_CHANNEL_UNASSIGN:
        msg = ChannelUnassignMessage()
    elif self.type_ == MESSAGE_CHANNEL_ASSIGN:
        msg = ChannelAssignMessage()
    elif self.type_ == MESSAGE_CHANNEL_ID:
        msg = ChannelIDMessage()
    elif self.type_ == MESSAGE_CHANNEL_PERIOD:
        msg = ChannelPeriodMessage()
    elif self.type_ == MESSAGE_CHANNEL_SEARCH_TIMEOUT:
        msg = ChannelSearchTimeoutMessage()
    elif self.type_ == MESSAGE_CHANNEL_FREQUENCY:
        msg = ChannelFrequencyMessage()
    elif self.type_ == MESSAGE_CHANNEL_TX_POWER:
        msg = ChannelTXPowerMessage()
    elif self.type_ == MESSAGE_NETWORK_KEY:
        msg = NetworkKeyMessage()
    elif self.type_ == MESSAGE_TX_POWER:
        msg = TXPowerMessage()
    elif self.type_ == MESSAGE_SYSTEM_RESET:
        msg = SystemResetMessage()
    elif self.type_ == MESSAGE_CHANNEL_OPEN:
        msg = ChannelOpenMessage()
    elif self.type_ == MESSAGE_CHANNEL_CLOSE:
        msg = ChannelCloseMessage()
    elif self.type_ == MESSAGE_CHANNEL_REQUEST:
        msg = ChannelRequestMessage()
    elif self.type_ == MESSAGE_CHANNEL_BROADCAST_DATA:
        msg = ChannelBroadcastDataMessage()
    elif self.type_ == MESSAGE_CHANNEL_ACKNOWLEDGED_DATA:
        msg = ChannelAcknowledgedDataMessage()
    elif self.type_ == MESSAGE_CHANNEL_BURST_DATA:
        msg = ChannelBurstDataMessage()
    elif self.type_ == MESSAGE_CHANNEL_EVENT:
        msg = ChannelEventMessage()
    elif self.type_ == MESSAGE_CHANNEL_STATUS:
        msg = ChannelStatusMessage()
    elif self.type_ == MESSAGE_VERSION:
        msg = VersionMessage()
    elif self.type_ == MESSAGE_CAPABILITIES:
        msg = CapabilitiesMessage()
    elif self.type_ == MESSAGE_SERIAL_NUMBER:
        msg = SerialNumberMessage()
    elif self.type_ == MESSAGE_STARTUP:
        msg = NotificationStartupMessage()
    else:
        raise MessageError('Could not find message handler ' \
                           '(unknown message type).')

    msg.set_payload(self.get_payload())
    return msg


class Message(object):

    def get_class_for_message(self, raw):

    def __init__(self, type_=0x00, payload=''):
        self.set_type(type_)
        self.set_payload(payload)

    def get_payload(self):
        return ''.join(self.payload)

    def set_payload(self, payload):
        if len(payload) > 9:
            raise MessageError(
                  'Could not set payload (payload too long).')

        self.payload = []
        for byte in payload:
            self.payload += byte

    def get_type(self):
        return self.type_

    def set_type(self, type_):
        if (type_ > 0xFF) or (type_ < 0x00):
            raise MessageError('Could not set type (type out of range).')

        self.type_ = type_

    def get_checksum(self):
        data = chr(len(self.get_payload()))
        data += chr(self.get_type())
        data += self.get_payload()

        checksum = MESSAGE_TX_SYNC
        for byte in data:
            checksum = (checksum ^ ord(byte)) % 0xFF

        return checksum

    def get_size(self):
        """
        Returns the size in bytes of the message.
        The size of the message is the size of the payload
            +1 for Sync byte
            +1 for Msg Len byte
            +1 for Msg ID byte
            +1 for Check sum byte
        :return: the size in bytes of the whole message
        """
        return len(self.get_payload()) + 4

    def encode(self):
        raw = struct.pack('BBB',
                          MESSAGE_TX_SYNC,
                          len(self.get_payload()),
                          self.get_type())
        raw += self.get_payload()
        raw += chr(self.get_checksum())  # Converts the checksum to a single hex byte

        return raw

    def decode(self, raw):
        if len(raw) < 5:
            raise MessageError('Could not decode (message is incomplete).')

        sync, length, type_ = struct.unpack('BBB', raw[:3])

        if sync != MESSAGE_TX_SYNC:
            raise MessageError('Could not decode (expected TX sync).')
        if length > 9:
            raise MessageError('Could not decode (payload too long).')
        if len(raw) < (length + 4):
            raise MessageError('Could not decode (message is incomplete).')

        self.set_type(type_)
        self.set_payload(raw[3:length + 3])

        if self.get_checksum() != ord(raw[length + 3]):
            raise MessageError('Could not decode (bad checksum).',
                               internal='CHECKSUM')

        return self.get_size()

    def get_handler(self, raw=None):
        if raw:
            self.decode(raw)

        msg = None
        if self.type_ == MESSAGE_CHANNEL_UNASSIGN:
            msg = ChannelUnassignMessage()
        elif self.type_ == MESSAGE_CHANNEL_ASSIGN:
            msg = ChannelAssignMessage()
        elif self.type_ == MESSAGE_CHANNEL_ID:
            msg = ChannelIDMessage()
        elif self.type_ == MESSAGE_CHANNEL_PERIOD:
            msg = ChannelPeriodMessage()
        elif self.type_ == MESSAGE_CHANNEL_SEARCH_TIMEOUT:
            msg = ChannelSearchTimeoutMessage()
        elif self.type_ == MESSAGE_CHANNEL_FREQUENCY:
            msg = ChannelFrequencyMessage()
        elif self.type_ == MESSAGE_CHANNEL_TX_POWER:
            msg = ChannelTXPowerMessage()
        elif self.type_ == MESSAGE_NETWORK_KEY:
            msg = NetworkKeyMessage()
        elif self.type_ == MESSAGE_TX_POWER:
            msg = TXPowerMessage()
        elif self.type_ == MESSAGE_SYSTEM_RESET:
            msg = SystemResetMessage()
        elif self.type_ == MESSAGE_CHANNEL_OPEN:
            msg = ChannelOpenMessage()
        elif self.type_ == MESSAGE_CHANNEL_CLOSE:
            msg = ChannelCloseMessage()
        elif self.type_ == MESSAGE_CHANNEL_REQUEST:
            msg = ChannelRequestMessage()
        elif self.type_ == MESSAGE_CHANNEL_BROADCAST_DATA:
            msg = ChannelBroadcastDataMessage()
        elif self.type_ == MESSAGE_CHANNEL_ACKNOWLEDGED_DATA:
            msg = ChannelAcknowledgedDataMessage()
        elif self.type_ == MESSAGE_CHANNEL_BURST_DATA:
            msg = ChannelBurstDataMessage()
        elif self.type_ == MESSAGE_CHANNEL_EVENT:
            msg = ChannelEventMessage()
        elif self.type_ == MESSAGE_CHANNEL_STATUS:
            msg = ChannelStatusMessage()
        elif self.type_ == MESSAGE_VERSION:
            msg = VersionMessage()
        elif self.type_ == MESSAGE_CAPABILITIES:
            msg = CapabilitiesMessage()
        elif self.type_ == MESSAGE_SERIAL_NUMBER:
            msg = SerialNumberMessage()
        elif self.type_ == MESSAGE_STARTUP:
            msg = NotificationStartupMessage()
        else:
            raise MessageError('Could not find message handler ' \
                               '(unknown message type).')

        msg.set_payload(self.get_payload())
        return msg

    def get_message_length(self):
        return len(self.payload)

    def raw(self):
        data = self.encode()
        hex_data = ['%02X' % ord(byte) for byte in data]
        hex_string = ' '.join(hex_data)
        return hex_string

    def pretty_raw(self):
        payload = self.get_payload()
        hex_data = ['%02X' % ord(byte) for byte in payload]
        hex_payload = ' '.join(hex_data)
        pretty = '{:02X}|{:02X}|{:02X}|{}|{:02X}'.format(MESSAGE_TX_SYNC,
                                                         len(self.get_payload()),
                                                         self.get_type(),
                                                         hex_payload,
                                                         self.get_checksum())
        return pretty

    def __repr__(self):
        return "<{} type:{:02X} {}>".format(self.__class__, self.type_, self.pretty_raw())


class ExtendedMessage(Message):
    def __init__(self, type_=0x00, payload=''):
        self.set_type(type_)
        self.set_payload(payload)
        self.payload = []
        self.flag_byte = 0x80

    def get_payload(self):
        return ''.join(self.payload)

    def set_payload(self, payload):
        if len(payload) > 9:
            raise MessageError(
                  'Could not set payload (payload too long).')

        for byte in payload:
            self.payload += byte

    def get_type(self):
        return self.type_

    def set_type(self, type_):
        if (type_ > 0xFF) or (type_ < 0x00):
            raise MessageError('Could not set type (type out of range).')

        self.type_ = type_

    def get_checksum(self):
        data = chr(len(self.get_payload()))
        data += chr(self.get_type())
        data += self.get_payload()

        checksum = MESSAGE_TX_SYNC
        for byte in data:
            checksum = (checksum ^ ord(byte)) % 0xFF

        return checksum

    def get_size(self):
        """
        Returns the size in bytes of the message.
        The size of the message is the size of the payload
            +1 for Sync byte
            +1 for Msg Len byte
            +1 for Msg ID byte
            +1 for Check sum byte
        :return: the size in bytes of the whole message
        """
        return len(self.get_payload()) + 4

    def encode(self):
        raw = struct.pack('BBB',
                          MESSAGE_TX_SYNC,
                          len(self.get_payload()),
                          self.get_type())
        raw += self.get_payload()
        raw += chr(self.get_checksum())  # Converts the checksum to a single hex byte

        return raw

    def decode(self, raw):
        if len(raw) < 5:
            raise MessageError('Could not decode (message is incomplete).')

        sync, length, type_ = struct.unpack('BBB', raw[:3])

        if sync != MESSAGE_TX_SYNC:
            raise MessageError('Could not decode (expected TX sync).')
        if length > 9:
            raise MessageError('Could not decode (payload too long).')
        if len(raw) < (length + 4):
            raise MessageError('Could not decode (message is incomplete).')

        self.set_type(type_)
        self.set_payload(raw[3:length + 3])

        if self.get_checksum() != ord(raw[length + 3]):
            raise MessageError('Could not decode (bad checksum).',
                               internal='CHECKSUM')

        return self.get_size()

    def get_handler(self, raw=None):
        if raw:
            self.decode(raw)

        msg = None
        if self.type_ == MESSAGE_CHANNEL_UNASSIGN:
            msg = ChannelUnassignMessage()
        elif self.type_ == MESSAGE_CHANNEL_ASSIGN:
            msg = ChannelAssignMessage()
        elif self.type_ == MESSAGE_CHANNEL_ID:
            msg = ChannelIDMessage()
        elif self.type_ == MESSAGE_CHANNEL_PERIOD:
            msg = ChannelPeriodMessage()
        elif self.type_ == MESSAGE_CHANNEL_SEARCH_TIMEOUT:
            msg = ChannelSearchTimeoutMessage()
        elif self.type_ == MESSAGE_CHANNEL_FREQUENCY:
            msg = ChannelFrequencyMessage()
        elif self.type_ == MESSAGE_CHANNEL_TX_POWER:
            msg = ChannelTXPowerMessage()
        elif self.type_ == MESSAGE_NETWORK_KEY:
            msg = NetworkKeyMessage()
        elif self.type_ == MESSAGE_TX_POWER:
            msg = TXPowerMessage()
        elif self.type_ == MESSAGE_SYSTEM_RESET:
            msg = SystemResetMessage()
        elif self.type_ == MESSAGE_CHANNEL_OPEN:
            msg = ChannelOpenMessage()
        elif self.type_ == MESSAGE_CHANNEL_CLOSE:
            msg = ChannelCloseMessage()
        elif self.type_ == MESSAGE_CHANNEL_REQUEST:
            msg = ChannelRequestMessage()
        elif self.type_ == MESSAGE_CHANNEL_BROADCAST_DATA:
            msg = ChannelBroadcastDataMessage()
        elif self.type_ == MESSAGE_CHANNEL_ACKNOWLEDGED_DATA:
            msg = ChannelAcknowledgedDataMessage()
        elif self.type_ == MESSAGE_CHANNEL_BURST_DATA:
            msg = ChannelBurstDataMessage()
        elif self.type_ == MESSAGE_CHANNEL_EVENT:
            msg = ChannelEventMessage()
        elif self.type_ == MESSAGE_CHANNEL_STATUS:
            msg = ChannelStatusMessage()
        elif self.type_ == MESSAGE_VERSION:
            msg = VersionMessage()
        elif self.type_ == MESSAGE_CAPABILITIES:
            msg = CapabilitiesMessage()
        elif self.type_ == MESSAGE_SERIAL_NUMBER:
            msg = SerialNumberMessage()
        elif self.type_ == MESSAGE_STARTUP:
            msg = NotificationStartupMessage()
        else:
            raise MessageError('Could not find message handler ' \
                               '(unknown message type).')

        msg.set_payload(self.get_payload())
        return msg

    def get_message_length(self):
        return len(self.payload)

    def raw(self):
        data = self.encode()
        hex_data = ['%02X' % ord(byte) for byte in data]
        hex_string = ' '.join(hex_data)
        return hex_string

    def pretty_raw(self):
        payload = self.get_payload()
        hex_data = ['%02X' % ord(byte) for byte in payload]
        hex_payload = ' '.join(hex_data)
        pretty = '{:02X}|{:02X}|{:02X}|{}|{:02X}'.format(MESSAGE_TX_SYNC,
                                                         len(self.get_payload()),
                                                         self.get_type(),
                                                         hex_payload,
                                                         self.get_checksum())
        return pretty

    def __repr__(self):
        return "<{} type:{:02X} {}>".format(self.__class__, self.type_, self.pretty_raw())


class ChannelMessage(Message):
    def __init__(self, type_, payload='', number=0x00):
        Message.__init__(self, type_, '\x00' + payload)
        self.setChannelNumber(number)

    def get_channel_number(self):
        return ord(self.payload[0])

    def setChannelNumber(self, number):
        if (number > 0xFF) or (number < 0x00):
            raise MessageError('Could not set channel number ' \
                                   '(out of range).')

        self.payload[0] = chr(number)


# Config messages
class ChannelUnassignMessage(ChannelMessage):
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_UNASSIGN,
                         number=number)


class ChannelAssignMessage(ChannelMessage):
    def __init__(self, number=0x00, type_=0x00, network=0x00):
        payload = struct.pack('BB', type_, network)
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_ASSIGN,
                                payload=payload, number=number)

    def getChannelType(self):
        return ord(self.payload[1])

    def setChannelType(self, type_):
        self.payload[1] = chr(type_)

    def getNetworkNumber(self):
        return ord(self.payload[2])

    def setNetworkNumber(self, number):
        self.payload[2] = chr(number)


class ChannelIDMessage(ChannelMessage):
    def __init__(self, number=0x00, device_number=0x0000, device_type=0x00,
                 trans_type=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_ID,
                                payload='\x00' * 4, number=number)
        self.setDeviceNumber(device_number)
        self.setDeviceType(device_type)
        self.setTransmissionType(trans_type)

    def getDeviceNumber(self):
        return struct.unpack('<H', self.get_payload()[1:3])[0]

    def setDeviceNumber(self, device_number):
        self.payload[1:3] = struct.pack('<H', device_number)

    def getDeviceType(self):
        return ord(self.payload[3])

    def setDeviceType(self, device_type):
        self.payload[3] = chr(device_type)

    def getTransmissionType(self):
        return ord(self.payload[4])

    def setTransmissionType(self, trans_type):
        self.payload[4] = chr(trans_type)


class ChannelPeriodMessage(ChannelMessage):
    def __init__(self, number=0x00, period=8192):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_PERIOD,
                                payload='\x00' * 2, number=number)
        self.setChannelPeriod(period)

    def getChannelPeriod(self):
        return struct.unpack('<H', self.get_payload()[1:3])[0]

    def setChannelPeriod(self, period):
        self.payload[1:3] = struct.pack('<H', period)


class ChannelSearchTimeoutMessage(ChannelMessage):
    def __init__(self, number=0x00, timeout=0xFF):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_SEARCH_TIMEOUT,
                                payload='\x00', number=number)
        self.setTimeout(timeout)

    def getTimeout(self):
        return ord(self.payload[1])

    def setTimeout(self, timeout):
        self.payload[1] = chr(timeout)


class ChannelFrequencyMessage(ChannelMessage):
    def __init__(self, number=0x00, frequency=66):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_FREQUENCY,
                                payload='\x00', number=number)
        self.setFrequency(frequency)

    def getFrequency(self):
        return ord(self.payload[1])

    def setFrequency(self, frequency):
        self.payload[1] = chr(frequency)


class ChannelTXPowerMessage(ChannelMessage):
    def __init__(self, number=0x00, power=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_TX_POWER,
                                payload='\x00', number=number)

    def getPower(self):
        return ord(self.payload[1])

    def setPower(self, power):
        self.payload[1] = chr(power)


class NetworkKeyMessage(Message):
    def __init__(self, number=0x00, key='\x00' * 8):
        Message.__init__(self, type_=MESSAGE_NETWORK_KEY, payload='\x00' * 9)
        self.setNumber(number)
        self.setKey(key)

    def getNumber(self):
        return ord(self.payload[0])

    def setNumber(self, number):
        self.payload[0] = chr(number)

    def getKey(self):
        return self.get_payload()[1:]

    def setKey(self, key):
        self.payload[1:] = key


class TXPowerMessage(Message):
    def __init__(self, power=0x00):
        Message.__init__(self, type_=MESSAGE_TX_POWER, payload='\x00\x00')
        self.setPower(power)

    def getPower(self):
        return ord(self.payload[1])

    def setPower(self, power):
        self.payload[1] = chr(power)


# Control messages
class SystemResetMessage(Message):
    def __init__(self):
        Message.__init__(self, type_=MESSAGE_SYSTEM_RESET, payload='\x00')


class ChannelOpenMessage(ChannelMessage):
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_OPEN,
                                number=number)


class ChannelCloseMessage(ChannelMessage):
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_CLOSE,
                                number=number)


class ChannelRequestMessage(ChannelMessage):
    def __init__(self, number=0x00, message_id=MESSAGE_CHANNEL_STATUS):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_REQUEST,
                                number=number, payload='\x00')
        self.setMessageID(message_id)

    def getMessageID(self):
        return ord(self.payload[1])

    def setMessageID(self, message_id):
        if (message_id > 0xFF) or (message_id < 0x00):
            raise MessageError('Could not set message ID ' \
                                   '(out of range).')

        self.payload[1] = chr(message_id)


class RequestMessage(ChannelRequestMessage):
    pass


# Data messages
class ChannelBroadcastDataMessage(ChannelMessage):
    def __init__(self, number=0x00, data='\x00' * 7):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_BROADCAST_DATA,
                                payload=data, number=number)


class ChannelAcknowledgedDataMessage(ChannelMessage):
    def __init__(self, number=0x00, data='\x00' * 7):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_ACKNOWLEDGED_DATA,
                                payload=data, number=number)


class ChannelBurstDataMessage(ChannelMessage):
    def __init__(self, number=0x00, data='\x00' * 7):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_BURST_DATA,
                                payload=data, number=number)


# Channel event messages
class ChannelEventMessage(ChannelMessage):
    def __init__(self, number=0x00, message_id=0x00, message_code=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_EVENT,
                                number=number, payload='\x00\x00')
        self.setMessageID(message_id)
        self.setMessageCode(message_code)

    def getMessageID(self):
        """
        Returns the ID of the message being responded to.
        This is set to 1 for an RF Event. (Message codes prefixed by EVENT_)
        :return: The ID of the message being responded to.

        """
        return ord(self.payload[1])

    def setMessageID(self, message_id):
        if (message_id > 0xFF) or (message_id < 0x00):
            raise MessageError('Could not set message ID ' \
                                   '(out of range).')

        self.payload[1] = chr(message_id)

    def getMessageCode(self):
        """
        The response code or event code for a specific response or event
        :return:
        """
        return ord(self.payload[2])

    def setMessageCode(self, message_code):
        if (message_code > 0xFF) or (message_code < 0x00):
            raise MessageError('Could not set message code ' \
                                   '(out of range).')

        self.payload[2] = chr(message_code)


# Requested response messages
class ChannelStatusMessage(ChannelMessage):
    def __init__(self, number=0x00, status=0x00):
        ChannelMessage.__init__(self, type_=MESSAGE_CHANNEL_STATUS,
                                payload='\x00', number=number)
        self.setStatus(status)

    def getStatus(self):
        return ord(self.payload[1])

    def setStatus(self, status):
        if (status > 0xFF) or (status < 0x00):
            raise MessageError('Could not set channel status ' \
                                   '(out of range).')

        self.payload[1] = chr(status)

#class ChannelIDMessage(ChannelMessage):


class VersionMessage(Message):
    def __init__(self, version='\x00' * 9):
        Message.__init__(self, type_=MESSAGE_VERSION, payload='\x00' * 9)
        self.setVersion(version)

    def getVersion(self):
        return self.get_payload()

    def setVersion(self, version):
        if (len(version) != 9):
            raise MessageError('Could not set ANT version ' \
                               '(expected 9 bytes).')

        self.set_payload(version)


class CapabilitiesMessage(Message):
    def __init__(self, max_channels=0x00, max_nets=0x00, std_opts=0x00,
                 adv_opts=0x00,
                 adv_opts2=0x00,
                 adv_opts3=0x00):
        Message.__init__(self, type_=MESSAGE_CAPABILITIES, payload='\x00' * 8)
        self.setMaxChannels(max_channels)
        self.setMaxNetworks(max_nets)
        self.setStdOptions(std_opts)
        self.setAdvOptions(adv_opts)
        self.setAdvOptions2(adv_opts2)
        self.setAdvOptions3(adv_opts3)

    def getMaxChannels(self):
        return ord(self.payload[0])

    def getMaxNetworks(self):
        return ord(self.payload[1])

    def getStdOptions(self):
        return ord(self.payload[2])

    def getAdvOptions(self):
        return ord(self.payload[3])

    def getAdvOptions2(self):
        return ord(self.payload[4]) if len(self.payload) == 5 else 0x00

    def getAdvOptions3(self):
        return ord(self.payload[6]) if len(self.payload) == 7 else 0x00

    def setMaxChannels(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set max channels ' \
                                   '(out of range).')

        self.payload[0] = chr(num)

    def setMaxNetworks(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set max networks ' \
                                   '(out of range).')

        self.payload[1] = chr(num)

    def setStdOptions(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set std options ' \
                                   '(out of range).')

        self.payload[2] = chr(num)

    def setAdvOptions(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set adv options ' \
                                   '(out of range).')

        self.payload[3] = chr(num)

    def setAdvOptions2(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set adv options 2 ' \
                                   '(out of range).')

        self.payload[4] = chr(num)

    def setAdvOptions3(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set adv options 3 ' \
                                   '(out of range).')
        self.payload[6] = chr(num)


class SerialNumberMessage(Message):
    def __init__(self, serial='\x00' * 4):
        Message.__init__(self, type_=MESSAGE_SERIAL_NUMBER)
        self.setSerialNumber(serial)

    def getSerialNumber(self):
        return self.get_payload()

    def setSerialNumber(self, serial):
        if (len(serial) != 4):
            raise MessageError('Could not set serial number ' \
                               '(expected 4 bytes).')

        self.set_payload(serial)


class NotificationStartupMessage(Message):
    def __init__(self, startup_message='\x00'):
        Message.__init__(self, type_=MESSAGE_STARTUP)
        self.setStartupMessage(startup_message)

    def getStartupMessage(self):
        return self.get_payload()

    def setStartupMessage(self, startup_message):
        self.set_payload(startup_message)



class Capability(object):

    def __init__(self, capability_constant):
        self.capability_constant = capability_constant
        self.raw = self.capability_constant[0]
        self.string = self.capability_constant[1]

    def raw(self):
        return self.raw

    def __repr__(self):
        return self.string


class Capabilities(object):
    def __init__(self, capabilities_message):
        self.capabilities_message = capabilities_message

    def has_standard_option(self, option):
        return self.capabilities_message.getStdOptions() & option == option

    def has_advanced_option(self, option):
        return self.capabilities_message.getAdvOptions() & option == option

    def has_advanced_option_2(self, option):
        return self.capabilities_message.getAdvOptions2() & option == option

    def has_advanced_option_3(self, option):
        return self.capabilities_message.getAdvOptions3() & option == option

    def get_available_standard_options(self):
        available_standard_capabilities = filter(lambda opt: self.has_standard_option(opt),
                                                 STANDARD_CAPABILITIES)
        return available_standard_capabilities

    def get_available_advanced_options(self):
        available_advanced_capabilities = filter(lambda opt: self.has_advanced_option(opt),
                                                 ADVANCED_CAPABILITIES)
        return available_advanced_capabilities

    def get_available_advanced_options_2(self):
        available_advanced_capabilities_2 = filter(lambda opt: self.has_advanced_option_2(opt),
                                                   ADVANCED_CAPABILITIES_2)
        return available_advanced_capabilities_2

    def get_available_advanced_options_3(self):
        available_advanced_capabilities_3 = filter(lambda opt: self.has_advanced_option_3(opt),
                                                   ADVANCED_CAPABILITIES_3)
        return available_advanced_capabilities_3

    def __repr__(self):
        return "<{}:{}|{}|{}|{}>".format(self.__class__,
                                         self.get_available_standard_options(),
                                         self.get_available_advanced_options(),
                                         self.get_available_advanced_options_2(),
                                         self.get_available_advanced_options_3())

