import struct
import base64
import logging
from io import BytesIO, SEEK_CUR, SEEK_END
from typing import Union, Tuple

from luckydonaldUtils.encoding import to_unicode
from luckydonaldUtils.exceptions import assert_type_or_raise

logger = logging.getLogger(__name__)


def base64url_decode(string):
    # add missing padding # http://stackoverflow.com/a/9807138
    return base64.urlsafe_b64decode(string + '='*(4 - len(string)%4))
# end def


def base64url_encode(string):
    return to_unicode(base64.urlsafe_b64encode(string)).rstrip("=")
# end def


def rle_decode(binary) -> bytearray:
    """
    Returns the byte array of the given string.
    :param string:
    :return: The array of ints.
    :rtype: bytearray
    """
    # https://github.com/danog/MadelineProto/blob/38d6ee07b3a7785bcc77ed4ba3ef9ddd8e915975/pwrtelegram_debug_bot.php#L28-L42
    # https://github.com/danog/MadelineProto/blob/1485d3879296a997d47f54469b0dd518b9230b06/src/danog/MadelineProto/TL/Files.php#L66
    base256 = bytearray()
    last = None
    for cur in binary:
        if last == 0:
            for i in range(cur):
                base256.append(0)
            # end for
            last = None
        else:
            if last is not None:
                base256.append(last)
            # end if
            last = cur
        # end if
    # end for
    if last is not None:
        base256.append(last)
    # end if
    return base256
# end def


def rle_encode(binary):
    # https://github.com/danog/MadelineProto/blob/1485d3879296a997d47f54469b0dd518b9230b06/src/danog/MadelineProto/TL/Files.php#L85
    new = bytearray()
    count = 0
    for cur in binary:
        if cur == 0:
            count += 1
        else:  # not 0 (any more)
            if count > 0:
                new.append(0)
                new.append(count)
                count = 0
            # end if
            new.append(cur)
        # end if
    # end for
    return new
# end def


def posmod(a, b):
    """
    Positive modulo
    Works just like the % (modulus) operator, only returns always a postive number.

    :return:
    """
    rest = a % b
    return rest + abs(b) if rest < 0 else rest
# end def


def pack_tl_string(string: Union[str, bytes]) -> bytes:
    if isinstance(string, str):
        string = string.encode()
    # end if
    length = len(string)
    concat = b''
    if length <= 253:
        concat += chr(length).encode()
        fill = posmod(-length - 1, 4)
    else:
        concat += chr(254).encode()
        concat += struct.pack('<L', length)[0:3]
        fill = posmod(-length, 4)
    # end if
    concat += string
    concat += b'\x00' * fill
    return concat
# end def

# pack_tl_string('test')


def unpack_tl_string(buffer: BytesIO, as_string: bool = False) -> Union[str, bytes]:
    """
    https://github.com/danog/tg-file-decoder/blob/afcdb9a4a7239e36e8ab3b9a02db72eaa95db66e/src/type.php#L395
    :param data:
    :return:
    """
    length: int = ord(buffer.read(1))

    if length > 254:
        raise ValueError('length too big for a single field.')
    # end if

    if length == 254:
        # untested
        length = int(struct.unpack('<L', (buffer.read(3) + b'\x00'))[0])
        fill = posmod(-1 * length, 4)
    else:
        fill = posmod(-(length + 1), 4)
    # end if
    string = buffer.read(length)
    buffer.seek(fill, SEEK_CUR)
    if as_string:
        string = string.decode('utf-8')
    # end if
    return string
# end def


def unpack_null_terminated_string(buffer: BytesIO, as_string: bool = False) -> Union[str, bytes]:
    char = buffer.read(1)
    new_buff = b''
    while char != b'\00':
        new_buff += char
        char = buffer.read(1)
    # end while
    if as_string:
        new_buff = new_buff.decode('utf-8')
    # end if
    return new_buff
# end def


