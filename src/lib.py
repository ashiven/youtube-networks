"""This file contains the main functions to interact with the Youtube Data API and
create tree and graph structures of related videos.
"""

import logging
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from helpers import (
    get_colors,
    get_layers,
    get_tree,
    hierarchy_pos,
    save_layers,
    video_id_to_channel_id_dict,
    video_id_to_channel_name_dict,
    video_id_to_title_dict,
)

logger = logging.getLogger(__name__)


DATA_PATH = "./src/data/"
GRAPHS_PATH = "./src/graphs/"
TITLES_PATH = "./src/titles/"


def _draw_tree(tree: nx.Graph, root: str, colors: List[str], labels: Dict, title: str) -> None:
    """Helper function to draw the tree with the specified parameters."""
    plt.figure(figsize=(15, 10))
    pos = hierarchy_pos(tree, root)
    nx.draw(tree, pos=pos, with_labels=False, node_color=colors)
    nx.draw_networkx_labels(tree, pos, labels, font_size=9)
    plt.title(title)
    plt.show()


def _convert_to_graph(
    tree: nx.Graph,
    root: str,
    video_id_to_channel_name: Dict,
    graph: Optional[nx.Graph] = None,
    log_line: Optional[int] = 0,
) -> nx.Graph:
    """Helper function to convert the tree into a network graph."""
    graph = graph or nx.Graph()

    for edge in tree.edges():
        u_video_id, v_video_id = edge
        u_channel_name = video_id_to_channel_name[u_video_id]
        v_channel_name = video_id_to_channel_name[v_video_id]
        if (
            v_channel_name not in graph.nodes()
            and u_channel_name == "Not Found"
            and v_channel_name != "Not Found"
        ):
            graph.add_node(v_channel_name, size=1)
            continue
        elif (
            u_channel_name not in graph.nodes()
            and v_channel_name == "Not Found"
            and u_channel_name != "Not Found"
        ):
            graph.add_node(u_channel_name, size=1)
            continue
        elif (
            u_channel_name,
            v_channel_name,
        ) not in graph.edges() and u_channel_name != v_channel_name:
            graph.add_edge(u_channel_name, v_channel_name, weight=1)
        elif (u_channel_name, v_channel_name) in graph.edges():
            graph.edges[u_channel_name, v_channel_name]["weight"] += 1

    for node in tree.nodes():
        u_channel_name = video_id_to_channel_name[node]
        if u_channel_name == "Not Found":
            continue
        elif log_line == 0 or (log_line > 0 and node != root):
            current_size = graph.nodes[u_channel_name].get("size", 1)
            current_size += 0.1
            nx.set_node_attributes(graph, {u_channel_name: current_size}, "size")

    return graph


def _save_graph(graph: nx.Graph, channel_name: str) -> None:
    """Saves the graph to a GraphML file."""
    channel_name = re.sub(r"\s+", "_", channel_name)
    channel_name = re.sub(r"[^\w\s-]", "", channel_name)
    nx.write_graphml(graph, f"{GRAPHS_PATH}{channel_name}.graphml")
    logger.info("Created graph: %s%s.graphml", GRAPHS_PATH, channel_name)


