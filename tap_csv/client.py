"""Custom client handling, including CSVStream base class."""

from __future__ import annotations

import csv
import os
import typing as t
from datetime import datetime, timezone
from functools import cached_property

from singer_sdk import typing as th
from singer_sdk.streams import Stream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

SDC_SOURCE_FILE_COLUMN = "_sdc_source_file"
SDC_SOURCE_LINENO_COLUMN = "_sdc_source_lineno"
SDC_SOURCE_FILE_MTIME_COLUMN = "_sdc_source_file_mtime"


class CSVStream(Stream):
    """Stream class for CSV streams."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Init CSVStram."""
        # cache file_config so we dont need to go iterating the config list again later
        self.file_config = kwargs.pop("file_config")
        self._file_paths: list[str] = []
        self._header: list[str] | None = None
        super().__init__(*args, **kwargs)

        self._primary_keys: list[str] = self.file_config.get("keys", [])

    def get_records(self, context: Context | None) -> t.Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        header = self.header
        for file_path in self.get_file_paths():
            file_last_modified = datetime.fromtimestamp(
                os.path.getmtime(file_path), timezone.utc
            )

            file_lineno = -1

            for row in self.get_rows(file_path):
                file_lineno += 1

                if not file_lineno:
                    continue

                if self.config.get("add_metadata_columns", False):
                    row = [file_path, file_last_modified, file_lineno, *row]

                yield dict(zip(header, row))

    def _get_recursive_file_paths(self, file_path: str) -> list:
        file_paths = []

        for dirpath, _, filenames in os.walk(file_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if self.is_valid_filename(file_path):
                    file_paths.append(file_path)

        return file_paths

    @property
    def file_paths(self) -> list[str]:
        """Return the file paths of the stream."""
        return self._file_paths

    @file_paths.setter
    def file_paths(self, paths: list[str]) -> None:
        """Set the file paths of the stream."""
        self._file_paths = paths

    def get_file_paths(self) -> list[str]:
        """Return a list of file paths to read.

        This tap accepts file names and directories so it will detect
        directories and iterate files inside.
        """
        # Cache file paths so we dont have to iterate multiple times
        if self.file_paths:
            return self.file_paths

        file_path = self.file_config["path"]
        if not os.path.exists(file_path):
            raise Exception(f"File path does not exist {file_path}")

        file_paths = []
        if os.path.isdir(file_path):
            clean_file_path = os.path.normpath(file_path) + os.sep
            file_paths = self._get_recursive_file_paths(clean_file_path)
        elif self.is_valid_filename(file_path):
            file_paths.append(file_path)

        if not file_paths:
            raise RuntimeError(
                f"Stream '{self.name}' has no acceptable files. \
                    See warning for more detail."
            )
        self.file_paths = file_paths
        return file_paths

    def is_valid_filename(self, file_path: str) -> bool:
        """Return a boolean of whether the file includes CSV extension."""
        is_valid = True
        if file_path[-4:] != ".csv":
            is_valid = False
            self.logger.warning(f"Skipping non-csv file '{file_path}'")
            self.logger.warning(
                "Please provide a CSV file that ends with '.csv'; e.g. 'users.csv'"
            )
        return is_valid

    def get_rows(self, file_path: str) -> t.Iterable[list[t.Any]]:
        """Return a generator of the rows in a particular CSV file."""
        encoding = self.file_config.get("encoding", None)
        csv.register_dialect(
            "tap_dialect",
            delimiter=self.file_config.get("delimiter", ","),
            doublequote=self.file_config.get("doublequote", True),
            escapechar=self.file_config.get("escapechar", None),
            quotechar=self.file_config.get("quotechar", '"'),
            skipinitialspace=self.file_config.get("skipinitialspace", False),
            strict=self.file_config.get("strict", False),
        )
        with open(file_path, encoding=encoding) as f:
            yield from csv.reader(f, dialect="tap_dialect")

    @property
    def header(self) -> list[str]:
        """Parse the header of the CSV file."""
        if self._header is not None:
            return self._header

        first_file = self.get_file_paths()[0]
        for row in self.get_rows(first_file):
            names = [str(col) for col in row]
            break

        if self.config.get("add_metadata_columns", False):
            names = [
                SDC_SOURCE_FILE_COLUMN,
                SDC_SOURCE_FILE_MTIME_COLUMN,
                SDC_SOURCE_LINENO_COLUMN,
                *names,
            ]
        self._header = names
        return names

    @cached_property
    def schema(self) -> dict:
        """Return dictionary of record schema.

        Dynamically detect the json schema for the stream.

        This property is accessed multiple times for each record
        so it's important to cache the result.
        """
        properties: list[th.Property] = []
        properties.extend(
            th.Property(column, th.StringType()) for column in self.header
        )
        # If enabled, add file's metadata to output
        if self.config.get("add_metadata_columns", False):
            properties.extend(
                (
                    th.Property(SDC_SOURCE_FILE_COLUMN, th.StringType),
                    th.Property(SDC_SOURCE_FILE_MTIME_COLUMN, th.DateTimeType),
                    th.Property(SDC_SOURCE_LINENO_COLUMN, th.IntegerType),
                )
            )

        return th.PropertiesList(*properties).to_dict()
