# Copyright (c) 2025 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( MODULE )
from swiftstorage import Storage, StreamBuffer
from swiftstorage.utilities.logging import log


# MOCKUP FUNCTIONS
def display_progress(buffer: StreamBuffer):
    """Placeholder stream progress tracker."""
    progress = buffer.current / buffer.total * 100
    formatted = f"{round(progress, 2)} % ({buffer.current}/{buffer.total} bytes)"
    log.info(f"step: [{buffer.step}] {formatted}")


# MAIN DEFINITION
def main() -> None:

    TEST_FOLDER: str = "tests/sandbox"

    # [1] Prepare endpoints
    disk = Storage(f"{TEST_FOLDER}/local", create=True)
    cloud = Storage(f"{TEST_FOLDER}/remote", create=True)

    # [2] ( OPTIONAL ) Hook into transfer streams ( for the directions we care about )
    disk.stream.download.connect(display_progress)
    cloud.stream.upload.connect(display_progress)

    # [3] Backup data to cloud
    if not disk.copy(cloud, "test.txt", overwrite=True):
        raise RuntimeError("cloud backup failed")

    # [4] If necessary, release stream observers
    disk.stream.download.disconnect(display_progress)
    cloud.stream.upload.disconnect(display_progress)


# ENTRY POINT
if __name__ == "__main__":
    main()
