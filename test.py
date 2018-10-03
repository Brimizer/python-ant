import time

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import better_log
from ant.plus import NETWORK_KEY  # Use the ANT+ Network Key instead of the default 'Public' key
from ant.core.message import *
from ant.core.canned import CannedDriver


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
        logger.info(">>> Listener received message: {}".format(msg))
        if isinstance(msg, CapabilitiesMessage):
            capabilities = Capabilities(msg)
            logger.info("Available Capabilities: {}".format(capabilities))
        elif isinstance(msg, SerialNumberMessage):
            logger.info("Serial #: {}".format(encode_bytes(msg.getSerialNumber(), separator=' ')))
        # if isinstance(msg, ChannelBroadcastDataMessage):
        #     print 'Heart Rate:', ord(msg.payload[-1])
        if isinstance(msg, ChannelEventMessage):
            msg_code = msg.getMessageCode()
            if msg_code != RESPONSE_NO_ERROR:
                logger.error("Error response: {:02X}".format(msg_code))


# stick = driver.USB2Driver(SERIAL, log=LOG, debug=DEBUG)

stick = CannedDriver(SERIAL, log=LOG, debug=DEBUG)

antnode = node.Node(stick)
antnode.registerEventListener(Listener())

serial_response = CapabilitiesMessage(max_channels=0x05, max_nets=0x01)
antnode.respond_with(serial_response)
antnode.start()

# # Set network key
key = node.NetworkKey('N:ANT+', NETWORK_KEY)
antnode.respond_with(ChannelEventMessage(message_id=MESSAGE_NETWORK_KEY))
antnode.setNetworkKey(0, key)

#
# # Get the first unused channel. Returns an instance of the node.Channel class.
channel = antnode.getFreeChannel()
#
# # Let's give our channel a nickname
# channel.name = 'C:HRM'
#
# # Initialize it as a receiving channel using our network key
# channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
#
# # Now set the channel id for pairing with an ANT+ HR monitor
# channel.setID(120, 0, 0)
#
# # Listen forever and ever (not really, but for a long time)
# channel.setSearchTimeout(TIMEOUT_NEVER)
#
# # We want a ~4.06 Hz transmission period
# channel.setPeriod(8070)
#
# # And ANT frequency 57
# channel.setFrequency(57)
#
# # Time to go live
antnode.respond_with(ChannelEventMessage(message_id=MESSAGE_CHANNEL_OPEN))
channel.open()

# Request the serial number just for fun.
# serial_msg = ChannelRequestMessage(message_id=MESSAGE_SERIAL_NUMBER)
# channel.write(serial_msg)


print("Listening for HR monitor events ({} seconds)...".format(LISTEN_DURATION))

try:
    time.sleep(LISTEN_DURATION)
    antnode.respond_with(ChannelBroadcastDataMessage())

finally:
    pass

# Shutdown channel
antnode.respond_with(ChannelEventMessage(message_id=MESSAGE_CHANNEL_CLOSE))
antnode.respond_with(ChannelEventMessage(message_id=MESSAGE_CHANNEL_CLOSE, message_code=EVENT_CHANNEL_CLOSED))
channel.close()

antnode.respond_with(ChannelEventMessage(message_id=MESSAGE_CHANNEL_UNASSIGN))
channel.unassign()


# Shutdown
antnode.respond_with(NotificationStartupMessage())
antnode.stop()