class FileId(object):
    TYPE_ID_WEB_LOCATION_FLAG = 1 << 24
    TYPE_ID_FILE_REFERENCE_FLAG = 1 << 25

    def __init__(
        self,
        file_id: str,
        type_id: int,
        has_reference: bool, file_reference: bytearray,
        has_web_location: bool,
        type_generic: str, type_detailed: str,
        dc_id: int, id: int, access_hash: int,
        version=2, sub_version=0,
    ):
        """
        :param file_id: Telegram file_id
        :type  file_id: str

        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param has_reference: If the file has a reference.
        :type  type_id: bool

        :param has_reference: If the file has a web location.
        :type  type_id: bool

        :param type_generic: A string showing which datatype this file_id is. Could also be checked with `isinstance(...)`
        :type  type_generic: str

        :param type_detailed: a human readable string of the type
        :type  type_detailed: str

        :param dc_id: The if of the Telegram Datacenter
        :type  dc_id: int

        :param id: The file id (long)
        :type  id: int

        :param file_reference: telegram need this piece of blackbox. Raw data, therefore here base64 encoded as string, or a byte format. Can be None too.
        :type  file_reference: bytes | bytearray | str | None

        :param version: version number of the file id.
        :type  version: int

        :param sub_version: sub-version number of the file id, corresponds to the tdlib version (only meaningful if version == 4)
        :type  sub_version: int

        :return:
        :rtype:
        """
        self.file_id = file_id
        self.type_id = type_id
        self.has_reference = has_reference
        self.file_reference = file_reference
        self.has_web_location = has_web_location
        self.type_generic = type_generic
        self.type_detailed = type_detailed
        self.dc_id = dc_id
        self.id = id
        self.access_hash = access_hash
        self.version = version
        self.sub_version = sub_version
    # end def __init__

    @property
    def owner_id(self):
        if not (self.version in (2, 4) and self.type_id == DocumentFileId.TYPE_STICKER):
            return None
        # end if
        return (self.id & (((1 << 24) - 1) << 32)) // 2 ** 32
        # last 4 bits of that, parsed as '<I' basically.
    # end def

    @staticmethod
    def generate_new(file_id, type_id, type_detailed, dc_id, id, access_hash, location=None):
        if location:
            return PhotoFileId(file_id, type_id, type_detailed, dc_id, id, access_hash, location)
        # end if
        return DocumentFileId(file_id, type_id, type_detailed, dc_id, id, access_hash)
    # end def

    @classmethod
    def from_file_id(cls, file_id, decoded=None):
        """

        :param file_id:
        :param decoded: if the file_id binary data is already decoded (rle + base64url).
        :except ValueError: Unknown type id.
        :return:
        """
        if not decoded:
            decoded = rle_decode(base64url_decode(file_id))
        # end if
        data, version, sub_version = cls._parse_version(decoded)
        buffer = BytesIO(data)
        type_id = struct.unpack('<i', buffer.read(4))[0]
        type_id, has_reference, has_web_location = cls._normalize_type_id(type_id)
        dc_id = struct.unpack('<i', buffer.read(4))[0]
        if has_reference:
            file_reference = unpack_tl_string(buffer)
        else:
            file_reference = None
        # end if
        if has_web_location:
            url = unpack_tl_string(buffer)
            access_hash = struct.unpack('<q', buffer.read(8))
            return WebLocationFileId(
                file_id=file_id, type_id=type_id, has_reference=has_reference, has_web_location=has_web_location,
                # type_detailed=PhotoFileId.TYPES[type_id],
                file_reference=file_reference,
                url=url, access_hash=access_hash
            )
        # end if
        # v2,00: AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABLefjdP8kuxqa7ABAAEC via @teleflaskBot
        # type_id, dc_id, id, access_hash, location_volume_id, location_secret, location_local_id = struct.unpack('<iiqqqqi', data)
        # v4,22: AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABAEAAwIAA3gAA2uwAQABFgQ via @teleflaskBot
        # v4,27: AgACAgIAAxkBAAIBp19C0Fkv9R4D-TriZLzK7vBUw-DrAAJFqjEbrisJSV-bd-PeeKFbc8dRDwAEAQADAgADbQADbbABAAEbBA via @teleflaskBot
        media_id = struct.unpack('<q', buffer.read(8))[0]
        access_hash = struct.unpack('<q', buffer.read(8))[0]
        if type_id in PhotoFileId.TYPES:
            volume_id = struct.unpack('<q', buffer.read(8))[0]
            # $result['photosize_source'] = $result['version'] >= 4 ? \unpack('V', \stream_get_contents($fileId, 4))[1] : 0;
            photosize_source = 0 if version < 4 else struct.unpack('<L', buffer.read(4))[0]
            photosize = None
            # switch($result['photosize_source']) {
            # case PHOTOSIZE_SOURCE_LEGACY:
            if photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_LEGACY:
                # $result += \unpack(LONG.'secret', \stream_get_contents($fileId, 8));
                secret = struct.unpack('<q', buffer.read(8))[0]
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                photosize = PhotoFileId.PhotosizeSourceLegacy(volume_id=volume_id, secret=secret, location_local_id=location_local_id)
            # case PHOTOSIZE_SOURCE_THUMBNAIL:
            elif photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_THUMBNAIL:
                file_type = struct.unpack('<L', buffer.read(4))[0]
                thumbnail_type = unpack_null_terminated_string(buffer)
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                photosize = PhotoFileId.PhotosizeSourceThumbnail(volume_id=volume_id, file_type=file_type, thumbnail_type=thumbnail_type, location_local_id=location_local_id)
            elif photosize_source in [PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL, PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_BIG]:
                # $result['photo_size'] = $result['photosize_source'] === PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL ? 'photo_small' : 'photo_big';
                # $result['dialog_id'] = unpackLong(\stream_get_contents($fileId, 8));
                dialog_id = struct.unpack('<q', buffer.read(8))[0]
                # $result['dialog_access_hash'] = \unpack(LONG, \stream_get_contents($fileId, 8))[1];
                dialog_access_hash = struct.unpack('<q', buffer.read(8))[1]
                # fixLong($result, 'dialog_access_hash');
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                if photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL:
                    photosize = PhotoFileId.PhotosizeSourceDialogPhotoSmall(volume_id=volume_id, dialog_id=dialog_id, dialog_access_hash=dialog_access_hash, location_local_id=location_local_id)
                else:
                    photosize = PhotoFileId.PhotosizeSourceDialogPhotoBig(volume_id=volume_id, dialog_id=dialog_id, dialog_access_hash=dialog_access_hash, location_local_id=location_local_id)
                # end if
            elif photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_STICKERSET_THUMBNAIL:
                # $result += \unpack(LONG.'sticker_set_id/'.LONG.'sticker_set_access_hash', \stream_get_contents($fileId, 16));
                sticker_set_id = struct.unpack('<q', buffer.read(8))[0]
                sticker_set_access_hash = struct.unpack('<q', buffer.read(8))[0]
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                photosize = PhotoFileId.PhotosizeSourceStickersetThumbnail(volume_id=volume_id, sticker_set_id=sticker_set_id, sticker_set_access_hash=sticker_set_access_hash, location_local_id=location_local_id)
            # end if
            # $result += \unpack('llocal_id', \stream_get_contents($fileId, 4));

            file_id_obj = PhotoFileId(
                file_id=file_id, type_id=type_id, has_reference=has_reference, has_web_location=has_web_location,
                type_detailed=PhotoFileId.TYPES[type_id],
                file_reference=file_reference,
                dc_id=volume_id, id=media_id, access_hash=access_hash,
                photosize=photosize,
                version=version, sub_version=sub_version,
            )
        else:
            file_id_obj = DocumentFileId(
                file_id=file_id, type_id=type_id, has_reference=has_reference, has_web_location=has_web_location,
                type_detailed=DocumentFileId.TYPES[type_id],
                file_reference=file_reference,
                dc_id=dc_id, id=media_id, access_hash=access_hash,
                version=version, sub_version=sub_version,
            )
        # end if

        version_suffix_length = 1 if version < 4 else 2

        end_position = buffer.tell()
        buffer.seek(0, SEEK_END)
        stuff_left = buffer.tell() - end_position
        stuff_left -= version_suffix_length
        if stuff_left > 0:
            logger.warning(f'Found {stuff_left} leftover data.')
        # end if

        return file_id_obj
    # end def

    def recalculate(self):
        """ Recalculates the file_id """
        file_id = self.to_file_id()
        self.file_id = file_id
        return file_id
    # end def

    def to_file_id(self):
        """
        Subclasses do calculation here.
        :return:
        """
        return self.file_id
    # end def

    def __repr__(self):
        return "FileId(file_id={file_id!r}, type_id={type_id!r}, type_generic={type_generic!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, version={version!r}, owner_id={owner_id!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_generic=self.type_generic, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, version=self.version,
        )
    # end def __str__

    TYPE_THUMBNAIL = 0
    TYPE_PROFILE_PHOTO = 1  # Used for users and channels, chat photos are normal PHOTOs.
    TYPE_PHOTO = 2
    TYPE_VOICE = 3
    TYPE_VIDEO = 4
    TYPE_DOCUMENT = 5
    TYPE_ENCRYPTED = 6  # Secret chat document
    TYPE_TEMP = 7  # Temporary document
    TYPE_STICKER = 8
    TYPE_SONG = 9
    TYPE_ANIMATION = 10
    TYPE_ENCRYPTED_THUMBNAIL = 11
    TYPE_WALLPAPER = 12
    TYPE_VIDEO_NOTE = 13
    TYPE_SECURE_RAW = 14
    TYPE_SECURE = 15
    TYPE_BACKGROUND = 16
    TYPE_SIZE = 17
    TYPE_NONE = 18

    SUPPORTED_VERSIONS = (
        (2, 0),
        (4, 22),
        (4, 27),
    )
    MAX_VERSION = (4, 27)

    @classmethod
    def _normalize_type_id(cls, type_id: int) -> Tuple[int, bool, bool]:
        has_reference = bool(type_id & cls.TYPE_ID_FILE_REFERENCE_FLAG)
        has_web_location = bool(type_id & cls.TYPE_ID_WEB_LOCATION_FLAG)
        type_id &= ~ cls.TYPE_ID_FILE_REFERENCE_FLAG
        type_id &= ~ cls.TYPE_ID_WEB_LOCATION_FLAG
        return type_id, has_reference, has_web_location
    # end def

    @classmethod
    def _parse_version(cls, decoded: bytearray) -> Tuple[bytearray, int, int]:
        data, version = decoded[:-1], decoded[-1]
        if version == 4:
            data, sub_version = data[:-1], data[-1]
        else:
            sub_version = 0
        # end if

        if (version, sub_version) not in FileId.SUPPORTED_VERSIONS:
            raise ValueError(f'Unsupported file_id (sub_)version: {version, sub_version}')
        # end if
        return data, version, sub_version
    # end def
