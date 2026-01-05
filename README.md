# photorec-sorter

A tool to sort/organize files recovered by the [PhotoRec](https://www.cgsecurity.org/wiki/PhotoRec) tool

This fork is maintained independently by RecRanger.

## Description

PhotoRec does a great job when recovering deleted files. But the result is a huge, unsorted, unnamed amount of files. Especially for external hard drives serving as backup of all the personal data, sorting them is an endless job.

This program helps you sorting your files. It does the following steps:
1. Files are copied to folders for each file type.
2. Using exif data, `.jpg` files are distinguished by the year (and optionally by month) captured, and by the event

We define an "event" as a time span during them photos are taken. It has a delta of 4 days without a photo to another event. If no date from the past can be detected, these jpgs are put into one folder to be sorted manually.

## Installation and Usage

Install this project:

```bash
uv tool install photorec_sorter
```

Run this project with either of the following:

```bash
photorec_sorter "path_to_files_recovered_by_PhotoRec" "destination_folder"
```

This copies the recovered files to their file type folder in the destination directory. The recovered files are not modified. If a file already exists in the destination directory, it is skipped. This means that the program can be interrupted with Ctrl+C and then continued at a later point by running it again.

The first output of the program is the number of files to copy. To count them might take some minutes depending on the amount of recovered files. Afterwards, you get some feedback on the processed files.

### Arguments

For an overview of all arguments, run with the `-h` option: `photorec_sorter -h`.

```
usage: photorec_sorter [-h] [-n MAX_PER_DIR] [-m] [-k] [-d MIN_EVENT_DELTA] [-j] src dest

Sort files recovered by PhotoRec. The input files are first copied to the destination, sorted by file type. Then, JPG files are sorted based on creation
year (and optionally month). Finally, any directories containing more than a maximum number of files are accordingly split into separate directories."

positional arguments:
  src                   source directory with files recovered by PhotoRec
  dest                  destination directory to write sorted files to

options:
  -h, --help            show this help message and exit
  -n MAX_PER_DIR, --max-per-dir MAX_PER_DIR
                        maximum number of files per directory (default: 500)
  -m, --split-months    split JPEG files not only by year but by month as well (default: False)
  -k, --keep_filename   keeps the original filenames when copying (default: False)
  -d MIN_EVENT_DELTA, --min-event-delta MIN_EVENT_DELTA
                        minimum delta in days between two days (default: 4)
  -j, --enable_datetime_filename
                        sets the filename to the exif date and time if possible - otherwise keep the original filename (default: False)
```


#### Max Files per Folder

All directories contain a maximum of 500 files by default. If there are more for a file type, numbered subdirectories are created. If you want another file-limit, e.g. 1000, pass that number with the `-n` flag.

```bash
photorec_sorter "path_to_files_recovered_by_PhotoRec" "destination_folder" -n1000
```

#### Folder for Each Month

By default, `photorec-sorter` sorts your photos by year:

```
destination
|- 2015
    |- 1.jpg
    |- 2.jpg
    |- ...
|- 2016
    |- ...
```

Sometimes, you might want to sort each year by month:

```bash
photorec_sorter "path_to_files_recovered_by_PhotoRec" "destination_folder" -m
```

Now, the destination structure will be:

```
destination
|- 2015
    |- 1
      |- 1.jpg
      |- 2.jpg
    |- 2
      |- 3.jpg
      |- 4.jpg
    |- ...
|- 2016
    |- ...
```

#### Keep Original Filenames

Use the `-k` parameter to keep the original filenames (as recovered):

```bash
photorec_sorter "path_to_files_recovered_by_PhotoRec" "destination_folder" -k
```

#### Adjust Max Event Duration

For the case you want to reduce or increase the time span between events, simply use the parameter `-d`. The default is 4 days. To use 10 days, run:

```bash
photorec_sorter "path_to_files_recovered_by_PhotoRec" "destination_folder" -d10
```

#### Rename .jpg Files with EXIF Date/Time

If the original jpg image files were named by `<Date>_<Time>` it might be useful to rename the recovered files in the same way. This can be done by adding the `-j` flag.

```bash
photorec_sorter "path_to_files_recovered_by_PhotoRec" "destination_folder" -j
```

If no EXIF data can be retrieved, the original filename is kept.

In case there are two or more files with the same EXIF data, the filename is extended by an index to avoid overwriting files.

The result will look like:
```
20210121_134407.jpg
20210122_145205.jpg
20210122_145205(1).jpg
20210122_145205(2).jpg
20210122_145813.jpg
20210122_153155.jpg
```

## Contributing

Please open GitHub Issues/Pull Requests to help improve this project.

## Acknowledgements

* Thanks to [Christophe Grenier at CGSecurity](https://www.cgsecurity.org/) for creating [TestDisk/PhotoRec](https://github.com/cgsecurity/testdisk).
* Thanks to [ChrisMagnuson](https://github.com/ChrisMagnuson) for the
[original creation of sort-PhotorecRecoveredFiles](https://github.com/ChrisMagnuson/sort-PhotorecRecoveredFiles).
* Thanks to [tfrdidi](https://github.com/tfrdidi) for
[their fork of sort-PhotorecRecoveredFiles](https://github.com/tfrdidi/sort-PhotorecRecoveredFiles),
upon which this `photorec-sorter` project is based.
