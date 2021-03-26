import shutil

from pathlib import Path

from typing import Tuple, List, Set

import common.paths as path_to

from common.exceptions import (
    CommitIdError, ImpossibleCheckoutError
)

from common.helper_funcs import (
    handle_references_file, get_head_id, get_relpaths
)

from loguru import logger

import inner.status as status



def is_checkout_possible(
    image_dir_path: Path, to_be_committed: List[str], not_staged_for_commit: List[str]
) -> bool:
    """The checkout command will not run if the commit_id is wrong;
    if there are any files that are to be committed;
    or any files that are not staged for commit.
    """
    if not image_dir_path.exists():
        raise FileNotFoundError(
            f"The path '{image_dir_path}' does not exist. You might have entered the wrong branch name / commit id."
        )
    return not any((to_be_committed, not_staged_for_commit))


def handle_activated_file(image_commit_id, original_user_input) -> None:
    """If the user passed a branch name, it will appear under activated.txt.
    Else, there will be no active branch and the file will be empty.
    """
    # Checks if the user passed a branch name or a commit id
    if original_user_input != image_commit_id:
        content = original_user_input
    else:
        content = ""

    with open(path_to.active_branch, "w") as f:
        f.write(content)


def replace_staging_area_with_image(image_path: Path) -> None:
    """After replacing the committed repo content, the entire content of staging_area will be replaced
    with the chosen image content.
    """
    shutil.rmtree(path_to.staging_area)  # TODO: dangerous?
    shutil.copytree(image_path, path_to.staging_area)
    

def remove_except(untracked_files: Set[Path]) -> None:
    """Removes all dirs and files in the repository, 
    except for `.wit` and untracked files (including parents).
    This is used before the content of `staging_area` is copied.
    """
    entries = get_relpaths(path_to.repo, ignore_wit=True, only_files=False)
    dir_ignore = get_dirpaths_to_ignore(untracked_files)
    remove = entries - untracked_files - dir_ignore
    print(remove)
    for entry in remove:
        if entry.is_dir():
            shutil.rmtree(entry)
            # shutil is used because the dir doesn't have to be empty (compared to pathlib\os).
        if entry.is_file():
            entry.unlink()


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


def inner_checkout(user_input, image_commit_id, image_dir_path):
    """Replaces the content of the repository with the content of the chosen image;
    As well as replacing the content of staging_area;
    updating activated.txt, and then references.txt.
    """
    head_id = get_head_id()
    info = status.get_status_info(head_id)
    # Raise error if checkout is impossible:
    if not is_checkout_possible(image_dir_path, info["Changes to Be Committed"], info["Changes Not Staged for Commit"]):
        logger.error(
            "Please make sure that 'Changes to Be Committed' and 'Changes Not Staged for Commit' are empty:"
            )
        status.print_status(head_id, info)
        raise ImpossibleCheckoutError
    # Remove all repo content, except for .wit dir and untracked files; 
    # copy the content of chosen image to repo
    remove_except(info["Untracked Files"])
    shutil.copytree(image_dir_path, path_to.repo, dirs_exist_ok=True)
    # Replace the content of staging_area with chosen image
    replace_staging_area_with_image(image_dir_path)
    # Note: Updating activated.txt should remain before references.txt
    handle_activated_file(image_commit_id, user_input)
    handle_references_file(image_commit_id)