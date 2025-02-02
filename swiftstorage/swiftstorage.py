# Copyright (c) 2025 Sean Yeatts, Inc. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
import os
import shutil
from abc import ABC as Abstract
from abc import abstractmethod
from typing import Callable, List

# IMPORT ( PROJECT )
from .utilities import *


# CORE CLASS
class Storage:
    """
    Storage
    =======
    A conceptual container representing a datastore. Configurable to handle
    local or remote services ( ex. AWS S3 ).
    
    By default, Storage objects are configured as local datastores. Filepaths
    are always evaluated relative to the Storage root if a path argument is
    not specified for a given method.
    """

    # INTRINSIC METHODS
    def __init__(self, root: str, specification: StorageSpecification = None):
        self.stream = Stream()
        
        # Initialize specification
        self._specification = specification or LocalSpecification()
        self._specification.bind(self)

        # Clean up root directory
        self.root = self._delimit(root)
        self.specification.make(self.root)

    # SPECIFICATION PROPERTY
    @property
    def specification(self):
        return self._specification
    
    @specification.setter
    def specification(self, value: StorageSpecification):
        message = "A Storage object's specification is immutable. Instead, create a new Storage object."
        raise RuntimeError(message)

    # INTROSPECTIVE METHODS
    def contains(self, file: str) -> bool:
        """Checks whether a file exists within the datastore."""
        return self.specification.contains(file)
    
    def files(self, folder: str = None, subfolders: bool = False) -> list[str]:
        """Returns a list of all files contained within a folder."""
        path = self.format_path(folder or self.root)
        return self.specification.files(path, subfolders)

    def size(self) -> tuple[float, str]:
        """Returns the total size of the datastore. Returns a tuple containing
        the result and its unit suffix."""
        return self.specification.size()

    # FILE MANIPULATION
    def move(self, file: str, destination: Storage, rename: str = None,
        overwrite: bool = True) -> bool:
        """Transfers a file to another datastore. The original file is NOT preserved."""
        if self.copy(file, destination, rename, overwrite):
            self.delete(file)

    def copy(self, file: str, destination: Storage, rename: str = None,
        overwrite: bool = True) -> bool:
        """Transfers a file to another datastore. The original file is preserved."""
        path = self.format_path(file)
        if not self.contains(path):
            print(f"failed to locate file: {file}")
            return False
        return self.specification.copy(file, destination, (rename or file), overwrite)

    def delete(self, file: str) -> bool:
        """Deletes a file from the datastore. Returns True if the file was removed."""
        path = self.format_path(file)
        if not self.contains(path):
            print(f"failed to locate file: {file}")
            return False
        self.specification.delete(path)
        return True
    
    # FOLDER MANIPULATION
    def make(self, folder: str) -> None:
        """Creates a new folder."""
        path = self.format_path(folder)
        self.specification.make(path)

    def purge(self, folder: str = None) -> None:
        """Deletes all files and subfolders from a folder."""
        path = self.format_path(folder or self.root)
        self.specification.purge(path)

    def remove(self, folder: str = None) -> None:
        """Removes a folder from the datastore."""
        path = self.format_path(folder or self.root)
        self.specification.remove(path)

    # DATA STREAMING METHODS
    def download(self, file: str) -> bytes:
        """Streams a file from the datastore."""
        path = self.format_path(file)
        return self.specification.download(path)

    def upload(self, stream: bytes, rename: str, overwrite: bool = True) -> bool:
        """Streams a file to the datastore."""
        path = self.format_path(rename)
        return self.specification.upload(stream, path, overwrite)

    # HELPER METHODS
    def format_path(self, path: str) -> str:
        """Performs standard formatting operations for filepath arguments."""
        delimitted = self._delimit(path)
        return self._make_relative(delimitted)

    def _make_relative(self, path: str) -> str:
        """Formats a raw path to become relative to the Storage root."""
        return str(self.root + self.specification.delimiter + path)
    
    def _delimit(self, path: str) -> str:
        """Replaces delimiter symbols in the provided path using the correct
        symbol according to the StorageSpecification."""
        replacement: str = None
        match self.specification.delimiter:
            case '\\':
                replacement = '/'
            case '/':
                replacement = '\\'
        return path.replace(replacement, self.specification.delimiter)


