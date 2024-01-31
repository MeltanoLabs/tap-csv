"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

import os

from singer_sdk.testing import get_standard_tap_tests

from tap_csv.tap import TapCSV


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    test_data_dir = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_CONFIG = {
        "files": [
            {
                "entity": "test",
                "path": f"{test_data_dir}/data/alphabet.csv",
                "keys": [],
            }
        ]
    }
    tests = get_standard_tap_tests(TapCSV, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# Run standard built-in tap tests from the SDK, with different encoding:
def test_standard_tap_tests_encoding():
    """Run standard built-in tap tests from the SDK, with different encoding."""
    test_data_dir = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_CONFIG = {
        "files": [
            {
                "entity": "test",
                "path": f"{test_data_dir}/data/alphabet_encoding.csv",
                "keys": [],
                "encoding": "latin1",
            }
        ]
    }
    tests = get_standard_tap_tests(TapCSV, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# Run standard built-in tap tests from the SDK, with different CSV dialect settings:
def test_standard_tap_tests_csv_dialect():
    """Run standard built-in tap tests from the SDK.

    With different CSV dialect settings.
    """
    test_data_dir = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_CONFIG = {
        "files": [
            {
                "entity": "test",
                "path": f"{test_data_dir}/data/alphabet_encoding.csv",
                "keys": [],
                "delimiter": ",",
                "doublequote": True,
                "escapechar": "^",
                "quotechar": '"',
                "skipinitialspace": True,
                "strict": True,
            }
        ]
    }
    tests = get_standard_tap_tests(TapCSV, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# Run standard built-in tap tests from the SDK, with metadata columns included:
def test_standard_tap_tests_metadata_cols():
    """Run standard tap tests from the SDK, with metadata columns included."""
    test_data_dir = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_CONFIG = {
        "add_metadata_columns": True,
        "files": [
            {
                "entity": "test",
                "path": f"{test_data_dir}/data/alphabet.csv",
                "keys": [],
            }
        ],
    }
    tests = get_standard_tap_tests(TapCSV, config=SAMPLE_CONFIG)
    for test in tests:
        test()
