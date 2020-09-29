from .file_id import (
    FileId, base64url_decode, base64url_encode, rle_decode, rle_encode, pack_tl_string,
    unpack_tl_string, WebLocationFileId, PhotoFileId,
)

import struct
import logging
from io import BytesIO, SEEK_END
from typing import Union, Type, TypeVar

from luckydonaldUtils.exceptions import assert_type_or_raise

logger = logging.getLogger(__name__)
CLASS = TypeVar('CLASS')

class FileUniqueId(object):
    # type: def __init__(self, type_id: int, id: int, unique_id: Union[str, None]): pass
    # type: def __init__(self, type_id: int, volume_id: int, local_id: int, unique_id: Union[str, None]): pass
    # type: def __init__(self, type_id: int, url: str, unique_id: Union[str, None]): pass
    def __init__(self, type_id: int, id: Union[int, None] = None, volume_id: Union[int, None] = None,
                 local_id: Union[int, None] = None, url: Union[str, None] = None, _unique_id: Union[str, None] = None):
        """
        :param type_id: Number describing the type. See `type_detailed` for a human readable string
        :type  type_id: int

        :param type_detailed: a human readable string of the type
        :type  type_detailed: str

        :param id: The file id (long)
        :type  id: int

        :param url: url
        :type  url: str | None

        :param _unique_id: Original file_unique_id
        :type  _unique_id: str

        :return:
        :rtype:
        """
        self.unique_id = _unique_id
        self.type_id = type_id
        self.type_detailed = self.TYPES[type_id]
        self.url = url
        self.volume_id = volume_id
        self.local_id = local_id
        self.id = id
    # end def __init__

    @property
    def owner_id(self):
        return (self.id & (((1 << 24) - 1) << 32)) // 2 ** 32
        # last 4 bits of that, parsed as '<I' basically.
    # end def

    @classmethod
    def from_unique_id(cls, unique_id, decoded=None):
        """

        :param unique_id:
        :param decoded: if the file_id binary data is already decoded (rle + base64url).
        :except ValueError: Unknown type id.
        :return:
        """
        if not decoded:
            decoded = rle_decode(base64url_decode(unique_id))
        # end if
        logger.debug(f'parsing unique_id {unique_id!r}')

        buffer = BytesIO(decoded)
        type_id = struct.unpack('<i', buffer.read(4))[0]
        if type_id not in cls.TYPES:
            raise ValueError(f"Type is invalid: {type_id}")
        # end if
        if type_id == cls.TYPE_WEB:
            url = unpack_tl_string(buffer)
            file_id_obj = FileUniqueId(type_id=type_id, url=url, _unique_id=unique_id)
        elif len(decoded) - 4 == 12:
            volume_id = struct.unpack('<q', buffer.read(8))[0]
            local_id = struct.unpack('<l', buffer.read(4))[0]
            file_id_obj = FileUniqueId(type_id=type_id, volume_id=volume_id, local_id=local_id, _unique_id=unique_id)
        else:
            media_id = struct.unpack('<q', buffer.read(8))[0]
            file_id_obj = FileUniqueId(type_id=type_id, id=media_id, _unique_id=unique_id)
        # end if

        end_position = buffer.tell()
        buffer.seek(0, SEEK_END)
        stuff_left = buffer.tell() - end_position
        if stuff_left > 0:
            logger.warning(f'Found {stuff_left} leftover data.')
        # end if

        return file_id_obj
    # end def

    def __repr__(self):
        return "FileUniqueId(unique_id={unique_id!r}, type_id={type_id!r}, type_detailed={type_detailed!r}, id={id!r}, volume_id={volume_id!r}, local_id={local_id!r}, id={id!r}, owner_id={owner_id!r})".format(
            unique_id=self.unique_id, type_id=self.type_id, type_detailed=self.type_detailed,
            id=self.id,
            volume_id=self.volume_id, local_id=self.local_id,
            owner_id=self.owner_id,
        )
    # end def __str__

    def to_unique_id(self) -> str:
        assert self.type_id in self.TYPES
        binary = b''
        binary += struct.pack('<l', self.type_id)
        if self.type_id == self.TYPE_WEB:
            binary += pack_tl_string(self.url)
        elif self.type_id == self.TYPE_PHOTO:
            binary += struct.pack('<ql', self.volume_id, self.local_id)
        else:
            binary += struct.pack('<Q', self.id)
        # end if

        return base64url_encode(rle_encode(binary))
    # end def

    @classmethod
    def from_file_id(cls: Type[CLASS], file_id: Union[str, FileId, WebLocationFileId]) -> CLASS:
        assert_type_or_raise(file_id, str, FileId, parameter_name="file_id")
        if isinstance(file_id, str):
            file_id = FileId.from_file_id(file_id)
        # end if
        unique_type_id = cls.FULL_TO_UNIQUE_MAP[file_id.type_id]
        if unique_type_id == cls.TYPE_WEB:
            assert_type_or_raise(file_id, WebLocationFileId, parameter_name="file_id of type FileUniqueId.TYPE_WEB")
            unique_id_obj = FileUniqueId(type_id=unique_type_id, url=file_id.url, _unique_id=None)
        elif unique_type_id == cls.TYPE_PHOTO:
            assert_type_or_raise(file_id, PhotoFileId, parameter_name="file_id of type FileUniqueId.TYPE_PHOTO")
            file_id: PhotoFileId
            unique_id_obj = FileUniqueId(
                type_id=unique_type_id,
                volume_id=file_id.photosize.volume_id, local_id=file_id.photosize.location_local_id,
                _unique_id=None
            )
        else:
            unique_id_obj = FileUniqueId(type_id=unique_type_id, id=file_id.id, _unique_id=None)
        # end if

        return unique_id_obj
    # end def

    TYPE_WEB = 0
    TYPE_PHOTO = 1
    TYPE_DOCUMENT = 2
    TYPE_SECURE = 3
    TYPE_ENCRYPTED = 4
    TYPE_TEMP = 5

    TYPES = (
        TYPE_WEB, TYPE_PHOTO, TYPE_DOCUMENT, TYPE_SECURE, TYPE_ENCRYPTED, TYPE_TEMP,
    )

    FULL_TO_UNIQUE_MAP = {
        FileId.TYPE_PHOTO: TYPE_PHOTO,
        FileId.TYPE_PROFILE_PHOTO: TYPE_PHOTO,
        FileId.TYPE_THUMBNAIL: TYPE_PHOTO,
        FileId.TYPE_ENCRYPTED_THUMBNAIL: TYPE_PHOTO,
        FileId.TYPE_WALLPAPER: TYPE_PHOTO,

        FileId.TYPE_VIDEO: TYPE_DOCUMENT,
        FileId.TYPE_VOICE: TYPE_DOCUMENT,
        FileId.TYPE_DOCUMENT: TYPE_DOCUMENT,
        FileId.TYPE_STICKER: TYPE_DOCUMENT,
        FileId.TYPE_AUDIO: TYPE_DOCUMENT,
        FileId.TYPE_ANIMATION: TYPE_DOCUMENT,
        FileId.TYPE_VIDEO_NOTE: TYPE_DOCUMENT,
        FileId.TYPE_BACKGROUND: TYPE_DOCUMENT,

        FileId.TYPE_SECURE: TYPE_SECURE,
        FileId.TYPE_SECURE_RAW: TYPE_SECURE,

        FileId.TYPE_ENCRYPTED: TYPE_ENCRYPTED,

        FileId.TYPE_TEMP: TYPE_TEMP,
    }
# end class FileId
