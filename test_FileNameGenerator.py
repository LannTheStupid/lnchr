
import unittest
import unittest.mock

from datetime import date

from recorder_file_handler import file_name_generator

class RecordFileNameGeneratorTestCase(unittest.TestCase):

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    def test_get_two_filenames(self, mock_date):
        file_name_gen = file_name_generator('fr0st')
        mock_date.today.return_value = date(2009, 8, 31)
        self.assertEqual(next(file_name_gen), 'fr0st.2009.08.31.1.ts')
        self.assertEqual(next(file_name_gen), 'fr0st.2009.08.31.2.ts')

    @unittest.mock.patch("recorder_file_handler.date", autospec=True)
    def test_get_last_filename(self, mock_date):
        mock_date.today.return_value = date(1980, 7, 5)
        for fname in file_name_generator('fido'):
            pass
        self.assertEqual(fname, 'fido.1980.07.05.9.ts')
