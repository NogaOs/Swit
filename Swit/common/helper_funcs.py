import os
import random
import re
import shutil
from filecmp import cmp
from pathlib import Path
from typing import List, Set, Tuple, Optional

import Swit.common.paths as path_to
from Swit.common.exceptions import CommitIdError, BranchNameExistsError


# Paths:

def get_relpaths(
    p: Path, ignore_wit: bool = False, only_files: bool = True
) -> Set[Path]:
    """Get the relative path of all files and dirs (default: only files), 
    starting from a given directory.
    The relative path should be identical within the repo, 
    staging_area, and the image dir.
    `ignore_wit` is True when used on the repository.
    """
    entries = set(p.rglob("*"))
    if ignore_wit:
        entries.remove(path_to.wit_repo)
        entries = entries - set(p.rglob("*.swit/**/*"))

    if only_files:
        return {x.relative_to(p) for x in entries if x.is_file()}

    return {x.relative_to(p) for x in entries}


def get_valid_commit_path(commit_id: str, image_indicator: str) -> Tuple[str, Path]:
    """Returns the path to the image dir, based on the user input (branch or commit id).
    If the dir does not exist, it means the user's input is problematic, 
    and a CommitIdError is thrown.
    """
    dir_path = path_to.images / commit_id
    if not dir_path.exists():
        raise CommitIdError(f"'{image_indicator}' is not a branch name, nor a commit id.")
    return dir_path


# Commit Id:

def generate_commit_id(id_length: int = 40) -> str:
    """Creates a random string using 0-9a-f, of a certain length."""
    chars = "1234567890abcdef"
    return "".join(random.choice(chars) for _ in range(id_length))


def resolve_commit_id(user_input: str) -> str:
    """Returns a commit id, whether if the param passed was a branch name or the commit id itself."""
    branch_commit_id = get_commit_id_of_branch(user_input)
    return branch_commit_id or user_input


def get_head_id() -> str:
    """Returns the commit id of HEAD."""
    lines = path_to.references.read_text().split("\n")
    name, _, head_id = lines[0].partition("=")
    return head_id


def get_parent() -> Optional[str]:
    return get_head_id() if path_to.references.exists() else None


# Files:


def copy_changed_files(
    path_from: Path, path_to: Path, changed_files: Set[Path], replace: bool = False
) -> None:
    """Copies specified files from dir1 into dir2. If the files have parent folders, the dir hierarchy will
    be preserved. replace=True is used when the file already exists, so that the dir2 version shall
    be deleted.
    Doesn't support moving, renaming or deleting files, yet.

    - When called from `checkout()`, replaces all of the committed files in the repository with their 
    version in the specified commit id (untracked files remain unchanged);
    - When called from `merge()`, replaces or adds files in staging_area with files that were either 
    changed or added since the common base dir until the user input dir.
    """
    for fp in changed_files:
        source = path_from / fp
        dest = path_to / fp
        hierarchy = dest.parent
        if not hierarchy.exists():
            hierarchy.mkdir(parents=True)
        if replace:
            dest.unlink()  # originally os.remove
        shutil.copy2(source, hierarchy)


def get_files_with_different_content(
    path_to_dir1: Path, path_to_dir2: Path, mutual_files: Set[Path]
) -> Set[Path]:
    """Joins the relative path of each file and compares its content.
    Returns a list of filepaths with different content.
    Mutual files are files that appear in both dirs.

    - When called through `status()`, gets files from the repository and from staging area, 
    thus returning changes not staged for commit;
    - When called through `merge()`, gets files from the branch or commit id the user has 
    entered, and the first mutual parent of the latter and of HEAD.
    """
    files_with_different_content = set()
    for fp in mutual_files:
        p1 = path_to_dir1 / fp
        p2 = path_to_dir2 / fp
        if not cmp(p1, p2):
            files_with_different_content.add(fp)
    return files_with_different_content


# Branches:


def get_active_branch_name() -> str:
    """Returns the content of `activated.txt`."""
    return path_to.active_branch.read_text()


def get_branch_index(references_content: List[str], branch_name: str = "") -> int:
    """Returns the line number of the given branch name (in the references file).
    If a branch name is not given, the index of the active branch will be returned.
    Returns -1 if there currently isn't an active branch.
    """
    branch_name = branch_name or get_active_branch_name()
    if not branch_name:
        return -1

    for i, line in enumerate(references_content):
        name, _, _id = line.partition("=")
        if name == branch_name:
            return i


def is_branch_id_equal_to_head_id(
    references_content: List[str], branch_index: int
) -> bool:
    """Returns True if the id of the given brnach is identical to the id of HEAD;
    False if otherwise.
    """
    if branch_index == -1:
        return False

    head, _, head_id = references_content[0].strip().partition("=")
    branch_name, _, branch_id = references_content[branch_index].strip().partition("=")
    return head_id == branch_id


def get_commit_id_of_branch(user_input: str) -> str:
    """Tries to find the branch name in references.txt.
    If the branch is found, returns the commit_id of the branch;
    else, returns an empty string (may happen if the user used a
    commit_id as a parameter).
    """
    lines = path_to.references.read_text().split("\n")
    for line in lines:
        branch_name, _, commit_id = line.partition("=")
        if branch_name == user_input:
            return commit_id.strip()
    return ""


def initiate_references_file(commit_id: str) -> None:
    path_to.references.write_text(f"HEAD={commit_id}\nmaster={commit_id}\n")


def should_change_active_branch(
    active_branch_index: int, ref_content: List[str], is_merge: bool
) -> bool:
    """The active branch id will always be updated to match HEAD after a merge.
    When not merged, the active branch shall be updated only if it's id matches the
    id or HEAD already.
    """
    if is_merge:
        return True
    return is_branch_id_equal_to_head_id(ref_content, active_branch_index)


def update_branches(
    commit_id: str,
    active_branch_index: int,
    ref_content: List[str],
    change_active_branch: bool,
) -> List[str]:
    """Recieves the content of references.txt, and returns an updated version of it.
    HEAD will always be updated; the active branch may or may not be updated.
    """
    ref_content[0] = f"HEAD={commit_id}\n"
    if change_active_branch:
        branch_name, _, branch_id = ref_content[active_branch_index].partition("=")
        ref_content[active_branch_index] = f"{branch_name}={commit_id}\n"
    return ref_content


def handle_references_file(commit_id: str, is_merge: bool = False) -> None:
    """Used after `commit`, `checkout`, and `merge`.
    Updates the current HEAD id to a new commit id.

    If the active branch has the same id as HEAD, both shall be updated.
    If the function is called via `merge` (is_merge=True), the active branch
    shall be updated regardless of the id.
    """
    if not path_to.references.exists():
        initiate_references_file(commit_id)
        return

    with open(path_to.references, "r") as f:
        lines = f.readlines()
        # didn't use `.read_text()` because it fucks the "\n" up

    active_branch_index = get_branch_index(lines)
    change_active_branch = should_change_active_branch(
        active_branch_index, lines, is_merge
    )
    lines = update_branches(commit_id, active_branch_index, lines, change_active_branch)
    path_to.references.write_text("".join(lines))
