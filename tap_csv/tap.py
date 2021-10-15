"""CSV tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_csv.client import CSVStream


class TapCSV(Tap):
    """CSV tap class."""

    name = "tap-csv"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "files",
            th.ArrayType(
                th.ObjectType(
                    th.Property("entity", th.StringType, required=True),
                    th.Property("path", th.StringType, required=True),
                    th.Property("keys", th.ArrayType(th.StringType), required=True),
                )
            ),
            required=True,
            description="An array of csv file stream settings.",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [
            CSVStream(
                tap=self,
                name=file_config.get("entity"),
                file_config=file_config,
            )
            for file_config in self.config["files"]
        ]


if __name__ == "__main__":
    TapCSV.cli()
