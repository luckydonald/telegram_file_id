#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
from base64 import b64decode

from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from tg_file_id.file_id import FileId, PhotoFileId
from tg_file_id.file_unique_id import FileUniqueId

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


try:
    from somewhere import API_KEY
except ImportError:
    API_KEY = os.getenv('API_KEY', os.getenv('TG_API_KEY', None))
# end if

try:
    from somewhere import CHAT_ID
except ImportError:
    CHAT_ID = os.getenv('CHAT_ID', os.getenv('TG_CHAT_ID', None))  # -1001377646352: https://t.me/joinchat/AKOLAhGYNdvTEwPnp2vUYQ
# end if
if CHAT_ID:
    CHAT_ID = int(CHAT_ID)
# end if


# noinspection DuplicatedCode
class MyTestCase(unittest.TestCase):
    def test_a_bunch_of_file_ids(self):
        file_ids = ['CAADBAADwwADmFmqDf6xBrPTReqHFgQ', 'CAACAgQAAxkBAAIC4l9CWDGzVUcDejU0TETLWbOdfsCoAALDAAOYWaoN_rEGs9NF6ocbBA', 'CAADBAADwwADmFmqDf6xBrPTReqHAg']
        for file_id in file_ids:
            with self.subTest(f'file_id: {file_id}'):
                file = FileId.from_file_id(file_id)
                self.assertEqual('AgADwwADmFmqDQ', FileUniqueId.from_file_id(file).to_unique_id())
            # end with
        # end for
    # end def

    def test_send_sticker(self):
        original_file_id = 'CAACAgIAAx0EUh03EAADDl-oWPT0MOIQZ93aktaAu8hU8rPEAAK2BgACAoujAAFGAUWZ6DSbtR4E'
        try:
            from pytgbot import Bot
        except ImportError:
            return self.fail('pytgbot dependency missing')
        # end try

        if not API_KEY:
            return self.fail('API_KEY not set')
        # end if
        if not CHAT_ID:
            return self.fail('CHAT_ID not set')
        # end if

        bot = Bot(API_KEY)

        msg = bot.send_sticker(chat_id=CHAT_ID, sticker=original_file_id)
        print(msg)

        sticker_file = FileId.from_file_id(msg.sticker.file_id)
        sticker_file_unique_id = FileUniqueId.from_file_id(msg.sticker.file_id).to_unique_id()
        self.assertEqual(msg.sticker.file_unique_id, sticker_file_unique_id)
        self.assertEqual(FileId.TYPE_STICKER, sticker_file.type_id)
        self.assertEqual('sticker', sticker_file.type_detailed)
        self.assertEqual('document', sticker_file.type_generic)
        self.assertEqual(sticker_file.version, FileId.MAX_VERSION[0], 'sticker should be supported max (sub_)version')
        self.assertEqual(sticker_file.sub_version, FileId.MAX_VERSION[1], 'sticker should be supported max (sub_)version')
        self.assertEqual(46033261910034102, sticker_file.id)
        self.assertEqual(-5360632757845950138, sticker_file.access_hash)
        self.assertEqual(2, sticker_file.dc_id)
        # self.assertEqual(b64decode('BFIdNxAAAAAOX6hY9PQw4hBn3dqS1oC7yFTys8Q='), sticker_file.file_reference)

        thumb_file = FileId.from_file_id(msg.sticker.thumb.file_id)
        # 'AAMCAgADGQMAAQHUiF-oKLkvxChbEROPTTw6Aagft9bPAAK2BgACAoujAAFGAUWZ6DSbtUufgioABAEAB20AAwpQAAIeBA'
        thumb_file_unique_id = FileUniqueId.from_file_id(thumb_file).to_unique_id()
        self.assertEqual(msg.sticker.thumb.file_unique_id, thumb_file_unique_id)
        self.assertEqual(FileId.TYPE_THUMBNAIL, thumb_file.type_id)
        self.assertEqual('thumbnail', thumb_file.type_detailed)
        self.assertEqual('photo', thumb_file.type_generic)
        self.assertEqual(sticker_file.version, thumb_file.version)
        self.assertEqual(sticker_file.sub_version, thumb_file.sub_version)
        self.assertEqual(sticker_file.id, thumb_file.id)
        self.assertEqual(sticker_file.access_hash, thumb_file.access_hash)
        self.assertEqual(sticker_file.dc_id, thumb_file.dc_id)
        self.assertEqual(sticker_file.file_reference, thumb_file.file_reference)
        # PhotosizeSource
        self.assertIsInstance(thumb_file.photosize, PhotoFileId.PhotosizeSource)
        self.assertEqual(20490, thumb_file.photosize.location_local_id)
        self.assertEqual(713203531, thumb_file.photosize.volume_id)
        self.assertEqual(PhotoFileId.PHOTOSIZE_SOURCE_THUMBNAIL, thumb_file.photosize.type_id)
        # PhotosizeSourceThumbnail
        self.assertIsInstance(thumb_file.photosize, PhotoFileId.PhotosizeSourceThumbnail)
        self.assertEqual(b'm', thumb_file.photosize.thumbnail_type)
        self.assertEqual(FileId.TYPE_THUMBNAIL, thumb_file.photosize.file_type)
    # end if

    def test_get_chat_picture(self):
        try:
            from pytgbot import Bot
        except ImportError:
            return self.fail('pytgbot dependency missing')
        # end try

        if not API_KEY:
            return self.fail('API_KEY not set')
        # end if
        if not CHAT_ID:
            return self.fail('CHAT_ID not set')
        # end if

        bot = Bot(API_KEY)

        chat = bot.get_chat(chat_id=CHAT_ID)
        print(chat)
        if not chat.photo:
            return self.skipTest('Test chat has no picture')
        # end if

        # big picture

        big_file = FileId.from_file_id(chat.photo.big_file_id)  # 'AQADAgATqfDdly4AAwMAA4siCOX_____AAhKowIAAR4E'

        big_file_unique_id = FileUniqueId.from_file_id(chat.photo.big_file_id).to_unique_id()
        self.assertEqual(chat.photo.big_file_unique_id, big_file_unique_id)

        self.assertEqual(FileId.TYPE_PROFILE_PHOTO, big_file.type_id)
        self.assertEqual('profile picture', big_file.type_detailed)
        self.assertEqual('photo', big_file.type_generic)
        self.assertEqual(big_file.version, FileId.MAX_VERSION[0], 'sticker should be supported max (sub_)version')
        self.assertEqual(big_file.sub_version, FileId.MAX_VERSION[1], 'sticker should be supported max (sub_)version')
        self.assertEqual(0, big_file.id)
        self.assertEqual(0, big_file.access_hash)
        self.assertEqual(False, big_file.has_reference)
        self.assertEqual(False, big_file.has_web_location)

        self.assertIsInstance(big_file.photosize, PhotoFileId.PhotosizeSource)
        # self.assertEqual(200116400297, big_file.photosize.volume_id)
        # self.assertEqual(172874, big_file.photosize.location_local_id)

        self.assertEqual(PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_BIG, big_file.photosize.type_id)
        self.assertIsInstance(big_file.photosize, PhotoFileId.PhotosizeSourceDialogPhotoBig)
        self.assertEqual(CHAT_ID, big_file.photosize.dialog_id)
        self.assertEqual(0, big_file.photosize.dialog_access_hash)

        # small picture

        small_file = FileId.from_file_id(chat.photo.small_file_id)  # 'AQADAgATqfDdly4AAwIAA4siCOX_____AAhIowIAAR4E'
        small_file_unique_id = FileUniqueId.from_file_id(chat.photo.small_file_id).to_unique_id()
        self.assertEqual(chat.photo.small_file_unique_id, small_file_unique_id)

        self.assertEqual(FileId.TYPE_PROFILE_PHOTO, small_file.type_id)
        self.assertEqual(big_file.type_detailed, small_file.type_detailed)
        self.assertEqual(big_file.type_generic, small_file.type_generic)
        self.assertEqual(big_file.version, small_file.version)
        self.assertEqual(big_file.sub_version, small_file.sub_version)
        self.assertEqual(big_file.id, small_file.id)
        self.assertEqual(big_file.access_hash, small_file.access_hash)
        self.assertEqual(big_file.has_reference, small_file.has_reference)
        self.assertEqual(big_file.has_web_location, small_file.has_web_location)

        self.assertIsInstance(small_file.photosize, PhotoFileId.PhotosizeSource)
        self.assertEqual(big_file.photosize.volume_id, small_file.photosize.volume_id)
        # self.assertEqual(172872, small_file.photosize.location_local_id)

        self.assertEqual(PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL, small_file.photosize.type_id)
        self.assertIsInstance(small_file.photosize, PhotoFileId.PhotosizeSourceDialogPhotoSmall)
        self.assertEqual(CHAT_ID, small_file.photosize.dialog_id)
        self.assertEqual(big_file.photosize.dialog_access_hash, small_file.photosize.dialog_access_hash)
    # end if
# end class
