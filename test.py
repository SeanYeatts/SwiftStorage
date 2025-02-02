# Copyright (c) 2025 Sean Yeatts, Inc. All rights reserved.

from __future__ import annotations


# IMPORTS ( PROJECT )
import sys

# IMPORTS ( PROJECT )
from swiftstorage import Storage


# MAIN DEFINITION
def main(args: list[str]) -> None:
    
    server  = Storage(fr"cache\server")
    client  = Storage(fr"cache\client")

    file = "test-file.jpg"

    server.stream.connect(monitor)
    client.stream.connect(monitor)

    data = server.download(file)
    client.upload(data, file)


def monitor(percent: float) -> None:
    print(f"monitor: {percent}%")


# ENTRY POINT
if __name__ == "__main__":
    main(sys.argv[1:])
