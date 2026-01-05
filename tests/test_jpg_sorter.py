import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock

from datetime import datetime
from PIL import Image

from photorec_sorter import jpg_sorter


def test_postprocess_organize_images_calls_postprocess_and_writeImages(
    monkeypatch: Any, tmp_path: Path
) -> None:
    """Contrived test for postprocess_organize_images.

    `postprocess_organize_images` should:
    - walk the directory
    - call postprocessImage for each file
    - pass the collected images to writeImages with correct arguments
    """

    # --- Arrange ---
    image_dir = tmp_path

    fake_files = ["img1.jpg", "img2.jpg"]

    # Mock os.walk to simulate files in directory
    monkeypatch.setattr(
        os,
        "walk",
        lambda _: [(str(image_dir), [], fake_files)],
    )

    # Capture images list passed through postprocessImage
    def fake_postprocess_image(images, imageDirectory, fileName):
        images.append((123.0, str(imageDirectory / fileName)))

    postprocess_mock = Mock(side_effect=fake_postprocess_image)
    monkeypatch.setattr(jpg_sorter, "postprocessImage", postprocess_mock)

    write_images_mock = Mock()
    monkeypatch.setattr(jpg_sorter, "writeImages", write_images_mock)

    # --- Act ---
    jpg_sorter.postprocess_organize_images(
        image_dir,
        min_event_delta_days=3,
        enable_split_by_month=True,
    )

    # --- Assert ---
    # postprocess_organize_images called once per file
    assert postprocess_mock.call_count == len(fake_files)

    # writeImages called once
    write_images_mock.assert_called_once()

    images_arg, destination_root = write_images_mock.call_args.args
    kwargs = write_images_mock.call_args.kwargs

    assert destination_root == image_dir
    assert kwargs["min_event_delta_days"] == 3
    assert kwargs["enable_split_by_month"] is True

    # Ensure images list contains entries for each file
    assert len(images_arg) == len(fake_files)


def _create_jpeg_with_exif(path: Path, dt: datetime) -> None:
    """Create a real JPEG file with a real EXIF DateTimeOriginal."""
    img = Image.new("RGB", (10, 10), color="red")

    exif = img.getexif()
    exif[36867] = dt.strftime("%Y:%m:%d %H:%M:%S")  # DateTimeOriginal
    exif[36868] = dt.strftime("%Y:%m:%d %H:%M:%S")  # DateTimeDigitized
    exif[306] = dt.strftime("%Y:%m:%d %H:%M:%S")  # DateTime

    img.save(path, exif=exif)


def test_sorts_by_real_exif_dates(tmp_path: Path) -> None:
    """
    Files with real EXIF dates should be:
    - grouped into events
    - placed under year/eventNumber
    - not put into date-unknown
    """

    image_dir = tmp_path / "images"
    image_dir.mkdir()

    # Two distinct events separated by > 1 day
    dt1 = datetime(2022, 5, 10, 12, 0, 0)
    dt2 = datetime(2022, 5, 12, 12, 0, 0)

    img1a = image_dir / "img1.jpg"
    img1b = image_dir / "img1b.jpg"
    img2 = image_dir / "img2.jpg"

    _create_jpeg_with_exif(img1a, dt1)
    _create_jpeg_with_exif(img1b, dt1)
    _create_jpeg_with_exif(img2, dt2)

    # Run
    jpg_sorter.postprocess_organize_images(
        imageDirectory=image_dir,
        min_event_delta_days=1,
        enable_split_by_month=False,
    )

    # --- Assertions ---

    # date-unknown must NOT exist (dates are not today)
    assert not (image_dir / jpg_sorter.unknownDateFolderName).exists()

    # Event folders created
    event1 = image_dir / "2022" / "1"
    event2 = image_dir / "2022" / "2"

    assert event1.is_dir()
    assert event2.is_dir()

    assert (event1 / "img1.jpg").is_file()
    assert (event1 / "img1b.jpg").is_file()
    assert (event2 / "img2.jpg").is_file()

    # Originals removed
    assert not img1a.exists()
    assert not img1b.exists()
    assert not img2.exists()
