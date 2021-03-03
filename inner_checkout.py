from pathlib import Path

from typing import Tuple

import shutil


import paths

from exceptions import CommitIdError

from general_funcs import (
    get_image_dir, handle_references_file, resolve_commit_id, get_image_data,
    copy_changed_files
)

from inner_status import (
    get_org_and_added_files, get_files_with_different_content, 
    get_changes_to_be_committed
)

# from wit import status  # should I use only inner functions?



def is_checkout_possible(image_dir_path: Path) -> bool:
    """The checkout command will not run if the commit_id is wrong;
    if there are any files that are to be committed;
    or any files that are not staged for commit.
    """
    if not image_dir_path.exists():
        raise FileNotFoundError(
            f"The path '{image_dir_path}' does not exist. You might have entered the wrong branch name / commit id."
        )

    original_files, added_files = get_org_and_added_files()
    changes_not_staged_for_commit = get_files_with_different_content(
        paths.repo, paths.staging_area, original_files.intersection(added_files)
    )
    changes_to_be_committed = get_changes_to_be_committed()
    return not any((changes_not_staged_for_commit, changes_to_be_committed))


def print_impossible_checkout_message() -> None:
    print("\n" + "-" * 60)
    print(
        "\n>>> Please make sure that 'Changes to Be Committed' and 'Changes Not Staged for Commit' are empty:\n"
    )
    # status()


def handle_activated_file(image_commit_id, original_user_input) -> None:
    """If the user passed a branch name, it will appear under activated.txt.
    Else, there will be no active branch and the file will be empty.
    """
    # Checks if the user passed a branch name or a commit id
    if original_user_input != image_commit_id:
        content = original_user_input
    else:
        content = ""

    with open(paths.active_branch, "w") as f:
        f.write(content)


def replace_staging_area_with_commit_dir(path_to_commit_dir):
    """After replacing the committed repo content, the entire content of staging_area will be replaced
    with the chosen image content.
    """
    shutil.rmtree(paths.staging_area, ignore_errors=True)  # dangerous?
    shutil.copytree(path_to_commit_dir, paths.staging_area)
    # Sometimes I get this error:
    # FileExistsError: [WinError 183] Cannot create a file when that file already exists:
    # 'C:\\Users\\noga.osin\\Desktop\\codeStuff\\mesickasCourse\\week10\\stupidFolder\\.wit\\staging_area'
    # out of the blue. wtf? if I call the function again, problem solved!
    # whaaaaathe fuckkkkk


def remove_all_but_wit() -> None:
    """Removes all dirs and files in the repository, except for `.wit`.
    This is used before the content of `staging_area` is copied.
    """
    not_wit_entries = set(paths.repo.glob("*")) - set(paths.repo.glob("*.wit"))
    for entry in not_wit_entries:
        if entry.is_dir():
            shutil.rmtree(entry)
            # shutil is used because the dir doesn't have to be empty (compared to pathlib\os).
        elif entry.is_file():
            entry.unlink()


def inner_checkout(user_input, image_commit_id, image_dir_path):
    """Replaces the content of the repository with the content of the chosen image;
    As well as replacing the content of staging_area;
    updating activated.txt, and then references.txt.
    """
    # Erase all repo content, except for .wit dir; copy the content of chosen image to repo
    remove_all_but_wit()
    shutil.copytree(image_dir_path, paths.repo, dirs_exist_ok=True)
    # Replace the content of staging_area with chosen image
    replace_staging_area_with_commit_dir(image_dir_path)
    # Note: Updating activated.txt should remain before references.txt
    handle_activated_file(image_commit_id, user_input)
    handle_references_file(image_commit_id)