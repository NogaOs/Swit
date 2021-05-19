import os
from glob import glob
from pathlib import Path
from sys import argv, exit

from loguru import logger

from Swit.common.exceptions import WitDirectoryNotFoundError


def is_init() -> bool:  # TODO: is there a better way?
    if len(argv) == 2:
        return argv[1] == "init"
    return False


def get_uppermost_dir(cwd: Path) -> Path:
    """Returns the root directory.
    Example: `C:\\` fow windows, `/` for Linux.
    """
    cur_path = cwd.parent
    parent = cur_path.parent
    while cur_path != parent:
        cur_path, parent = cur_path.parent, parent.parent
    return cur_path


def get_repo_path(cwd: Path) -> Path:
    """Starting from the current working directory, moves up the tree until it finds a directory
    containing a `.swit` directory. That dir shall be referenced to as the repository.
    """
    uppermost_dir = get_uppermost_dir(cwd)
    while cwd != uppermost_dir:
        for dir_name in cwd.glob("*.swit"):
            if dir_name:
                return cwd
        cwd = cwd.parent
    raise WitDirectoryNotFoundError(
        "No `.swit` directory found. Please make sure you're set to the correct cwd, or create a repository using the `init()` method."
    )


cwd = Path(os.getcwd())

# Program will fail if repo not found, in any command except for `init`.
if not is_init():
    try:
        repo = get_repo_path(cwd)
    except WitDirectoryNotFoundError as e:
        logger.error(e)
        exit()


    wit_repo = repo / ".swit"

    staging_area = wit_repo / "staging_area"

    references = wit_repo / "references.txt"

    images = wit_repo / "images"

    parents = wit_repo / "parents.txt"

    changes_to_be_committed = wit_repo / "changes_to_be_committed.txt"

    active_branch = wit_repo / "activated.txt"
