"""
Data Files Management
===================

This module provides some helper functions to manage files.
"""
import os
import logging

from digs.exc import InvalidChunkSizeError
from digs.data_node.actions import (parser, HeartBeat, GetDataChunk)


logger = logging.getLogger(__name__)


@parser.register_handler(GetDataChunk)
async def get_data_chunk(protocol, action):
    """Get a specific substring of a data file. Returned value in bytes.

    :param file_path: path to file
    :param chunk_start: starting chunk position
    :param chunk_end: ending chunk position
    """

    file_path = action['file_path']
    chunk_start = action['chunk_start']
    chunk_end = action['chunk_end']

    file_size = os.stat(file_path).st_size
    if file_size < chunk_end:
        raise InvalidChunkSizeError(
            "File does not contain this chunk size."
        )
    if chunk_start >= chunk_end:
        raise InvalidChunkSizeError(
            "Invalid chunk size (zero or smaller)."
        )

    f = open(file_path, 'rb')
    f.seek(chunk_start)
    chunk_data = f.read(chunk_end-chunk_start)

    return chunk_data




