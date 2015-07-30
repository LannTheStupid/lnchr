from stream_launcher import UserStat
from appdirs import user_data_dir

import os
import unittest

class UserStatTest(unittest.TestCase):
    def setUp(self):
        self.stat = UserStat()

    def test_empty_hash(self):
        self.assertEqual(self.stat.toString(), '{}')

    def test_add_usage(self):
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/holly_forve')

        self.assertEqual(self.stat.toString(),
                         "{'http://cybergame.tv/skymaybe': 1, 'http://twitch.tv/holly_forve': 2}")

    def test_save(self):
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.save()

        

        
if __name__ == '__main__':
    unittest.main()
