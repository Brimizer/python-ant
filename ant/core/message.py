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

from ant.core.helpers import *
from ant.core.exceptions import MessageError
from ant.core.constants import *


MAX_PAYLOAD_LENGTH = 8

MESSAGE_SIZE = 13

# def encode(self):
#     raw = struct.pack('BBB',
#                       MESSAGE_TX_SYNC,
#                       len(self.get_payload()),
#                       self.msg_id)
#     raw += self.get_payload()
#     raw += chr(self.get_checksum())  # Converts the checksum to a single hex byte
#
#     return raw


def checksum(data=b''):
    if not data or len(data) == 0:
        return 0
    cksum = 0x00
    for byte in data:
        cksum = (cksum ^ byte) % 0xFF
    return cksum


def get_proper_message(raw=b''):
    if raw is None or not len(raw):
        return None
    # print("get_proper_message raw: {}".format(encode_bytes(raw, separator=' ')))
    msg_id = raw[2]
    # print("get_proper_message msg_id: {:02X}".format(msg_id))

    if msg_id == MESSAGE_CHANNEL_UNASSIGN:
        msg = ChannelUnassignMessage()
    elif msg_id == MESSAGE_CHANNEL_ASSIGN:
        msg = ChannelAssignMessage()
    elif msg_id == MESSAGE_CHANNEL_ID:
        msg = ChannelIDMessage()
    elif msg_id == MESSAGE_CHANNEL_PERIOD:
        msg = ChannelPeriodMessage()
    elif msg_id == MESSAGE_CHANNEL_SEARCH_TIMEOUT:
        msg = ChannelSearchTimeoutMessage()
    elif msg_id == MESSAGE_CHANNEL_FREQUENCY:
        msg = ChannelFrequencyMessage()
    elif msg_id == MESSAGE_CHANNEL_TX_POWER:
        msg = ChannelTXPowerMessage()
    elif msg_id == MESSAGE_NETWORK_KEY:
        msg = NetworkKeyMessage()
    elif msg_id == MESSAGE_TX_POWER:
        msg = TXPowerMessage()
    elif msg_id == MESSAGE_SYSTEM_RESET:
        msg = SystemResetMessage()
    elif msg_id == MESSAGE_CHANNEL_OPEN:
        msg = ChannelOpenMessage()
    elif msg_id == MESSAGE_CHANNEL_CLOSE:
        msg = ChannelCloseMessage()
    elif msg_id == MESSAGE_CHANNEL_REQUEST:
        msg = ChannelRequestMessage()
    elif msg_id == MESSAGE_CHANNEL_BROADCAST_DATA:
        msg = ChannelBroadcastDataMessage()
    elif msg_id == MESSAGE_CHANNEL_ACKNOWLEDGED_DATA:
        msg = ChannelAcknowledgedDataMessage()
    elif msg_id == MESSAGE_CHANNEL_BURST_DATA:
        msg = ChannelBurstDataMessage()
    elif msg_id == MESSAGE_CHANNEL_EVENT:
        msg = ChannelEventMessage()
    elif msg_id == MESSAGE_CHANNEL_STATUS:
        msg = ChannelStatusMessage()
    elif msg_id == MESSAGE_VERSION:
        msg = VersionMessage()
    elif msg_id == MESSAGE_CAPABILITIES:
        msg = CapabilitiesMessage()
    elif msg_id == MESSAGE_SERIAL_NUMBER:
        msg = SerialNumberMessage()
    elif msg_id == MESSAGE_STARTUP:
        msg = NotificationStartupMessage()
    else:
        raise MessageError('Could not find message handler ' \
                           '(unknown message type).')

    msg.decode(raw)
    return msg


