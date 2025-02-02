# Copyright (c) 2024 Sean Yeatts. All rights reserved.

from __future__ import annotations


# IMPORTS ( EXTERNAL )
import yaml

# IMPORTS ( STANDARD )
import json
import base64
from abc import ABC as Abstract
from abc import abstractmethod
from typing import Any


# CONSTANTS
ENCODING_STANDARD: str = 'utf-8'


# CLASSES
class Serializer(Abstract):
    """Interface for the storage & retrieval of data encoded in bytes."""
    
    # CONVERSION METHODS
    @abstractmethod
    def encode(self, data: Any) -> bytes:
        """Converts structured data to a binary format."""
        ... # extended by subclasses

    @abstractmethod
    def decode(self, binary: bytes) -> Any:
        """Converts binary data to a structured format."""
        ... # extended by subclasses

    # STRUCTURED STORAGE METHODS
    @abstractmethod
    def save(self, data: Any, file: str) -> None:
        """Saves structured data to a file."""
        ... # extended by subclasses

    @abstractmethod
    def load(self, file: str) -> Any:
        """Loads structured data from a file."""
        ... # extended by subclasses

    # BINARY STORAGE METHODS
    def serialize(self, binary: bytes, file: str) -> None:
        """Saves binary data to a file."""
        with open(file, 'wb') as target:
            target.write(binary)

    def deserialize(self, file: str) -> bytes:
        """Loads binary data from a file."""
        with open(file, 'rb') as target:
            binary = target.read()
        return binary
    
    # HELPER METHODS
    def flatten(self, data: Any) -> dict:
        """Deconstructs nested data into single key-value pairs."""
        
        result = {}

        def traverse(source, old_key=[]) -> dict:
            """Recursively traverses nested structures."""
            for key, value in source.items():           # for each item
                new_key = old_key + [key]               # update current key path
                if isinstance(value, dict):             # if we're still seeing a dictionary...
                    nesting = traverse(value, new_key)  # go one deeper
                    result.update(nesting)              # when we get back out, overwrite entry
                else:
                    result[tuple(new_key)] = value      # ...otherwise create entry
            return result
        
        return traverse(data)
    
    def fold(self, data: Any) -> dict:
        """Reconstructs nested data from single key-value pairs."""
        
        result = {}
    
        def insert(level, keys, value):
            """Injects a value into a nested dictionary structure."""
            if isinstance(keys, tuple):                 # if the key is a tuple...
                for key in keys[:-1]:                   # get all parent keys
                    level = level.setdefault(key, {})   # initialize a dict
                level[keys[-1]] = value                 # set the value of the final key
            else:
                level[keys] = value                     # ...otherwise set value directly

        for keys, value in data.items():                # for every entry in our dataset
            if isinstance(value, dict):                 # if the value is a dictionary...
                nested_dict = self.fold(value)          # recursively fold
                insert(result, keys, nested_dict)       # insert folded result
            else:
                insert(result, keys, value)             # ...otherwise insert value directly

        return result

    def pack(self, data: Any, file: str) -> None:
        """Folds and saves structured data to a file."""
        folded = self.fold(data)
        self.save(folded, file)

    def unpack(self, file: str) -> dict:
        """Loads and flattens structured data from a file."""
        data = self.load(file)
        return self.flatten(data)


class JSONSerializer(Serializer):

    # OVERRIDDEN METHODS : Serializer
    def encode(self, data: Any) -> bytes:
        super().encode(data)
        string  = json.dumps(data)
        encoded = string.encode(ENCODING_STANDARD)
        stream  = base64.b64encode(encoded)
        return stream
    
    def decode(self, binary: bytes) -> Any:
        super().decode(binary)
        stream  = base64.b64decode(binary)
        decoded = stream.decode(ENCODING_STANDARD)
        data    = json.loads(decoded)
        return data
    
    def save(self, data: Any, file: str) -> None:
        super().save(data, file)
        with open(file, 'w') as target:
            json.dump(data, target, sort_keys=False, indent=4)

    def load(self, file: str) -> Any:
        super().load(file)
        with open(file, 'r') as target:
            data = json.load(target)
        return data


class YAMLSerializer(Serializer):

    # OVERRIDDEN METHODS : Serializer
    def encode(self, data: Any) -> bytes:
        super().encode(data)
        string  = yaml.dump(data)
        encoded = string.encode(ENCODING_STANDARD)
        stream  = base64.b64encode(encoded)
        return stream
    
    def decode(self, binary: bytes) -> Any:
        super().decode(binary)
        stream  = base64.b64decode(binary)
        decoded = stream.decode(ENCODING_STANDARD)
        data    = yaml.safe_load(decoded)
        return data
    
    def save(self, data: Any, file: str) -> None:
        super().save(data, file)
        with open(file, 'w') as target:
            yaml.dump(data, target, sort_keys=False)

    def load(self, file: str) -> Any:
        super().load(file)
        with open(file, 'r') as target:
            data = yaml.safe_load(target)
        return data
