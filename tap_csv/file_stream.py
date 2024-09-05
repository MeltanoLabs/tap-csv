"""Stream class for file-based streams."""

from __future__ import annotations

import abc
import os
import typing as t
from functools import cached_property

import fsspec
from singer_sdk.streams import Stream


class FileStream(Stream, metaclass=abc.ABCMeta):
    """Abstract class for file streams."""

    def __init__(self, filesystem: str, *args, options: dict[str, t.Any], **kwargs):
        """Init CSVStram."""
        # cache file_config so we dont need to go iterating the config list again later
        self.file_config = kwargs.pop("file_config")
        self.fs: fsspec.AbstractFileSystem = fsspec.filesystem(filesystem, **options)
        self._file_paths: list[str] = []

        super().__init__(*args, **kwargs)

    def _get_recursive_file_paths(self, file_path: str) -> list:
        file_paths = []

        for dirpath, _, filenames in self.fs.walk(file_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if self.is_valid_filename(file_path):
                    file_paths.append(file_path)

        return file_paths

    def get_file_paths(self) -> list[str]:
        """Return a list of file paths to read.

        This tap accepts file names and directories so it will detect
        directories and iterate files inside.
        """
        # Cache file paths so we dont have to iterate multiple times
        if self._file_paths:
            return self._file_paths

        file_path = self.file_config["path"]
        if not self.fs.exists(file_path):
            errmsg = f"File path does not exist {file_path}"
            raise Exception(errmsg)

        file_paths = []
        if self.fs.isdir(file_path):
            clean_file_path = os.path.normpath(file_path) + os.sep
            file_paths = self._get_recursive_file_paths(clean_file_path)

        elif self.is_valid_filename(file_path):
            file_paths.append(file_path)

        if not file_paths:
            msg = f"Stream '{self.name}' has no acceptable files"
            raise RuntimeError(msg)

        self._file_paths = file_paths

        return self._file_paths

    def get_all_field_names(self) -> list[str]:
        """Return a set of all field names, including metadata columns.

        If metadata columns are enabled, they will be **prepended** to the list.
        """
        fields = list(self.field_names)
        if self.include_metadata_columns:
            fields = [*self.metadata_fields, *fields]

        return fields

    @cached_property
    def include_metadata_columns(self) -> bool:
        """Return a boolean of whether to include metadata columns."""
        return self.config.get("add_metadata_columns", False)

    @property
    def metadata_fields(self) -> t.Iterable[str]:
        """Get an iterable of metadata columns names."""
        return []

    def get_metadata_columns_schemas(self) -> t.Iterable[tuple[str, dict]]:
        """Get an iterable of metadata columns names and schemata."""
        return []

    @property
    @abc.abstractmethod
    def field_names(self) -> t.Sequence[str]:
        """A sequence of field names for the stream."""
        ...

    @abc.abstractmethod
    def get_schema(self) -> dict:
        """Return the schema for a particular file stream."""
        ...

    @abc.abstractmethod
    def is_valid_filename(self, file_path: str) -> bool:
        """Return a boolean of whether the file name is valid for the format."""
        ...

    @abc.abstractmethod
    def get_rows(self, file_path: str) -> t.Iterable[list]:
        """Return a generator of the rows in a particular file."""
        ...

    @cached_property
    def schema(self) -> dict:
        """Return dictionary of record schema.

        Dynamically detect the json schema for the stream.
        This is evaluated prior to any records being retrieved.
        """
        _schema = self.get_schema()

        # If enabled, add file's metadata to output
        if self.include_metadata_columns:
            metadata_schema = self.get_metadata_columns_schemas()
            _schema["properties"].update(dict(metadata_schema))

        return _schema
