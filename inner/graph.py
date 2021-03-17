from collections import defaultdict

from pathlib import Path

from typing import Dict, List, Tuple

import networkx as nx

from matplotlib import pyplot as plt


import common.paths as path_to

from common.helper_funcs import get_head_id



def get_parent_file_content() -> List[str]:
    with open(path_to.parents, "r") as f:
        lines = f.readlines()
    return lines


def get_parents_of_image_dict(show_first_six_digits=False) -> Dict[str, List[str]]:
    """Returns a defaultdict representing each commit id, and the commit id of it's parent(s).
    Example: {'123': ['234'], '234': ['345', '678']}
    """
    parent_file_content = get_parent_file_content()

    batman_commit_id = parent_file_content[0].split("=")[0]  # cuz it has no parents
    image_and_parents = defaultdict(list, {batman_commit_id: []})

    for line in parent_file_content[1:]:
        image, _, parents = line.partition("=")
        parents = parents.split(", ")
        for parent in parents:
            image_and_parents[image].append(parent.strip())

    return image_and_parents


def edgenerator(
    image_and_parents: Dict[str, List[str]]
) -> List[Tuple[str, str]]:
    """For a list ['a', 'b', 'c'], will yield [('a', 'b'), ('b', 'c')]."""
    return [
        (node, parent)
        for node, parents in image_and_parents.items()
        for parent in parents
    ]


def get_parent_edges_of(
    image_and_parents: Dict[str, List[str]], image_id: str
) -> List[Tuple[str, str]]:
    """Returns the EDGES for the graph method."""
    edges = []
    awaiting = [image_id]
    i = 0
    while i < len(awaiting):
        # There was also a parents != [] condition, but it was removed. Just leaving this here in case it broke something
        cur_image = awaiting[i]
        parents = image_and_parents[cur_image]
        for parent in parents:
            edges.append((cur_image, parent))
            awaiting.append(parent)
        i += 1
    return edges


def plot_graph(edges: List[Tuple[str, str]]) -> None:
    g = nx.DiGraph()
    g.add_edges_from(edges)
    plt.tight_layout()
    nx.draw_networkx(g, arrows=True)
    plt.show()


def inner_graph(is_all: bool, show_first_six_digits=True) -> None:
    parents_dict = get_parents_of_image_dict()

    if is_all:
        edges = edgenerator(parents_dict)
    else:
        head_id = get_head_id()
        edges = get_parent_edges_of(parents_dict, head_id)

    if show_first_six_digits:
        edges = [(x[:6], y[:6]) for x, y in edges]

    plot_graph(edges)
