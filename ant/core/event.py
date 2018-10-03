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

#
# Beware s/he who enters: uncommented, non unit-tested,
# don't-fix-it-if-it-ain't-broken kind of threaded code ahead.
#

import logging
import threading
import time

from ant.core.constants import *
import ant.core.message
from ant.core.exceptions import MessageError

MAX_ACK_QUEUE = 25
MAX_MSG_QUEUE = 25

logger = logging.getLogger(__name__)


def ProcessBuffer(buffer_):
    messages = []

    while True:
        # hf = Message()
        try:
            # msg = hf.get_handler(buffer_)
            msg = ant.core.message.get_proper_message(buffer_)
            if not msg:
                break
            buffer_ = buffer_[len(msg.get_payload()) + 4:]
            messages.append(msg)
        except MessageError as e:
            # print("MessageError for: {}".format(hf))
            if e.internal == "CHECKSUM":
                buffer_ = buffer_[ord(buffer_[1]) + 4:]
            else:
                logger.debug(e)
                break
    return (buffer_, messages,)


class EventPumper(object):
    def __init__(self):
        self._forced_buffer = []

    def force_buffer(self, byte_data=b''):
        self._forced_buffer.append(byte_data)

    def pump(self, evm):
        evm.pump_lock.acquire()
        evm.pump = True
        evm.pump_lock.release()

        go = True
        buffer_ = b''
        while go:
            evm.running_lock.acquire()
            if not evm.running:
                go = False
            evm.running_lock.release()

            if len(self._forced_buffer):
                buffer_ += self._forced_buffer[0]
                self._forced_buffer = [] if len(self._forced_buffer) == 1 else self._forced_buffer[1:]
            else:
                buffer_ += evm.driver.read(30)
            if len(buffer_) == 0:
                continue
            buffer_, messages = ProcessBuffer(buffer_)

            evm.callbacks_lock.acquire()
            # print("acquired callbacks_lock. messages: {}".format(messages))
            for message in messages:
                for callback in evm.callbacks:
                    # try:
                    callback.process(message)
                    # except Exception as e:
                    # pass

            evm.callbacks_lock.release()

            time.sleep(0.002)

        evm.pump_lock.acquire()
        evm.pump = False
        evm.pump_lock.release()



class EventCallback(object):
    def process(self, msg):
        pass


class AckCallback(EventCallback):
    def __init__(self, evm):
        self.evm = evm

    def process(self, msg):
        if isinstance(msg, ant.core.message.ChannelEventMessage):
            self.evm.ack_lock.acquire()
            self.evm.ack.append(msg)
            if len(self.evm.ack) > MAX_ACK_QUEUE:
                self.evm.ack = self.evm.ack[-MAX_ACK_QUEUE:]
            self.evm.ack_lock.release()


class MsgCallback(EventCallback):
    def __init__(self, evm):
        self.evm = evm

    def process(self, msg):
        self.evm.msg_lock.acquire()
        self.evm.msg.append(msg)
        if len(self.evm.msg) > MAX_MSG_QUEUE:
            self.evm.msg = self.evm.msg[-MAX_MSG_QUEUE:]
        self.evm.msg_lock.release()


class EventMachine(object):
    callbacks_lock = threading.Lock()
    running_lock = threading.Lock()
    pump_lock = threading.Lock()
    ack_lock = threading.Lock()
    msg_lock = threading.Lock()

    def __init__(self, driver):
        self.driver = driver
        self.callbacks = []
        self.running = False
        self.pump = False
        self.ack = []
        self.msg = []
        self.registerCallback(AckCallback(self))
        self.registerCallback(MsgCallback(self))
        self.event_thread = None
        self.event_pumper = EventPumper()

    def registerCallback(self, callback):
        self.callbacks_lock.acquire()
        if callback not in self.callbacks:
            self.callbacks.append(callback)
        self.callbacks_lock.release()

    def removeCallback(self, callback):
        self.callbacks_lock.acquire()
        if callback in self.callbacks:
            self.callbacks.remove(callback)
        self.callbacks_lock.release()

    def waitForAck(self, msg):
        while True:
            self.ack_lock.acquire()
            for emsg in self.ack:
                # print("Original msg id:{:02X} received msg id:{:02X}".format(msg.msg_id,
                #                                                              emsg.getMessageID()))
                if msg.msg_id != emsg.getMessageID():
                    continue
                self.ack.remove(emsg)
                self.ack_lock.release()
                return emsg.getMessageCode()
            self.ack_lock.release()
            time.sleep(0.002)

    def waitForMessage(self, class_):
        while True:
            self.msg_lock.acquire()
            for emsg in self.msg:
                if not isinstance(emsg, class_):
                    continue
                self.msg.remove(emsg)
                self.msg_lock.release()
                return emsg
            self.msg_lock.release()
            time.sleep(0.002)

    def start(self, driver=None):
        self.running_lock.acquire()

        if self.running:
            self.running_lock.release()
            return
        self.running = True
        if driver is not None:
            self.driver = driver

        self.event_thread = threading.Thread(target=self.event_pumper.pump, args=(self,))
        self.event_thread.start()
        while True:
            self.pump_lock.acquire()
            if self.pump:
                self.pump_lock.release()
                break
            self.pump_lock.release()
            time.sleep(0.001)

        self.running_lock.release()

    def stop(self):
        self.running_lock.acquire()

        if not self.running:
            self.running_lock.release()
            return
        self.running = False
        self.running_lock.release()

        while True:
            self.pump_lock.acquire()
            if not self.pump:
                self.pump_lock.release()
                break
            self.pump_lock.release()
            time.sleep(0.001)

        self.event_thread.join()
