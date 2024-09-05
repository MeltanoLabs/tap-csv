"""Custom client handling, including CSVStream base class."""

from __future__ import annotations

import csv
import sys
import typing as t
from functools import cached_property

from singer_sdk import typing as th

from .file_stream import FileStream

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

SDC_SOURCE_FILE_COLUMN = "_sdc_source_file"
SDC_SOURCE_LINENO_COLUMN = "_sdc_source_lineno"
SDC_SOURCE_FILE_MTIME_COLUMN = "_sdc_source_file_mtime"


class CSVStream(FileStream):
    """Stream class for CSV streams."""

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        """Initialize CSVStream."""
        super().__init__(*args, **kwargs)

    @cached_property
    def primary_keys(self) -> list[str]:
        """Return the primary keys for the stream."""
        return self.file_config.get("keys", [])

    def get_records(self, context: Context | None) -> t.Iterable[dict]:  # noqa: ARG002
        """Return a generator of row-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        for file_path in self.get_file_paths():
            self.logger.info("Reading file at %s", file_path)
            try:
                file_last_modified = self.fs.modified(file_path)
            except NotImplementedError:
                self.logger.warning(
                    "Filesystem implementation for %s does not support modified time, "
                    "skipping",
                    self.fs.protocol,
                )
                file_last_modified = None

            file_lineno = -1

            for row in self.get_rows(file_path):
                file_lineno += 1

                if not file_lineno:
                    continue

                if self.include_metadata_columns:
                    row = [file_path, file_last_modified, file_lineno, *row]

                yield dict(zip(self.get_all_field_names(), row))

    @cached_property
    def metadata_fields(self) -> tuple[str, ...]:
        """Generate metadata columns names."""
        return (
            SDC_SOURCE_FILE_COLUMN,
            SDC_SOURCE_FILE_MTIME_COLUMN,
            SDC_SOURCE_LINENO_COLUMN,
        )

    def get_metadata_columns_schemas(self) -> t.Generator[tuple[str, dict], None, None]:
        """Get schema for metadata columns."""
        yield SDC_SOURCE_FILE_COLUMN, {"type": "string"}
        yield (
            SDC_SOURCE_FILE_MTIME_COLUMN,
            {"type": ["string", "null"], "format": "date-time"},
        )
        yield SDC_SOURCE_LINENO_COLUMN, {"type": "integer"}

    @override
    @cached_property
    def field_names(self) -> list[str]:
        """Return a sequence of field names for the stream."""
        for file_path in self.get_file_paths():
            for row in self.get_rows(file_path):
                return row

        return []

    @override
    def get_schema(self) -> dict:
        """Return the schema for a particular file stream."""
        props = [th.Property(col, th.StringType) for col in self.field_names]
        return th.PropertiesList(*props).to_dict()

    @override
    def is_valid_filename(self, file_path: str) -> bool:
        """Return a boolean of whether the file includes CSV extension."""
        is_valid = True
        if file_path[-4:] != ".csv":
            is_valid = False
            self.logger.warning(
                "Skipping non-csv file '%s', please provide a CSV file that ends with "
                "'.csv'; e.g. 'users.csv'",
                file_path,
            )
        return is_valid

    @override
    def get_rows(self, file_path: str) -> t.Iterable[list]:
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
        with self.fs.open(file_path, mode="r", encoding=encoding) as f:
            yield from csv.reader(f, dialect="tap_dialect")
