#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase

from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

from tg_file_id.file_id import DocumentFileId


class TestDocumentFileId(TestCase):
    def test_from_file_id_sticker_old(self):
        file_id_str = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str)
        print(file_id)
        self.assertEqual(file_id_str, file_id.file_id, "PhotoFileId file_id.file_id field matches")
        self.assertEqual(2, file_id.version, "PhotoFileId file_id.version field matches")
        self.assertEqual(984697977903775939, file_id.id, "PhotoFileId file_id.id field matches")
        self.assertEqual(4, file_id.dc_id, "PhotoFileId file_id.dc_id field matches")
        self.assertEqual(DocumentFileId.TYPE_STICKER, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual(8, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('document', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('sticker', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        self.assertEqual(-8653026958495010306, file_id.access_hash, "PhotoFileId file_id.access_hash field matches")
    # end def

    def test_from_file_id_sticker_new(self):
        file_id_str = 'CAADBAADwwADmFmqDf6xBrPTReqHFgQ'
        file_id = DocumentFileId.from_file_id(file_id_str)
        print(file_id)
        self.assertEqual(file_id_str, file_id.file_id, "PhotoFileId file_id.file_id field matches")
        self.assertEqual(4, file_id.version, "PhotoFileId file_id.version field matches")  # diff
        self.assertEqual(984697977903775939, file_id.id, "PhotoFileId file_id.id field matches")
        self.assertEqual(4, file_id.dc_id, "PhotoFileId file_id.dc_id field matches")
        self.assertEqual(DocumentFileId.TYPE_STICKER, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual(8, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('document', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('sticker', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        self.assertEqual(-8653026958495010306, file_id.access_hash, "PhotoFileId file_id.access_hash field matches")
    # end def

    def test_to_file_id_sticker_new_to_new(self):
        file_id_str_new = 'CAADBAADwwADmFmqDf6xBrPTReqHFgQ'
        file_id_str_old = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str_new)
        self.assertEqual(4, file_id.version, "PhotoFileId file_id.version field matches")
        print(file_id)
        file_id_str = file_id.to_file_id(version=4, sub_version=22)
        self.assertEqual(file_id_str, file_id_str_new)
    # end def

    def test_to_file_id_sticker_new_to_old(self):
        file_id_str_new = 'CAADBAADwwADmFmqDf6xBrPTReqHFgQ'
        file_id_str_old = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str_new)
        self.assertEqual(4, file_id.version, "PhotoFileId file_id.version field matches")
        print(file_id)
        file_id_str = file_id.to_file_id(version=2)
        self.assertEqual(file_id_str, file_id_str_old)
    # end def

    def test_to_file_id_sticker_old_to_old(self):
        file_id_str_new = 'CAADBAADwwADmFmqDf6xBrPTReqHFgQ'
        file_id_str_old = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str_old)
        self.assertEqual(2, file_id.version, "PhotoFileId file_id.version field matches")
        print(file_id)
        file_id_str = file_id.to_file_id(version=2)
        self.assertEqual(file_id_str, file_id_str_old)
    # end def

    def test_to_file_id_sticker_old_to_new(self):
        file_id_str_new = 'CAADBAADwwADmFmqDf6xBrPTReqHFgQ'
        file_id_str_old = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str_old)
        self.assertEqual(2, file_id.version, "PhotoFileId file_id.version field matches")
        print(file_id)
        file_id_str = file_id.to_file_id(version=4, sub_version=22)
        self.assertEqual(file_id_str, file_id_str_new)
    # end def

    def test_swap_type_sticker_old_to_doc(self):
        file_id_str_old = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str_old)
        self.assertEqual(DocumentFileId.TYPE_STICKER, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('document', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('sticker', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        print(file_id)
        file_id.swap_type_sticker()
        self.assertEqual(DocumentFileId.TYPE_DOCUMENT, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('document', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('document', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
    # end def

    def test_change_type(self):
        file_id_str_old = 'CAADBAADwwADmFmqDf6xBrPTReqHAg'
        file_id = DocumentFileId.from_file_id(file_id_str_old)
        self.assertEqual(DocumentFileId.TYPE_STICKER, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('document', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('sticker', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
        file_id.change_type(DocumentFileId.TYPE_DOCUMENT)
        self.assertEqual(DocumentFileId.TYPE_DOCUMENT, file_id.type_id, "PhotoFileId file_id.type_id field matches")
        self.assertEqual('document', file_id.type_str, "PhotoFileId file_id.type_str field matches")
        self.assertEqual('document', file_id.type_detailed, "PhotoFileId file_id.type_detailed field matches")
    # end def

