import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple

from loguru import logger

import Swit.common.helper_funcs as helper
import Swit.common.paths as path_to
from Swit.common.exceptions import CommitIdError, ImpossibleMergeError
from Swit.inner.commit import inner_commit
from Swit.inner.graph import get_parent_file_content, get_parents_by_image


def is_merge_possible(head_dir_path: Path) -> bool:
    """`merge()` will fail to execute if the content of staging_area 
    is different from the content of HEAD.
    Returns a boolean value of if files were either added or changed.
    """
    head_files = helper.get_relpaths(head_dir_path)
    staging_area_files = helper.get_relpaths(path_to.staging_area)

    return not (
        head_files.symmetric_difference(staging_area_files)
        or any(get_changed_files(head_dir_path, path_to.staging_area))
    )


def get_commit_ids(user_input: str) -> Tuple[str, str, str]:
    """Returns the commit id of HEAD, of the chosen image, and common parent image."""
    head_commit_id = helper.get_head_id()
    user_commit_id = helper.resolve_commit_id(user_input)
    common_base_id = get_first_mutual_parent(head_commit_id, user_commit_id)
    return head_commit_id, user_commit_id, common_base_id


def get_parents_of(image_and_parents: Dict[str, List[str]], commit_id: str) -> Set[str]:
    """Returns a set of all parents of a given commit id."""
    parents = None
    parents_list = [commit_id]
    i = 0
    while i < len(parents_list):
        cur_image = parents_list[i]
        parents = image_and_parents[cur_image]
        for parent in parents:
            parents_list.append(parent)
        i += 1
    return set(parents_list)


def get_first_mutual_parent(head_commit_id: str, user_commit_id: str) -> str:
    """Returns the the commit id of the first mutual parent of HEAD and the chosen image."""
    parent_file_content = get_parent_file_content()
    parents_dict = get_parents_by_image()

    head_parents = get_parents_of(parents_dict, head_commit_id)
    input_parents = get_parents_of(parents_dict, user_commit_id)
    mutual_parents = head_parents & input_parents

    # Beginning from the end, 
    # checks the parent list to see if the commit id is included in the mutual parents.
    reversed_content = parent_file_content[::-1]
    for line in reversed_content:
        commit_id = line.split("=")[0]
        if commit_id in mutual_parents:
            return commit_id


def get_changed_files(since_dir: Path, until_dir: Path) -> Tuple[Set[Path], Set[Path]]:
    """Returns files that were added and files that were changed, between dir a and dir b.
    When called through `merge()`, the returned files are since the first mutual parent,
    until the chosen image to merge.
    """
    since_dir_files = helper.get_relpaths(since_dir)
    until_dir_files = helper.get_relpaths(until_dir)
    added_files = until_dir_files - since_dir_files
    mutual_files = until_dir_files & since_dir_files
    changed_files = helper.get_files_with_different_content(since_dir, until_dir, mutual_files)
    return added_files, changed_files


def update_staging_area(
    path_to_user_dir: Path, added_files: Set[Path], changed_files: Set[Path]
) -> None:
    """Added files are the files that exist in the chosen image to merge, and do not exist in the
    mutual parent dir. Those files shall be added to staging_area;
    Mutual files are files that exist it both versions, but the content has changed. Those files
    shall be replaced to their newer version (merge conflicts are not handled).
    """
    helper.copy_changed_files(path_to_user_dir, path_to.staging_area, added_files)
    helper.copy_changed_files(
        path_to_user_dir, path_to.staging_area, changed_files, replace=True
    )


def get_commit_merge_message(
    head_commit_id: str, user_commit_id: str, user_input: str
) -> str:
    """Shortens the commit ids and adds them to a commit message;
    if user used a branch name, the latter will appear next to the id.
    Example: `Merged 123456 (HEAD) with 654321 (<branch_name>)`.
    """
    shortened_head_id = head_commit_id[:6]
    is_id = user_input == user_commit_id
    merged_with = (
        user_commit_id[:6] if is_id else f"{user_commit_id[:6]} ({user_input})"
    )
    commit_message = f"Merged {shortened_head_id} (HEAD) with {merged_with}."
    return commit_message


def commit_merge(
    new_commit_id: str, head_commit_id: str, user_commit_id: str, 
    user_input: str
) -> None:
    """A commit is performed automatically after merging.

    Differences from a normal commit:
    - Different message
    - Two parents
    - Active branch will always be updated with HEAD
    (default: active branch will be updated only if the id is same as HEAD.)
    """
    commit_message = get_commit_merge_message(
        head_commit_id, user_commit_id, user_input
    )
    parents = f"{head_commit_id},{user_commit_id}"
    inner_commit(commit_message, new_commit_id, parents, is_merge=True)


def get_merge_paths(user_input: str):
    """Returns the commit id and image path of the user image, HEAD, and their first mutual parent."""
    # Head:
    head_commit_id = helper.get_head_id()
    head_dir_path = path_to.images / head_commit_id
    # User Image:
    user_commit_id = helper.resolve_commit_id(user_input)
    user_dir_path = helper.get_valid_commit_path(user_commit_id, user_input)
    # Common Base Image:
    common_base_id = get_first_mutual_parent(head_commit_id, user_commit_id)
    common_base_dir_path = path_to.images / common_base_id

    return (
        head_commit_id,
        user_commit_id,
        head_dir_path,
        user_dir_path,
        common_base_dir_path
    )


def inner_merge(
    user_input: str,
    head_commit_id: str,
    user_commit_id: str,
    head_dir: Path,
    user_dir: Path,
    common_base_dir: Path,
) -> None:
    """Integrates HEAD and another chosen commit (by branch name or commit id).
    staging_area will be updated to the integrated version, and commit normally.
    The content of the repository will not change.
    """
    if not is_merge_possible(head_dir):
        raise ImpossibleMergeError(
            "Seems like you are not working on the most up to date version. To do so, please execute `checkout HEAD`."
        )
    # Get added\changed files, replace content of staging area:
    changed_files = get_changed_files(common_base_dir, user_dir)
    update_staging_area(user_dir, *changed_files)
    # Commit:
    new_commit_id = helper.generate_commit_id()
    commit_merge(new_commit_id, head_commit_id, user_commit_id, user_input)


def merge(indicator: str) -> bool:
    try:
        paths = get_merge_paths(indicator)
    except CommitIdError as e:
        logger.warning(e)
        return False

    try:
        inner_merge(indicator, *paths)
    except ImpossibleMergeError as e:
        logger.warning(e)
        return False

    logger.info(">>> Merge was executed successfully.")
    return True
    