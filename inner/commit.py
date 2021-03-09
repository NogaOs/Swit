import shutil

from datetime import datetime

from pathlib import Path

from typing import List


import common.paths as path_to

from common.helper_funcs import (
    generate_commit_id, get_image_dir, get_parent, handle_references_file
)


def get_cur_date_and_timezone() -> str:
    """Returns the current date and a timezone stamp. 
    Example: Fri Jan 29 04:35:12 2021 +02:00
    """
    d = datetime.now()
    date = d.ctime()
    timezone = d.astimezone().isoformat(timespec="minutes").split("+")[1]
    return f"{date} +{timezone}"


def get_image_file(commit_id: str) -> Path:
    return path_to.images / f"{commit_id}.txt"


def create_metadata_file(path_to_metadata_file, message: str, parent: str) -> None:
    """Metadata file is called by the name of the commit id, and contains parent, date, and user message. Example:
    parent=6462de3e3cf99d94e38afd18d11d5251483e320c
    date=Wed Jan 13 23:04:29 2021 +02:00
    message=I like trains."""
    date = get_cur_date_and_timezone()
    with open(path_to_metadata_file, "w") as f:
        f.write(f"parent={parent}\ndate={date}\nmessage={message}")


def clear_changes_to_be_committed() -> None:
    with open(path_to.changes_to_be_committed, "w") as f:
        f.write("")


def add_to_parents_file(commit_id: str, parents) -> None:
    """parents.txt contains all of the commit ids, and their parent(s)."""
    with open(path_to.parents, "a") as f:
        f.write(f"{commit_id}={parents}\n")


def inner_commit(user_message, commit_id=generate_commit_id(), parents=None) -> None:
    """Creates the image dir and metadata file; updates all relevant files."""
    parents = parents if parents else get_parent()
    metadata_path = get_image_file(commit_id)
    image_dir_path = get_image_dir(commit_id)
    # Create the image dir and file:
    image_dir_path.mkdir()
    create_metadata_file(metadata_path, user_message, parents)
    # Copy the content of staging_area into the new image dir:
    shutil.copytree(path_to.staging_area, image_dir_path, dirs_exist_ok=True)
    # Update references.txt, parents.txt, and changes_to_be_committed.txt
    handle_references_file(commit_id)
    add_to_parents_file(commit_id, parents)
    clear_changes_to_be_committed()
