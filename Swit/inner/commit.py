import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger

import Swit.common.paths as path_to
from Swit.common.helper_funcs import (
    generate_commit_id, get_parent, handle_references_file
)


def get_image_file(commit_id: str) -> Path:
    return path_to.images / f"{commit_id}.txt"


def get_cur_date_and_timezone() -> str:
    """Returns the current date and a timezone stamp. 
    Example: Fri Jan 29 04:35:12 2021 +02:00
    """
    d = datetime.now()
    date = d.ctime()
    timezone = d.astimezone().isoformat(timespec="minutes").split("+")[1]
    return f"{date} +{timezone}"


def create_metadata_file(path_to_metadata_file: Path, message: str, parent: Optional[str]) -> None:
    """Metadata file is called by the name of the commit id, and contains parent, date, and user message. 
    Example:
    parent=6462de3e3cf99d94e38afd18d11d5251483e320c
    date=Wed Jan 13 23:04:29 2021 +02:00
    message=I like trains.
    """
    date = get_cur_date_and_timezone()
    path_to_metadata_file.write_text(f"parent={parent}\ndate={date}\nmessage={message}")


def add_to_parents_file(commit_id: str, parents: str) -> None:
    """parents.txt contains all of the commit ids, and their parent(s)."""
    with open(path_to.parents, "a") as f:
        f.write(f"{commit_id}={parents}\n")


def clear_changes_to_be_committed() -> None:
    """Every time an `add` command is performed, the filepath is added to this file;
    Every time a commit is performed, this file will be cleared out.
    """
    path_to.changes_to_be_committed.write_text("")


def inner_commit(user_message: str, commit_id: str = generate_commit_id(), parents: Optional[str] = None, is_merge: bool = False) -> None:
    """Creates a snapshot of the staging area.
    Creates the image dir and the metadata file; copies the content of staging area into the image dir;
    updates references, parents, and chenges to be committed files.
    """
    parents = parents or get_parent()
    metadata_path = get_image_file(commit_id)
    image_dir_path = path_to.images / commit_id
    # Create the image dir and file:
    image_dir_path.mkdir()
    create_metadata_file(metadata_path, user_message, parents)
    # Copy the content of staging_area into the new image dir:
    shutil.copytree(path_to.staging_area, image_dir_path, dirs_exist_ok=True)
    # Update references.txt, parents.txt, and changes_to_be_committed.txt
    handle_references_file(commit_id, is_merge)
    add_to_parents_file(commit_id, parents)
    clear_changes_to_be_committed()


def commit(message: str) -> bool:
    inner_commit(message)
    logger.info(">>> Commit executed successfully.")
    return True