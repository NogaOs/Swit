import sys

from loguru import logger


import paths

from exceptions import ImpossibleMergeError, WitDirectoryNotFoundError, CommitIdError

from general_funcs import (
    get_head_id, add_branch_name_to_references
)

from inner_init import inner_init

from inner_add import inner_add, get_abs_path

from inner_commit import inner_commit

from inner_status import print_status, get_status_data

import inner_checkout as ck

from inner_graph import inner_graph

from inner_merge import inner_merge, get_merge_paths



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
    head_id = get_head_id()
    data = get_status_data(head_id)
    print_status(head_id, *data)


def checkout():
    try:
        user_input = sys.argv[2]
    except IndexError:
        logger.error(
            "Usage: <python> <path/to/wit.py> <checkout> <branch name OR commit id>"
        )
        return False

    try:
        image_commit_id, image_dir_path = ck.get_image_data(user_input)
    except CommitIdError as e:
        logger.error(e)
        return False

    try:
        if not ck.is_checkout_possible(image_dir_path):
            ck.print_impossible_checkout_message()
            return False
    except FileNotFoundError as e:
        logger.error(e)
        return False

    ck.inner_checkout(user_input, image_commit_id, image_dir_path)
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


def merge():
    try:
        user_input = sys.argv[2]
    except IndexError:
        logger.error("Usage: <python> <path/to/wit.py> <merge> <BRANCH_NAME>")
        return False

    try:
        paths = get_merge_paths(user_input)
    except CommitIdError as e:
        logger.error(e)
        return False

    try:
        inner_merge(user_input, *paths)
    except ImpossibleMergeError as e:
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
