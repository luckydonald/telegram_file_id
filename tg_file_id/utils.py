#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import struct
from io import BytesIO, SEEK_CUR
from typing import Union

from luckydonaldUtils.encoding import to_unicode
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


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


def unpack_null_terminated_string(buffer: Union[BytesIO, bytes, bytearray], as_string: bool = False) -> Union[str, bytes]:
    """
    Unpack a null terminated (\0) string.
    :param buffer: Input buffer. Needs support for `.read(1)`.
    :param as_string: if we should return it as utf-8 decoded `str` instead of `bytes`.
    :return: The unpacked string.
    """
    if isinstance(buffer, (bytes, bytearray)):
        buffer = BytesIO(buffer)
    # end if

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

