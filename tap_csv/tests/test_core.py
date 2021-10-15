"""Tests standard tap features using the built-in SDK tests library."""

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