def draw_tree(
    youtube: Any,
    video_id: str,
    width: int,
    depth: int,
    display: str,
    convert_graph: bool,
) -> None:
    """
    Takes the tree retrieved from get_tree, visualizes it, and optionally converts it to
    a graph.

    :param layers: The layers that were returned by get_layers
    :param display: The type of display ('videoId', 'title', 'channelId', 'channelName')
    :param convert_graph: If True, converts the tree to a graph and saves it as a
        GraphML file
    :return: None
    """
    layers = get_layers(youtube, video_id, width, depth)
    save_layers(layers, video_id)
    tree, root = get_tree(layers)
    colors = get_colors(layers, tree)

    if display == "channelName":
        labels = video_id_to_channel_name_dict(layers, tree, use_noembed=True)
        _draw_tree(
            tree,
            root,
            colors,
            labels,
            "Channel Name Tree",
        )
    elif display == "videoId":
        labels = {node: node for node in tree.nodes()}
        _draw_tree(
            tree,
            root,
            colors,
            labels,
            "Video ID Tree",
        )
    elif display == "channelId":
        labels = video_id_to_channel_id_dict(layers, tree)
        _draw_tree(
            tree,
            root,
            colors,
            labels,
            "Channel ID Tree",
        )
    elif display == "title":
        labels = video_id_to_title_dict(layers, tree)
        _draw_tree(
            tree,
            root,
            colors,
            labels,
            "Video Title Tree",
        )

    if convert_graph:
        video_id_to_channel_name = video_id_to_channel_name_dict(layers, tree)
        graph = _convert_to_graph(tree, root, video_id_to_channel_name)
        root_channel_name = video_id_to_channel_name[root]
        _save_graph(graph, root_channel_name)


def _layers_list_from_logfile(logpath: str) -> List[Dict]:
    """Reads the logfile and returns a list of layers."""
    layers_list = []
    with open(logpath, "r", encoding="utf-8") as logfile:
        for line in logfile:
            layers = eval(line)  # pylint: disable=eval-used
            layers_list.append(layers)
    return layers_list


def convert_imports(logpath: str) -> None:
    """
    Given the path to a logfile that contains multiple tree-representing layers,
    converts this set of layers into one network graph that will be saved in the graphs
    folder.

    :param logpath: The name of the logfile containing the layers
    :return: None
    """
    file_name, use_noembed = None, True
    graph = nx.Graph()
    layers_list = _layers_list_from_logfile(logpath)

    for log_line, layers in enumerate(layers_list):
        subtree, subroot = get_tree(layers)
        use_noembed = not use_noembed if log_line % 20 == 0 and log_line > 0 else use_noembed
        video_id_to_channel_name = video_id_to_channel_name_dict(
            layers, subtree, use_noembed=use_noembed
        )
        subroot_channel_name = video_id_to_channel_name[subroot]
        file_name = subroot_channel_name if file_name is None else file_name

        logger.info("Converting subtree: %d with root: %s", log_line, subroot_channel_name)
        graph = _convert_to_graph(
            subtree,
            subroot,
            video_id_to_channel_name,
            graph=graph,
            log_line=log_line,
        )

    logger.info(
        "Converted %d subtrees into a network graph with %d nodes and %d edges",
        len(layers_list),
        len(graph.nodes()),
        len(graph.edges()),
    )
    _save_graph(graph, file_name)


def _save_breakpoint(
    video_id: str,
    start_line: int,
    leaf_index: int,
    current_leafs: int,
    next_leafs: int,
    current_depth: int,
    leaf_layer_video_ids: List[str],
    evaluating_root: bool,
) -> None:
    """Saves the current state of the calculation to a breakpoint file."""
    with open(f"{DATA_PATH}{video_id}_breakpoint.txt", "w", encoding="utf-8") as file:
        file.write(str(start_line) + "\n")
        file.write(str(leaf_index) + "\n")
        if evaluating_root:
            file.write(str(0) + "\n")
            file.write(str(next_leafs) + "\n")
        else:
            file.write(str(current_leafs) + "\n")
            file.write(str(next_leafs - len(leaf_layer_video_ids)) + "\n")
        file.write(str(current_depth))
    logger.info("Saved logfile: %s%s.log", DATA_PATH, video_id)
    logger.info("Saved breakpoint: %s%s_breakpoint.txt", DATA_PATH, video_id)