class Message(object):

    def __init__(self,
                 msg_id=0x00,
                 payload=b''):
        """
        If including a channel number, the channel number should be the first byte of the payload.
        :param msg_id:
        :param payload:
        """
        self.sync = MESSAGE_TX_SYNC
        self._msg_id = msg_id

        self.is_extended_message = False
        self.flag_byte = None
        self._extended_data_bytes = bytearray()
        self._payload = bytearray()
        self.set_payload(payload)

    @property
    def msg_id(self):
        return self._msg_id

    @msg_id.setter
    def msg_id(self, value):
        if value < 0 or value > 0xFF:
            raise MessageError('Could not decode (message id is invalid).')
        self._msg_id = value

    def get_payload(self):
        # return ''.join([str(int(i)) for i in self._payload])
        return self._payload

    def set_payload(self, payload):
        """
        A payload can be 8 bytes + 1 for the channel number.
        :param payload:
        :return:
        """
        if len(payload) > 9:
            raise MessageError(
                  'Could not set payload (payload too long).')
        self._payload = bytearray(payload)

    def get_channel_num(self):
        if not self._payload or len(self._payload) == 0:
            return 0x00
        return self.get_payload()[0]

    def get_checksum(self):
        data = bytearray()
        data.append(self.sync)
        data.append(self.msg_id)
        data.append(len(self.get_payload()))
        data.extend(self.get_payload())

        return checksum(data)

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
        raw = bytearray()
        raw.append(self.sync)
        raw.append(len(self.get_payload()))
        raw.append(self.msg_id)
        raw.extend(self.get_payload())
        raw.append(self.get_checksum())  # Converts the checksum to a single hex byte

        return bytes(raw)

    def decode(self, raw):
        """
        :param raw: a bytes object
        :return:
        """
        if len(raw) < 5:
            raise MessageError('Could not decode (message is incomplete).')

        if checksum(raw[:len(raw) - 1]) != raw[-1]:
            raise MessageError('Could not decode (bad checksum).',
                               internal='CHECKSUM')

        # Unpack the first 3 bytes
        sync = raw[0]
        msg_length = raw[1]
        msg_id = raw[2]

        if sync != MESSAGE_TX_SYNC:
            raise MessageError('Could not decode (expected TX sync).')

        self.sync = sync
        self.msg_id = msg_id
        self.set_payload(raw[3:msg_length + 3])

        # 2 Types: Standard and Extended
        if msg_length > 9 and len(raw) >= 12 and raw[12] == EXTENDED_FORMAT_FLAG_BYTE:
            # Only valid if the message is in Flagged Extended Data Message Format
            self.flag_byte = EXTENDED_FORMAT_FLAG_BYTE
            self.is_extended_message = True
        elif msg_length > 9:
            raise MessageError('Could not decode (payload too long).')

        # Checks that the supplied msg_length byte == the length of the actual raw message
        if len(raw) < (msg_length + 4):  # 4 because of sync, len, id, crc
            raise MessageError('Could not decode (message is incomplete).')

        return self.get_size()

    def get_message_length(self):
        """
        Length of the payload.
        :return: Returns length of the "message" section.
        """
        return len(self._payload)

    def set_extended(self, flag_byte, data_for_flag):
        self.flag_byte = flag_byte
        self._extended_data_bytes = data_for_flag

    # def get_flag_byte(self):
    #     if not self.is_extended_message:
    #         raise MessageError('only extended data format messages support flag bytes.')
    #     return self._extended_data_bytes[0]

    def get_device_number(self):
        if not self.is_extended_message:
            raise MessageError('device number not supported. Not an extended message.')
        return self._extended_data_bytes[0:2]
    # def get_measurement_type(self):
    #     if not self.is_extended_message:
    #         raise MessageError('only extended data format messages support flag bytes.')
    #     return self._extended_data_bytes[1]


    def raw(self):
        data = self.encode()
        hex_data = ['%02X' % ord(byte) for byte in data]
        hex_string = ' '.join(hex_data)
        return hex_string

    def pretty_raw(self):
        payload = self.get_payload()
        hex_data = ['%02X' % byte for byte in payload]
        hex_payload = ' '.join(hex_data)
        pretty = '{:02X}|{:02X}|{:02X}|{}|{:02X}'.format(MESSAGE_TX_SYNC,
                                                                len(self.get_payload()),
                                                                self.msg_id,
                                                                hex_payload,
                                                                self.get_checksum())
        return pretty

    def __repr__(self):
        return "<{} type:{:02X} {}>".format(self.__class__, self.msg_id, self.pretty_raw())


