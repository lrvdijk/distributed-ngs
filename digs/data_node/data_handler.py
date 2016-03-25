"""
Data Files Management
===================

This module provides some helper functions to manage files.
"""
import os
from digs.exc import InvalidChunkSizeError

def get_data_chunk(file_path, chunk_start, chunk_end):
    """Get a specific substring of a data file. Returned value in bytes.

    :param file_path: path to file
    :param chunk_start: starting chunk position
    :param chunk_end: ending chunk position
    """
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




