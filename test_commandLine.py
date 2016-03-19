from argparse import ArgumentError

from stream_launcher import create_parser

import unittest


class CommandLineTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = create_parser()

    def test_empty_string(self):
        parsed = self.parser.parse_args([])

        self.assertRaises(ArgumentError)

    def test_stattistics(self):
        parsed = self.parser.parse_args(['-s', 'http://twitch.tv/belkao_o', 'video'])

        self.assertEqual(parsed.streamer, 'http://twitch.tv/belkao_o')

    def test_clear_stat(self):
        parsed = self.parser.parse_args(['-c', '2'])
        self.assertEqual(parsed.clear, '2')
        parsed = self.parser.parse_args(['-c'])
        self.assertEqual(parsed.clear, '1')

    def test_regression(self):
        parsed = self.parser.parse_args(['http://twitch.tv/holly_forve'])
        self.assertFalse(parsed.mode)
        self.assertEqual(parsed.streamer, 'http://twitch.tv/holly_forve')
        parsed = self.parser.parse_args(['http://twitch.tv/holly_forve', 'video'])
        self.assertEqual(parsed.streamer, 'http://twitch.tv/holly_forve')

if __name__ == '__main__':
    unittest.main()
