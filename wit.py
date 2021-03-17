import sys

from loguru import logger


import inner.checkout as ck

import common.exceptions as err

from common.helper_funcs import (
    add_branch_name_to_references, get_head_id, get_image_data
)

from inner.add import get_abs_path, inner_add

from inner.commit import inner_commit

from inner.graph import inner_graph

from inner.init import inner_init

from inner.merge import get_merge_paths, inner_merge

from inner.status import inner_status



def init():
    try:
        inner_init(".wit", ("images", "staging_area"))
    except FileExistsError:
        logger.error("Cannot initiate a repository inside of another repository.")
        return False
    logger.info(">>> All folders were created.")
    return True


def add():
    try:
        backup_path = get_abs_path(sys.argv[2])
    except IndexError:
        logger.error("Usage: python <path/to/wit.py> <add> <backup path>")
        return False
    except FileNotFoundError as e:
        logger.error(e)
        return False

    inner_add(backup_path)

    logger.info(">>> Backup created.")
    return True


def commit():
    try:
        user_message = sys.argv[2]
    except IndexError:
        logger.error("Usage: <python> <path/to/wit.py> <commit> <MESSAGE>")
        return False

    inner_commit(user_message)

    logger.info(">>> Commit executed successfully.")
    return True


def status() -> None:
    try:
        inner_status()
    except err.ImpossibleStatusError as e:
        logger.error(e)
        return False


def checkout():
    try:
        user_input = sys.argv[2]  # TODO: deleted an untracked file
    except IndexError:
        logger.error(
            "Usage: <python> <path/to/wit.py> <checkout> <branch name OR commit id>"
        )
        return False

    try:
        image_commit_id, image_dir_path = get_image_data(user_input)
    except err.CommitIdError as e:
        logger.error(e)
        return False

    try:
        ck.inner_checkout(user_input, image_commit_id, image_dir_path)
    except err.ImpossibleCheckoutError:
        # The error is being handled within `inner_checkout`.
        return False
    except FileNotFoundError as e:
        logger.error(e)
        return False

    
    logger.info(">>> Checkout Executed Successfully.")


def graph():
    is_all = False
    if len(sys.argv) == 3:
        is_all = sys.argv[2] == "--all"  # TODO: is there a better way?
        if not is_all:
            logger.error("Usage: <python> <path/to/wit.py> <branch> [--all]")
            return False

    inner_graph(is_all)
    return


def branch():
    try:
        branch_name = sys.argv[2]
    except IndexError:
        logger.error("Usage: <python> <path/to/wit.py> <branch> <NAME>")
        return False

    add_branch_name_to_references(branch_name)
    logger.info(">>> Branch added.")


def merge():  # TODO: didn't workkkkk
    try:
        user_input = sys.argv[2]
    except IndexError:
        logger.error("Usage: <python> <path/to/wit.py> <merge> <BRANCH_NAME>")
        return False

    try:
        paths = get_merge_paths(user_input)
    except err.CommitIdError as e:
        logger.error(e)
        return False

    try:
        inner_merge(user_input, *paths)
    except err.ImpossibleMergeError as e:
        logger.error(e)
        return False

    logger.info(">>> Merge was executed successfully.")



WIT_FUNCTIONS = {
    "init": init,
    "add": add,
    "commit": commit,
    "status": status,
    "checkout": checkout,
    "graph": graph,
    "branch": branch,
    "merge": merge,
}


if __name__ == "__main__":
    try:
        WIT_FUNCTIONS[sys.argv[1]]()
    except (IndexError, KeyError) as e:
        print("\nPlease pass one of the following functions as an argument:")
        [print(f"{i} - {func}") for i, func in enumerate(WIT_FUNCTIONS.keys(), 1)]
