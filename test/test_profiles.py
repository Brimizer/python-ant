import unittest
from ant.plus.profiles import *

class ProfileTest(unittest.TestCase):
    def setUp(self):
        self.profile = Profile()

    def test_profile(self):
        self.assertEqual(0x00, self.profile.channel_type)
        self.assertEqual(NETWORK_KEY, self.profile.network_key)
        self.assertEqual(57, self.profile.rf_channel_frequency)
        self.assertEqual(0x00, self.profile.transmission_type)
        self.assertEqual(0x0B, self.profile.device_type)
        self.assertEqual(0x00, self.profile.device_number)
        self.assertEqual(8182, self.profile.channel_period)
        self.assertEqual(30, self.profile.search_timeout)