# DATA STREAMING
class Stream:
    """The transmission channel through which a Storage object's data transfer
    operations are performed."""

    # INTRINSIC METHODS
    def __init__(self):
        self.callbacks: List[Callable[[float]]] = []

    # TELEMETRY METHODS
    def connect(self, progress_hook: Callable[[float]] = None) -> None:
        """Binds a callback function to the stream."""
        if not progress_hook:
            return
        if progress_hook in self.callbacks:
            return
        self.callbacks.append(progress_hook)

    def disconnect(self, progress_hook: Callable[[float]]) -> None:
        """Unbinds a callback function from the stream."""
        if not progress_hook in self.callbacks:
            return
        self.callbacks.remove(progress_hook)

    # PRIVATE METHODS
    def partition(self, file_size: float, increments: int = 5, limit: int = 10) -> bytes:
        """Computes the size ( bytes ) of a single streamable chunk based on
        a file's size and a specified number of divisions ( increments ). Returns
        the smaller value between the actual chunk size or the maximum allowable
        size ( limit )."""
        calculated  = file_size // increments
        allowable   = limit * 1000000   # convert megabytes --> bytes
        chunk = min(calculated, allowable)
        return chunk
    
    def on_chunk_processed(self, current: int, total: int) -> None:
        """Runs when a chunk is processed."""
        percent = current / total * 100
        percent = round(percent, 3)
        # print(f"{current} / {total} - {percent}%")
        for callback in self.callbacks:
            callback(percent)


# SPECIFICATIONS
class StorageSpecification(Abstract):
    """A collection of properties and methods that define the behavior of a
    Storage object."""

    # CLASS ATTRIBUTES
    delimiter: str = "\\"   # some architectures use different delimiting characters

    # INTRINSIC METHODS
    def __init__(self):
        super().__init__()
        self.storage: Storage = None

    # SETUP METHODS
    def bind(self, storage: Storage) -> None:
        """Creates a link to the reference Storage object."""
        self.storage = storage

    # INTROSPECTIVE METHODS
    @abstractmethod
    def contains(self, file: str) -> bool: ...

    @abstractmethod
    def files(self, folder: str, subfolders: bool = False) -> list[str]: ...

    @abstractmethod
    def size(self) -> tuple[float, str]: ...

    # FILE MANIPULATION
    @abstractmethod
    def copy(self, file: str, destination: Storage, rename: str, overwrite: bool) -> bool: ...

    @abstractmethod
    def delete(self, file: str) -> None: ...

    # FOLDER MANIPULATION
    @abstractmethod
    def make(self, folder: str) -> None: ...

    @abstractmethod
    def purge(self, folder: str) -> None: ...

    @abstractmethod
    def remove(self, folder: str) -> None: ...

    # DATA STREAMING METHODS
    @abstractmethod
    def download(self, file: str) -> bytes: ...

    @abstractmethod
    def upload(self, stream: bytes, rename: str, overwrite: bool) -> bool: ...


