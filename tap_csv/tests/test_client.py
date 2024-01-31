"""Tests client methods."""

from __future__ import annotations

import os

from tap_csv.tap import CSVStream, TapCSV


def test_get_file_paths_recursively():
    """Test get file paths recursively."""
    test_data_dir = os.path.dirname(os.path.abspath(__file__))

    SAMPLE_CONFIG = {
        "files": [
            {
                "entity": "test",
                "path": f"{test_data_dir}/data/subfolder1/",
                "keys": [],
            }
        ]
    }

    stream = CSVStream(
        tap=TapCSV(config=SAMPLE_CONFIG, catalog={}, state={}),
        name="test_recursive",
        file_config=SAMPLE_CONFIG.get("files")[0],
    )
    assert stream.get_file_paths() == [
        f"{test_data_dir}/data/subfolder1/alphabet.csv",
        f"{test_data_dir}/data/subfolder1/subfolder2/alphabet.csv",
    ]
