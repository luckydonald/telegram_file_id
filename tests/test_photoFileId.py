#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from base64 import b64decode
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

    def test_from_file_id_4_22_photo(self):
        file_id_str = 'AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABAEAAwIAA3gAA2uwAQABFgQ'
        file_id = PhotoFileId.from_file_id(file_id_str)
        print(file_id)
        reference_impl_result = {
            "version": 4, "subVersion": 22, "typeId": 2, "dc_id": 2, "hasReference": False, "hasWebLocation": False,
            "type": "photo", "id": 5262785666339678789, "access_hash": 6602691427396197215, "volume_id": 257017715,
            "secret": 0, "photosize_source": 1, "file_type": 2, "thumbnail_type": "x", "local_id": 110699
        }

        self.assertEqual(file_id_str, file_id.file_id, "PhotoFileId file_id.file_id field matches")
        self.assertEqual(4, file_id.version, "PhotoFileId file_id.version field matches")  # diff
        self.assertEqual(5262785666339678789, file_id.id, "PhotoFileId file_id.id field matches")
        self.assertEqual(2, file_id.dc_id, "PhotoFileId file_id.dc_id field matches")
        self.assertEqual(PhotoFileId.TYPE_PHOTO, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual(2, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('photo', file_id.type_generic, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('photo', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        self.assertEqual(6602691427396197215, file_id.access_hash, "PhotoFileId file_id.access_hash field matches")
        self.assertEqual(257017715, file_id.photosize.volume_id, "PhotoFileId file_id.location.volume_id field matches")
        self.assertEqual(110699, file_id.photosize.location_local_id, "PhotoFileId file_id.location.local_id field matches")  # changes
        # self.assertEqual(120, file_id.something, "PhotoFileId file_id.something field matches")  # diff
    # end def

    def test_from_file_id_4_30_photo(self):
        file_id_str = 'AgACAgIAAxkBAAIE2F-nHvTX7tX2Hg946DOPJWEahhgUAAI1sDEbClw4SX8n9AqBZEu9FpVJli4AAwEAAwIAA3gAA-YMBAABHgQ'
        reference_impl_result = {
            "version": 4, "subVersion": 30, "typeId": 2, "dc_id": 2, "hasReference": True, "hasWebLocation": False,
            "type": "photo", "fileReference": "AQAABNhfpx701+7V9h4PeOgzjyVhGoYYFA==", "id": 5276068161940205621,
            "access_hash": -4806637671890540673, "volume_id": 200089900310, "secret": 0, "photosize_source": 1,
            "file_type": 2, "thumbnail_type": "x", "local_id": 265446
        }

        file_id: PhotoFileId = PhotoFileId.from_file_id(file_id_str)
        print(file_id)
        self.assertEqual(file_id_str, file_id.file_id, "PhotoFileId file_id.file_id field matches")
        self.assertEqual(reference_impl_result['version'], file_id.version, "PhotoFileId file_id.version field matches")
        self.assertEqual(reference_impl_result['id'], file_id.id, "PhotoFileId file_id.id field matches")
        self.assertEqual(reference_impl_result['dc_id'], file_id.dc_id, "PhotoFileId file_id.dc_id field matches")
        self.assertEqual(reference_impl_result['typeId'], file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual(reference_impl_result['type'], file_id.type_generic, "PhotoFileId file_id.type_str field matches")
        self.assertEqual(PhotoFileId.TYPES[reference_impl_result['typeId']], file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        self.assertEqual(reference_impl_result['access_hash'], file_id.access_hash, "PhotoFileId file_id.access_hash field matches")
        self.assertEqual(reference_impl_result['volume_id'], file_id.photosize.volume_id, "PhotoFileId file_id.photosize.volume_id field matches")
        self.assertEqual(reference_impl_result['local_id'], file_id.photosize.location_local_id, "PhotoFileId file_id.photosize.local_id field matches")
        self.assertEqual(b64decode(reference_impl_result['fileReference']), file_id.file_reference, "PhotoFileId file_id.file_reference field matches")
        self.assertEqual(bool(reference_impl_result['fileReference']), file_id.has_reference, "PhotoFileId file_id.has_reference field matches")
    # end def
