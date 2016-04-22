"""
Data Files Management
===================

This module provides some helper functions to manage files.
"""

import os
import logging


from digs.exc import InvalidChunkSizeError
from digs.common.actions import GetDataChunk, FindOffsetsFASTQ, ChunkOffsets
from digs.messaging.protocol import DigsProtocolParser


logger = logging.getLogger(__name__)

transient_parser = DigsProtocolParser()


@transient_parser.register_handler(GetDataChunk)
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

    with open(file_path, 'rb') as f:
        f.seek(chunk_start)
        chunk_data = f.read(chunk_end-chunk_start)

        protocol._stream_writer.write(chunk_data)
        await protocol._stream_writer.drain()


def _calculate_fastq_offsets(fh, chunk_size=64):
    """Parses a FASTQ file and determines proper splitting byte offsets,
    while keeping the records complete. This function does not do a lot of
    error checking: we assume the file is properly formatted.

    It simply checks if a line starts with a '@', which indicates the start
    of a new record, see if we exceed the current chunk size, and store the
    chunk start and end positions when necessary.

    :param fh: Open file handle to the FASTQ file
    :type fh: file
    :param chunk_size: Approximate size of each chunk in MB
    :type chunk_size: int
    """
    fh.seek(0)
    current_chunk_start = 0

    # Cannot use normal iteration, because then telling the cursor position
    # is disabled
    while True:
        # Ok, we've come across a quality score header, now parse the
        # quality scores until the next record.
        pos = fh.tell()
        line = fh.readline()

        if not line:
            # EOF
            break

        if line.startswith('@'):
            current_chunk_size = pos - current_chunk_start

            if current_chunk_size >= chunk_size * 1024**2:
                yield (current_chunk_start, pos)
                current_chunk_start = pos


@transient_parser.register_handler(FindOffsetsFASTQ)
async def find_offsets_fastq(protocol, action):
    """Determine sensible byte offsets for splitting up a fastq file,
    while maintaining the records."""

    file_path = action['file_path']

    with open(file_path) as f:
        chunks = list(_calculate_fastq_offsets(f))

        action = ChunkOffsets(offsets=chunks)
        await protocol.send_action(action)
