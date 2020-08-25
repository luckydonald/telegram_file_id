#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase

from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

from tg_file_id.file_id import PhotoFileId


class TestPhotoFileId(TestCase):
    def test_from_file_id_old(self):
        file_id_str = 'AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABA0Pma0G3xt2bLABAAEC'
        file_id = PhotoFileId.from_file_id(file_id_str)
        print(file_id)
        self.assertEqual(file_id_str, file_id.file_id, "PhotoFileId file_id.file_id field matches")
        self.assertEqual(2, file_id.version, "PhotoFileId file_id.version field matches")
        self.assertEqual(5262785666339678789, file_id.id, "PhotoFileId file_id.id field matches")
        self.assertEqual(2, file_id.dc_id, "PhotoFileId file_id.dc_id field matches")
        self.assertEqual(PhotoFileId.TYPE_PHOTO, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual(2, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('photo', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('photo', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        self.assertEqual(6602691427396197215, file_id.access_hash, "PhotoFileId file_id.access_hash field matches")
        self.assertEqual(257017715, file_id.location.volume_id, "PhotoFileId file_id.location.volume_id field matches")
        self.assertEqual(8510641140621971213, file_id.location.secret, "PhotoFileId file_id.location.secret field matches")
        self.assertEqual(110700, file_id.location.local_id, "PhotoFileId file_id.location.local_id field matches")
        self.assertEqual(None, file_id.something, "PhotoFileId file_id.something field matches")  # diff
    # end def

    def test_from_file_id_new(self):
        file_id_str = 'AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABAEAAwIAA3gAA2uwAQABFgQ'
        file_id = PhotoFileId.from_file_id(file_id_str)
        print(file_id)
        self.assertEqual(file_id_str, file_id.file_id, "PhotoFileId file_id.file_id field matches")
        self.assertEqual(4, file_id.version, "PhotoFileId file_id.version field matches")  # diff
        self.assertEqual(5262785666339678789, file_id.id, "PhotoFileId file_id.id field matches")
        self.assertEqual(2, file_id.dc_id, "PhotoFileId file_id.dc_id field matches")
        self.assertEqual(PhotoFileId.TYPE_PHOTO, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual(2, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('photo', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('photo', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        self.assertEqual(6602691427396197215, file_id.access_hash, "PhotoFileId file_id.access_hash field matches")
        self.assertEqual(257017715, file_id.location.volume_id, "PhotoFileId file_id.location.volume_id field matches")
        self.assertEqual(8589934593, file_id.location.secret, "PhotoFileId file_id.location.secret field matches")  # changes
        self.assertEqual(110699, file_id.location.local_id, "PhotoFileId file_id.location.local_id field matches")  # changes
        self.assertEqual(120, file_id.something, "PhotoFileId file_id.something field matches")  # diff
    # end def
