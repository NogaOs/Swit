import shutil

from pathlib import Path

from typing import Dict, List, Set, Tuple


import common.helper_funcs as helper

import common.paths as path_to

from common.exceptions import ImpossibleMergeError

from inner.commit import generate_commit_id, inner_commit

from inner.graph import get_parent_file_content, get_parents_of_image_dict



def is_merge_possible(head_dir_path: Path) -> bool:
    """`merge()` will fail to execute if the content of staging_area is different from the content of the HEAD image.
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
    parents_dict = get_parents_of_image_dict(parent_file_content)

    parents_of_head = get_parents_of(parents_dict, head_commit_id)
    parents_of_input = get_parents_of(parents_dict, user_commit_id)
    mutual_parents = parents_of_head.intersection(parents_of_input)

    # Beginning from the end, checks the parent list to see if the commit id is included in the mutual parents.
    reversed_content = parent_file_content[::-1]
    for line in reversed_content:
        commit_id = line.split("=")[0]
        if commit_id in mutual_parents:
            return commit_id


def get_changed_files(since_dir: Path, until_dir: Path) -> Tuple[list, list]:
    """Returns files that were added and files that were changed, between dir a and dir b.
    When called through `merge()`, the returned files are since the first mutual parent,
    until the user dir or head dir.
    """
    since_dir_files = helper.get_relpaths(since_dir)
    until_dir_files = helper.get_relpaths(until_dir)
    added_files = until_dir_files - since_dir_files
    mutual_files = until_dir_files.intersection(since_dir_files)
    changed_files = helper.get_files_with_different_content(since_dir, until_dir, mutual_files)
    return added_files, changed_files


def update_staging_area(path_to_user_dir, added_files, changed_files) -> None:
    helper.copy_changed_files(path_to_user_dir, path_to.staging_area, added_files)
    helper.copy_changed_files(
        path_to_user_dir, path_to.staging_area, changed_files, replace=True
    )


def update_head_and_active_branch(new_commit_id: str) -> None:
    """After a merge has been executed, the HEAD and the active branch are updated with the new commit ID."""
    with open(path_to.references, "r") as f:
        lines = f.readlines()

    lines[0] = f"HEAD={new_commit_id}\n"
    active_branch_name = helper.get_active_branch_name()

    if active_branch_name:
        i = helper.get_branch_index(lines, active_branch_name)
        lines[i] = f"{active_branch_name}={new_commit_id}\n"

    with open(path_to.references, "w") as f:
        f.write("".join(lines))


def get_commit_merge_message(
    head_commit_id: str, user_commit_id: str, user_input: str
) -> str:
    """Shortens the commit ids and adds them to a commit message;
    if user used a branch name, the latter will appear next to the id.
    Example: `Merged 123456 (HEAD) with 654321` (<branch_name>).
    """
    is_id = user_input == user_commit_id
    shortened_head_id = head_commit_id[:6]
    merged_with = (
        user_commit_id[:6] if is_id else f"{user_commit_id[:6]} ({user_input})"
    )
    commit_message = f"Merged {shortened_head_id} (HEAD) with {merged_with}."
    return commit_message


def commit_merge(
    new_commit_id: str, head_commit_id: str, user_commit_id: str, 
    user_input: str
) -> None:
    commit_message = get_commit_merge_message(
        head_commit_id, user_commit_id, user_input
    )
    parents = f"{head_commit_id}, {user_commit_id}"
    # Commit:
    inner_commit(commit_message, new_commit_id, parents)
    # Update references file:
    update_head_and_active_branch(new_commit_id)


def get_merge_paths(user_input: str):
    """Returns the commit id and image path of the user image, HEAD, and their first mutual parent."""
    # Head:
    head_commit_id = helper.get_head_id()
    head_dir_path = helper.get_image_dir(head_commit_id)
    # User Image:
    user_commit_id, user_dir_path = helper.get_image_data(user_input)
    # Common Base Image:
    common_base_id = get_first_mutual_parent(head_commit_id, user_commit_id)
    common_base_dir_path = helper.get_image_dir(common_base_id)

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
    """MISSING!"""
    if not is_merge_possible(head_dir):
        raise ImpossibleMergeError(
            "Seems like you are not working on the most up to date version. To do so, please execute `checkout HEAD`."
        )
    # Get added\changed files, replace content of staging area:
    changed_files = get_changed_files(common_base_dir, user_dir)
    update_staging_area(user_dir, *changed_files)
    # Commit:
    new_commit_id = generate_commit_id()
    commit_merge(new_commit_id, head_commit_id, user_commit_id, user_input)
    # Update reference file:
    update_head_and_active_branch(new_commit_id)
