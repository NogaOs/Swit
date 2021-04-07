import argparse
import sys

from loguru import logger

import common.exceptions as err
import inner.checkout as checkout_
from common.helper_funcs import get_head_id, resolve_commit_id, get_valid_commit_path
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


def add(path: str) -> bool:
    try:
        backup_path = get_abs_path(path)
    except FileNotFoundError as e:
        logger.warning(e)
        return False

    inner_add(backup_path)
    logger.info(">>> Backup created.")
    return True


def commit(user_message: str) -> bool:
    inner_commit(user_message)
    logger.info(">>> Commit executed successfully.")
    return True


def status() -> bool:
    try:
        inner_status()
    except err.CommitRequiredError as e:
        logger.warning(e)
        return False
    return True


def checkout(indicator: str) -> bool:
    try:
        image_commit_id = resolve_commit_id(indicator)
        image_dir_path = get_valid_commit_path(image_commit_id, indicator)
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


def graph(is_all: bool, is_entire: bool) -> bool:
    inner_graph(is_all, is_entire)
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
        description="Wit is an open source version control system.",
        epilog="Thank you for supporting wit! <3"
    )
    subparser = parser.add_subparsers(
        dest="command", description="Wit commands:", required=True
    )

    # Init:
    _init = subparser.add_parser(
        "init",
        description="Create a new wit repository.",
    )

    # Add:
    _add = subparser.add_parser(
        "add",
        description="Tells wit to include updates to a particular file or folder in the next commit.",
    )
    _add.add_argument(
        "path", type=str, help="an absolute or relative path to a file or dir"
    )

    # Commit:
    _commit = subparser.add_parser(
        "commit",
        description="Creates a snapshot of the repository.",
    )
    _commit.add_argument("--message", "--m", type=str, help="user message")

    # Status:
    _status = subparser.add_parser(
        "status",
        description="Display the repository and the staging area. Shows which changes have been staged, which haven't, and which files aren't being tracked by wit.",
    )

    # Checkout:
    _checkout = subparser.add_parser(
        "checkout",
        description="Updates files in the repository to match the version in the specified image.",
    )
    _checkout.add_argument(
        "indicator", type=str, help="either a branch name or a commit id"
    )

    # Graph:
    _graph = subparser.add_parser(
        "graph",
        description="Shows a graph of all parental hierarchy, starting from HEAD.",
    )
    _graph.add_argument("--all", action="store_true", help="show all commits and the relations between them")
    _graph.add_argument("--entire", "--e", action="store_true", help="show the entire id of each entry (default: first 6 chars)")

    # Branch:
    _branch = subparser.add_parser(
        "branch",
        description="Create another line of development in the project. Committing under a branch will give your commits a name that's easy to remember.",
    )
    _branch.add_argument("name", type=str, help="branch name")

    # Merge:
    _merge = subparser.add_parser(
        "merge",
        description="Creates a new commit, that is an integration of two other commits.",
    )
    _merge.add_argument(
        "indicator", type=str, help="either a branch name or a commit id"
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
        graph(args.all, args.entire)

    elif args.command == "branch":
        branch(args.name)

    elif args.command == "merge":
        merge(args.indicator)