# class ExtendedMessage(Message):
#     def __init__(self, msg_id=0x00, payload=''):
#         self.set_msg_id(msg_id)
#         self.set_payload(payload)
#         self._payload = []
#         self.flag_byte = 0x80
#
#     def get_payload(self):
#         return ''.join(self._payload)
#
#     def set_payload(self, payload):
#         if len(payload) > 9:
#             raise MessageError(
#                   'Could not set payload (payload too long).')
#
#         for byte in payload:
#             self._payload += byte
#
#     def get_msg_id(self):
#         return self.type_
#
#     def set_msg_id(self, type_):
#         if (type_ > 0xFF) or (type_ < 0x00):
#             raise MessageError('Could not set type (type out of range).')
#
#         self.type_ = type_
#
#     def get_checksum(self):
#         data = chr(len(self.get_payload()))
#         data += chr(self.get_msg_id())
#         data += self.get_payload()
#
#         checksum = MESSAGE_TX_SYNC
#         for byte in data:
#             checksum = (checksum ^ ord(byte)) % 0xFF
#
#         return checksum
#
#     def get_size(self):
#         """
#         Returns the size in bytes of the message.
#         The size of the message is the size of the payload
#             +1 for Sync byte
#             +1 for Msg Len byte
#             +1 for Msg ID byte
#             +1 for Check sum byte
#         :return: the size in bytes of the whole message
#         """
#         return len(self.get_payload()) + 4
#
#     def encode(self):
#         raw = struct.pack('BBB',
#                           MESSAGE_TX_SYNC,
#                           len(self.get_payload()),
#                           self.get_msg_id())
#         raw += self.get_payload()
#         raw += chr(self.get_checksum())  # Converts the checksum to a single hex byte
#
#         return raw
#
#     def decode(self, raw):
#         if len(raw) < 5:
#             raise MessageError('Could not decode (message is incomplete).')
#
#         sync, length, type_ = struct.unpack('BBB', raw[:3])
#
#         if sync != MESSAGE_TX_SYNC:
#             raise MessageError('Could not decode (expected TX sync).')
#         if length > 9:
#             raise MessageError('Could not decode (payload too long).')
#         if len(raw) < (length + 4):
#             raise MessageError('Could not decode (message is incomplete).')
#
#         self.set_msg_id(type_)
#         self.set_payload(raw[3:length + 3])
#
#         if self.get_checksum() != ord(raw[length + 3]):
#             raise MessageError('Could not decode (bad checksum).',
#                                internal='CHECKSUM')
#
#         return self.get_size()
#
#     def get_handler(self, raw=None):
#         if raw:
#             self.decode(raw)
#
#         msg = None
#         if self.type_ == MESSAGE_CHANNEL_UNASSIGN:
#             msg = ChannelUnassignMessage()
#         elif self.type_ == MESSAGE_CHANNEL_ASSIGN:
#             msg = ChannelAssignMessage()
#         elif self.type_ == MESSAGE_CHANNEL_ID:
#             msg = ChannelIDMessage()
#         elif self.type_ == MESSAGE_CHANNEL_PERIOD:
#             msg = ChannelPeriodMessage()
#         elif self.type_ == MESSAGE_CHANNEL_SEARCH_TIMEOUT:
#             msg = ChannelSearchTimeoutMessage()
#         elif self.type_ == MESSAGE_CHANNEL_FREQUENCY:
#             msg = ChannelFrequencyMessage()
#         elif self.type_ == MESSAGE_CHANNEL_TX_POWER:
#             msg = ChannelTXPowerMessage()
#         elif self.type_ == MESSAGE_NETWORK_KEY:
#             msg = NetworkKeyMessage()
#         elif self.type_ == MESSAGE_TX_POWER:
#             msg = TXPowerMessage()
#         elif self.type_ == MESSAGE_SYSTEM_RESET:
#             msg = SystemResetMessage()
#         elif self.type_ == MESSAGE_CHANNEL_OPEN:
#             msg = ChannelOpenMessage()
#         elif self.type_ == MESSAGE_CHANNEL_CLOSE:
#             msg = ChannelCloseMessage()
#         elif self.type_ == MESSAGE_CHANNEL_REQUEST:
#             msg = ChannelRequestMessage()
#         elif self.type_ == MESSAGE_CHANNEL_BROADCAST_DATA:
#             msg = ChannelBroadcastDataMessage()
#         elif self.type_ == MESSAGE_CHANNEL_ACKNOWLEDGED_DATA:
#             msg = ChannelAcknowledgedDataMessage()
#         elif self.type_ == MESSAGE_CHANNEL_BURST_DATA:
#             msg = ChannelBurstDataMessage()
#         elif self.type_ == MESSAGE_CHANNEL_EVENT:
#             msg = ChannelEventMessage()
#         elif self.type_ == MESSAGE_CHANNEL_STATUS:
#             msg = ChannelStatusMessage()
#         elif self.type_ == MESSAGE_VERSION:
#             msg = VersionMessage()
#         elif self.type_ == MESSAGE_CAPABILITIES:
#             msg = CapabilitiesMessage()
#         elif self.type_ == MESSAGE_SERIAL_NUMBER:
#             msg = SerialNumberMessage()
#         elif self.type_ == MESSAGE_STARTUP:
#             msg = NotificationStartupMessage()
#         else:
#             raise MessageError('Could not find message handler ' \
#                                '(unknown message type).')
#
#         msg.set_payload(self.get_payload())
#         return msg
#
#     def get_message_length(self):
#         return len(self._payload)
#
#     def raw(self):
#         data = self.encode()
#         hex_data = ['%02X' % ord(byte) for byte in data]
#         hex_string = ' '.join(hex_data)
#         return hex_string
#
#     def pretty_raw(self):
#         payload = self.get_payload()
#         hex_data = ['%02X' % ord(byte) for byte in payload]
#         hex_payload = ' '.join(hex_data)
#         pretty = '{:02X}|{:02X}|{:02X}|{}|{:02X}'.format(MESSAGE_TX_SYNC,
#                                                          len(self.get_payload()),
#                                                          self.get_msg_id(),
#                                                          hex_payload,
#                                                          self.get_checksum())
#         return pretty
#
#     def __repr__(self):
#         return "<{} type:{:02X} {}>".format(self.__class__, self.type_, self.pretty_raw())


