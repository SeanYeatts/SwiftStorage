# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from typing import Type

# IMPORTS ( MODULE )
from swiftstorage import Storage, StorageSpecification
from swiftstorage.classes import LocalSpecification, RemoteSpecification
from swiftstorage.utilities.logging import log


# MOCKUP CLASSES
class S3Specification(RemoteSpecification):

    delim: str = "/"
    
    def upload(self, datastore, stream, data, filename):
        return super().upload(datastore, stream, data, filename)
    
    def download(self, datastore, stream, filename):
        return super().download(datastore, stream, filename)
    
    def delete(self, filename):
        return super().delete(filename)
    
    def create(self, folder):
        return super().create(folder)

    def remove(self, folder):
        return super().remove(folder)

    def contains(self, path):
        return super().contains(path)
    
    def files(self, path, subfolders):
        return super().files(path, subfolders)
    
    def folders(self, path, subfolders):
        return super().folders(path, subfolders)
    
    def paths(self, path, subfolders):
        return super().paths(path, subfolders)
    
    def validate(self, root):
        return super().validate(root)


class AzureSpecification(RemoteSpecification):

    delim: str = "/"

    def upload(self, datastore, stream, data, filename):
        return super().upload(datastore, stream, data, filename)
    
    def download(self, datastore, stream, filename):
        return super().download(datastore, stream, filename)
    
    def delete(self, filename):
        return super().delete(filename)
    
    def create(self, folder):
        return super().create(folder)

    def remove(self, folder):
        return super().remove(folder)

    def contains(self, path):
        return super().contains(path)
    
    def files(self, path, subfolders):
        return super().files(path, subfolders)
    
    def folders(self, path, subfolders):
        return super().folders(path, subfolders)
    
    def paths(self, path, subfolders):
        return super().paths(path, subfolders)
    
    def validate(self, root):
        return super().validate(root)


# MAIN DEFINITION
def main() -> None:

    TEST_FOLDER: str = "tests/sandbox"

    # [1] Prepare endpoint configurations
    endpoints: dict[str, Type[StorageSpecification]] = {
        "local": LocalSpecification,
        "cloud": S3Specification,
        "backup": AzureSpecification,
    }

    # [2] Construct a singular datastore interface
    storage = Storage(TEST_FOLDER, create=True)

    # [3] Propagate an operation to all endpoints
    for alias, endpoint in endpoints.items():
        log.info(f"initializing new endpoint: {alias}")
        storage.spec = endpoint() # re-configure Storage with new endpoint
        storage.create("test-folder")


# ENTRY POINT
if __name__ == "__main__":
    main()
