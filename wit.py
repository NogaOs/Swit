import argparse
import sys

from loguru import logger

import common.exceptions as err
import inner.checkout as checkout_
from common.helper_funcs import get_head_id, get_image_data
from inner.add import get_abs_path, inner_add
from inner.branch import add_branch_name_to_references
from inner.commit import inner_commit
from inner.graph import inner_graph
from inner.init import inner_init
from inner.merge import get_merge_paths, inner_merge
from inner.status import inner_status


def init() -> bool:
    try:
        inner_init(".wit", ("images", "staging_area"))
    except FileExistsError:
        logger.warning("Cannot initiate a repository inside of another repository.")
        return False
    logger.info(">>> All folders were created.")
    return True


def add(path) -> bool:
    try:
        backup_path = get_abs_path(path)
    except FileNotFoundError as e:
        logger.warning(e)
        return False

    inner_add(backup_path)
    logger.info(">>> Backup created.")
    return True


def commit(user_message) -> bool:
    inner_commit(user_message)
    logger.info(">>> Commit executed successfully.")
    return True


def status() -> None:
    try:
        inner_status()
    except err.CommitRequiredError as e:
        logger.warning(e)
        return False


def checkout(indicator: str) -> bool:
    # The indicator could be either a branch name or a commit id.
    try:
        image_commit_id, image_dir_path = get_image_data(indicator)
    except err.CommitIdError as e:
        logger.warning(e)
        return False

    try:
        checkout_.inner_checkout(indicator, image_commit_id, image_dir_path)
    except err.ImpossibleCheckoutError:
        # The error is handled within `inner_checkout`.
        return False
    except FileNotFoundError as e:
        logger.warning(e)
        return False

    logger.info(">>> Checkout Executed Successfully.")
    return True


def graph(is_all: bool) -> bool:
    inner_graph(is_all)
    return True


def branch(branch_name: str) -> bool:
    try:
        add_branch_name_to_references(branch_name)
    except (err.CommitRequiredError, err.BranchNameExistsError) as e:
        logger.warning(e)
        return False

    logger.info(">>> Branch added.")
    return True


def merge(indicator: str) -> bool:
    try:
        paths = get_merge_paths(indicator)
    except err.CommitIdError as e:
        logger.warning(e)
        return False

    try:
        inner_merge(indicator, *paths)
    except err.ImpossibleMergeError as e:
        logger.warning(e)
        return False

    logger.info(">>> Merge was executed successfully.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wit is an open source version control system."
    )
    subparser = parser.add_subparsers(
        dest="command", description="Choose a wit command from the list below:"
    )

    # Init:
    _init = subparser.add_parser(
        "init",
        description="INITTTT",
    )

    # Add:
    _add = subparser.add_parser(
        "add",
        description="Tells wit to include updates to a particular file or folder in the next commit.",
    )
    _add.add_argument(
        "path", type=str, help="An absolute or relative path to a file or dir"
    )

    # Commit:
    _commit = subparser.add_parser(
        "commit",
        description="Creates a snapshot of the repository.",
    )
    _commit.add_argument(
        "--message", "--m", type=str, help="User message"
    )

    # Status:
    _status = subparser.add_parser(
        "status",
        description="---",
    )

    # Checkout:
    _checkout = subparser.add_parser(
        "checkout",
        description="---",
    )
    _checkout.add_argument(
        "indicator", type=str, help="Either a branch name or a commit id"
    )

    # Graph:
    _graph = subparser.add_parser(
        "graph",
        description="---",
    )
    _graph.add_argument('--all', action='store_true', help='---')

    # Branch:
    _branch = subparser.add_parser(
        "branch",
        description="---",
    )
    _branch.add_argument(
        "name", type=str, help="A branch name"
    )

    # Merge:
    _merge = subparser.add_parser(
        "merge",
        description="---",
    )
    _merge.add_argument(
        "indicator", type=str, help="Either a branch name or a commit id"
    )


    args = parser.parse_args()


    if args.command == "init":
        init()

    elif args.command == "add":
        add(args.path)

    elif args.command == "commit":
        commit(args.message)

    elif args.command == "status":
        status()

    elif args.command == "checkout":
        checkout(args.indicator)

    elif args.command == "graph":
        graph(args.all)

    elif args.command == "branch":
        branch(args.name)

    elif args.command == "merge":
        merge(args.indicator)





    # try:
    #     WIT_FUNCTIONS[sys.argv[1]]()
    # except (IndexError, KeyError) as e:
    #     print("\nPlease pass one of the following functions as an argument:")
    #     for i, func in enumerate(WIT_FUNCTIONS.keys(), 1):
    #         print(f"{i} - {func}")
