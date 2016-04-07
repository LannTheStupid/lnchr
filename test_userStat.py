from os import path, remove
import unittest

from appdirs import user_data_dir

import application_local_file


class UserStatTest(unittest.TestCase):
    def setUp(self):
        self.stat = application_local_file.UserStat('test_app', 'test.dat')
        self.filename = path.join(user_data_dir('test_app', False), 'test.dat')

    def tearDown(self):
        try:
            remove(self.filename)
        except OSError:
            pass

    def test_empty_hash(self):
        self.assertEqual(str.format("{0}", self.stat), '{}')

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
        self.assertEqual(str(self.stat), "[('http://twitch.tv/holly_forve', 2), ('http://cybergame.tv/skymaybe', 1)]")

    def test_filter1(self):
        self.stat.add_usage('http://twitch.tv/adybah')
        self.stat.add_usage('http://twitch.tv/belkao_o')
        self.stat.add_usage('http://cybergame.tv/cuddlez')
        self.stat.add_usage('http://twitch.tv/belkao_o')
        self.stat.add_usage('http://twitch.tv/manana')

        filtered = self.stat.fltr(lambda key, value: value > 1)
        self.assertEqual(str(self.stat), "[('http://twitch.tv/belkao_o', 2)]")
        self.assertEqual(filtered, 3)

    def test_filter2(self):
        self.stat.add_usage('http://twitch.tv/belkao_o')
        self.stat.add_usage('http://cybergame.tv/adybah')
        self.stat.add_usage('http://twitch.tv/skymaybe')
        self.stat.add_usage('http://twitch.tv/belkao_o')
        self.stat.add_usage('http://cybergame.tv/skymaybe')
        self.stat.add_usage('http://goodgame.ru/channel/skymaybe/')

        filtered = self.stat.fltr(lambda key, value: 'skymaybe' not in key)

        self.assertEqual(str(self.stat), "[('http://twitch.tv/belkao_o', 2), ('http://cybergame.tv/adybah', 1)]")
        self.assertEqual(filtered, 3)


if __name__ == '__main__':
    unittest.main()
