#!/usr/bin/env python

import argparse

from loguru import logger

from photorec_sorter.recovery import sort_photorec_folder


def get_args():
    description = """
Sort files recovered by PhotoRec.

The input files are first copied to the destination, sorted by file type.
Then, JPG files are sorted based on creation year (and optionally month).
Finally, any directories containing more than a maximum number of files are
accordingly split into separate directories."
    """.strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source",
        metavar="src",
        type=str,
        help="source directory with files recovered by PhotoRec",
    )
    parser.add_argument(
        "destination",
        metavar="dest",
        type=str,
        help="destination directory to write sorted files to",
    )
    parser.add_argument(
        "-n",
        "--max-per-dir",
        type=int,
        default=500,
        required=False,
        help="maximum number of files per directory",
    )
    parser.add_argument(
        "-m",
        "--split-months",
        action="store_true",
        required=False,
        help="split JPEG files not only by year but by month as well",
    )
    parser.add_argument(
        "-k",
        "--keep_filename",
        action="store_true",
        required=False,
        help="keeps the original filenames when copying",
    )
    parser.add_argument(
        "-d",
        "--min-event-delta",
        type=int,
        default=4,
        required=False,
        help="minimum delta in days between two days",
    )
    parser.add_argument(
        "-j",
        "--enable_datetime_filename",
        action="store_true",
        required=False,
        help="sets the filename to the exif date and time if possible - otherwise keep the original filename",
    )

    return parser.parse_args()


def main_cli():
    args = get_args()

    logger.info(f"Arguments: {args}")

    sort_photorec_folder(
        source=args.source,
        destination=args.destination,
        max_files_per_folder=args.max_per_dir,
        enable_split_months=args.split_months,
        enable_keep_filename=args.keep_filename,
        enable_datetime_filename=args.enable_datetime_filename,
        min_event_delta_days=args.min_event_delta,
    )


if __name__ == "__main__":
    main_cli()
