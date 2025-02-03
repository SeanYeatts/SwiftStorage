SwiftStorage
============

*Copyright (c) 2025 Sean Yeatts, Inc. All rights reserved.*

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

  from swiftstorage import Storage

**Example** - a simple script that transfers a file between two directories on the user's local machine :

.. code:: python

  # IMPORTS
  from swiftstorage import Storage


  # MOCKUP FUNCTIONS
  def monitor_download(percent: float) -> None:
      print(f"downloaded: {percent}%")
  
  def monitor_upload(percent: float) -> None:
      print(f"uploaded: {percent}%")


  # MAIN DEFINITION
  def main() -> None:
      
      # [1] Prepare datastores using basic paths
      source      = Storage(fr"cache\folder-1")
      destination = Storage(fr"cache\folder-2")
  
      # [2] ( OPTIONAL ) Hook into data streams to monitor transfer progress
      source.stream.connect(monitor_download)
      destination.stream.connect(monitor_upload)
  
      # [3] Perform a simple copy ( + rename ) operation
      file    = "test-file.jpg"
      renamed = "test-file-copy.jpg"
      source.copy(file, destination, renamed, overwrite=True)
  
  
  # ENTRY POINT
  if __name__ == "__main__":
      main()


Installation
------------
**Prerequisites:**

- Python 3.8 or higher is recommended
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

