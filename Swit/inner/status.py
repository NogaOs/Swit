import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

import Swit.common.paths as path_to
from Swit.common.exceptions import CommitRequiredError
from Swit.common.helper_funcs import (
    get_files_with_different_content, get_head_id, get_relpaths
)
from loguru import logger


def get_changes_to_be_committed() -> Set[Path]:
    """After every time `add` is performed, the filepath is added to this text file."""
    return {Path(path) for path in path_to.changes_to_be_committed.read_text().split("\n") if path}


def get_status_info(head_id: str) -> Dict[str, Set[Path]]:
    """Returns a dict item of all status sections."""
    original_files = get_relpaths(path_to.repo, ignore_wit=True)
    added_files = get_relpaths(path_to.staging_area)    
    not_staged = get_files_with_different_content(
        path_to.repo, path_to.staging_area, original_files & added_files
    )
    to_be_committed = get_changes_to_be_committed()
    untracked = original_files - added_files

    return {
        "Changes to Be Committed": to_be_committed,
        "Changes Not Staged for Commit": not_staged,
        "Untracked Files": untracked
    }


def print_section(section_name: str, filepaths: Union[Set[Path], Set[str]]) -> None:
    print(f"\n>>> {section_name}:")
    if filepaths:
        for i, fp in enumerate(filepaths, 1):
            print(f"{i} - {fp}")
    else:
        print("No current changes.")


def print_status(
    HEAD: str, status_info: Dict[str, Set[Path]]  #: Dict[Set[Path]]
) -> None:
    print("-" * 60)
    print(f"\n>>> HEAD: {HEAD}")
    for section_name, filepaths in status_info.items():
        print_section(section_name, filepaths)
    print("\n" + "-" * 60)


def inner_status() -> None:
    """Prints a message to the user, including:
    - Changes to Be Committed:
        Files that have been added, but not committed yet.
    - Changes Not Staged for Commit:
        Files that have a different content from the indexed file.
    - Untracked Files:
        Files that were neither added nor committed.
    """
    try:
        head_id = get_head_id()
    except FileNotFoundError:
        raise CommitRequiredError(
            "Must commit at least once before executing status."
        )
    info = get_status_info(head_id)
    print_status(head_id, info)


def status() -> bool:
    try:
        inner_status()
    except CommitRequiredError as e:
        logger.warning(e)
        return False
    return True