# end class FileId


class DocumentFileId(FileId):
    def __init__(
            self,
            file_id: str,
            type_id: int,
            has_reference: bool, file_reference: bytearray,
            has_web_location: bool,
            type_detailed: str,
            dc_id: int, id: int, access_hash: int,
            version=2, sub_version=0,
        ):
        """
        :param file_id: Telegram file_id
        :type  file_id: str

        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param has_reference: If the file has a reference.
        :type  type_id: bool

        :param has_reference: If the file has a web location.
        :type  type_id: bool

        :param type_detailed: a human readable string of the type
        :type  type_detailed: str

        :param dc_id: The if of the Telegram Datacenter
        :type  dc_id: int

        :param id: The file id (long)
        :type  id: int

        :param file_reference: telegram need this piece of blackbox. Raw data, therefore here base64 encoded as string, or a byte format. Can be None too.
        :type  file_reference: bytes | bytearray | str | None

        :param version: version number of the file id.
        :type  version: int

        :param sub_version: sub-version number of the file id, corresponds to the tdlib version (only meaningful if version == 4)
        :type  sub_version: int

        :return:
        :rtype:
        """
        super(DocumentFileId, self).__init__(
            file_id=file_id,
            type_id=type_id, has_reference=has_reference, file_reference=file_reference, has_web_location=has_web_location,
            type_generic="document", type_detailed=type_detailed,
            dc_id=dc_id, id=id, access_hash=access_hash, version=version, sub_version=sub_version,
        )
    # end def __init__

    TYPES = {
        FileId.TYPE_VOICE: "voice", FileId.TYPE_VIDEO: "video", FileId.TYPE_DOCUMENT: "document",
        FileId.TYPE_STICKER: "sticker", FileId.TYPE_SONG: "song", FileId.TYPE_VIDEO_NOTE: "video note",
        FileId.TYPE_ANIMATION: "animation",
    }
    """ A human readable string of the type """

    def swap_type_sticker(self):
        """
        This swaps out the document types "document" <-> "sticker"

        :param data: Can be a dict as obtained by `take_apart_file_id(file_id)`.
                     Otherwise a file_id is assumed and said function `take_apart_file_id` is called.
        :type  data: dict or bytearray or bytes

        :return: new file id
        :rtype: str
        """

        self.change_type(FileId.TYPE_STICKER if self.type_id == FileId.TYPE_DOCUMENT else FileId.TYPE_DOCUMENT)
        return self.recalculate()
    # end def

    def change_type(self, type_id):
        """
        Changes the type of the document.

        :param type_id:
        :return:
        """
        self.type_id = type_id
        self.type_detailed = DocumentFileId.TYPES[self.type_id]
        return self.recalculate()
    # end def

    @classmethod
    def from_file_id(cls, file_id, decoded=None):
        """
        :param file_id:
        :param decoded:
        :return:
        """
        return FileId.from_file_id(file_id=file_id, decoded=decoded)
    # end def

    def to_file_id(self, version=None, sub_version=None):
        assert self.type_id in DocumentFileId.TYPES
        if version is None:
            version = self.version
            sub_version = self.sub_version
        # end if
        if version is None:
            version, sub_version = self.MAX_VERSION
        # end if
        if version == 2:
            binary = struct.pack(
                "<iiqqb",
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash
                self.access_hash if self.access_hash else 0,
                # version
                2
            )
        elif version == 4 and sub_version == 22:
            binary = struct.pack(
                "<iiqqbb",
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash,
                self.access_hash if self.access_hash else 0,
                # twentytwo, version
                22, 4
            )
        else:
            raise ValueError(f'Unknown version flag: ({version},{sub_version})')
        # end if
        return base64url_encode(rle_encode(binary))
    # end def

    def __repr__(self):
        return "DocumentFileId(file_id={file_id!r}, type_id={type_id!r}, type_generic={type_generic!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, version={version!r}, owner_id={owner_id!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_generic=self.type_generic, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, owner_id=self.owner_id, version=self.version,
        )
    # end def __repr__
