# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from dataclasses import dataclass
from typing import Callable, Optional


# CLASSES
class StorageStream:
    
    # INTRINSIC METHODS
    def __init__(self, max_chunk_size: float):
        self.upload = StreamDispatcher()
        self.download = StreamDispatcher()
        self.max_chunk_size = max_chunk_size # megabytes

    def segment(self, file_size: float, scale: Optional[float] = 0.25) -> int:
        """Computes the size ( bytes ) of a streamable chunk based on a file's size
        and a target segment size ( percent ). Uses the smaller value between the
        computed chunk size and the prescribed chunk limit ( megabytes )."""

        # NOTE: We try to calculate a chunk size by using a percentage of the file
        # size (defined by the "segment" parameter). If this is larger than our
        # configured limit, we instead default to our limit.

        ceiling = self.max_chunk_size * 1000000 # convert megabytes --> bytes
        calculated = file_size * scale

        minimum: int = 1
        if (size := min(ceiling, calculated)) >= minimum:
            return int(size) # cast to int
        else:
            return minimum

    # PUBLIC METHODS
    def on_chunk_uploaded(self, buffer: StreamBuffer) -> None:
        """Responds to a chunk upload step."""
        self.upload.dispatch(buffer)
    
    def on_chunk_downloaded(self, buffer: StreamBuffer) -> None:
        """Responds to a chunk download step."""
        self.download.dispatch(buffer)


@dataclass
class StreamBuffer:
    """Characterizes the contents of a stream."""
    filename:   str                 # the name of the file
    total:      int                 # file size ( bytes )
    current:    Optional[int] = 0   # total chunks processed ( bytes )
    step:       Optional[int] = 0   # number of chunks procesed


class StreamDispatcher:
    """Handles callback registration & notifications for a data stream."""

    # INTRINSIC METHODS
    def __init__(self):
        self.callbacks: list[Callable[[StreamBuffer], None]] = []

    # PUBLIC METHODS
    def connect(self, callback: Callable[[StreamBuffer], None]) -> None:
        if not callback in self.callbacks:
            self.callbacks.append(callback)

    def disconnect(self, callback: Callable[[StreamBuffer], None]) -> None:
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def dispatch(self, data: StreamBuffer) -> None:
        for callback in self.callbacks:
            callback(data)
