from pathlib import Path

import pytest
from photorec_sorter.recovery import sort_photorec_folder


@pytest.mark.parametrize("max_files_per_folder", [100, 500, 1000])
@pytest.mark.parametrize("enable_split_months", [True, False])
@pytest.mark.parametrize("enable_keep_filename", [True, False])
@pytest.mark.parametrize("enable_datetime_filename", [True, False])
@pytest.mark.parametrize("min_event_delta_days", [1, 7, 30])
def test_empty_folder(
    tmp_path: Path,
    max_files_per_folder: int,
    enable_split_months: bool,
    enable_keep_filename: bool,
    enable_datetime_filename: bool,
    min_event_delta_days: int,
) -> None:
    source_path = tmp_path / "source"
    destination_path = tmp_path / "destination"
    source_path.mkdir()
    destination_path.mkdir()

    sort_photorec_folder(
        source=source_path,
        destination=destination_path,
        max_files_per_folder=max_files_per_folder,
        enable_split_months=enable_split_months,
        enable_keep_filename=enable_keep_filename,
        enable_datetime_filename=enable_datetime_filename,
        min_event_delta_days=min_event_delta_days,
    )
