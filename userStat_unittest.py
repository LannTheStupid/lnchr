from os.path import exists
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
        self.assertTrue(os.path.isfile(os.path.join(user_data_dir('stream_launcher', False), 'most_used.dat')))

        
    def test_load(self):
        with open(os.path.join(user_data_dir('stream_launcher', False), 'most_used.dat'), 'w+') as f:
            f.write('{"http://twitch.tv/holly_forve": 2, "http://cybergame.tv/skymaybe": 1}')

        self.stat.load()
        self.assertTrue(self.stat.toString(), '{"http://twitch.tv/holly_forve": 2, "http://cybergame.tv/skymaybe": 1}')
        
if __name__ == '__main__':
    unittest.main()
