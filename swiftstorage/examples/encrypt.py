# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( STANDARD )
from uuid import uuid4

# IMPORTS ( MODULE )
from swiftstorage import Storage


# MOCKUP FUNCTIONS
def encrypt(data: bytes) -> tuple[bytes, str]:
    """Placeholder mock encryption service."""
    return data, str(uuid4()).upper() + ".bin"


# MAIN DEFINITION
def main() -> None:

    TEST_FOLDER: str = "tests/sandbox"

    # [1] Prepare endpoints
    disk = Storage(f"{TEST_FOLDER}/local", create=True)
    cloud = Storage(f"{TEST_FOLDER}/cloud", create=True)

    # [2] Download data from source
    if not (data := disk.download("test.txt")):
        raise RuntimeError("failed to download file")
    
    # [2] Inject middleman service ( ex: encryption )
    encrypted, renamed = encrypt(data)

    # [4] Upload transformed data to destination
    if not cloud.upload(encrypted, renamed, overwrite=True):
        raise RuntimeError("cloud backup failed")


# ENTRY POINT
if __name__ == "__main__":
    main()
