import shutil
from pathlib import Path
from typing import List, Set, Tuple, Dict

import Swit.common.paths as path_to
from Swit.common.exceptions import CommitIdError, ImpossibleCheckoutError
from Swit.common.helper_funcs import (
    get_head_id, get_relpaths, handle_references_file
)
from loguru import logger

import Swit.inner.status as status
from Swit.common.helper_funcs import get_head_id, resolve_commit_id, get_valid_commit_path


def is_checkout_possible(
    image_dir_path: Path, to_be_committed: Set[Path], not_staged_for_commit: Set[Path]
) -> bool:
    """The checkout command will not run if the commit_id is wrong;
    if there are any files that are to be committed;
    or any files that are not staged for commit.
    """
    if not image_dir_path.exists():
        raise FileNotFoundError(
            f"The path '{image_dir_path}' does not exist. You may have entered the wrong branch name / commit id."
        )
    return not any((to_be_committed, not_staged_for_commit))


def handle_impossible_checkout(
    head_id: str, image_dir_path: Path, 
    to_be_committed: Tuple[str, Set[Path]],
    not_staged: Tuple[str, Set[Path]]
) -> None:
    """If checkout is impossible to perform, an error is raised and the relevant status info is printed."""
    if not is_checkout_possible(
        image_dir_path, to_be_committed[1], not_staged[1]
    ):
        logger.warning(
            "Please make sure that 'Changes to Be Committed' and 'Changes Not Staged for Commit' are empty:"
            )
        status.print_section(*to_be_committed)
        status.print_section(*not_staged)
        raise ImpossibleCheckoutError


def get_dirpaths_to_ignore(untracked_files: Set[Path]) -> Set[Path]:
    """Returns all parent dirs of the untracked files, 
    so that they will not be removed.
    """
    dirpaths = set()
    for fp in untracked_files:
        cur_path = fp.parent
        parent = cur_path.parent
        while cur_path != parent:
            dirpaths.add(cur_path)
            cur_path, parent = cur_path.parent, parent.parent
    return dirpaths


def remove_except(untracked_files: Set[Path]) -> None:
    """Removes all dirs and files in the repository, 
    except for `.swit` and untracked files (including parents).
    This is used before the content of `staging_area` is copied.
    """
    entries = get_relpaths(path_to.repo, ignore_wit=True, only_files=False)
    dirs_to_ignore = get_dirpaths_to_ignore(untracked_files)
    remove = entries - untracked_files - dirs_to_ignore
    for entry in remove:
        if entry.is_dir():
            shutil.rmtree(entry)
            # shutil is used because the dir doesn't have to be empty (compared to pathlib\os).
        if entry.is_file():
            entry.unlink()


def update_repo(untracked_files: Set[Path], image_path: Path) -> None:
    """Replaces the content of the repository with the content of the chosen commit.
    Removes all content except for .swit dir and untracked files;
    then copies the content of the image.
    """
    remove_except(untracked_files)
    shutil.copytree(image_path, path_to.repo, dirs_exist_ok=True)


def update_staging_area(image_path: Path) -> None:
    """Replaces the content of staging area with the content of the chosen commit.
    Removes all content; then copies the content of the image.
    """
    shutil.rmtree(path_to.staging_area)
    shutil.copytree(image_path, path_to.staging_area)


def handle_activated_file(image_commit_id: str, original_user_input: str) -> None:
    """If the user passed a branch name, it will appear under activated.txt;
    else, there will be no active branch and the file will be empty.
    """
    # Checks if the user passed a branch name or a commit id
    if original_user_input != image_commit_id:
        content = original_user_input
    else: 
        content = ""

    path_to.active_branch.write_text(content)


def inner_checkout(user_input: str, image_commit_id: str, image_dir_path: Path) -> None:
    """Updates files in the repository and in staging area to match the version 
    in the specified image.
    Updates the activated file and references files.
    """
    head_id = get_head_id()
    status_info = status.get_status_info(head_id)
    to_be_committed, not_staged, untracked = status_info.items()
    handle_impossible_checkout(head_id, image_dir_path, to_be_committed, not_staged)
    update_repo(untracked[1], image_dir_path)
    update_staging_area(image_dir_path)
    # Note: Updating activated.txt should remain before references.txt
    handle_activated_file(image_commit_id, user_input)
    handle_references_file(image_commit_id)


def checkout(indicator: str) -> bool:
    try:
        image_commit_id = resolve_commit_id(indicator)
        image_dir_path = get_valid_commit_path(image_commit_id, indicator)
    except CommitIdError as e:
        logger.warning(e)
        return False

    try:
        inner_checkout(indicator, image_commit_id, image_dir_path)
    except ImpossibleCheckoutError:
        # The error is handled within `inner_checkout`.
        return False
    except FileNotFoundError as e:
        logger.warning(e)
        return False

    logger.info(">>> Checkout Executed Successfully.")
    return True