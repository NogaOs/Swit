from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import Swit.common.paths as path_to
import networkx as nx
from Swit.common.helper_funcs import get_head_id
from matplotlib import pyplot as plt


def get_parent_file_content() -> List[str]:
    return path_to.parents.read_text().split("\n")


def get_parents_by_image() -> Dict[str, List[str]]:
    """Returns a defaultdict representing each commit id, and the commit id of it's parent(s).
    Example: {'123': ['234'], '234': ['345', '678']}
    """
    parent_file_content = get_parent_file_content()

    batman_commit_id, _, no_parents = parent_file_content[0].partition("=")
    image_and_parents = defaultdict(list, {batman_commit_id: []})

    for line in parent_file_content[1:]:
        image, _, parents = line.strip().partition("=")
        parents = parents.split(",")
        image_and_parents[image].extend(parent for parent in parents)

    return image_and_parents


def edgenerator(
    image_and_parents: Dict[str, List[str]]
) -> List[Tuple[str, str]]:
    """Iterates over the parents_by_image dict, and returns a list of tuples -
    each tuple represents the child and parent nodes. If a node has more than one
    parent, it shall be represented with multiple tuples.
    For a list ['a', 'b', 'c'], will return [('a', 'b'), ('b', 'c')]."""
    return [
        (node, parent)
        for node, parents in image_and_parents.items()
        for parent in parents
    ]


def get_parent_edges_of(
    image_and_parents: Dict[str, List[str]], image_id: str
) -> List[Tuple[str, str]]:
    """Starting from a certain id (HEAD in this case), returns all parents until the first commit."""
    edges = []
    awaiting = [image_id]
    i = 0
    for i in range(len(awaiting)):
        cur_image = awaiting[i]
        parents = image_and_parents[cur_image]
        for parent in parents:
            edges.append((cur_image, parent))
            awaiting.append(parent)
    return edges


def plot_graph(edges: List[Tuple[str, str]]) -> None:
    g = nx.DiGraph()
    g.add_edges_from(edges)
    plt.tight_layout()
    nx.draw_networkx(g, arrows=True)
    plt.show()


def inner_graph(is_all: bool, show_entire_id: bool) -> None:
    """Shows a graph of all parental hierarchy, starting from HEAD.
    If is_all is True, the graph will show ALL commits and the relations between them.
    If is_entire is True, it will show the entire id of each entry.
    """
    parents_by_image = get_parents_by_image()

    if is_all:
        edges = edgenerator(parents_by_image)
    else:
        head_id = get_head_id()
        edges = get_parent_edges_of(parents_by_image, head_id)

    if not show_entire_id:
        edges = [(x[:6], y[:6]) for x, y in edges]

    plot_graph(edges)


def graph(full: bool, entire: bool) -> bool:
    inner_graph(full, entire)
    return True