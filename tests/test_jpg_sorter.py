import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock

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