class ChannelMessage(Message):
    def __init__(self, msg_id, payload=b'', number=0x00):
        Message.__init__(self, msg_id, b'\x00' + payload)
        self.setChannelNumber(number)

    def get_channel_number(self):
        return self._payload[0]

    def setChannelNumber(self, number):
        if (number > 0xFF) or (number < 0x00):
            raise MessageError('Could not set channel number ' \
                                   '(out of range).')

        self._payload[0] = number


# Config messages
class ChannelUnassignMessage(ChannelMessage):
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_UNASSIGN,
                                number=number)


class ChannelAssignMessage(ChannelMessage):
    def __init__(self, number=0x00, msg_id=0x00, network=0x00):
        payload = struct.pack('BB', msg_id, network)
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_ASSIGN,
                                payload=payload, number=number)

    def getChannelType(self):
        return self._payload[1]

    def setChannelType(self, type_):
        self._payload[1] = type_

    def getNetworkNumber(self):
        return self._payload[2]

    def setNetworkNumber(self, number):
        self._payload[2] = number


class ChannelIDMessage(ChannelMessage):
    def __init__(self, number=0x00, device_number=0x0000, device_type=0x00,
                 trans_type=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_ID,
                                payload=b'\x00' * 4, number=number)
        self.setDeviceNumber(device_number)
        self.setDeviceType(device_type)
        self.setTransmissionType(trans_type)

    def getDeviceNumber(self):
        return struct.unpack('<H', self.get_payload()[1:3])[0]

    def setDeviceNumber(self, device_number):
        self._payload[1:3] = struct.pack('<H', device_number)

    def getDeviceType(self):
        return self._payload[3]

    def setDeviceType(self, device_type):
        self._payload[3] = device_type

    def getTransmissionType(self):
        return self._payload[4]

    def setTransmissionType(self, trans_type):
        self._payload[4] = trans_type


class ChannelPeriodMessage(ChannelMessage):
    def __init__(self, number=0x00, period=8192):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_PERIOD,
                                payload=b'\x00' * 2, number=number)
        self.setChannelPeriod(period)

    def getChannelPeriod(self):
        return struct.unpack('<H', self.get_payload()[1:3])[0]

    def setChannelPeriod(self, period):
        self._payload[1:3] = struct.pack('<H', period)


class ChannelSearchTimeoutMessage(ChannelMessage):
    def __init__(self, number=0x00, timeout=0xFF):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_SEARCH_TIMEOUT,
                                payload=b'\x00', number=number)
        self.setTimeout(timeout)

    def getTimeout(self):
        return self._payload[1]

    def setTimeout(self, timeout):
        self._payload[1] = timeout


