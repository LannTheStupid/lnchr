from os import path, remove
import unittest

from appdirs import user_data_dir

import stream_launcher


class UserStatTest(unittest.TestCase):
    def setUp(self):
        self.stat = stream_launcher.UserStat('test.dat')
        self.filename = path.join(user_data_dir('stream_launcher', False), 'test.dat')

    def tearDown(self):
        try:
            remove(self.filename)
        except OSError:
            pass

    def test_empty_hash(self):
        self.assertEqual(str.format("{0}", self.stat), '[]')

    def test_add_usage(self):
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/holly_forve')

        self.assertEqual("{0}".format(self.stat),
                         "[('http://twitch.tv/holly_forve', 2), ('http://cybergame.tv/skymaybe', 1)]")

    def test_save(self):
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.save()
        self.assertTrue(path.isfile(self.filename))

    def test_load_from_non_existent(self):
        self.stat.load()

        self.assertTrue(str(self.stat), '{}')

    def test_load(self):
        with open(self.filename, 'w+') as f:
            f.write('{"http://twitch.tv/holly_forve": 2, "http://cybergame.tv/skymaybe": 1}')

        self.stat.load()
        self.assertTrue(str(self.stat), '{"http://twitch.tv/holly_forve": 2, "http://cybergame.tv/skymaybe": 1}')


if __name__ == '__main__':
    unittest.main()
