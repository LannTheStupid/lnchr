import os
import unittest

from appdirs import user_data_dir

from stream_launcher import UserStat


class UserStatTest(unittest.TestCase):
    def setUp(self):
        self.stat = UserStat()
        self.filename = os.path.join(user_data_dir('stream_launcher', False), 'most_used.dat')

    def tearDown(self):
        try:
            os.remove(self.filename)
        except OSError:
            pass

    def test_empty_hash(self):
        self.assertEqual(self.stat.toString(), '[]')

    def test_add_usage(self):
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/holly_forve')

        self.assertEqual(self.stat.toString(),
                         "[('http://twitch.tv/holly_forve', 2), ('http://cybergame.tv/skymaybe', 1)]")

    def test_save(self):
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/holly_forve')
        self.stat.save()
        self.assertTrue(os.path.isfile(self.filename))

    def test_load_from_non_existent(self):
        self.stat.load()

        self.assertTrue(self.stat.toString(), '{}')

    def test_load(self):
        with open(self.filename, 'w+') as f:
            f.write('{"http://twitch.tv/holly_forve": 2, "http://cybergame.tv/skymaybe": 1}')

        self.stat.load()
        self.assertTrue(self.stat.toString(), '{"http://twitch.tv/holly_forve": 2, "http://cybergame.tv/skymaybe": 1}')


if __name__ == '__main__':
    unittest.main()
