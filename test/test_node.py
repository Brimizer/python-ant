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

from ant.core.node import *
from ant.core.message import *

from ant.plus import NETWORK_KEY

# TODO

# class TestNetworkKey(unittest.TestCase):
#     def setUp(self):
#         self.network_key = NetworkKey(name='ANT+', key=NETWORK_KEY)
#         self.message = NetworkKeyMessage(key=self.network_key.key)
#
#     def test_get_setPayload(self):
#         self.assertRaises(MessageError, self.message.set_payload,
#                           b'\xFF' * 15)
#         self.message.set_payload(b'\x11' * 5)
#         self.assertEqual(self.message.get_payload(), b'\x11' * 5)
#
#     def test_get_setType(self):
#         def set(i): self.message.msg_id = i
#         self.assertRaises(MessageError, set, -1)
#         self.assertRaises(MessageError, set, 300)
#         self.message.msg_id = 0x23
#         self.assertEqual(self.message.msg_id, 0x23)
#
#     def test_getChecksum(self):
#         self.message = Message(msg_id=MESSAGE_SYSTEM_RESET, payload=b'\x00')
#         self.assertEqual(self.message.get_checksum(), 0xEF)
#         self.message = Message(msg_id=MESSAGE_CHANNEL_ASSIGN,
#                                payload=b'\x00' * 3)
#         self.assertEqual(self.message.get_checksum(), 0xE5)
#
#     def test_getSize(self):
#         self.message.set_payload(b'\x11' * 7)
#         self.assertEqual(self.message.get_size(), 11)
#
#     def test_encode(self):
#         self.message = Message(msg_id=MESSAGE_CHANNEL_ASSIGN,
#                                payload=b'\x00' * 3)
#         self.assertEqual(self.message.encode(),
#                          b'\xA4\x03\x42\x00\x00\x00\xE5')
#
#     def test_decode(self):
#         self.assertRaises(MessageError, self.message.decode,
#                           b'\xA5\x03\x42\x00\x00\x00\xE5')
#         self.assertRaises(MessageError, self.message.decode,
#                           b'\xA4\x14\x42' + (b'\x00' * 20) + b'\xE5')
#         self.assertRaises(MessageError, self.message.decode,
#                           b'\xA4\x03\x42\x01\x02\xF3\xE5')
#         self.assertEqual(7, self.message.decode(b'\xA4\x03\x42\x00\x00\x00\xE5'))
#         self.assertEqual(MESSAGE_CHANNEL_ASSIGN, self.message.msg_id)
#         self.assertEqual(b'\x00' * 3, self.message.get_payload())
#         self.assertEqual(0xE5, self.message.get_checksum())
#
#     def test_getHandler(self):
#         msg = get_proper_message(b'\xA4\x03\x42\x00\x00\x00\xE5')
#         self.assertTrue(isinstance(msg, ChannelAssignMessage))
#         self.assertRaises(MessageError, get_proper_message,
#                           b'\xA4\x03\xFF\x00\x00\x00\xE5')
#         self.assertRaises(MessageError, get_proper_message,
#                           b'\xA4\x03\x42')
#         self.assertRaises(MessageError, get_proper_message,
#                           b'\xA4\x05\x42\x00\x00\x00\x00')
