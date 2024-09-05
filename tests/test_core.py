"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

import os

from singer_sdk.testing import get_tap_test_class

from tap_csv.tap import TapCSV

TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__))

TestTapCSV = get_tap_test_class(
    TapCSV,
    config={
        "files": [
            {
                "entity": "test",
                "path": f"{TEST_DATA_DIR}/data/alphabet.csv",
                "keys": [],
            },
        ],
    },
)


TestTapCSVEncoding = get_tap_test_class(
    TapCSV,
    config={
        "files": [
            {
                "entity": "test",
                "path": f"{TEST_DATA_DIR}/data/alphabet_encoding.csv",
                "keys": [],
                "encoding": "latin1",
            },
        ],
    },
)


TestCSVDialect = get_tap_test_class(
    TapCSV,
    config={
        "files": [
            {
                "entity": "test",
                "path": f"{TEST_DATA_DIR}/data/alphabet_encoding.csv",
                "keys": [],
                "delimiter": ",",
                "doublequote": True,
                "escapechar": "^",
                "quotechar": '"',
                "skipinitialspace": True,
                "strict": True,
            },
        ],
    },
)


TestTapCSVMetadataCols = get_tap_test_class(
    TapCSV,
    config={
        "add_metadata_columns": True,
        "files": [
            {
                "entity": "test",
                "path": f"{TEST_DATA_DIR}/data/alphabet.csv",
                "keys": [],
            },
        ],
    },
)
