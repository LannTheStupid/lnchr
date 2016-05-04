
import unittest
import unittest.mock

from datetime import date
from pathlib import Path, PurePath

from application_local_file import Nicknames

from recorder_file_handler import file_name_generator
from recorder_file_handler import get_file_name

from stream_recorder import parse_streamer_url, next_try

class RecordFileNameGeneratorTestCase(unittest.TestCase):

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    def test_get_two_filenames(self, mock_date):
        file_name_gen = file_name_generator('fr0st', 10)
        mock_date.today.return_value = date(2009, 8, 31)
        self.assertEqual(next(file_name_gen), 'fr0st.2009.08.31.1.ts')
        self.assertEqual(next(file_name_gen), 'fr0st.2009.08.31.2.ts')

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    def test_get_last_filename(self, mock_date):
        mock_date.today.return_value = date(1980, 7, 5)
        for fname in file_name_generator('fido', 10):
            pass
        self.assertEqual(fname, 'fido.1980.07.05.9.ts')

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    def test_filenames_for_number_of_attempts_greater_than_10_should_have_leading_zeroes(self, mock_date):
        mock_date.today.return_value = date(1980, 7, 5)
        for fname in file_name_generator('fido', 45):
            pass
        self.assertEqual(fname, 'fido.1980.07.05.99.ts')
        file_name_gen = file_name_generator('fido', 105)
        self.assertEqual(next(file_name_gen), 'fido.1980.07.05.001.ts')
        self.assertEqual(next(file_name_gen), 'fido.1980.07.05.002.ts')

class GetFileNameTestCase(unittest.TestCase):

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    @unittest.mock.patch("recorder_file_handler.Path.is_file", autospec=True)
    def test_gen_file_name_iterates_till_the_first_non_existent_file(self, mock_path, mock_date):
        mock_date.today.return_value = date(2009, 8, 31)
        mock_path.side_effect = lambda x: not x.name == 'fr0st.2009.08.31.44.ts'
        self.assertEqual(next(get_file_name(PurePath('c:\\tmp'), 'fr0st', 50)), 'c:\\tmp\\fr0st.2009.08.31.44.ts')

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    @unittest.mock.patch("recorder_file_handler.Path.is_file", autospec=True)
    def test_gen_file_name_never_increases_the_counter_if_the_file_does_not_exist(self, mock_path, mock_date):
        mock_date.today.return_value = date(2009, 8, 31)
        mock_path.return_value = False
        self.assertEqual(next(get_file_name(PurePath('c:\\tmp'), 'fr0st')), 'c:\\tmp\\fr0st.2009.08.31.1.ts')
        self.assertEqual(next(get_file_name(PurePath('c:\\tmp'), 'fr0st')), 'c:\\tmp\\fr0st.2009.08.31.1.ts')
        self.assertEqual(next(get_file_name(PurePath('c:\\tmp'), 'fr0st')), 'c:\\tmp\\fr0st.2009.08.31.1.ts')


class GetURLByAliasOrParseURLTestCase(unittest.TestCase):

    @unittest.mock.patch('stream_recorder.Nicknames', autospec=True)
    def test_if_alias_is_given_and_exists_then_URL_is_defined_by_alias(self, mock_nicknames):
        mock_nicknames.find.return_value = True
        mock_nicknames.get.return_value = 'http://twitch.tv/bushwackerua'
        (alias, url) = parse_streamer_url('bush', mock_nicknames)
        self.assertEqual(alias, 'bush')
        self.assertEqual(url, 'http://twitch.tv/bushwackerua')

    @unittest.mock.patch('stream_recorder.Nicknames', autospec=True)
    def test_if_URL_is_given_then_use_this_URL_and_deduce_the_alias_from_it(self, mock_nicknames):
        mock_nicknames.find.return_value = False
        (alias, url) = parse_streamer_url('http://goodgame.ru/drewoko/', mock_nicknames)
        self.assertEqual(alias, 'drewoko')
        self.assertEqual(url, 'http://goodgame.ru/drewoko/')

    @unittest.mock.patch('stream_recorder.Nicknames', autospec=True)
    def test_if_alias_is_given_and_does_not_exist_then_exit(self, mock_nicknames):
        mock_nicknames.find.return_value = False
        (alias, url) = parse_streamer_url('drewoko', mock_nicknames)
        self.assertIsNone(alias)


class AttemptsAndFileNameGeneratorTestCase(unittest.TestCase):

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    @unittest.mock.patch("recorder_file_handler.Path.is_file", autospec=True)
    def test_that_generator_stops_when_the_number_of_attempts_is_reached(self, mock_path, mock_date):
        mock_date.today.return_value = date(2009, 9, 1)
        mock_path.return_value = False
        for (attempt, file_name) in next_try(15, PurePath('c:\\tmp\\encode'), 'drewoko'):
            pass
        self.assertEqual(attempt + 1, 15)
        self.assertEqual(file_name, str(Path('c:', '\\tmp\\encode', 'drewoko.2009.09.01.01.ts')))