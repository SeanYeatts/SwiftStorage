# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
import os
import shutil
from dataclasses import dataclass

# IMPORTS ( MODULE )
from swiftstorage.core.specification import StorageSpecification
from swiftstorage.core.stream import StreamBuffer
from swiftstorage.utilities.helpers import PrettyPrint
from swiftstorage.utilities.logging import log


# CLASSES
@dataclass(frozen=True)
class LocalSpecification(StorageSpecification):
    """Represents a datastore on the local machine."""

    delim: str = "\\"

    # STREAMING METHODS
    def upload(self, datastore, stream, data, filename):
        super().upload(datastore, stream, data, filename)
    
        # [1] Calculate chunk size
        if not (file_size := len(data)) > 0:
            message = "cannot upload empty file"
            log.error(message)
            raise Exception(message)

        chunk_size = stream.segment(file_size)

        pretty_file_size = PrettyPrint.format_bytes(file_size)
        pretty_chunk_size = PrettyPrint.format_bytes(chunk_size)

        log.debug(f"file size: {pretty_file_size.number} {pretty_file_size.units}")
        log.debug(f"chunk size: {pretty_chunk_size.number} {pretty_chunk_size.units}")

        # [2] Perform upload operation
        log.debug("uploading...")
        buffer = StreamBuffer(filename, file_size)
        try:
            with open(filename, 'wb') as file:
                progress: int = 0
                while progress < file_size:
                    remaining = file_size - progress
                    current = min(chunk_size, remaining)
                    chunk = data[progress:progress + current]
                    file.write(chunk)
                    progress += current
                    buffer.current = progress
                    stream.on_chunk_uploaded(buffer)
                    buffer.step += 1
            log.debug("upload complete!")
            return True
        except Exception as error:
            log.error(f"error uploading file: {filename}")
            log.error(error)
            return None
    
    def download(self, datastore, stream, filename):
        super().download(datastore, stream, filename)
    
        # [1] Calculate chunk size
        if not (file_size := os.path.getsize(filename)) > 0:
            message = "cannot download empty file"
            log.error(message)
            raise Exception(message)

        chunk_size = stream.segment(file_size)

        pretty_file_size = PrettyPrint.format_bytes(file_size)
        pretty_chunk_size = PrettyPrint.format_bytes(chunk_size)

        log.debug(f"file size: {pretty_file_size.number} {pretty_file_size.units}")
        log.debug(f"chunk size: {pretty_chunk_size.number} {pretty_chunk_size.units}")

        # [2] Perform download operation
        log.debug("downloading...")
        datastream = bytearray()
        buffer = StreamBuffer(filename, file_size)
        try:
            with open(filename, 'rb') as file:
                progress: int = 0
                while True:
                    if not (chunk := file.read(chunk_size)):
                        break
                    progress += len(chunk)
                    datastream.extend(chunk)
                    buffer.current = progress
                    stream.on_chunk_downloaded(buffer)
                    buffer.step += 1
            log.debug("download complete!")
            return datastream
        except Exception as error:
            log.error(f"error downloading file: {file}")
            log.error(error)
            return None
    
    # FILE METHODS
    def delete(self, filename):
        super().delete(filename)
        os.remove(filename)
        return True

    # FOLDER METHODS
    def create(self, folder):
        super().create(folder)
        if os.path.exists(folder):
            return
        os.makedirs(folder)
        return True
    
    def remove(self, folder):
        super().remove(folder)
        shutil.rmtree(folder)
        return True
    
    # INTROSPECTIVE METHODS
    def contains(self, path):
        super().contains(path)
        return os.path.exists(path)
    
    def files(self, path, subfolders):
        super().files(path, subfolders)
        result: list[str] = []
        if subfolders:
            for root, dirs, files in os.walk(path):
                for file in files:
                    result.append(os.path.join(root, file))
        else:
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if os.path.isfile(full_path):
                    result.append(full_path)
        return result
    
    def folders(self, path, subfolders):
        super().folders(path, subfolders)
        result: list[str] = []
        if subfolders:
            for root, dirs, files in os.walk(path):
                for folder in dirs:
                    result.append(os.path.join(root, folder))
        else:
            for f in os.listdir(path):
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    result.append(full_path)
        return result
    
    def paths(self, path, subfolders):
        super().paths(path, subfolders)
        result: list[str] = []
        if subfolders:
            for root, dirs, files in os.walk(path):
                for folder in dirs:
                    result.append(os.path.join(root, folder))
                for file in files:
                    result.append(os.path.join(root, file))
        else:
            for file in os.listdir(path):
                result.append(os.path.join(path, file))
        return result

    # HELPER METHODS
    def validate(self, root):
        super().validate(root)
        return os.path.exists(root)
