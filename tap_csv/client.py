"""Custom client handling, including CSVStream base class."""

from __future__ import annotations

import csv
import typing as t

from .file_stream import FileStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class CSVStream(FileStream):
    """Stream class for CSV streams."""

    def get_records(self, context: Context | None) -> t.Iterable[dict]:
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
                    "Filesystem implementation for %s does not support modified time, skipping",
                    self.fs.protocol,
                )
                file_last_modified = None

            file_lineno = -1

            for row in self.get_rows(file_path):
                file_lineno += 1

                if not file_lineno:
                    continue

                if self.config.get("add_metadata_columns", False):
                    row = [file_path, file_last_modified, file_lineno, *row]

                yield dict(zip(self.header, row))

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
