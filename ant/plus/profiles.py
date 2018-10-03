
from ant.plus import NETWORK_KEY

class Profile(object):
    def __init__(self,
                 channel_type=0x00,
                 network_key=NETWORK_KEY,
                 rf_channel_frequency=57,
                 transmission_type=0x00,
                 device_type=0x0B,
                 device_number=0,
                 channel_period=8182,
                 search_timeout=30):
        self.channel_type = channel_type
        self.network_key = network_key
        self.rf_channel_frequency = rf_channel_frequency
        self.transmission_type = transmission_type
        self.device_type = device_type
        self.device_number = device_number
        self.channel_period = channel_period
        self.search_timeout = search_timeout

class BicyclePower(Profile):
    def __init__(self):
        super(BicyclePower).__init__(channel_type=0x00,
                 network_key=NETWORK_KEY,
                 rf_channel_frequency=57,
                 transmission_type=0x00,
                 device_type=0x0B,
                 device_number=0,
                 channel_period=8182,
                 search_timeout=30)