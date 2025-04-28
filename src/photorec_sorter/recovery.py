import os
import shutil
from time import strftime, strptime

# dependencies
import exifread
from loguru import logger

# project libraries
from photorec_sorter import jpg_sorter
from photorec_sorter import files_per_folder_limiter


def getNumberOfFilesInFolderRecursively(start_path="."):
    numberOfFiles = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                numberOfFiles += 1
    return numberOfFiles


def getNumberOfFilesInFolder(path):
    return len(os.listdir(path))


def sort_photorec_folder(
    source: str,
    destination: str,
    max_files_per_folder: int,
    enable_split_months: bool,
    enable_keep_filename: bool,
    enable_datetime_filename: bool,
    min_event_delta_days: int,
):

    if not os.path.isdir(source):
        raise ValueError(f"Source directory does not exist: {source}")
    if not os.path.isdir(destination):
        raise ValueError(
            "Destination directory does not exist. "
            f"Please create the directory first: {destination}"
        )

    logger.info(
        "Reading from source '%s', writing to destination '%s' (max %i files per directory, splitting by year %s)."
        % (
            source,
            destination,
            max_files_per_folder,
            enable_split_months and "and month" or "only",
        )
    )
    if enable_keep_filename:
        logger.info("Filename Plan: Keep the original filenames.")
    elif enable_datetime_filename:
        logger.info(
            "Filename Plan: If possible, rename files like <Date>_<Time>.jpg. Otherwise, keep the original filenames."
        )
    else:
        logger.info("Filename Plan: Rename files sequentially, like '1.jpg'")

    total_file_count = getNumberOfFilesInFolderRecursively(source)
    if total_file_count > 100:
        log_frequency_file_count = int(total_file_count / 100)
    else:
        log_frequency_file_count = total_file_count
    logger.info(f"Total files to copy: {total_file_count:,}")

    cur_file_number = 0
    for root, dirs, files in os.walk(source, topdown=False):

        for file in files:
            extension = os.path.splitext(file)[1][1:].lower()
            source_file_path = os.path.join(root, file)

            if extension:
                dest_directory = os.path.join(destination, extension)
            else:
                dest_directory = os.path.join(destination, "no_extension")

            if not os.path.exists(dest_directory):
                os.mkdir(dest_directory)

            if enable_keep_filename:
                file_name = file

            elif enable_datetime_filename:
                index = 0
                image = open(source_file_path, "rb")
                try:
                    exifTags = exifread.process_file(image, details=False)
                    creationTime = jpg_sorter.getMinimumCreationTime(exifTags)
                    creationTime = strptime(
                        str(creationTime), "%Y:%m:%d %H:%M:%S"
                    )
                    creationTime = strftime("%Y%m%d_%H%M%S", creationTime)
                    file_name = str(creationTime) + "." + extension.lower()
                    while os.path.exists(
                        os.path.join(dest_directory, file_name)
                    ):
                        index += 1
                        file_name = (
                            str(creationTime)
                            + "("
                            + str(index)
                            + ")"
                            + "."
                            + extension.lower()
                        )
                except:
                    file_name = file
                image.close()
            else:
                if extension:
                    file_name = str(cur_file_number) + "." + extension.lower()
                else:
                    file_name = str(cur_file_number)

            dest_file_path = os.path.join(dest_directory, file_name)
            if not os.path.exists(dest_file_path):
                shutil.copy2(source_file_path, dest_file_path)

            cur_file_number += 1
            if (cur_file_number % log_frequency_file_count) == 0:
                logger.info(
                    f"{cur_file_number} / {total_file_count} processed ({cur_file_number/total_file_count:.2%})."
                )

    logger.info(
        "Starting special file treatment (JPG sorting and folder splitting)..."
    )
    jpg_sorter.postprocessImages(
        os.path.join(destination, "JPG"),
        min_event_delta_days,
        enable_split_months,
    )

    logger.info("Applying max files-per-folder limit...")
    files_per_folder_limiter.limitFilesPerFolder(
        destination, max_files_per_folder
    )

    logger.info("Done.")