# end class DocumentFileId


class WebLocationFileId(object):
    def __init__(
        self,
        file_id, type_id, has_reference, has_web_location,
        file_reference,
        url, access_hash,
    ):
        self.file_id = file_id
        self.type_id = type_id
        self.has_reference = has_reference
        self.has_web_location = has_web_location
        self.file_reference = file_reference
        self.url = url
        self.access_hash = access_hash
    # end def __init__

    def __repr__(self):
        return f"{self.__class__.__name__}()"
    # end def __repr__

    def __str__(self):
        return self.__repr__()
    # end def __str__
# end class WebLocationFileId


class PhotoFileId(FileId):
    class PhotosizeSource(object):
        def __init__(self, type_id: int, volume_id: int, location_local_id: int):
            self.volume_id: int = volume_id
            self.type_id: int = type_id
            self.location_local_id: int = location_local_id
        # end def __init__

        def __repr__(self):
            return f"{self.__class__.__name__}(type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r})"
        # end def __repr__

        def __str__(self):
            return self.__repr__()
        # end def __str__
    # end class PhotosizeSource

    class PhotosizeSourceLegacy(PhotosizeSource):
        def __init__(self, volume_id: int, location_local_id: int, secret):
            self.secret = secret
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_LEGACY, volume_id=volume_id, location_local_id=location_local_id)
        # end def __init__

        def __repr__(self):
            return f"{self.__class__.__name__}(type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r}, secret={self.secret})"
        # end def __repr__
    # end class PhotosizeSourceLegacy

    class PhotosizeSourceThumbnail(PhotosizeSource):
        def __init__(self, volume_id: int, location_local_id: int, file_type, thumbnail_type):
            self.file_type = file_type
            self.thumbnail_type = thumbnail_type
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_THUMBNAIL, volume_id=volume_id, location_local_id=location_local_id)
        # end def __init__

        def __repr__(self):
            return (
                f"{self.__class__.__name__}("
                f"type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r}, "
                f"file_type={self.file_type}, thumbnail_type={self.thumbnail_type}, photosize={self.photosize}"
                f")"
            )
        # end def __repr__
    # end class PhotosizeSourceThumbnail

    class PhotosizeSourceDialogPhoto(PhotosizeSource):
        def __init__(self, type_id: int, volume_id: int, location_local_id: int, dialog_id, dialog_access_hash):
            self.dialog_id = dialog_id
            self.dialog_access_hash = dialog_access_hash
            super().__init__(type_id, volume_id=volume_id, location_local_id=location_local_id)
        # end def __init__

        def __repr__(self):
            return (
                f"{self.__class__.__name__}("
                f"type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r}, "
                f"dialog_id={self.dialog_id}, dialog_access_hash={self.dialog_access_hash}"
                f")"
            )
        # end def __repr__
    # end class PhotosizeSourceDialogPhoto

    class PhotosizeSourceDialogPhotoSmall(PhotosizeSourceDialogPhoto):
        def __init__(self, volume_id: int, location_local_id: int, dialog_id, dialog_access_hash):
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL, volume_id, location_local_id, dialog_id, dialog_access_hash)
        # end def __init__
    # end class PhotosizeSourceDialogPhotoSmall

    class PhotosizeSourceDialogPhotoBig(PhotosizeSourceDialogPhoto):
        def __init__(self, volume_id: int, location_local_id: int, dialog_id, dialog_access_hash):
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_BIG, volume_id, location_local_id, dialog_id, dialog_access_hash)
        # end def __init__
    # end class PhotosizeSourceDialogPhotoBig

    class PhotosizeSourceStickersetThumbnail(PhotosizeSource):
        def __init__(self, volume_id: int, location_local_id: int, sticker_set_id, sticker_set_access_hash):
            self.sticker_set_id = sticker_set_id
            self.sticker_set_access_hash = sticker_set_access_hash
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_STICKERSET_THUMBNAIL, volume_id=volume_id, location_local_id=location_local_id)
        # end def __init__

        def __repr__(self):
            return (
                f"{self.__class__.__name__}("
                f"type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r}, "
                f"sticker_set_id={self.sticker_set_id}, sticker_set_access_hash={self.sticker_set_access_hash}"
                f")"
            )
        # end def __repr__

    # end class PhotosizeSourceStickersetThumbnail

    def __init__(self, file_id, type_id, has_reference, has_web_location, type_detailed, file_reference: bytearray, dc_id, id, access_hash, photosize: PhotosizeSource, version=2, sub_version=0):
        """
        :param file_id: Telegram file_id
        :type  file_id: str

        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param has_reference: If the file has a reference.
        :type  type_id: bool

        :param has_web_location: If the file has a web location.
        :type  type_id: bool

        :param type_detailed: str
        :type  type_detailed: str

        :param dc_id: The if of the Telegram Datacenter
        :type  dc_id: int

        :param id: The file id (long)
        :type  id: int

        :return:
        :rtype:
        """
        super(PhotoFileId, self).__init__(
            file_id=file_id,
            type_id=type_id, has_reference=has_reference, file_reference=file_reference,
            has_web_location=has_web_location,
            type_generic="photo", type_detailed=type_detailed,
            dc_id=dc_id, id=id, access_hash=access_hash,
            version=version, sub_version=sub_version,
        )
        assert_type_or_raise(photosize, PhotoFileId.PhotosizeSource, parameter_name='photosize')
        self.photosize = photosize
    # end def __init__

    TYPES = {FileId.TYPE_THUMBNAIL: "thumbnail", FileId.TYPE_PROFILE_PHOTO: "profile picture", FileId.TYPE_PHOTO: "photo"}
    """ A human readable string of the type """

    PHOTOSIZE_SOURCE_LEGACY: int = 0
    """ Legacy, used for file IDs with the deprecated secret field """

    PHOTOSIZE_SOURCE_THUMBNAIL: int = 1
    """ Used for document and photo thumbnail """

    PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL: int = 2
    """ Used for dialog photos """

    PHOTOSIZE_SOURCE_DIALOGPHOTO_BIG: int = 3
    """ Used for dialog photos """

    PHOTOSIZE_SOURCE_STICKERSET_THUMBNAIL: int = 4
    """ Used for document and photo thumbnails """

    @classmethod
    def from_file_id(cls, file_id, decoded=None):
        return FileId.from_file_id(file_id=file_id, decoded=decoded)
    # end def

    def to_file_id(self, version=None):
        assert self.type_id in PhotoFileId.TYPES
        if version == 2:
            binary = struct.pack(
                '<iiqqqqib',
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash,
                self.access_hash if self.access_hash else 0,
                # location_volume_id, location_secret,
                self.location.volume_id, self.location.secret,
                # location_local_id,
                self.location.local_id,
                # version
                2
            )
        elif version == 4:
            binary = struct.pack(
                '<iiqqqqiibb',
                # type, dc_id, id,
                self.type_id, self.dc_id, self.id if self.id else 0,
                # access_hash,
                self.access_hash if self.access_hash else 0,
                # location_volume_id, location_secret,
                self.location.volume_id, self.location.secret,
                # something,
                self.something,
                #  location_local_id,
                self.location.local_id,
                # twentytwo, version
                22, 4
            )
        else:
            raise ValueError(f'Unknown version to use: {version}')
        # end if
        return base64url_encode(rle_encode(binary))
    # end def

    def __repr__(self):
        return f"PhotoFileId(" \
               f"file_id={self.file_id!r}, type_id={self.type_id!r}, type_generic={self.type_generic!r}, " \
               f"type_detailed={self.type_detailed!r}, dc_id={self.dc_id!r}, id={self.id!r}, " \
               f"access_hash={self.access_hash!r}, location={self.has_web_location!r}, version={self.version!r}, " \
               f"owner_id={self.owner_id!r}" \
               f")"
    # end def __str__
# end class PhotoFileId
# end def
