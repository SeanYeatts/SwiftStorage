# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from abc import ABC as Abstract
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

# IMPORTS ( MODULE )
from swiftstorage.core.stream import StorageStream
from swiftstorage.utilities.logging import log

if TYPE_CHECKING:
    from swiftstorage.swiftstorage import Storage


# CLASSES
@dataclass(frozen=True)
class StorageSpecification(Abstract):
    """Provides implementation details for a Storage object."""

    delim: str
    max_chunk_size: Optional[float] = 1.0 # megabytes

    # STREAMING METHODS
    @abstractmethod
    def upload(self, datastore: Storage, stream: StorageStream, data: bytes, filename: str) -> bool:
        log.info(f"uploading file: {filename}")

    @abstractmethod
    def download(self, datastore: Storage, stream: StorageStream, filename: str) -> bytes:
        log.info(f"downloading file: {filename}")

    # FILE METHODS
    @abstractmethod
    def delete(self, filename: str) -> bool:
        log.info(f"deleting file: {filename}")

    # FOLDER METHODS
    @abstractmethod
    def create(self, folder: str) -> bool:
        log.info(f"creating folder: {folder}")

    @abstractmethod
    def remove(self, folder: str) -> bool:
        log.info(f"removing folder: {folder}")

    # INTROSPECTIVE METHODS
    @abstractmethod
    def contains(self, path: str) -> bool: ...

    @abstractmethod
    def files(self, path: str, subfolders: bool) -> list[str]: ...

    @abstractmethod
    def folders(self, path: str, subfolders: bool) -> list[str]: ...

    @abstractmethod
    def paths(self, path: str, subfolders: bool) -> list[str]: ...

    # HELPER METHODS
    @abstractmethod
    def validate(self, root: str) -> bool: ...