class ChannelFrequencyMessage(ChannelMessage):
    def __init__(self, number=0x00, frequency=66):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_FREQUENCY,
                                payload=b'\x00', number=number)
        self.setFrequency(frequency)

    def getFrequency(self):
        return self._payload[1]

    def setFrequency(self, frequency):
        self._payload[1] = frequency


class ChannelTXPowerMessage(ChannelMessage):
    def __init__(self, number=0x00, power=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_TX_POWER,
                                payload=b'\x00', number=number)

    def getPower(self):
        return self._payload[1]

    def setPower(self, power):
        self._payload[1] = power


class NetworkKeyMessage(Message):
    def __init__(self, number=0x00, key=b'\x00' * 8):
        Message.__init__(self, msg_id=MESSAGE_NETWORK_KEY, payload=b'\x00' * 9)
        self.setNumber(number)
        self.setKey(key)

    def getNumber(self):
        return self._payload[0]

    def setNumber(self, number):
        self._payload[0] = number

    def getKey(self):
        return self.get_payload()[1:]

    def setKey(self, key):
        assert isinstance(key, (bytes, bytearray))
        for idx, byte in enumerate(key):
            # print("idx: {:02X}".format(idx))
            # One offset for the number portion
            self._payload[idx + 1] = byte


class TXPowerMessage(Message):
    def __init__(self, power=0x00):
        Message.__init__(self, msg_id=MESSAGE_TX_POWER, payload=b'\x00\x00')
        self.setPower(power)

    def getPower(self):
        return self._payload[1]

    def setPower(self, power):
        self._payload[1] = power


# Control messages
class SystemResetMessage(Message):
    def __init__(self):
        Message.__init__(self, msg_id=MESSAGE_SYSTEM_RESET, payload=b'\x00')


class ChannelOpenMessage(ChannelMessage):
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_OPEN,
                                number=number)


class ChannelCloseMessage(ChannelMessage):
    def __init__(self, number=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_CLOSE,
                                number=number)


class ChannelRequestMessage(ChannelMessage):
    def __init__(self, number=0x00, message_id=0x01):
        """

        :param number: The Channel number
        :param message_id: 1 if originating a request or the ID of the original request if a response.
        """
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_REQUEST,
                                number=number, payload=b'\x00')
        self.setMessageID(message_id)

    def getMessageID(self):
        return self._payload[1]

    def setMessageID(self, message_id):
        if (message_id > 0xFF) or (message_id < 0x00):
            raise MessageError('Could not set message ID ' \
                                   '(out of range).')

        self._payload[1] = message_id


class RequestMessage(ChannelRequestMessage):
    pass


# Data messages
class ChannelBroadcastDataMessage(ChannelMessage):
    def __init__(self, number=0x00, data=b'\x00' * 7):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_BROADCAST_DATA,
                                payload=data, number=number)


class ChannelAcknowledgedDataMessage(ChannelMessage):
    def __init__(self, number=0x00, data=b'\x00' * 7):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_ACKNOWLEDGED_DATA,
                                payload=data, number=number)


class ChannelBurstDataMessage(ChannelMessage):
    def __init__(self, number=0x00, data=b'\x00' * 7):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_BURST_DATA,
                                payload=data, number=number)


# Channel event messages
class ChannelEventMessage(ChannelMessage):
    def __init__(self, number=0x00, message_id=0x00, message_code=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_EVENT,
                                number=number, payload=b'\x00\x00')
        self.setMessageID(message_id)
        self.setMessageCode(message_code)

    def getMessageID(self):
        """
        Returns the ID of the message being responded to.
        This is set to 1 for an RF Event. (Message codes prefixed by EVENT_)
        :return: The ID of the message being responded to.

        """
        return self._payload[1]

    def setMessageID(self, message_id):
        if (message_id > 0xFF) or (message_id < 0x00):
            raise MessageError('Could not set message ID ' \
                                   '(out of range).')

        self._payload[1] = message_id

    def getMessageCode(self):
        """
        The response code or event code for a specific response or event
        :return:
        """
        return self._payload[2]

    def setMessageCode(self, message_code):
        if (message_code > 0xFF) or (message_code < 0x00):
            raise MessageError('Could not set message code ' \
                                   '(out of range).')

        self._payload[2] = message_code


