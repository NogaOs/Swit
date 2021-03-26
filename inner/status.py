import os
import re
import shutil
from collections import namedtuple
from pathlib import Path
from typing import List, Set, Tuple, Union, Dict

import common.paths as path_to
from common.exceptions import CommitRequiredError
from common.helper_funcs import (
    get_files_with_different_content, get_head_id, get_relpaths
)


def get_changes_to_be_committed() -> List[str]:  # I can change it to return paths for the sake of type annotations, but is it worth it?
    return [path for path in path_to.changes_to_be_committed.read_text().split("\n") if path]


def get_status_info(head_id: str) -> dict:  # -> Dict[Set[Union[Path, str]]]:
    original_files = get_relpaths(path_to.repo, ignore_wit=True)
    added_files = get_relpaths(path_to.staging_area)    
    not_staged = get_files_with_different_content(
        path_to.repo, path_to.staging_area, original_files.intersection(added_files)
    )
    to_be_committed = get_changes_to_be_committed()
    untracked = original_files - added_files

    return {
        "Changes to Be Committed": to_be_committed,
        "Changes Not Staged for Commit": not_staged,
        "Untracked Files": untracked
    }


def print_section(section_name: str, filepaths: Set[Union[Path, str]]) -> None:
    print(f"\n>>> {section_name}:")
    if filepaths:
        for i, fp in enumerate(filepaths, 1):
            print(f"{i} - {fp}")
    else:
        print("No current changes.")


def print_status(
    HEAD: str, status_info: dict  #: Dict[Set[Path]]
) -> None:
    print("-" * 60)
    print(f"\n>>> HEAD: {HEAD}")
    for section_name, filepaths in status_info.items():
        print_section(section_name, filepaths)
    print("\n" + "-" * 60)


def inner_status() -> None:
    try:
        head_id = get_head_id()
    except FileNotFoundError:
        raise CommitRequiredError(
            "Must commit at least once before executing status."
        )
    info = get_status_info(head_id)
    print_status(head_id, info)
