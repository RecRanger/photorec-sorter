from datetime import datetime, timedelta
import os
from pathlib import Path
from time import localtime, strftime, strptime, mktime
import shutil

import exifread
from loguru import logger

UNKNOWN_DATE_FOLDER_NAME = "date-unknown"


def get_min_creation_time_from_exif(exif_data):
    creationTime = None
    dateTime = exif_data.get("DateTime")
    if dateTime is None:
        dateTime = exif_data.get("Image DateTime")
    dateTimeOriginal = exif_data.get("EXIF DateTimeOriginal")
    dateTimeDigitized = exif_data.get("EXIF DateTimeDigitized")

    # 3 different time fields that can be set independently result in 9 if-cases
    if dateTime is None:
        if dateTimeOriginal is None:
            # case 1/9: dateTime, dateTimeOriginal, and dateTimeDigitized = None
            # case 2/9: dateTime and dateTimeOriginal = None, then use dateTimeDigitized
            creationTime = dateTimeDigitized
        else:
            # case 3/9: dateTime and dateTimeDigitized = None, then use dateTimeOriginal
            # case 4/9: dateTime = None, prefer dateTimeOriginal over dateTimeDigitized
            creationTime = dateTimeOriginal
    else:
        # case 5-9: when creationTime is set, prefer it over the others
        creationTime = dateTime

    return creationTime


def get_image_creation_timestamp(image_path: Path) -> datetime:
    """Writes the image creation time and path to the images list."""
    with image_path.open("rb") as image:
        creation_time = None
        try:
            exifTags = exifread.process_file(image, details=False)
            creation_time = get_min_creation_time_from_exif(exifTags)
        except Exception:
            logger.warning(f"Failed to read EXIF from image: {image_path}")

        # Distinct different time types.
        if creation_time is None:
            creation_time = localtime(os.path.getctime(image_path))
        else:
            try:
                creation_time = strptime(str(creation_time), "%Y:%m:%d %H:%M:%S")
            except Exception:
                creation_time = localtime(os.path.getctime(image_path))

    return datetime.fromtimestamp(mktime(creation_time))


# Creates the requested path recursively.
def createPath(newPath):
    if not os.path.exists(newPath):
        os.makedirs(newPath)


# Pass None for month to create 'year/eventNumber' directories instead of
# 'year/month/eventNumber'.
def createNewFolder(destinationRoot, year, month, eventNumber):
    if month is not None:
        newPath = os.path.join(destinationRoot, year, month, str(eventNumber))
    else:
        newPath = os.path.join(destinationRoot, year, str(eventNumber))

    createPath(newPath)


def createUnknownDateFolder(destinationRoot):
    path = os.path.join(destinationRoot, UNKNOWN_DATE_FOLDER_NAME)
    createPath(path)


def writeImages(
    images: list[tuple[datetime, Path]],
    destination_root: Path,
    *,
    min_event_delta_days: int | float,
    enable_split_by_month: bool = False,
) -> None:
    minEventDelta = timedelta(days=min_event_delta_days)
    sortedImages = sorted(images)
    previousTime = None
    eventNumber = 0
    previousDestination: str | Path | None = None
    today = strftime("%d/%m/%Y")

    for image_datetime, image_path in sortedImages:
        year = image_datetime.strftime("%Y")
        month = enable_split_by_month and image_datetime.strftime("%m") or None
        creationDate = image_datetime.strftime("%d/%m/%Y")

        if creationDate == today:
            createUnknownDateFolder(destination_root)
            destination: Path = destination_root / UNKNOWN_DATE_FOLDER_NAME
            destinationFilePath: Path = destination / image_path.name

        else:
            if (previousTime is None) or (
                (previousTime + minEventDelta) < image_datetime
            ):
                eventNumber = eventNumber + 1
                createNewFolder(destination_root, year, month, eventNumber)

            previousTime = image_datetime

            destComponents = [destination_root, year, month, str(eventNumber)]
            destComponents = [v for v in destComponents if v is not None]
            destination = os.path.join(*destComponents)

            # it may be possible that an event covers 2 years.
            # in such a case put all the images to the event in the old year
            if not (os.path.exists(destination)) and (previousDestination is not None):
                destination = previousDestination
                # destination = os.path.join(destinationRoot, str(int(year) - 1), str(eventNumber))

            previousDestination = destination
            destinationFilePath = os.path.join(destination, fileName)

        if not (os.path.exists(destinationFilePath)):
            shutil.move(imageTuple[1], destination)
        else:
            if os.path.exists(imageTuple[1]):
                os.remove(imageTuple[1])


def postprocess_organize_images(
    imageDirectory: Path, *, min_event_delta_days: int, enable_split_by_month: bool
) -> None:
    images: list[tuple[datetime, Path]] = [
        (get_image_creation_timestamp(image_path), image_path)
        for image_path in imageDirectory.rglob("*")
        if image_path.is_file()
    ]

    logger.info(f"Found {len(images):,} images to organize.")

    writeImages(
        images,
        imageDirectory,
        min_event_delta_days=min_event_delta_days,
        enable_split_by_month=enable_split_by_month,
    )