# Requested response messages
class ChannelStatusMessage(ChannelMessage):
    def __init__(self, number=0x00, status=0x00):
        ChannelMessage.__init__(self, msg_id=MESSAGE_CHANNEL_STATUS,
                                payload=b'\x00', number=number)
        self.setStatus(status)

    def getStatus(self):
        return self._payload[1]

    def setStatus(self, status):
        if (status > 0xFF) or (status < 0x00):
            raise MessageError('Could not set channel status ' \
                                   '(out of range).')

        self._payload[1] = status

#class ChannelIDMessage(ChannelMessage):


class VersionMessage(Message):
    def __init__(self, version=b'\x00' * 9):
        Message.__init__(self, msg_id=MESSAGE_VERSION, payload=b'\x00' * 9)
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
        Message.__init__(self, msg_id=MESSAGE_CAPABILITIES, payload=b'\x00' * 8)
        self.setMaxChannels(max_channels)
        self.setMaxNetworks(max_nets)
        self.setStdOptions(std_opts)
        self.setAdvOptions(adv_opts)
        self.setAdvOptions2(adv_opts2)
        self.setAdvOptions3(adv_opts3)

    # def get_payload(self):
    #     # For only this message type, strip trailing null characters.
    #     payload = super(CapabilitiesMessage, self).get_payload()
    #     # return payload.rstrip(b'\x00')
    #     return payload

    def getMaxChannels(self):
        return self._payload[0]

    def getMaxNetworks(self):
        return self._payload[1]

    def getStdOptions(self):
        return self._payload[2]

    def getAdvOptions(self):
        return self._payload[3]

    def getAdvOptions2(self):
        return self._payload[4] if len(self._payload) >= 5 else 0x00

    def getAdvOptions3(self):
        return self._payload[6] if len(self._payload) >= 7 else 0x00

    def setMaxChannels(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set max channels ' \
                                   '(out of range).')

        self._payload[0] = num

    def setMaxNetworks(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set max networks ' \
                                   '(out of range).')

        self._payload[1] = num

    def setStdOptions(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set std options ' \
                                   '(out of range).')
        if num is None or 0x00:
            del self._payload[2]
        self._payload[2] = num

    def setAdvOptions(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set adv options ' \
                                   '(out of range).')

        self._payload[3] = num

    def setAdvOptions2(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set adv options 2 ' \
                                   '(out of range).')

        self._payload[4] = num

    def setAdvOptions3(self, num):
        if (num > 0xFF) or (num < 0x00):
            raise MessageError('Could not set adv options 3 ' \
                                   '(out of range).')
        self._payload[6] = num


class SerialNumberMessage(Message):
    def __init__(self, serial=b'\x00' * 4):
        Message.__init__(self, msg_id=MESSAGE_SERIAL_NUMBER)
        self.setSerialNumber(serial)

    def getSerialNumber(self):
        return self.get_payload()

    def setSerialNumber(self, serial):
        if (len(serial) != 4):
            raise MessageError('Could not set serial number ' \
                               '(expected 4 bytes).')

        self.set_payload(serial)


class NotificationStartupMessage(Message):
    def __init__(self, startup_message=b'\x00'):
        Message.__init__(self, msg_id=MESSAGE_STARTUP)
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
        available_standard_capabilities = [opt for opt in STANDARD_CAPABILITIES if
                                           self.has_advanced_option(opt)]

        return available_standard_capabilities

    def get_available_advanced_options(self):
        available_advanced_capabilities = [opt for opt in ADVANCED_CAPABILITIES if
                                           self.has_advanced_option(opt)]
        return available_advanced_capabilities

    def get_available_advanced_options_2(self):
        available_advanced_capabilities_2 = [opt for opt in ADVANCED_CAPABILITIES_2 if
                                           self.has_advanced_option(opt)]
        return available_advanced_capabilities_2

    def get_available_advanced_options_3(self):
        available_advanced_capabilities_3 = [opt for opt in ADVANCED_CAPABILITIES_3 if
                                           self.has_advanced_option(opt)]
        return available_advanced_capabilities_3

    def __repr__(self):
        return "<{}:{}|{}|{}|{}>".format(self.__class__,
                                         self.get_available_standard_options(),
                                         self.get_available_advanced_options(),
                                         self.get_available_advanced_options_2(),
                                         self.get_available_advanced_options_3())

