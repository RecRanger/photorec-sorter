from pathlib import Path
import uuid

import pytest
from photorec_sorter.recovery import (
    count_files_in_folder_recursively,
    sort_photorec_folder,
)


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


@pytest.mark.parametrize(
    "enable_keep_filename", [True, False], ids=["keep", "not_keep"]
)
@pytest.mark.parametrize(
    "enable_datetime_filename", [True, False], ids=["datetime", "not_datetime"]
)
def test_basic_sort_no_images(
    tmp_path: Path,
    enable_keep_filename: bool,
    enable_datetime_filename: bool,  # Should have no effect on output.
) -> None:
    source_path = tmp_path / "source"
    destination_path = tmp_path / "destination"
    source_path.mkdir()
    destination_path.mkdir()

    # Seed the source folder with tons of files.
    for file_path in (
        [source_path / "recup_dir.1" / f"file_{i:03}.txt" for i in range(123)]
        + [source_path / "recup_dir.1" / f"db_{i:03}.sqlite" for i in range(71)]
        + [source_path / "recup_dir.2" / f"doc_{i:03}.pdf" for i in range(93)]
    ):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(uuid.uuid4()) + "\n" + file_path.name)

    sort_photorec_folder(
        source=source_path,
        destination=destination_path,
        max_files_per_folder=100,
        enable_split_months=False,
        enable_keep_filename=enable_keep_filename,
        enable_datetime_filename=enable_datetime_filename,
        min_event_delta_days=1,
    )

    source_file_count = count_files_in_folder_recursively(source_path)
    destination_file_count = count_files_in_folder_recursively(destination_path)
    assert source_file_count == (123 + 71 + 93)
    assert destination_file_count == source_file_count

    if enable_keep_filename:
        # txt gets an extra layer of folders because there are over 100.
        assert (destination_path / "txt" / "1" / "file_000.txt").is_file()
        assert (destination_path / "txt" / "1" / "file_099.txt").is_file()
        assert (destination_path / "txt" / "2" / "file_100.txt").is_file()
        assert (destination_path / "txt" / "2" / "file_101.txt").is_file()

        assert (destination_path / "sqlite" / "db_000.sqlite").is_file()
        assert (destination_path / "pdf" / "doc_000.pdf").is_file()
