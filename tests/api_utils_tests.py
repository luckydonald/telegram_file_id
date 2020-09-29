import struct
import unittest
from codecs import decode, encode

from luckydonaldUtils.encoding import to_binary

from tg_file_id.file_id import (
    FileId, rle_decode, base64url_decode, DocumentFileId, PhotoFileId, base64url_encode,
    rle_encode,
)
from tg_file_id.file_unique_id import FileUniqueId


class MyTestCase(unittest.TestCase):
    def test_v2_before2020(self):
        file_id = FileId.from_file_id('CAADBAADwwADmFmqDf6xBrPTReqHAg')
        self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
        self.assertEqual('document', file_id.type_generic)
        self.assertEqual(file_id.type_detailed, 'sticker', 'type is sticker')
    # end def

    def test_v4_before2020(self):
        file_id = FileId.from_file_id('CAADBAADwwADmFmqDf6xBrPTReqHFgQ')
        self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
        self.assertEqual('document', file_id.type_generic)
        self.assertEqual(file_id.type_detailed, 'sticker', 'type is sticker')
    # end def

    def test_v4_post2020(self):
        file_id = FileId.from_file_id('CAACAgQAAxkBAAIC4l9CWDGzVUcDejU0TETLWbOdfsCoAALDAAOYWaoN_rEGs9NF6ocbBA')
        self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
        self.assertEqual('document', file_id.type_generic)
        self.assertEqual(file_id.type_detailed, 'sticker', 'type is sticker')
    # end def

    def test_01(self):
        file_id = FileId.from_file_id('AgADBAAD_a4xG5EpaFJ9trmvgJ_jKUAtoBoABDqqHjBWUjhBIgkBAAEC')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_02(self):
        file_id = FileId.from_file_id('BQADBAADwgQAArWB8VA7hTVCyclc2QI')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_03(self):
        file_id = FileId.from_file_id('BQADBAADdggAAuIf-FAgXs_aELTd4wI')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_04(self):
        file_id = FileId.from_file_id('AwADBAADcwMAAhE1WFMeQwq5P_t28gI')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_05(self):
        file_id = FileId.from_file_id('DQADAQADdgAD7HrwRIhNNhRczBGAAg')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_06(self):
        file_id = FileId.from_file_id('DQACAgEAAxkBAAEDwpNfQqMoig8g_nGkspL1ZGZ0mIQwYQACdgAD7HrwRIhNNhRczBGAGwQ')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_07(self):
        file_id = FileId.from_file_id('CgADBAADIaEAAqobZAfVqgLO2giGbAI')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_08(self):
        file_id = FileId.from_file_id('CQADBAAD-AADc7jIUkFI8kwZnWFDAg')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_09(self):
        file_id = FileId.from_file_id('AgADBAADb6kxGzVD2VJxFZJnnojLocawuxkABCpho4S-bEPOrboCAAEC')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_10(self):
        file_id = FileId.from_file_id('AgADBAADmK8xG5B8CVLPkd0jIGgFvmsRHxsABOpZnaBmJdfAI2wFAAEC')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_11(self):
        file_id = FileId.from_file_id('AgADAQADP7UxG8teKQICXFeh7eXaDtYD3ikABER9JkFQSzXqS6oAAgI')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_12(self):
        file_id = FileId.from_file_id('CAADBAAD2AADfDCoCh1TJEHYmiHfAg')
        self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_13(self):
        file_id = FileId.from_file_id('BAADBAADAgADpCP6CbTQbvd25YqQAg')
        # self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
    # end def

    def test_sticker_2018_nov(self):
        file_id = FileId.from_file_id('CAADAgAD8wkAAgKLowABpAz7kZfM7jcC')  # test4458pack, the bigger Test one.
        self.assertEqual(file_id.type_id, file_id.TYPE_STICKER, 'type is sticker')
        self.assertEqual(2, file_id.version)
        # self.assertEqual(0, file_id.sub_version)
    # end def

    def test_sticker_starlight_filly(self):
        file_unique_id_decoded = rle_decode(base64url_decode('AgADwwADmFmqDQ'))
        type_id = struct.unpack("<i", file_unique_id_decoded[0:4])[0]
        self.assertEqual(2, type_id)
        media_id = struct.unpack("<q", file_unique_id_decoded[-8:])[0]
        # sticker(pack: Story_pony_love)
        file_id_4_22 = FileId.from_file_id('CAADBAADwwADmFmqDf6xBrPTReqHFgQ')
        self.assertEqual(file_id_4_22.type_id, FileId.TYPE_STICKER, 'type is sticker')
        self.assertEqual(4, file_id_4_22.version)
        self.assertEqual(22, file_id_4_22.sub_version)
        self.assertIsInstance(file_id_4_22, DocumentFileId)
        self.assertEqual(media_id, file_id_4_22.id)

        file_id_4_27 = FileId.from_file_id('CAACAgQAAxkBAAIC4l9CWDGzVUcDejU0TETLWbOdfsCoAALDAAOYWaoN_rEGs9NF6ocbBA')  # (4,27)
        self.assertEqual(file_id_4_27.type_id, FileId.TYPE_STICKER, 'type is sticker')
        self.assertEqual(4, file_id_4_27.version)
        self.assertEqual(27, file_id_4_27.sub_version)
        self.assertIsInstance(file_id_4_27, DocumentFileId)
        self.assertEqual(media_id, file_id_4_27.id)

        self.assertEqual(file_id_4_22.type_id, file_id_4_27.type_id, msg='4.22->4.27: type_id')
        self.assertEqual(file_id_4_22.type_generic, file_id_4_27.type_generic, msg='4.22->4.27: type_generic')
        self.assertEqual(file_id_4_22.type_detailed, file_id_4_27.type_detailed, msg='4.22->4.27: type_detailed')
        self.assertEqual(file_id_4_22.dc_id, file_id_4_27.dc_id, msg='4.22->4.27: dc_id')
        self.assertEqual(file_id_4_22.id, file_id_4_27.id, msg='4.22->4.27: id')
        self.assertEqual(file_id_4_22.access_hash, file_id_4_27.access_hash, msg='4.22->4.27: access_hash')
        self.assertEqual(file_id_4_22.owner_id, file_id_4_27.owner_id, msg='4.22->4.27: owner_id')
    # end def

    def test_sticker_2019_july(self):
        # HotCherry, the waving one.
        file_id_4_22 = FileId.from_file_id('CAADAgADBQADwDZPE_lqX5qCa011FgQ')
        self.assertEqual(file_id_4_22.type_id, file_id_4_22.TYPE_STICKER, 'type is sticker')
        self.assertEqual(4, file_id_4_22.version)
        self.assertEqual(22, file_id_4_22.sub_version)

        file_id_4_27 = FileId.from_file_id('CAACAgIAAxkBAAIC1F9CrovDlZGS5umOiP0HdbMIxVhsAAIFAAPANk8T-WpfmoJrTXUbBA')  # (4,27)
        self.assertEqual(file_id_4_27.type_id, file_id_4_27.TYPE_STICKER, 'type is sticker')
        self.assertEqual(4, file_id_4_27.version)
        self.assertEqual(27, file_id_4_27.sub_version)
    # end def

    def test_xxx(self):
        file_ids = [
            "AgADBAAD_a4xG5EpaFJ9trmvgJ_jKUAtoBoABDqqHjBWUjhBIgkBAAEC",
            "BQADBAADwgQAArWB8VA7hTVCyclc2QI",
            "BQADBAADdggAAuIf-FAgXs_aELTd4wI",
            "AwADBAADcwMAAhE1WFMeQwq5P_t28gI",
            "DQADAQADdgAD7HrwRIhNNhRczBGAAg", "DQACAgEAAxkBAAEDwpNfQqMoig8g_nGkspL1ZGZ0mIQwYQACdgAD7HrwRIhNNhRczBGAGwQ",
            "CgADBAADIaEAAqobZAfVqgLO2giGbAI",
            "CQADBAAD-AADc7jIUkFI8kwZnWFDAg",
            "AgADBAADb6kxGzVD2VJxFZJnnojLocawuxkABCpho4S-EPOrboCAAEC",
            "AgADBAADmK8xG5B8CVLPkd0jIGgFvmsRHxsABOpZnaBmJdfAI2wFAAEC",
            "AgADAQADP7UxG8teKQICXFeh7eXaDtYD3ikABER9JkFQSzXqS6oAAgI",
            "CAADBAAD2AADfDCoCh1TJEHYmiHfAg",
            "BAADBAADAgADpCP6CbTQbvd25YqQAg",
        ]
        for file_id in file_ids:
            decoded = rle_decode(base64url_decode(file_id))
            data, version = decoded[:-1], decoded[-1]
            if version == 4:
                data, sub_version = data[:-1], data[-1]
            else:
                sub_version = 0
            # end if
            print(f'{file_id!r}: {version}, {sub_version}')
        # end for
    # end def

    def test_photo_a_v2_0(self):
        file_id = FileId.from_file_id('AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABLefjdP8kuxqa7ABAAEC')
        self.assertEqual(FileId.TYPE_PHOTO, file_id.type_id)
        self.assertIsInstance(file_id, PhotoFileId)
        self.assertEqual(2, file_id.version)
        self.assertEqual(0, file_id.sub_version)
    # end def

    def test_photo_a_v4_22(self):
        # same as AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABLefjdP8kuxqa7ABAAEC
        file_id = FileId.from_file_id('AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABAEAAwIAA3gAA2uwAQABFgQ')
        self.assertEqual(FileId.TYPE_PHOTO, file_id.type_id)
        self.assertIsInstance(file_id, PhotoFileId)
        self.assertEqual(4, file_id.version)
        self.assertEqual(22, file_id.sub_version)
    # end def

    def test_photo_a_v4_27(self):
        # same as AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABLefjdP8kuxqa7ABAAEC
        file_id = FileId.from_file_id('AgACAgIAAxkBAAIBp19C0Fkv9R4D-TriZLzK7vBUw-DrAAJFqjEbrisJSV-bd-PeeKFbc8dRDwAEAQADAgADbQADbbABAAEbBA')
        self.assertEqual(FileId.TYPE_PHOTO, file_id.type_id)
        self.assertIsInstance(file_id, PhotoFileId)
        self.assertEqual(4, file_id.version)
        self.assertEqual(27, file_id.sub_version)
    # end def

    def test_other_impl(self):
        false = False
        true = True
        null = None

        test_data = {
            'CAADBAADwwADmFmqDf6xBrPTReqHFgQ': {"version":4,"subVersion":22,"typeId":8,"dc_id":4,"hasReference":false,"hasWebLocation":false,"type":"sticker","id":984697977903775939,"access_hash":-8653026958495010306},
            'CAACAgQAAxkBAAIC4l9CWDGzVUcDejU0TETLWbOdfsCoAALDAAOYWaoN_rEGs9NF6ocbBA': {"version":4,"subVersion":27,"typeId":8,"dc_id":4,"hasReference":true,"hasWebLocation":false,"type":"sticker","fileReference":"01000002e25f425831b35547037a35344c44cb59b39d7ec0a8","id":984697977903775939,"access_hash":-8653026958495010306},
            'CAADBAADwwADmFmqDf6xBrPTReqHAg': {"version":2,"subVersion":0,"typeId":8,"dc_id":4,"hasReference":false,"hasWebLocation":false,"type":"sticker","id":984697977903775939,"access_hash":-8653026958495010306},
            'CAADAgAD8wkAAgKLowABpAz7kZfM7jcC': {"version":2,"subVersion":0,"typeId":8,"dc_id":2,"hasReference":false,"hasWebLocation":false,"type":"sticker","id":46033261910034931,"access_hash":4030383667904449700},
            'CAACAgIAAxkBAAIBGV9DozZKicI-6IkNYlzxMUPaNnwBAALzCQACAoujAAGkDPuRl8zuNxsE': {"version":4,"subVersion":27,"typeId":8,"dc_id":2,"hasReference":true,"hasWebLocation":false,"type":"sticker","fileReference":"01000001195f43a3364a89c23ee8890d625cf13143da367c01","id":46033261910034931,"access_hash":4030383667904449700},
            'BQADAgAD3AkAAgKLowABKlAd1pemg-gC': {"version":2,"subVersion":0,"typeId":5,"dc_id":2,"hasReference":false,"hasWebLocation":false,"type":"document","id":46033261910034908,"access_hash":-1692325863898656726},
            'CAACAgIAAxkBAAIEVF9Do80olppb0490gLH2I1cszuoMAALcCQACAoujAAEqUB3Wl6aD6BsE': {"version":4,"subVersion":27,"typeId":8,"dc_id":2,"hasReference":true,"hasWebLocation":false,"type":"sticker","fileReference":"01000004545f43a3cd28969a5bd38f7480b1f623572cceea0c","id":46033261910034908,"access_hash":-1692325863898656726},
            'CAADAgADIwYAAmpiTwttSWWW_Tc0aQI': {"version":2,"subVersion":0,"typeId":8,"dc_id":2,"hasReference":false,"hasWebLocation":false,"type":"sticker","id":814978264983406115,"access_hash":7580745635060861293},
            'CAACAgIAAxkBAAIEVl9DpKV6azEUxxqd204SZQzixxO0AAIjBgACamJPC21JZZb9NzRpGwQ': {"version":4,"subVersion":27,"typeId":8,"dc_id":2,"hasReference":true,"hasWebLocation":false,"type":"sticker","fileReference":"01000004565f43a4a57a6b3114c71a9ddb4e12650ce2c713b4","id":814978264983406115,"access_hash":7580745635060861293},
        }
        for file_id, expected in test_data.items():
            obj = FileId.from_file_id(file_id)
            self.assertIsInstance(obj, FileId, msg=f'file_id = {file_id!r}')
            self.assertIsInstance(obj, DocumentFileId, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('version'), obj.version, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('subVersion'), obj.sub_version, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('typeId'), obj.type_id, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('type'), obj.type_detailed, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('dc_id'), obj.dc_id, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('hasReference'), obj.has_reference, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('hasWebLocation'), obj.has_web_location, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('id'), obj.id, msg=f'file_id = {file_id!r}')
            self.assertEqual(expected.pop('access_hash', None), obj.access_hash, msg=f'file_id = {file_id!r}')
            self.assertEqual(to_binary(expected.pop('fileReference', b'')), encode((obj.file_reference if obj.file_reference else b''), 'hex'), msg=f'file_id = {file_id!r}')
            self.assertEqual({}, expected, msg=f'file_id = {file_id!r} - array shall be empty now.')
        # end for
    # end def

    def test_to_unique(self):
        given_file_id = 'CAACAgIAAxkBAAIEol9yQhBqFnT4HXldAh31a-hYXuDIAAIECwACAoujAAFFn1sl9AABHbkbBA'
        expected_unique_id = 'AgADBAsAAgKLowAB'

        file_id = FileId.from_file_id(given_file_id)
        self.assertEqual(8, file_id.type_id)
        self.assertEqual(46033261910035204, file_id.id)

        unique_id = FileUniqueId.from_file_id(file_id)
        self.assertEqual(2, unique_id.type_id)
        self.assertEqual(46033261910035204, unique_id.id)
        self.assertEqual(None, unique_id.volume_id)
        self.assertEqual(None, unique_id.local_id)
        self.assertEqual(None, unique_id.url)
        unique_id_str = unique_id.to_unique_id()

        self.assertEqual(expected_unique_id, unique_id_str)
    # end def

    def test_base64url_encode(self):
        given = b'\x02\x00\x00\x00\x04\x0b\x00\x00\x02\x8b\xa3\x00'
        expected = 'AgAAAAQLAAACi6MA'
        result = base64url_encode(given)
        self.assertEqual(expected, result)
    # end def

    def test_base64url_encode(self):
        given = b'\x02\x00\x00\x00\x04\x0b\x00\x00\x02\x8b\xa3\x00'
        expected = 'AgADBAsAAgKLowAB'
        result = base64url_encode(rle_encode(given))
        self.assertEqual(expected, result)
    # end def




    def test_user_ids(self):
        #https://getstickers.me/sticker/test4458pack/CAADAgAD1AkAAgKLowABByoNoHLboHEC/
        test_data = {
            'BQADAgAD3AkAAgKLowABKlAd1pemg-gC': None,
            'BQADAgAD7QkAAgKLowABuLSCK5e9BY0C': None,
            'CAADAgAD0gkAAgKLowAB_uE0vZEqv4oC': 10717954,
            'CAACAgIAAxkBAAIEVF9Do80olppb0490gLH2I1cszuoMAALcCQACAoujAAEqUB3Wl6aD6BsE': 10717954,
            'CAADAgAD1AkAAgKLowABByoNoHLboHEC': 10717954,
            'CAACAgIAAxkBAAIEWl9EYjGyD-ToGsSWHMIz19CYxsYWAAK7CgACAoujAAHTPCFEqkdBoxsE': 10717954,
        }
        for file_id, expected_owner_id in test_data.items():
            obj = FileId.from_file_id(file_id)
            self.assertIsInstance(obj, FileId, msg=f'file_id = {file_id!r}')
            self.assertIsInstance(obj, DocumentFileId, msg=f'file_id = {file_id!r}')
            self.assertIn(obj.type_id, [5, 8], msg=f'file_id = {file_id!r}')
            self.assertEqual('document', obj.type_generic, msg=f'file_id = {file_id!r}')
            self.assertIn(obj.type_detailed, ['document', 'sticker'], msg=f'file_id = {file_id!r}')
            self.assertEqual(expected_owner_id, obj.owner_id, msg=f'file_id = {file_id!r}')
        # end for
    # end def

    def test_user_ids_from_file(self):
        users = {}
        fails = 0
        successes = 0
        with open('/Users/luckydonald/Downloads/Telegram/tblsticker.csv.txt') as f:
            for line in f:
                file_id, _ = line.split(',', 1)
                try:
                    obj = FileId.from_file_id(file_id)
                    successes += 1
                except:
                    fails += 1
                    continue
                # end try
                owner_id = obj.owner_id
                if owner_id not in users:
                    users[owner_id] = []
                # end if
                users[owner_id].append(file_id)
            # end for
        # end with
        with open('/Users/luckydonald/Downloads/Telegram/tblsticker.json', 'w') as f:
            f.write(repr(users))
        # end with
        # print(users)
        print(len(users))
        print(successes)
        print(fails)
    # end def
# END CLASS

if __name__ == '__main__':
    unittest.main()