class LocalSpecification(StorageSpecification):
    """Represents a datastore that exists on the local machine."""
    
    # CLASS ATTRIBUTES
    delimiter: str = "\\"

    # INTROSPECTIVE METHODS
    def contains(self, file):
        super().contains(file)
        return os.path.exists(file)

    def files(self, folder, subfolders = False):
        super().files(folder, subfolders)
        results: list[str] = []
        if subfolders:  # we want to include subfolders
            for root, _, files in os.walk(folder):
                for file in files:
                    results.append(os.path.join(root, file))
        else:           # we don't want to include subfolders
            for file in os.listdir(folder):
                path = os.path.join(folder, file)
                if os.path.isfile(path):
                    results.append(path)
        return results

    def size(self):
        super().size()
        total: float = 0.0
        files = self.storage.files(subfolders=True)
        for file in files:
            total += os.path.getsize(file)
        return pretty_print_bytes(total)

    # FILE MANIPULATION
    def copy(self, file, destination, rename, overwrite):
        super().copy(file, destination, rename, overwrite)

        # [1] Are we allowed to overwrite?
        if destination.contains(rename) and not overwrite:
            print(f"prevented overwrite: {rename}")
            return False
        
        # [2] TBD - progress signal hookup

        # [3] Perform transfer operation
        if (data := self.storage.download(file)):
            return destination.upload(data, rename, overwrite)
        return

    def delete(self, file):
        super().delete(file)    
        print(f"deleting file: {file}")
        os.remove(file)

    # FOLDER MANIPULATION
    def make(self, folder):
        super().make(folder)
        if os.path.exists(folder):
            return
        print(f"creating folder: {folder}")
        os.makedirs(folder)
    
    def purge(self, folder):
        print(f"clearing folder: {folder}")
        super().purge(folder)
        for item in os.listdir(folder):
            path = os.path.join(folder, item)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    def remove(self, folder):
        super().remove(folder)
        print(f"removing folder: {folder}")
        shutil.rmtree(folder)

    # DATA STREAMING METHODS
    def download(self, file):
        super().download(file)
        print(f"preparing file download: {file}")

        # [1] Is this a valid file within the datastore?
        if not self.storage.contains(file):
            print(f"failed to locate file: {file}")
            print(file)
            return None

        # [2] Is this file empty?
        if (size := os.path.getsize(file)) == 0:
            print(f"cannot process empty file: {file}")
            return None
        
        # [3] Calculate chunk size & print info
        chunk_size              = self.storage.stream.partition(size)
        formatted_file_size     = pretty_print_bytes(size)
        formatted_chunk_size    = pretty_print_bytes(chunk_size)
        print(f"file size ({formatted_file_size[1]}): {formatted_file_size[0]}")
        print(f"chunk size ({formatted_chunk_size[1]}): {formatted_chunk_size[0]}")

        # [4] Perform download operation
        try:
            print('downloading...')
            progress = 0
            datastream = bytearray()
            with open(file, 'rb') as target:
                while True:
                    if not (chunk := target.read(chunk_size)):
                        break
                    progress += len(chunk)
                    datastream.extend(chunk)
                    self.storage.stream.on_chunk_processed(progress, size)
                print('download complete!')
                return datastream
        except Exception as exception:
            print(f"error downloading file: '{file}'")
            print(exception)
            return None
    
    def upload(self, stream, rename, overwrite):
        super().upload(stream, rename, overwrite)
        print(f"preparing file upload: {rename}")

        # [1] Is the stream empty?
        if (size := len(stream)) <= 0:
            print(f"cannot process empty stream: '{rename}'")
            return None
        
        # [2] Calculate chunk size & print info
        chunk_size              = self.storage.stream.partition(size)
        formatted_file_size     = pretty_print_bytes(size)
        formatted_chunk_size    = pretty_print_bytes(chunk_size)
        print(f"file size ({formatted_file_size[1]}): {formatted_file_size[0]}")
        print(f"chunk size ({formatted_chunk_size[1]}): {formatted_chunk_size[0]}")

        # [3] Perform upload operation
        try:
            print('uploading...')
            progress = 0
            with open(rename, 'wb') as target:
                while progress < size:
                    remaining = size - progress
                    current = min(chunk_size, remaining)
                    chunk = stream[progress:progress + current]
                    target.write(chunk)
                    progress += current
                    self.storage.stream.on_chunk_processed(progress, size)
                print('upload complete!')
                return True
        except Exception as exception:
            print(f"error uploading file: '{rename}'")
            print(exception)
            return False
