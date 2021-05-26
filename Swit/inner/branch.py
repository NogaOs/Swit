from Swit.common.exceptions import BranchNameExistsError, CommitRequiredError

from loguru import logger

import Swit.common.paths as path_to
from Swit.common.helper_funcs import get_head_id


def does_branch_exist(branch_name: str) -> bool:
    """Returns True if there's already a branch with the given name."""
    lines = path_to.references.read_text().split("\n")
    for line in lines:
        name, _, branch_id = line.partition("=")
        if name == branch_name:
            return True
    return False


def add_branch_name_to_references(
    branch_name: str,
) -> None:
    """Adds a line to references file with the given branch name.
    The branch id will be identical to the current HEAD id.
    Branch will be added only if there isn't another branch 
    with the same name.
    """
    if not path_to.references.exists():
        raise CommitRequiredError(
            "Must commit at least once before adding a branch name."
        )

    if does_branch_exist(branch_name):
        raise BranchNameExistsError(
            f"There is already a branch named {branch_name}."
        )

    head_id = get_head_id()
    with open(path_to.references, "a") as f:
        f.write(f"{branch_name}={head_id}\n")


def branch(name: str) -> bool:
    try:
        add_branch_name_to_references(name)
    except (CommitRequiredError, BranchNameExistsError) as e:
        logger.warning(e)
        return False

    logger.info(">>> Branch added.")
    return True