def _calc_leaf_trees(
    start_line: int,
    current_leaf_index: int,
    current_leafs: int,
    next_leafs: int,
    current_depth: int,
    youtube: Any,
    width: int,
    depth: int,
    max_depth: int,
    video_id: str,
) -> tuple[bool, Optional[int], Optional[int]]:
    """
    Starting at the line number specified in the start_line parameter, calculates the
    layers for all of the leaf nodes of the tree in the logfile <video_id>.log.

    :param start_line: The line number in the logfile where the calculation should start
    :param current_leaf_index: The index of the current leaf node in the layer
    :param current_leafs: The number of leaf nodes left in the current layer
    :param next_leafs: The number of leaf nodes in the next layer
    :param current_depth: The current overall depth of the tree
    :param youtube: The Youtube Data API object
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :param video_id: The ID of the Youtube video for which the layers should be
        calculated
    :return: A tuple containing a boolean indicating whether the evaluation should
        continue, the number of current leafs left, and the number of next leafs to be
        evaluated
    """
    evaluating_root = False
    with open(f"{DATA_PATH}{video_id}.log", "r", encoding="utf-8") as logfile:
        for line_number, line in enumerate(logfile):
            if line_number == start_line:
                start_layers = eval(line)  # pylint: disable=eval-used
                leaf_layer = start_layers[-1]
                leaf_layer_video_ids = list(leaf_layer.keys())
                if current_leafs == 0:
                    current_leafs = len(leaf_layer_video_ids) + 1
                    evaluating_root = True
                else:
                    next_leafs += len(leaf_layer_video_ids)

    with open(f"{DATA_PATH}{video_id}.log", "a", encoding="utf-8") as logfile:
        for leaf_index, leaf_video_id in enumerate(leaf_layer_video_ids):
            if leaf_index >= current_leaf_index:
                try:
                    if current_depth >= max_depth:
                        raise ValueError("max_depth has been reached")
                    layers = get_layers(youtube, leaf_video_id, width, depth)
                    print(layers, file=logfile)
                    logger.info("Saved leafTree: %d", leaf_index)
                except Exception:  # pylint: disable=broad-except
                    _save_breakpoint(
                        video_id,
                        start_line,
                        leaf_index,
                        current_leafs,
                        next_leafs,
                        current_depth,
                        leaf_layer_video_ids,
                        evaluating_root,
                    )
                    continue_eval, current_leafs, next_leafs = False, 0, 0
                    return continue_eval, current_leafs, next_leafs

    continue_eval = True
    return continue_eval, current_leafs, next_leafs


def _force_until_quota(
    start_line: int,
    current_leaf_index: int,
    current_leafs: int,
    next_leafs: int,
    current_depth: int,
    youtube: Any,
    width: int,
    depth: int,
    max_depth: int,
    video_id: str,
) -> None:
    """
    Repeatedly calls the function _calc_leaf_trees until either the API usage limit has
    been exceeded, or max_depth has been reached.

    :param start_line: The line number in the logfile where the calculation should start
    :param current_leaf_index: The index of the current leaf node in the layer
    :param current_leafs: The number of leaf nodes left in the current layer
    :param next_leafs: The number of leaf nodes in the next layer
    :param current_depth: The current overall depth of the tree
    :param youtube: The Youtube Data API object
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :param video_id: The ID of the Youtube video for which the layers should be
        calculated
    :return: None
    """
    continue_eval = True
    while continue_eval:
        logger.info("Calculating leaf trees on line: %d", start_line)

        # We calculated the tree for each leaf of the first tree (current_leafs)
        # and now we calculate the tree for each leaf of each tree we
        # just calculated (next_leafs) - one tree depth level has been completed
        if current_leafs == 0:
            current_depth += depth
            current_leafs = next_leafs
            next_leafs = 0

        continue_eval, current_leafs, next_leafs = _calc_leaf_trees(
            start_line,
            current_leaf_index,
            current_leafs,
            next_leafs,
            current_depth,
            youtube,
            width,
            depth,
            max_depth,
            video_id,
        )
        start_line += 1
        current_leaf_index = 0
        current_leafs -= 1


def _calc_new_tree(youtube: Any, video_id: str, width: int, depth: int, max_depth: int) -> None:
    """Helper to calculate a new tree from scratch."""
    layers = get_layers(youtube, video_id, width, depth)
    save_layers(layers, video_id)
    _force_until_quota(
        start_line=0,
        current_leaf_index=0,
        current_leafs=0,
        next_leafs=0,
        current_depth=0,
        youtube=youtube,
        width=width,
        depth=depth,
        max_depth=max_depth,
        video_id=video_id,
    )


