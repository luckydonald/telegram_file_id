#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct

from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from sticker_tag.api_utils import (
    rle_decode, base64url_decode, FileId, PhotoFileId, DocumentFileId, logger,
    base64url_encode, rle_encode,
)

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if


def debug_file_id(file_id):
    msg = "Input: {f}"
    try:
        decoded, info_array = take_apart_file_id(file_id)
    except ValueError:
        msg += 'Checksum wrong.'
        return msg
    msg += 'Bytes: {bytes!r}\n'.format(bytes=list(decoded))
    msg += 'Type: {type_detailed} ({type_id})\n'.format(**info_array)
    msg += 'File: id {id} on DC {dc_id} with access hash {access_hash}\n'.format(**info_array)
    if "location" in info_array:
        msg += 'Location: volume_id {volume_id}, local_id {local_id}, secret {secret}\n'.format(**info_array["location"])
    # end if
    if "owner_id" in info_array and info_array["owner_id"]:
        msg += 'Owner: id {owner_id}\n'.format(**info_array)
    # end if
    return msg
# end def


def take_apart_file_id(file_id, force_owner=False):
    """

    :param file_id:
    :param force_owner: If we should try to decode the owner, even if we can't be sure that it is valid.
    :return:
    """
    decoded = rle_decode(base64url_decode(file_id))
    version = struct.unpack("<b", decoded[-1:])[0]
    if version not in FileId.SUPPORTED_VERSIONS:
        raise ValueError(f'Unsupported file_id version: {version}')
    # end if
    type_id = None
    if version in FileId.SUPPORTED_VERSIONS:
        type_id = struct.unpack("<i", decoded[0:4])[0]
    # end if
    data = {"file_id": file_id, "type_id": type_id, "owner_id": None, "version": version}
    if type_id in PhotoFileId.TYPES:  # 0, 2
        if version == 2:
            # AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABLefjdP8kuxqa7ABAAEC via @teleflaskBot
            type_id, dc_id, id, access_hash, location_volume_id, location_secret, location_local_id, checksum = struct.unpack('<iiqqqqib', decoded)
        elif version == 4:
            # AgADAgADRaoxG64rCUlfm3fj3nihW3PHUQ8ABAEAAwIAA3gAA2uwAQABFgQ via @teleflaskBot
            type_id, dc_id, id, access_hash, location_volume_id, location_secret, something, location_local_id, twentytwo, checksum = struct.unpack('<iiqqqqiibb', decoded)
            data['something'] = something  # TODO.
            if twentytwo != 22:
                raise ValueError(f"Strange field expected to be 22.")
            # end if
        else:
            raise ValueError(f'Unsupported file_id version for image type {type_id}: {version}')
        # end if
        if checksum != version:
            raise ValueError(f"Version expected to be {version}")
        # end if
        data.update(dict(
            type="photo", type_detailed="thumbnail" if type_id == 0 else "photo", dc_id=dc_id, id=id,
            access_hash=access_hash,
            location=dict(volume_id=location_volume_id, secret=location_secret, local_id=location_local_id)
        ))
    elif type_id in DocumentFileId.TYPES:  # 3, 4, 5, 8, 9
        if version == 2:
            # CAADBAADwwADmFmqDf6xBrPTReqHAg sticker, @teleflaskBot
            type_id, dc_id, id, access_hash, checksum = struct.unpack('<iiqqb', decoded)
        elif version == 4:
            # CAADBAADwwADmFmqDf6xBrPTReqHFgQ sticker, @teleflaskBot
            type_id, dc_id, id, access_hash, twentytwo, checksum = struct.unpack('<iiqqbb', decoded)
            if twentytwo != 22:
                raise ValueError(f"Strange field expected to be 22.")
            # end if
        else:
            raise ValueError(f'Unsupported file_id version for document type {type_id}: {version}')
        # end if
        if checksum != version:
            raise ValueError(f"Version expected to be {version}")
        # end if
        data.update(dict(
            type="document", type_detailed=DocumentFileId.TYPES[type_id], dc_id=dc_id, id=id, access_hash=access_hash
        ))
    else:
        logger.warning("Found new type: {type} in {file_id}".format(type=type_id, file_id=file_id))
    # end if
    if force_owner or (version in (2, 4) and type_id == DocumentFileId.TYPE_STICKER):
        # at some point version 2 files stopped having that information, but they removed that without a version bump, so we can't really say.
        # now only stickers have valid information in there.
        position = 40 if len(decoded) in [54,] else 12
        try:
            owner_id = struct.unpack("<I", decoded[position : position + 4])[0]
            data["owner_id"] = owner_id
        except struct.error:
            logger.warning("owner_id failed")
        # end try
    # end def
    return decoded, data
