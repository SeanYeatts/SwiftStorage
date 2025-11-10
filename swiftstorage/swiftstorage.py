# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from pathlib import Path
from typing import Optional

# IMPORTS ( MODULE )
from swiftstorage.classes.local import LocalSpecification
from swiftstorage.core.specification import StorageSpecification
from swiftstorage.core.stream import StorageStream
from swiftstorage.utilities.logging import log


# WILDCARD SYMBOLS
__all__ = [
    "Storage",
]


# CLASSES
class Storage:
    """
    A conceptual container representing a datastore. Configurable to handle
    local or remote endpoints ( ex. AWS S3 ).
    
    By default, Storage objects are configured as local datastores.
    """

    # INTRINSIC METHODS
    def __init__(self, root: str, specification: Optional[StorageSpecification] = None, create: Optional[bool] = False):
        self.spec = specification if specification else LocalSpecification(max_chunk_size=10.0)
        self.root = self.delimit(root)
        self.stream = StorageStream(self.spec.max_chunk_size)

        self.constructed: bool = False
        if create and not self.validate():
            self.constructed = self.spec.create(self.root)

    # STREAMING METHODS
    def upload(self, data: bytes, filename: str, overwrite: Optional[bool] = False) -> bool:
        """Streams a file to the datastore."""
        absolute = self.relativize(filename)
        log.debug(f"preparing file upload: {filename}")

        # [1] Can we overwrite?
        if self.spec.contains(filename) and not overwrite:
            log.warning("overwrite prevented")
            return False

        # [2] Was the upload successful?
        if not (success := self.spec.upload(self, self.stream, data, absolute)):
            log.warning("upload failed")
        return success

    def download(self, filename: str) -> bytes:
        """Streams a file from the datastore."""
        absolute = self.relativize(filename)
        log.debug(f"preparing file download: {filename}")

        # [1] Can we find the source file?
        if not self.contains(filename):
            log.warning("file not found in datastore")
            return
        
        # [2] Was the download successful?
        if not (success := self.spec.download(self, self.stream, absolute)):
            log.warning("download failed")
        return success

    # FILE METHODS
    def move(self, destination: Storage, filename: str, rename: Optional[str] = None,
        overwrite: Optional[bool] = False) -> bool:
        """Transfers a file to another datastore. The original file is **NOT** preserved."""
        log.debug(f"moving file: {filename}")

        # [1] Was the copy successful?
        if not self.spec.copy(destination, filename, rename, overwrite):
            return False # if the copy failed, we don't want to delete the original
        
        # [2] Was the delete successful?
        if not (success := self.spec.delete(filename)):
            log.warning("source file was not deleted")
        return success

        # NOTE: ^ Unlikely to fail for offline transfers, but a possible condition for
        # dropped network connection during local-to-remote or remote-to-remote transfers.

    def copy(self, destination: Storage, filename: str, rename: Optional[str] = None,
        overwrite: Optional[bool] = False) -> bool:
        """Duplicates a file to another datastore. The original file is preserved."""
        log.debug(f"copying file: {filename}")
        renamed = rename if rename else filename

        # [1] Can we overwrite?
        if destination.contains(renamed) and not overwrite:
            log.warning("overwrite prevented")
            return False

        # [2] Was the download successful?
        if not (downloaded := self.download(filename)):
            return False
        
        # [3] Was the upload successful?
        return destination.upload(downloaded, renamed, overwrite)

    def delete(self, filename: str) -> bool:
        """Deletes a file from the datastore."""
        relative = self.relativize(filename)
        log.debug(f"preparing to delete file: {filename}")

        # [1] Is the file in the datastore?
        if not self.contains(filename):
            log.warning("file not found in datastore")
            return False

        # [2] Was the delete successful?
        return self.spec.delete(relative)

    # FOLDER METHODS
    def create(self, folder: str) -> bool:
        """Creates a folder in the datastore."""
        relative = self.relativize(folder)
        log.debug(f"preparing to create folder: {relative}")
        if self.contains(folder):
            log.debug("folder already exists")
            return False
        return self.spec.create(relative)

    def remove(self, folder: Optional[str] = None, forceful: Optional[bool] = False) -> bool:
        """Removes a folder from the datastore. If no path is provided, operates on
        the Storage root."""
        target = folder if folder else Path(self.root).name
        relative = self.relativize(target)
        log.debug(f"preparing to remove folder: {relative}")

        # [1] Can we ignore folder contents?
        if forceful:
            return self.spec.remove(relative)

        # [2] Get file count
        files = self.files(target, False)
        file_count = len(files)

        # [3] Get folder count
        folders = self.folders(target)
        folder_count = len(folders)

        # [4] Report search results
        if (file_count > 0) or (folder_count > 0):
            log.warning(f"removal prevented ( found {file_count + folder_count} times )")
            return False
        else:
            return self.spec.remove(relative)

    # HYBRID METHODS
    def purge(self, folder: Optional[str] = None, preview: Optional[bool] = False,
        brief: Optional[bool] = False) -> None:
        """Removes all files and destroys all subfolders contained within the path. If
        no path is provided, operates on the Storage root."""
        relative = self.relativize(folder)
        log.debug(f"preparing to purge folder: {relative}")
        preview_message = "identified for removal"

        # Remove folders - we do this first to auto-delete any files contained therein
        for target in self.folders(folder, subfolders=(preview and brief)):
            path = Path(target).relative_to(self.root)
            if preview:
                log.debug(f"{preview_message}: {path}")
            else:
                self.remove(str(path), forceful=True)

        # Remove remaining files
        for target in self.files(folder, subfolders=(preview and brief)):
            path = Path(target).relative_to(self.root)
            if preview:
                log.debug(f"{preview_message}: {path}")
            else:
                self.delete(str(path))

    # INTROSPECTIVE METHODS
    # NOTE: IN THEIR CURRENT STATE, THESE METHODS CAN BE EXPENSIVE FOR VERY LARGE DATASTORES!

    def contains(self, path: str) -> bool:
        """Checks whether a path ( file or folder ) exists within the datastore."""
        # return any(path in self.files() or path in self.folders()) <-- should we rely on internal methods?
        absolute = self.relativize(path)
        return self.spec.contains(absolute)

    def files(self, folder: Optional[str] = None, subfolders: Optional[bool] = False) -> list[str]:
        """Returns a list of all files contained within a folder. Optionally, include
        subfolders in the search. If no path is provided, operates on the Storage root."""
        target = self.relativize(folder)
        return self.spec.files(target, subfolders)

    def folders(self, folder: Optional[str] = None, subfolders: Optional[bool] = False) -> list[str]:
        """Returns a list of all folders contained within a folder. Optionally, include
        subfolders in the search. If no path is provided, operates on the Storage root."""
        target = self.relativize(folder)
        return self.spec.folders(target, subfolders)

    def paths(self, folder: Optional[str] = None, subfolders: Optional[bool] = False) -> list[str]:
        """Returns a list of all paths contained within a folder. Optionally, include 
        subfolders in the search. If no path is provided, operates on the Storage root."""
        target = self.relativize(folder)
        return self.spec.paths(target, subfolders)

    # HELPER METHODS    
    def validate(self) -> bool:
        """Checks whether the datastore root exists."""
        return self.spec.validate(self.root)

    def relativize(self, path: Optional[str] = None) -> str:
        """Formats the target path relative to the datastore root."""
        if not path:
            return self.root
        delimitted = self.delimit(path)
        return str(self.root + self.spec.delim + delimitted)
    
    def delimit(self, path: str) -> str:
        """Replaces delimiter symbols in the provided path using the correct symbol."""
        replacement: str = None
        match self.spec.delim:
            case '\\':
                replacement = '/'
            case '/':
                replacement = '\\'
        return path.replace(replacement, self.spec.delim)