def _continue_tree_calc(
    youtube: Any, video_id: str, width: int, depth: int, max_depth: int
) -> None:
    """Helper to continue the tree calculation from the last saved state in the
    breakpoint file.
    """
    start_line, current_leaf_index, current_leafs, next_leafs, current_depth = (
        0,
        0,
        0,
        0,
        0,
    )
    with open(f"{DATA_PATH}{video_id}_breakpoint.txt", "r", encoding="utf-8") as file:
        for line_index, line in enumerate(file):
            if line_index == 0:
                start_line = int(line.strip())
            if line_index == 1:
                current_leaf_index = int(line.strip())
            if line_index == 2:
                current_leafs = int(line.strip())
            if line_index == 3:
                next_leafs = int(line.strip())
            if line_index == 4:
                current_depth = int(line.strip())
    _force_until_quota(
        start_line,
        current_leaf_index,
        current_leafs,
        next_leafs,
        current_depth,
        youtube,
        width,
        depth,
        max_depth,
        video_id,
    )


def force_until_quota(
    youtube: Any,
    video_id: str,
    width: int,
    depth: int,
    max_depth: int,
) -> None:
    """
    Calculates the layers of related videos until the API usage limit has been exceeded
    or max_depth has been reached. If the logfile for the video_id does not exist, it
    will be created and the layers will be calculated from scratch. If the logfile
    exists, it will continue the calculation from the last saved state in the breakpoint
    file.

    :param youtube: The Youtube Data API object
    :param video_id: The ID of the Youtube video for which the layers should be
        calculated
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :return: None
    """
    if not os.path.isfile(f"{DATA_PATH}{video_id}.log"):
        logger.info("Starting tree calculation...")
        _calc_new_tree(youtube, video_id, width, depth, max_depth)
    elif not os.path.isfile(f"{DATA_PATH}{video_id}_breakpoint.txt"):
        logger.info("Log file exists, but no breakpoint file found. Starting from scratch...")
        _calc_new_tree(youtube, video_id, width, depth, max_depth)
    else:
        logger.info("Log file and breakpoint file found. Continuing tree calculation...")
        _continue_tree_calc(youtube, video_id, width, depth, max_depth)


def calculate_aggressive(
    api_keys: list[str],
    seed: str,
    width: int,
    depth: int,
    max_depth: int,
) -> None:
    """
    Calculates the layers of related videos for a given seed video using multiple API
    keys in an aggressive manner, meaning it will use all API keys in parallel until the
    quota is exceeded or max_depth is reached. Each API key will be used to start a new
    process that runs the main.py script with the specified parameters.

    :param api_keys: A list of API keys to use for the calculation
    :param seed: The ID of the Youtube video to start with
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :return: None
    """
    for api_key in api_keys:
        logger.info("Using API-Key: %s", api_key)
        force_process = subprocess.Popen(
            [
                "python",
                "main.py",
                f"-s {seed}",
                f"-w {width}",
                f"-d {depth}",
                f"-m {max_depth}",
                f"-a {api_key}",
                "-f",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for line in iter(force_process.stdout.readline, b""):
            logger.info("%s", line.rstrip().decode())


def get_titles(logpath: str) -> None:
    """
    Extracts the titles of every video from a specified logfile in the data folder and
    saves them in the titles folder.

    :param logpath: The path to the logfile containing the layers
    :return: None
    """
    video_titles = []
    layers_list = _layers_list_from_logfile(logpath)

    for layers in layers_list:
        for layer in layers:
            for video_info in layer.values():
                title = video_info[1]
                video_titles.append(title)

    filename = os.path.basename(logpath).replace(".log", ".titles")
    with open(f"{TITLES_PATH}{filename}", "w", encoding="utf-8") as title_file:
        for title in video_titles:
            title_file.write(title + "\n")

    logger.info("Extracted titles: %s", f"{TITLES_PATH}{filename}")
