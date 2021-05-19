import shutil
from os.path import abspath, relpath
from pathlib import Path
from typing import Tuple

from loguru import logger

import Swit.common.paths as paths


def get_abs_path(path: str) -> Path:
    """Returns an absolute Path.
    If the path doesn't exist, FileNotFoundError is raised.
    """
    abs_path = Path(abspath(path))
    if not abs_path.exists():
        raise FileNotFoundError(
            f"The path '{abs_path}' does not exist. Please make sure you're set to the correct working directory."
        )
    return abs_path


def add_file(original_filepath: Path, path_from_repo: Path) -> None:
    """Copies the file from the repository to staging area.
    All parent folders will be created, albeit empty.
    """
    hierarchy = paths.staging_area / path_from_repo
    if not hierarchy.exists():
        hierarchy.mkdir(parents=True)
    shutil.copy2(original_filepath, hierarchy)


def add_dir(
    backup_path: Path, rel_from_repo_to_backup: Path
) -> None:
    """Copies the dir from the repository to staging area.
    All parent folders will be created, albeit empty.
    """
    dir_hierarchy_from_staging_area = paths.staging_area / rel_from_repo_to_backup
    if not dir_hierarchy_from_staging_area.exists():
        dir_hierarchy_from_staging_area.mkdir(parents=True)
    shutil.copytree(backup_path, dir_hierarchy_from_staging_area, dirs_exist_ok=True)


def update_changes_to_be_committed(rel_from_repo_to_backup: Path) -> None:
    """Adds a relative filepath to the file that stores all changes to be committed.
    The File will be cleared out every time a commit is performed.
    """
    with open(paths.changes_to_be_committed, "a") as f:
        f.write(f"{rel_from_repo_to_backup}\n")


def inner_add(backup_path: Path) -> None:
    """Copies a file or dir from the repository to staging area;
    Updates changes to be committed file.
    """
    rel_from_repo_to_backup = backup_path.relative_to(paths.repo)
    if backup_path.is_file():
        rel_from_repo_to_dir = rel_from_repo_to_backup.parent
        add_file(backup_path, rel_from_repo_to_dir)
    elif backup_path.is_dir():
        add_dir(backup_path, rel_from_repo_to_backup)

    update_changes_to_be_committed(rel_from_repo_to_backup)


def add(path: str) -> bool:
    try:
        backup_path = get_abs_path(path)
    except FileNotFoundError as e:
        logger.warning(e)
        return False

    inner_add(backup_path)
    logger.info(">>> Backup created.")
    return True
