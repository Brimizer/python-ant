"""
Extending on demo-03, implements an event callback we can use to process the
incoming data.

"""

import sys
import time

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from config import *


# A run-the-mill event listener
class HRMListener(event.EventCallback):
    def process(self, msg):
        print "HRMListener received message: {}".format(msg)
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            print 'Heart Rate:', ord(msg.payload[-1])
        if isinstance(msg, message.ChannelEventMessage):
            print 'ChannelEventMessage payload: '


# Initialize
stick = driver.USB2Driver(SERIAL, log=LOG, debug=DEBUG)
print(stick)
antnode = node.Node(stick)
print(antnode)

# dummy = driver.DummyDriver(SERIAL, log=LOG, debug=DEBUG)
# antnode = node.Node(dummy)
antnode.registerEventListener(HRMListener())

antnode.start()

# Setup channel
key = node.NetworkKey('N:ANT+', NETKEY)
antnode.setNetworkKey(0, key)
channel = antnode.getFreeChannel()
channel.name = 'C:HRM'
channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
channel.setID(120, 0, 0)
channel.setSearchTimeout(TIMEOUT_NEVER)
channel.setPeriod(8070)
channel.setFrequency(57)
channel.open()

print "Channel number:", channel.number

# Setup callback
# Note: We could also register an event listener for non-channel events by
# calling registerEventListener() on antnode rather than channel.
channel.registerCallback(HRMListener())


# Wait
print "Listening for HR monitor events (indefinitely)..."
try:
    while True:
        # msg = message.ChannelBroadcastDataMessage()
        # msg.setPayload("01234567")
        # stick.write(msg.encode())
        time.sleep(1)

except KeyboardInterrupt as e:
    print "Interrupted! Closing channel and exiting"
finally:
    # Shutdown
    channel.close()
    channel.unassign()
    antnode.stop()