# end def


def put_together_file_id(data):
    if data["type"] == "photo":
        assert data["type_id"] in PhotoFileId.TYPES
        if data["version"] == 2:
            binary = struct.pack(
                '<iiqqqqib',
                # type, dc_id, id,
                data["type_id"], data["dc_id"], data["id"] if "id" in data else 0,
                # access_hash,
                data["access_hash"] if "access_hash" in data else 0,
                # location_volume_id, location_secret,
                data["location"]["volume_id"], data["location"]["secret"],
                # location_local_id,
                data["location"]["local_id"],
                # version
                2
            )
        elif data["version"] == 4:
            binary = struct.pack(
                # , location_local_id, twentytwo, checksum = struct.unpack(, decoded)
                '<iiqqqqiibb',
                # type, dc_id, id,
                data["type_id"], data["dc_id"], data["id"] if "id" in data else 0,
                # access_hash,
                data["access_hash"] if "access_hash" in data else 0,
                # location_volume_id, location_secret,
                data["location"]["volume_id"], data["location"]["secret"],
                # something,
                data["something"],
                #  location_local_id,
                data["location"]["local_id"],
                # twentytwo, version
                22, 4
            )
        else:
            raise ValueError(f'Unknown version to use: {data["version"]}')
        # end if
    else:  # document
        assert data["type_id"] in DocumentFileId.TYPES
        if data["version"] == 2:
            binary = struct.pack(
                "<iiqqb",
                # type, dc_id, id,
                data["type_id"], data["dc_id"], data["id"] if "id" in data else 0,
                # access_hash
                data["access_hash"] if "access_hash" in data else 0,
                # version
                2
            )
        elif data["version"] == 4:
            binary = struct.pack(
                "<iiqqbb",
                # type, dc_id, id,
                data["type_id"], data["dc_id"], data["id"] if "id" in data else 0,
                # access_hash,
                data["access_hash"] if "access_hash" in data else 0,
                # twentytwo, version
                22, 4
            )
        else:
            raise ValueError(f'Unknown version to use: {data["version"]}')
        # end if
    # end if
    return base64url_encode(rle_encode(binary))
# end def


def swap_sticker_type(data, as_sticker=None):
    """
    This swaps out the document types "document" <-> "sticker"

    :param data: Can be a dict as obtained by `take_apart_file_id(file_id)`.
                 Otherwise a file_id is assumed and said function `take_apart_file_id` is called.
    :type  data: dict or bytearray or bytes

    :param as_sticker: None: swap, True: Sticker, False: Document
    :type  as_sticker: None | bool

    :return: new file id
    :rtype: str
    """
    if not isinstance(data, dict):
        binary, data = take_apart_file_id(data)
    # end if
    assert isinstance(data, dict)
    assert data["type_id"] in (5, 8)  # document or sticker
    if as_sticker is None:
        # swap it
        data["type_id"] = 8 if data["type_id"] == 5 else 5
    else:
        # set it to either sticker (True) or document (False)
        data["type_id"] = 8 if as_sticker else 5
    # end if
    return put_together_file_id(data)
# end def
