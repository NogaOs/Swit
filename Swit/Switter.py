import argparse
import sys

from loguru import logger

from Swit.inner.add import add
from Swit.inner.branch import branch
from Swit.inner.checkout import checkout
from Swit.inner.commit import commit
from Swit.inner.graph import graph
from Swit.inner.init import init
from Swit.inner.merge import merge
from Swit.inner.status import status

parser = argparse.ArgumentParser(
    description="Swit is an open source version control system.",
    epilog="Thank you for supporting Swit! <3"
)
subparser = parser.add_subparsers(
    dest="command", description="Swit commands:", required=True
)

# Init:
_init = subparser.add_parser(
    "init",
    description="Create a new swit repository.",
)

# Add:
_add = subparser.add_parser(
    "add",
    description="Tells swit to include updates to a particular file or folder in the next commit.",
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
    description="Display the repository and the staging area. Shows which changes have been staged, which haven't, and which files aren't being tracked by swit.",
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
_graph.add_argument("--full", action="store_true", help="show all commits and the relations between them")
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


WIT_COMMANDS = {
        "init": init,
        "add": add,
        "commit": commit,
        "status": status,
        "checkout": checkout,
        "graph": graph,
        "branch": branch,
        "merge": merge,
    }


def main():
    func = WIT_COMMANDS[args.command]
    params = vars(args)
    params.pop("command")
    func(**params)


if __name__ == "__main__":
    main()
