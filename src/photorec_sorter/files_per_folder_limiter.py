from pathlib import Path
import shutil


def limit_files_per_folder(folder: Path, max_files_per_folder: int) -> None:
    # Walk bottom-up to avoid interfering with directory traversal.
    for root in sorted(folder.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not root.is_dir():
            continue

        files = [p for p in root.iterdir() if p.is_file()]
        file_count = len(files)

        if file_count <= max_files_per_folder:
            continue

        # Number of sub_folders needed.
        subfolder_count = ((file_count - 1) // max_files_per_folder) + 1

        # Create sub_folders: 1, 2, 3, ...
        sub_folders = []
        for i in range(1, subfolder_count + 1):
            subfolder = root / str(i)
            subfolder.mkdir(exist_ok=True)
            sub_folders.append(subfolder)

        # Move files into sub_folders.
        for index, file_path in enumerate(sorted(files)):
            target_folder = sub_folders[index // max_files_per_folder]
            shutil.move(file_path, target_folder / file_path.name)
