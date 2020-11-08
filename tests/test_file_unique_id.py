import unittest

from tg_file_id.file_id import FileId
from tg_file_id.file_unique_id import FileUniqueId


class MyTestCase(unittest.TestCase):
    def test_sticker(self):
        file_id_old = FileId.from_file_id('CAADAQADegAD997LEUiQZafDlhIeAg')
        file_id_new = FileId.from_file_id('CAACAgEAAx0CVgtngQACAuFfU1GY9wiRG7A7jlIBbP2yvAostAACegAD997LEUiQZafDlhIeGwQ')
        expected = 'AgADegAD997LEQ'
        self.assertEqual(expected, FileUniqueId.from_file_id(file_id_old).to_unique_id(), 'Old style file ID.')
        self.assertEqual(expected, FileUniqueId.from_file_id(file_id_new).to_unique_id(), 'Old style file ID.')


if __name__ == '__main__':
    unittest.main()
