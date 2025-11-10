SwiftStorage
============
*Copyright (c) 2025 Sean Yeatts. All rights reserved.*

A simple way to interact with local and remote file systems. Easily extendable to support custom endpoints.


Key Features
------------
- High level methods provide intuitive ways to move, copy, and delete files / folders with minimal code.
- Low level methods provide injection points for middleman services ( ex. data encryption ).
- Hook into data streams to monitor progress; useful for GUI apps that incorporate progress bars.


Quickstart
----------
Key ``import`` statements :

.. code:: python

  from swiftstorage import Storage, StreamBuffer
  from swiftstorage.classes import LocalSpecification, RemoteSpecification

**Example** - a simple script that transfers a file between two endpoints :

.. code:: python

    # IMPORTS
    from swiftstorage import Storage
    
    
    # MAIN DEFINITION
    def main() -> None:
    
        TEST_FOLDER: str = "tests/sandbox"
    
        # [1] Prepare endpoints
        disk = Storage(f"{TEST_FOLDER}/local", create=True)
        cloud = Storage(f"{TEST_FOLDER}/remote", create=True)
    
        # [2] Backup data to cloud
        if not disk.copy(cloud, "test.txt", overwrite=True):
            raise RuntimeError("cloud backup failed")
    
    
    # ENTRY POINT
    if __name__ == "__main__":
        main()


**Example** - adding callbacks to gain insight into transfer status :

.. code:: python

    # IMPORTS
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


**Example** - introducing a middleman service :

.. code:: python

    # IMPORTS
    from uuid import uuid4
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


Installation
------------
**Prerequisites:**

- Python 3.13 or higher is recommended
- pip 24.0 or higher is recommended

**For a pip installation:**

Open a new Command Prompt. Run the following command:

.. code:: sh

  py -m pip install swiftstorage

**For a local installation:**

Extract the contents of this module to a safe location. Open a new terminal and navigate to the top level directory of your project. Run the following command:

.. code:: sh

  py -m pip install "DIRECTORY_HERE\swiftstorage\dist\swiftstorage-1.0.0.tar.gz"

- ``DIRECTORY_HERE`` should be replaced with the complete filepath to the folder where you saved the SwiftStorage module contents.
- Depending on the release of SwiftStorage you've chosen, you may have to change ``1.0.0`` to reflect your specific version.
