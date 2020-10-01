import struct
import base64
import logging
from io import BytesIO, SEEK_CUR, SEEK_END
from typing import Union, Tuple, TypeVar, Type, Dict

from luckydonaldUtils.encoding import to_unicode
from luckydonaldUtils.exceptions import assert_type_or_raise

logger = logging.getLogger(__name__)
CLASS = TypeVar('CLASS')


def base64url_decode(string: str) -> bytes:
    # add missing padding # http://stackoverflow.com/a/9807138
    return base64.urlsafe_b64decode(string + '='*(4 - len(string)%4))
# end def


def base64url_encode(string: bytes) -> str:
    return to_unicode(base64.urlsafe_b64encode(string)).rstrip("=")
# end def


def rle_decode(binary: bytes) -> bytearray:
    """
    Returns the byte array of the given string.
    :param binary: Input data.
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


def rle_encode(binary: bytes) -> bytearray:
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
    if count > 0:
        new.append(0)
        new.append(count)
    # end if
    return new
# end def


def pos_mod(a: int, b: int) -> int:
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
        fill = pos_mod(-length - 1, 4)
    else:
        concat += chr(254).encode()
        concat += struct.pack('<L', length)[0:3]
        fill = pos_mod(-length, 4)
    # end if
    concat += string
    concat += b'\x00' * fill
    return concat
# end def

# pack_tl_string('test')


def unpack_tl_string(buffer: BytesIO, as_string: bool = False) -> Union[str, bytes]:
    """
    Unpack a tl_string.
    :param buffer: Input buffer. Needs support for `.read(1)` and `.seek(SEEK_CUR)`.
    :param as_string: if we should return it as utf-8 decoded `str` instead of `bytes`.
    :return: The unpacked string.
    """
    # https://github.com/danog/tg-file-decoder/blob/afcdb9a4a7239e36e8ab3b9a02db72eaa95db66e/src/type.php#L395
    length: int = ord(buffer.read(1))

    if length > 254:
        raise ValueError('length too big for a single field.')
    # end if

    if length == 254:
        # untested
        length = int(struct.unpack('<L', (buffer.read(3) + b'\x00'))[0])
        fill = pos_mod(-1 * length, 4)
    else:
        fill = pos_mod(-(length + 1), 4)
    # end if
    string = buffer.read(length)
    buffer.seek(fill, SEEK_CUR)
    if as_string:
        string = string.decode('utf-8')
    # end if
    return string
# end def


def unpack_null_terminated_string(buffer: BytesIO, as_string: bool = False) -> Union[str, bytes]:
    """
    Unpack a null terminated (\0) string.
    :param buffer: Input buffer. Needs support for `.read(1)`.
    :param as_string: if we should return it as utf-8 decoded `str` instead of `bytes`.
    :return: The unpacked string.
    """
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


def pack_null_terminated_string(string: Union[str, bytes]) -> bytes:
    """
    Packs a string and appends the null terminator \0 to it.
    :param string: The string to encode.
    :param as_string: if we should return it as utf-8 decoded `str` instead of `bytes`.
    :return: The unpacked string.
    """
    if isinstance(string, str):
        string: bytes = string.encode('utf-8')
    # end if
    string = string + b'\00'
    return string
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
    def owner_id(self) -> int:
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
    def from_file_id(cls, file_id, decoded: Union[None, bytes] = None) -> Union['PhotoFileId', 'DocumentFileId', 'WebLocationFileId']:
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
        type_id = struct.unpack('<L', buffer.read(4))[0]
        type_id, has_reference, has_web_location = cls._normalize_type_id(type_id)
        dc_id = struct.unpack('<L', buffer.read(4))[0]
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
            photosize_source = 0 if version < 4 else struct.unpack('<L', buffer.read(4))[0]
            photosize = None
            if photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_LEGACY:
                secret = struct.unpack('<q', buffer.read(8))[0]
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                photosize = PhotoFileId.PhotosizeSourceLegacy(volume_id=volume_id, secret=secret, location_local_id=location_local_id)
            elif photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_THUMBNAIL:
                file_type = struct.unpack('<L', buffer.read(4))[0]
                thumbnail_type = unpack_null_terminated_string(buffer)
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                photosize = PhotoFileId.PhotosizeSourceThumbnail(volume_id=volume_id, file_type=file_type, thumbnail_type=thumbnail_type, location_local_id=location_local_id)
            elif photosize_source in (PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL, PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_BIG):
                dialog_id = struct.unpack('<q', buffer.read(8))[0]
                dialog_access_hash = struct.unpack('<q', buffer.read(8))[1]
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                if photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL:
                    photosize = PhotoFileId.PhotosizeSourceDialogPhotoSmall(volume_id=volume_id, dialog_id=dialog_id, dialog_access_hash=dialog_access_hash, location_local_id=location_local_id)
                else:
                    photosize = PhotoFileId.PhotosizeSourceDialogPhotoBig(volume_id=volume_id, dialog_id=dialog_id, dialog_access_hash=dialog_access_hash, location_local_id=location_local_id)
                # end if
            elif photosize_source == PhotoFileId.PHOTOSIZE_SOURCE_STICKERSET_THUMBNAIL:
                sticker_set_id = struct.unpack('<q', buffer.read(8))[0]
                sticker_set_access_hash = struct.unpack('<q', buffer.read(8))[0]
                location_local_id = struct.unpack('<l', buffer.read(4))[0]
                photosize = PhotoFileId.PhotosizeSourceStickersetThumbnail(volume_id=volume_id, sticker_set_id=sticker_set_id, sticker_set_access_hash=sticker_set_access_hash, location_local_id=location_local_id)
            # end if

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

    def recalculate(self) -> str:
        """ Recalculates the file_id """
        return self.to_file_id(recalculate=True)
    # end def

    def to_file_id(self, *, recalculate: bool = False, version: Union[int, None] = None, sub_version: Union[int, None] = None) -> str:
        """
        Get a file_id.
        If we already have a cached one present (and `force_recalculate` is False), we will return that one instead.
        :param recalculate: if we should force a new calculation of it. Optional, default is False (unless it wasn't cached before, or the version differs).
        :param version:
        :param sub_version:
        :return:
        """
        if version and self.version != version:
            # version is different, we need to calculate it.
            return self.calculate_file_id(version=version, sub_version=sub_version)
        # end if
        if sub_version and self.sub_version != sub_version:
            # version is different, we need to calculate it.
            return self.calculate_file_id(version=version, sub_version=sub_version)
        # end if

        if not recalculate and not self.file_id:
            self.file_id = self.calculate_file_id()
        # end if
        return self.file_id
    # end def

    def calculate_file_id(self, *, version: Union[int, None] = None, sub_version: Union[int, None] = None) -> str:
        """
        Calculates a new file id from our fields.

        :param version: supply a different version
        :param sub_version: supply a different version
        :return:
        """
        if not version:
            version = self.version
        # end if
        if not sub_version:
            sub_version = self.sub_version
        # end if
        assert (version, sub_version) in self.SUPPORTED_VERSIONS

        type_id = self.type_id
        if self.file_reference:
            type_id |= self.TYPE_ID_FILE_REFERENCE_FLAG
        # end if
        if self.has_web_location:
            type_id |= self.TYPE_ID_WEB_LOCATION_FLAG
        # end if

        file_id = b''
        file_id += struct.pack('<LL', type_id, self.dc_id)
        if self.file_reference:
            file_id += pack_tl_string(self.file_reference)
        # end if
        if self.has_web_location:
            assert isinstance(self, WebLocationFileId)
            file_id += pack_tl_string(self.url)
            file_id += struct.pack('<iq', self.access_hash)
            return base64url_encode(rle_encode(file_id))
        # end if

        file_id += struct.pack('<qq', self.id, self.access_hash)

        if self.type_id <= self.TYPE_PHOTO:
            assert isinstance(self, PhotoFileId)
            file_id += struct.pack('<q', self.photosize.volume_id)  # Long
            if self.version >= 4:
                file_id += struct.pack('<L', self.photosize.type_id)  # V
            # end if
            if self.photosize.type_id == self.PHOTOSIZE_SOURCE_LEGACY:
                assert isinstance(self.photosize, PhotoFileId.PhotosizeSourceLegacy)
                file_id += struct.pack('<q', self.photosize.volume_id)  # Long
            elif self.photosize.type_id == self.PHOTOSIZE_SOURCE_THUMBNAIL:
                assert isinstance(self.photosize, PhotoFileId.PhotosizeSourceThumbnail)
                file_id += struct.pack('<L', self.photosize.file_type)
                file_id += pack_null_terminated_string(self.photosize.thumbnail_type)
            elif self.photosize.type_id in (self.PHOTOSIZE_SOURCE_DIALOGPHOTO_BIG, self.PHOTOSIZE_SOURCE_DIALOGPHOTO_SMALL):
                assert isinstance(self.photosize, (PhotoFileId.PhotosizeSourceDialogPhotoBig, PhotoFileId.PhotosizeSourceDialogPhotoSmall))
                assert isinstance(self.photosize, PhotoFileId.PhotosizeSourceDialogPhoto)
                file_id += struct.pack('<q', self.photosize.dialog_id)
                file_id += struct.pack('<q', self.photosize.dialog_access_hash)
            elif self.photosize.type_id == self.PHOTOSIZE_SOURCE_STICKERSET_THUMBNAIL:
                assert isinstance(self.photosize, PhotoFileId.PhotosizeSourceStickersetThumbnail)
                file_id += struct.pack('<q', self.photosize.sticker_set_id)
                file_id += struct.pack('<q', self.photosize.sticker_set_access_hash)
            # end if
            file_id += struct.pack('<l', self.photosize.location_local_id)
        # end if
        if version >= 4:
            file_id += chr(sub_version).encode()
        # end if
        file_id += chr(version).encode()
        return base64url_encode(rle_encode(file_id))
    # end def

    def __repr__(self) -> str:
        return "FileId(file_id={file_id!r}, type_id={type_id!r}, type_generic={type_generic!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, version={version!r}, owner_id={owner_id!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_generic=self.type_generic, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, version=self.version,
            owner_id=self.owner_id,
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
    TYPE_AUDIO = 9
    TYPE_SONG = TYPE_AUDIO
    TYPE_ANIMATION = 10
    TYPE_ENCRYPTED_THUMBNAIL = 11
    TYPE_WALLPAPER = 12
    TYPE_VIDEO_NOTE = 13
    TYPE_SECURE_RAW = 14
    TYPE_SECURE = 15
    TYPE_BACKGROUND = 16
    TYPE_SIZE = 17
    TYPE_NONE = 18

    SUPPORTED_VERSIONS: Tuple[Tuple[int, int], ...] = (
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

    TYPES: Dict[int, str] = {
        FileId.TYPE_VOICE: "voice", FileId.TYPE_VIDEO: "video", FileId.TYPE_DOCUMENT: "document",
        FileId.TYPE_STICKER: "sticker", FileId.TYPE_AUDIO: "song", FileId.TYPE_VIDEO_NOTE: "video note",
        FileId.TYPE_ANIMATION: "animation",
    }
    """ A human readable string of the type """

    def swap_type_sticker(self) -> str:
        """
        This swaps out the document types "document" <-> "sticker". Modifies the underlying data.
        :return: new file id
        :rtype: str
        """

        self.change_type(FileId.TYPE_STICKER if self.type_id == FileId.TYPE_DOCUMENT else FileId.TYPE_DOCUMENT)
        return self.recalculate()
    # end def

    def change_type(self, type_id: int):
        """
        Changes the type of the document to the given type

        :param type_id:
        :return:
        """
        self.type_detailed = DocumentFileId.TYPES[self.type_id]  # this raises KeyError if it isn't a valid type.
        self.type_id = type_id
        return self.recalculate()
    # end def

    @classmethod
    def from_file_id(cls: Type[CLASS], file_id, decoded: Union[None, bytes] = None) -> Union[FileId, CLASS]:
        """
        :param file_id:
        :param decoded:
        :return:
        """
        return FileId.from_file_id(file_id=file_id, decoded=decoded)
    # end def

    def __repr__(self) -> str:
        return "DocumentFileId(file_id={file_id!r}, type_id={type_id!r}, type_generic={type_generic!r}, type_detailed={type_detailed!r}, dc_id={dc_id!r}, id={id!r}, access_hash={access_hash!r}, version={version!r}, owner_id={owner_id!r})".format(
            file_id=self.file_id, type_id=self.type_id, type_generic=self.type_generic, type_detailed=self.type_detailed,
            dc_id=self.dc_id, id=self.id, access_hash=self.access_hash, owner_id=self.owner_id, version=self.version,
        )
    # end def __repr__
# end class DocumentFileId


class WebLocationFileId(object):  # TODO make proper (FileId) subclass:
    def __init__(
        self,
        file_id, type_id, has_reference, has_web_location,
        file_reference,
        url, access_hash,
    ):
        # super().__init__(
        #     file_id=file_id,
        #     type_id=type_id,
        #     has_reference=has_reference,
        #     file_reference=file_reference,
        #     has_web_location=has_web_location,
        # )
        self.file_id = file_id
        self.type_id = type_id
        self.has_reference = has_reference
        self.has_web_location = has_web_location
        self.file_reference = file_reference
        self.url = url
        self.access_hash = access_hash
    # end def __init__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
    # end def __repr__

    def __str__(self) -> str:
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

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}(type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r})"
        # end def __repr__

        def __str__(self) -> str:
            return self.__repr__()
        # end def __str__
    # end class PhotosizeSource

    class PhotosizeSourceLegacy(PhotosizeSource):
        def __init__(self, volume_id: int, location_local_id: int, secret):
            self.secret = secret
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_LEGACY, volume_id=volume_id, location_local_id=location_local_id)
        # end def __init__

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}(type_id={self.type_id!r}, volume_id={self.volume_id!r}, location_local_id={self.location_local_id!r}, secret={self.secret})"
        # end def __repr__
    # end class PhotosizeSourceLegacy

    class PhotosizeSourceThumbnail(PhotosizeSource):
        def __init__(self, volume_id: int, location_local_id: int, file_type, thumbnail_type):
            self.file_type = file_type
            self.thumbnail_type = thumbnail_type
            super().__init__(PhotoFileId.PHOTOSIZE_SOURCE_THUMBNAIL, volume_id=volume_id, location_local_id=location_local_id)
        # end def __init__

        def __repr__(self) -> str:
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

        def __repr__(self) -> str:
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

        def __repr__(self) -> str:
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

    TYPES: Dict[int, str] = {FileId.TYPE_THUMBNAIL: "thumbnail", FileId.TYPE_PROFILE_PHOTO: "profile picture", FileId.TYPE_PHOTO: "photo"}
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
    def from_file_id(cls: Type[CLASS], file_id, decoded: Union[None, bytes] = None) -> Union[FileId, CLASS]:
        return FileId.from_file_id(file_id=file_id, decoded=decoded)
    # end def

    def __repr__(self) -> str:
        return f"PhotoFileId(" \
               f"file_id={self.file_id!r}, type_id={self.type_id!r}, type_generic={self.type_generic!r}, " \
               f"type_detailed={self.type_detailed!r}, dc_id={self.dc_id!r}, id={self.id!r}, " \
               f"access_hash={self.access_hash!r}, location={self.has_web_location!r}, version={self.version!r}, " \
               f"owner_id={self.owner_id!r}" \
               f")"
    # end def __str__
# end class PhotoFileId
