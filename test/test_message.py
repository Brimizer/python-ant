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

import unittest

from ant.core.message import *


def test_checksum():
    data = b''
    assert checksum(data) == 0
    data = b'\xFF'
    assert checksum(data) == 0
    # data = [0xFF, 0x]. .



class MessageTest(unittest.TestCase):
    def setUp(self):
        self.message = Message()

    def test_get_setPayload(self):
        self.assertRaises(MessageError, self.message.set_payload,
                          b'\xFF' * 15)
        self.message.set_payload(b'\x11' * 5)
        self.assertEqual(self.message.get_payload(), b'\x11' * 5)

    def test_get_setType(self):
        def set(i): self.message.msg_id = i
        self.assertRaises(MessageError, set, -1)
        self.assertRaises(MessageError, set, 300)
        self.message.msg_id = 0x23
        self.assertEqual(self.message.msg_id, 0x23)

    def test_getChecksum(self):
        self.message = Message(msg_id=MESSAGE_SYSTEM_RESET, payload=b'\x00')
        self.assertEqual(self.message.get_checksum(), 0xEF)
        self.message = Message(msg_id=MESSAGE_CHANNEL_ASSIGN,
                               payload=b'\x00' * 3)
        self.assertEqual(self.message.get_checksum(), 0xE5)

    def test_getSize(self):
        self.message.set_payload(b'\x11' * 7)
        self.assertEqual(self.message.get_size(), 11)

    def test_encode(self):
        self.message = Message(msg_id=MESSAGE_CHANNEL_ASSIGN,
                               payload=b'\x00' * 3)
        self.assertEqual(self.message.encode(),
                         b'\xA4\x03\x42\x00\x00\x00\xE5')

    def test_decode(self):
        self.assertRaises(MessageError, self.message.decode,
                          b'\xA5\x03\x42\x00\x00\x00\xE5')
        self.assertRaises(MessageError, self.message.decode,
                          b'\xA4\x14\x42' + (b'\x00' * 20) + b'\xE5')
        self.assertRaises(MessageError, self.message.decode,
                          b'\xA4\x03\x42\x01\x02\xF3\xE5')
        self.assertEqual(7, self.message.decode(b'\xA4\x03\x42\x00\x00\x00\xE5'))
        self.assertEqual(MESSAGE_CHANNEL_ASSIGN, self.message.msg_id)
        self.assertEqual(b'\x00' * 3, self.message.get_payload())
        self.assertEqual(0xE5, self.message.get_checksum())

    def test_getHandler(self):
        msg = get_proper_message(b'\xA4\x03\x42\x00\x00\x00\xE5')
        self.assertTrue(isinstance(msg, ChannelAssignMessage))
        self.assertRaises(MessageError, get_proper_message,
                          b'\xA4\x03\xFF\x00\x00\x00\xE5')
        self.assertRaises(MessageError, get_proper_message,
                          b'\xA4\x03\x42')
        self.assertRaises(MessageError, get_proper_message,
                          b'\xA4\x05\x42\x00\x00\x00\x00')


class ChannelMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelMessage(msg_id=MESSAGE_SYSTEM_RESET)

    def test_get_setChannelNumber(self):
        self.assertEqual(self.message.get_channel_number(), 0)
        self.message.setChannelNumber(3)
        self.assertEqual(self.message.get_channel_number(), 3)


class ChannelUnassignMessageTest(unittest.TestCase):
    # No currently defined methods need testing
    pass


class ChannelAssignMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelAssignMessage()

    def test_get_setChannelType(self):
        self.message.setChannelType(0x10)
        self.assertEqual(self.message.getChannelType(), 0x10)

    def test_get_setNetworkNumber(self):
        self.message.setNetworkNumber(0x11)
        self.assertEqual(self.message.getNetworkNumber(), 0x11)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setChannelType(0x02)
        self.message.setNetworkNumber(0x03)
        self.assertEqual(self.message.get_payload(), b'\x01\x02\x03')


class ChannelIDMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelIDMessage()

    def test_get_setDeviceNumber(self):
        self.message.setDeviceNumber(0x10FA)
        self.assertEqual(self.message.getDeviceNumber(), 0x10FA)

    def test_get_setDeviceType(self):
        self.message.setDeviceType(0x10)
        self.assertEqual(self.message.getDeviceType(), 0x10)

    def test_get_setTransmissionType(self):
        self.message.setTransmissionType(0x11)
        self.assertEqual(self.message.getTransmissionType(), 0x11)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setDeviceNumber(0x0302)
        self.message.setDeviceType(0x04)
        self.message.setTransmissionType(0x05)
        self.assertEqual(b'\x01\x02\x03\x04\x05', self.message.get_payload())


class ChannelPeriodMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelPeriodMessage()

    def test_get_setChannelPeriod(self):
        self.message.setChannelPeriod(0x10FA)
        self.assertEqual(self.message.getChannelPeriod(), 0x10FA)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setChannelPeriod(0x0302)
        self.assertEqual(self.message.get_payload(), b'\x01\x02\x03')


class ChannelSearchTimeoutMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelSearchTimeoutMessage()

    def test_get_setTimeout(self):
        self.message.setTimeout(0x10)
        self.assertEqual(self.message.getTimeout(), 0x10)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setTimeout(0x02)
        self.assertEqual(self.message.get_payload(), b'\x01\x02')


class ChannelFrequencyMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelFrequencyMessage()

    def test_get_setFrequency(self):
        self.message.setFrequency(22)
        self.assertEqual(self.message.getFrequency(), 22)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setFrequency(0x02)
        self.assertEqual(self.message.get_payload(), b'\x01\x02')


class ChannelTXPowerMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelTXPowerMessage()

    def test_get_setPower(self):
        self.message.setPower(0xFA)
        self.assertEqual(self.message.getPower(), 0xFA)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setPower(0x02)
        self.assertEqual(self.message.get_payload(), b'\x01\x02')


class NetworkKeyMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = NetworkKeyMessage()

    def test_get_setNumber(self):
        self.message.setNumber(0xFA)
        self.assertEqual(self.message.getNumber(), 0xFA)

    def test_get_setKey(self):
        self.message.setKey(b'\xFD' * 8)
        self.assertEqual(self.message.getKey(), b'\xFD' * 8)

    def test_payload(self):
        self.message.setNumber(0x01)
        self.message.setKey(b'\x02\x03\x04\x05\x06\x07\x08\x09')
        self.assertEqual(self.message.get_payload(),
                          b'\x01\x02\x03\x04\x05\x06\x07\x08\x09')


class TXPowerMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = TXPowerMessage()

    def test_get_setPower(self):
        self.message.setPower(0xFA)
        self.assertEqual(self.message.getPower(), 0xFA)

    def test_payload(self):
        self.message.setPower(0x01)
        self.assertEqual(self.message.get_payload(), b'\x00\x01')


class SystemResetMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = SystemResetMessage()

    def test_payload(self):
        self.assertEqual(self.message.get_payload(), b'\x00')
        self.assertEqual(len(self.message.get_payload()), 1)


class ChannelOpenMessageTest(unittest.TestCase):
    # No currently defined methods need testing
    pass


class ChannelCloseMessageTest(unittest.TestCase):
    # No currently defined methods need testing
    pass


class ChannelRequestMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelRequestMessage()

    def test_get_setMessageID(self):
        self.message.setMessageID(0xFA)
        self.assertEqual(self.message.getMessageID(), 0xFA)
        self.assertRaises(MessageError, self.message.setMessageID, 0xFFFF)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setMessageID(0x02)
        self.assertEqual(self.message.get_payload(), b'\x01\x02')


class ChannelBroadcastDataMessageTest(unittest.TestCase):
    # No currently defined methods need testing
    pass


class ChannelAcknowledgedDataMessageTest(unittest.TestCase):
    # No currently defined methods need testing
    pass


class ChannelBurstDataMessageTest(unittest.TestCase):
    # No currently defined methods need testing
    pass


class ChannelEventMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelEventMessage()

    def test_get_setMessageID(self):
        self.message.setMessageID(0xFA)
        self.assertEqual(self.message.getMessageID(), 0xFA)
        self.assertRaises(MessageError, self.message.setMessageID, 0xFFFF)

    def test_get_setMessageCode(self):
        self.message.setMessageCode(0xFA)
        self.assertEqual(self.message.getMessageCode(), 0xFA)
        self.assertRaises(MessageError, self.message.setMessageCode, 0xFFFF)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setMessageID(0x02)
        self.message.setMessageCode(0x03)
        self.assertEqual(b'\x01\x02\x03', self.message.get_payload())


class ChannelStatusMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = ChannelStatusMessage()

    def test_get_setStatus(self):
        self.message.setStatus(0xFA)
        self.assertEqual(self.message.getStatus(), 0xFA)
        self.assertRaises(MessageError, self.message.setStatus, 0xFFFF)

    def test_payload(self):
        self.message.setChannelNumber(0x01)
        self.message.setStatus(0x02)
        self.assertEqual(self.message.get_payload(), b'\x01\x02')


class VersionMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = VersionMessage()

    def test_get_setVersion(self):
        self.message.setVersion(b'\xAB' * 9)
        self.assertEqual(self.message.getVersion(), b'\xAB' * 9)
        self.assertRaises(MessageError, self.message.setVersion, '1234')

    def test_payload(self):
        self.message.setVersion(b'\x01' * 9)
        self.assertEqual(self.message.get_payload(), b'\x01' * 9)


class CapabilitiesMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = CapabilitiesMessage()

    def test_get_setMaxChannels(self):
        self.message.setMaxChannels(0xFA)
        self.assertEqual(self.message.getMaxChannels(), 0xFA)
        self.assertRaises(MessageError, self.message.setMaxChannels, 0xFFFF)

    def test_get_setMaxNetworks(self):
        self.message.setMaxNetworks(0xFA)
        self.assertEqual(self.message.getMaxNetworks(), 0xFA)
        self.assertRaises(MessageError, self.message.setMaxNetworks, 0xFFFF)

    def test_get_setStdOptions(self):
        self.message.setStdOptions(0xFA)
        self.assertEqual(self.message.getStdOptions(), 0xFA)
        self.assertRaises(MessageError, self.message.setStdOptions, 0xFFFF)

    def test_get_setAdvOptions(self):
        self.message.setAdvOptions(0xFA)
        self.assertEqual(self.message.getAdvOptions(), 0xFA)
        self.assertRaises(MessageError, self.message.setAdvOptions, 0xFFFF)

    def test_get_setAdvOptions2(self):
        self.message.setAdvOptions2(0xFA)
        self.assertEqual(self.message.getAdvOptions2(), 0xFA)
        self.assertRaises(MessageError, self.message.setAdvOptions2, 0xFFFF)
        self.message = CapabilitiesMessage(adv_opts2=0x00)
        # self.assertEqual(len(self.message.get_payload()), 4)

    def test_payload(self):
        self.message.setMaxChannels(0x01)
        self.message.setMaxNetworks(0x02)
        self.message.setStdOptions(0x03)
        self.message.setAdvOptions(0x04)
        self.message.setAdvOptions2(0x05)
        self.assertEqual(b'\x01\x02\x03\x04\x05\x00\x00\x00', self.message.get_payload())

    def test_parse_from_bytes(self):
        data = b'\xA4\x06\x54\x08\x03\x00\xBA\x36\x00\x71'
        msg = get_proper_message(data)
        self.assertEquals(6, len(msg.get_payload()))

class SerialNumberMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = SerialNumberMessage()

    def test_get_setSerialNumber(self):
        self.message.setSerialNumber(b'\xFA\xFB\xFC\xFD')
        self.assertEqual(self.message.getSerialNumber(), b'\xFA\xFB\xFC\xFD')
        self.assertRaises(MessageError, self.message.setSerialNumber,
                          b'\xFF' * 8)

    def test_payload(self):
        self.message.setSerialNumber(b'\x01\x02\x03\x04')
        self.assertEqual(self.message.get_payload(), b'\x01\x02\x03\x04')

