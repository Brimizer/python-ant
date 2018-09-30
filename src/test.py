import time

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import better_log
from ant.plus import NETWORK_KEY  # Use the ANT+ Network Key instead of the default 'Public' key
from ant.core.message import *


import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DEBUG = True

LOG = better_log.LogWriter('shared.log')

SERIAL = '/dev/ttyUSB0'


LISTEN_DURATION = 5


# A run-the-mill event listener
class Listener(event.EventCallback):
    def process(self, msg):
        logger.debug(">>> Listener received message: {}".format(msg))
        if isinstance(msg, CapabilitiesMessage):
            capabilities = Capabilities(msg)
            logger.debug("Available Capabilities: {}".format(capabilities))
        elif isinstance(msg, SerialNumberMessage):
            logger.info("Serial #: {}".format(int(msg.getSerialNumber())))
        # if isinstance(msg, ChannelBroadcastDataMessage):
        #     print 'Heart Rate:', ord(msg.payload[-1])
        # if isinstance(msg, ChannelEventMessage):
        #     print 'ChannelEventMessage payload: '


stick = driver.USB2Driver(SERIAL, log=LOG, debug=DEBUG)

antnode = node.Node(stick)
antnode.registerEventListener(Listener())

antnode.start()

# Set network key
key = node.NetworkKey('N:ANT+', NETWORK_KEY)
antnode.setNetworkKey(0, key)

# Get the first unused channel. Returns an instance of the node.Channel class.
channel = antnode.getFreeChannel()

# Let's give our channel a nickname
channel.name = 'C:HRM'

# Initialize it as a receiving channel using our network key
channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)

# Now set the channel id for pairing with an ANT+ HR monitor
channel.setID(120, 0, 0)

# Listen forever and ever (not really, but for a long time)
channel.setSearchTimeout(TIMEOUT_NEVER)

# We want a ~4.06 Hz transmission period
channel.setPeriod(8070)

# And ANT frequency 57
channel.setFrequency(57)

# Time to go live
channel.open()

# Request the serial number just for fun.
serial_msg = ChannelRequestMessage(message_id=MESSAGE_SERIAL_NUMBER)
channel.write(serial_msg)

print "Listening for HR monitor events ({} seconds)...".format(LISTEN_DURATION)
time.sleep(LISTEN_DURATION)

# Shutdown channel
channel.close()
channel.unassign()

# Shutdown
antnode.stop()
