from pathlib import Path

from typing import Tuple, Set, List

import shutil

import os

import re


import paths

from general_funcs import (
    get_all_filepaths, get_files_with_different_content
)




def get_org_and_added_files() -> Tuple[Set[Path], Set[Path]]:
    """Recieves the path to repository, and createes the path to staging_area and the last committed dir.
    Returns a tuple of lists with the filepaths of each dir."""
    original_files = get_all_filepaths(paths.repo)
    added_files = get_all_filepaths(paths.staging_area)
    return original_files, added_files


# def get_difference(filepaths1: set, filepaths2: set) -> set:
#     """Returns all filepaths that exist in dir1, but not in dir2."""
#     return filepaths1 - filepaths2


def get_changes_to_be_committed() -> List[str]:
    with open(paths.changes_to_be_committed, "r") as f:
        lines = f.readlines()
    return lines


def get_status_data(head_id: str) -> Tuple[List[str], List[str], Set[str]]:
    original_files, added_files = get_org_and_added_files()
    changes_not_staged_for_commit = get_files_with_different_content(
        paths.repo, paths.staging_area, original_files.intersection(added_files)
    )
    changes_to_be_committed = get_changes_to_be_committed()
    untracked_files = original_files - added_files

    return (changes_to_be_committed, changes_not_staged_for_commit, untracked_files)


def print_status(
    HEAD, changes_to_be_committed, changes_not_staged_for_commit, untracked_files
) -> None:
    print("-" * 60)
    print(f"\n>>> HEAD: {HEAD}.")
    print("\n>>> Changes to Be Committed:")
    if changes_to_be_committed:
        for i, fp in enumerate(changes_to_be_committed, 1):
            print(f"{i} - {fp.strip()}")
    else:
        print("No current changes.")
    print("\n>>> Changes Not Staged for Commit:")
    if changes_not_staged_for_commit:
        for i, fp in enumerate(changes_not_staged_for_commit, 1):
            print(f"{i} - {fp}")
    else:
        print("No current changes.")
    print("\n>>> Untracked Files:")
    if untracked_files:
        for i, fp in enumerate(untracked_files, 1):
            print(f"{i} - {fp}")
    else:
        print("No current untracked files.")
    print("\n" + "-" * 60)