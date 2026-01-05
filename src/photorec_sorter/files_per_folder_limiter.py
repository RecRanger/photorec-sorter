import os
import shutil


def limitFilesPerFolder(folder, max_files_per_folder):
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            dirPath = os.path.join(root, dir)
            filesInFolder = len(os.listdir(dirPath))
            if filesInFolder > max_files_per_folder:
                subfolder_count = ((filesInFolder - 1) // max_files_per_folder) + 1
                for subFolderNumber in range(1, subfolder_count + 1):
                    subFolderPath = os.path.join(dirPath, str(subFolderNumber))
                    if not os.path.exists(subFolderPath):
                        os.mkdir(subFolderPath)
                fileCounter = 1
                for file in os.listdir(dirPath):
                    source = os.path.join(dirPath, file)
                    if os.path.isfile(source):
                        destDir = str(((fileCounter - 1) // max_files_per_folder) + 1)
                        destination = os.path.join(dirPath, destDir, file)
                        shutil.move(source, destination)
                        fileCounter += 1
