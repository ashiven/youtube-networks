"""
This file contains functions to interact with the Youtube Data API
and to visualize related videos as a graph.
"""

import logging
import os
import random
import re
import subprocess
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import requests

logger = logging.getLogger(__name__)


def parse_video_id(link: str) -> Optional[str]:
    """Uses a regular expression to extract the video ID  from a Youtube link

    :param link: The Youtube link from which the video ID should be extracted
    :return: The video ID if the link is valid, otherwise None
    """
    regex = r"(?:youtu\.be\/|youtube\.com\/watch\?v=|youtube\.com\/embed\/)([^?&\/]+)"
    res = re.search(regex, link)

    if res:
        video_id = res.group(1)
        return video_id
    return None


def get_video_info(youtube: Any, video_id: str) -> tuple[str, str]:
    """Takes a Youtube video ID and returns the title and channel ID of the video

    :param youtube: The Youtube Data API object
    :param video_id: The ID of the Youtube video
    :return: A tuple containing the title and channel ID of the video
    """
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    return (
        response["items"][0]["snippet"]["title"],
        response["items"][0]["snippet"]["channelId"],
    )


def get_channel_name(youtube: Any, channel_id: str) -> str:
    """Takes a Youtube channel ID and returns the name of the channel

    :param youtube: The Youtube Data API object
    :param channel_id: The ID of the Youtube channel
    :return: The name of the Youtube channel
    """
    response = youtube.channels().list(part="snippet", id=channel_id).execute()
    return response["items"][0]["snippet"]["title"]


def get_channel_name_embed(video_id: str, noembed: bool) -> Optional[str]:
    """Takes a Youtube channel ID and returns the name of the channel using oembed or noembed

    :param video_id: The ID of the Youtube video
    :param noembed: If True, uses noembed.com to fetch the channel name,
    otherwise uses youtube.com/oembed
    :return: The name of the Youtube channel or None if the request fails
    """
    try:
        if noembed:
            response = requests.get(
                "https://noembed.com/embed?url=https://www.youtube.com/watch?v="
                + video_id,
                timeout=10,
            )
        else:
            response = requests.get(
                "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v="
                + video_id,
                timeout=10,
            )
        response.raise_for_status()
        video_info = response.json()
        return video_info["author_name"]

    except requests.RequestException:
        return None


def get_related(youtube: Any, video_id: str, width: int) -> Dict:
    """Takes a video ID and returns related videos via the Youtube Data API

    :param youtube: The Youtube Data API object
    :param video_id: The ID of the Youtube video
    :param width: The number of related videos to retrieve
    :return: A dictionary containing related video IDs as keys and a list of
    [video_id, title, channel_id] as values
    """
    response = (
        youtube.search()
        .list(part="snippet", relatedToVideoId=video_id, maxResults=width, type="video")
        .execute()
    )

    related_videos = {}
    for item in response["items"]:
        related_video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel_id = item["snippet"]["channelId"]
        related_videos[related_video_id] = [video_id, title, channel_id]

    return related_videos


def get_layers(youtube: Any, video_id: str, width: int, depth: int) -> List[Dict]:
    """Calculates the layers of related videos with the help of get_related

    :param youtube: The Youtube Data API object
    :param video_id: The ID of the Youtube video to start with
    :param width: The number of related videos to retrieve at each layer
    :param depth: The number of layers to retrieve
    :return: A list of dictionaries, where each dictionary represents a layer
    of related videos. Each dictionary contains video IDs as keys and a list of
    [related_to, title, channel_id] as values
    """
    title, channel_id = get_video_info(youtube, video_id)
    layers = [{} for _ in range(depth + 1)]
    layers[0] = {video_id: [None, title, channel_id]}

    for layer_depth in range(1, depth + 1):
        if layer_depth == 1:
            layers[layer_depth] = get_related(youtube, video_id, width)
        else:
            for video in layers[layer_depth - 1]:
                related = get_related(youtube, video, width)
                layers[layer_depth].update(related)

    return layers


def layers_to_title_dict(layers: List[Dict]) -> Dict:
    """Takes the layers returned by get_layers and converts them into a dictionary
    mapping video IDs to video titles

    :param layers (List[Dict]): The layers that were returned by get_layers
    :return: A dictionary containing video IDs as keys and titles as values
    """
    video_id_to_title = {}
    for layer in layers:
        for video_id, video_info in layer.items():
            video_id_to_title[video_id] = video_info[1]
    return video_id_to_title


def layers_to_channel_dict(layers: List[Dict]) -> Dict:
    """Takes the layers returned by get_layers and converts them into a dictionary
    mapping video IDs to channel IDs

    :param layers (List[Dict]): The layers that were returned by get_layers
    :return: A dictionary containing video IDs as keys and channel IDs as values
    """
    video_id_to_channel_id = {}
    for layer in layers:
        for video_id, video_info in layer.items():
            video_id_to_channel_id[video_id] = video_info[2]

    return video_id_to_channel_id


def get_colors(layers: List[Dict], tree: nx.Graph) -> tuple[List[str], Dict]:
    """Takes the layers generated in get_layers and their tree representation
    and returns a coloring according to the Youtube channels

    :param layers (List[Dict]): The layers that were returned by get_layers
    :param tree (nx.Graph): The tree representation of the layers
    :return: A tuple containing a list of colors for each node in the tree
    and a dictionary mapping video IDs to channel IDs
    """
    video_id_to_channel_id = layers_to_channel_dict(layers)
    video_id_to_channel_id = {
        node: video_id_to_channel_id[node]
        for node in tree.nodes()
        if node in video_id_to_channel_id
    }
    unique_channel_ids = list(set(video_id_to_channel_id.values()))

    colors = [
        "gold",
        "violet",
        "blue",
        "silver",
        "limegreen",
        "orange",
        "darkorange",
        "yellow",
        "green",
        "red",
        "limegreen",
    ] * 10

    channel_id_to_color = {
        channel_id: colors[i] for i, channel_id in enumerate(unique_channel_ids)
    }
    node_to_color = {
        node: channel_id_to_color[video_id_to_channel_id[node]] for node in tree.nodes()
    }
    colorings = [node_to_color.get(node, "red") for node in tree.nodes()]

    return colorings, video_id_to_channel_id


def get_tree(layers: List[Dict]) -> tuple[nx.Graph, str]:
    """Converts the layers generated in get_layers to a tree, which can then be visualized

    :param layers (List[Dict]): The layers that were returned by get_layers
    :return: A tuple containing the tree as a networkx Graph and the root node ID
    """
    tree = nx.Graph()
    for layer in layers:
        for video_id, video_info in layer.items():
            related_to = video_info[0]
            if not tree.has_node(video_id) and related_to is not None:
                tree.add_node(video_id)
                parent_video_id = related_to
                tree.add_edge(parent_video_id, video_id)
    root = next(iter(layers[1].values()))[0]

    return tree, root


def draw_tree(
    youtube: Any,
    layers: List[Dict],
    display: str,
    convert_graph: bool,
) -> None:
    """Takes the tree retrieved from get_tree, visualizes it, and optionally converts it to a graph

    :param youtube: The Youtube Data API object
    :param layers: The layers that were returned by get_layers
    :param display: The type of display ('videoId', 'title', 'channelId', 'channelName')
    :param convert_graph: If True, converts the tree to a graph and saves it as a GraphML file
    :return: None
    """

    def _draw_tree(tree: nx.Graph, colors: List[str], labels: Dict, title: str) -> None:
        """Helper function to draw the tree with the specified parameters"""
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(tree, root)
        nx.draw(tree, pos=pos, with_labels=False, node_color=colors)
        nx.draw_networkx_labels(tree, pos, labels, font_size=9)
        plt.title(title)
        plt.show()

    def _convert_graph(
        tree: nx.Graph,
        root: str,
        video_id_to_channel_id: Dict,
        channel_id_to_channel_name: Dict,
    ) -> None:
        """Helper function to convert the tree into a network graph"""
        graph = nx.Graph()
        for edge in tree.edges():
            u_video_id, v_video_id = edge
            u_channel_name = channel_id_to_channel_name[
                video_id_to_channel_id[u_video_id]
            ]
            v_channel_name = channel_id_to_channel_name[
                video_id_to_channel_id[v_video_id]
            ]
            if (
                not (u_channel_name, v_channel_name) in graph.edges()
                and u_channel_name != v_channel_name
            ):
                graph.add_node(u_channel_name, size=1)
                graph.add_node(v_channel_name, size=1)
                graph.add_edge(u_channel_name, v_channel_name, weight=1)
            elif (u_channel_name, v_channel_name) in graph.edges():
                graph.edges[u_channel_name, v_channel_name]["weight"] += 1

        for node in tree.nodes():
            u_channel_name = channel_id_to_channel_name[video_id_to_channel_id[node]]
            graph.nodes[u_channel_name]["size"] += 1

        nx.write_graphml(graph, f"./graphs/{root}.graphml")
        logger.info("Created graph: ./graphs/%s.graphml", root)

    tree, root = get_tree(layers)
    colors, video_id_to_channel_id = get_colors(layers, tree)
    if display == "channelName" or convert_graph:
        unique_channel_ids = list(set(video_id_to_channel_id.values()))
        channel_id_to_channel_name = {
            channel_id: get_channel_name(youtube, channel_id)
            for channel_id in unique_channel_ids
        }
        labels = {
            node: channel_id_to_channel_name[video_id_to_channel_id[node]]
            for node in tree.nodes()
        }
        _draw_tree(
            tree,
            colors,
            labels,
            "Channel Name Tree",
        )
        if convert_graph:
            _convert_graph(
                tree, root, video_id_to_channel_id, channel_id_to_channel_name
            )
    elif display == "videoId":
        labels = {node: node for node in tree.nodes()}
        _draw_tree(
            tree,
            colors,
            labels,
            "Video ID Tree",
        )
    elif display == "channelId":
        labels = {node: video_id_to_channel_id[node] for node in tree.nodes()}
        _draw_tree(
            tree,
            colors,
            labels,
            "Channel ID Tree",
        )
    elif display == "title":
        video_id_to_title = layers_to_title_dict(layers)
        labels = {node: video_id_to_title[node] for node in tree.nodes()}
        _draw_tree(
            tree,
            colors,
            labels,
            "Video Title Tree",
        )


def convert_imports(filename: str) -> None:
    """Given the path to a logfile that contains multiple layers derived with get_layers,
    converts this set of layers into one network graph that will be saved in the graphs folder

    :param filename: The name of the logfile containing the layers
    :return: None
    """
    layers_list = []
    with open(f"./data/{filename}", "r", encoding="utf-8") as logfile:
        for line in logfile:
            layers = eval(line)  # pylint: disable=eval-used
            layers_list.append(layers)

    file_name = None
    use_noembed = True
    node_total = 0
    edge_total = 0
    graph = nx.Graph()
    for log_line, layers in enumerate(layers_list):
        tree, root = get_tree(layers)
        logger.info("Converting subtree: %d with root: %s", log_line, root)

        # name the file after the root of the first tree
        if file_name is None:
            file_name = channel_id_to_channel_name[video_id_to_channel_id[root]]

        # swap between noembed and oembed every 20 iterations
        if log_line % 20 == 0 and log_line > 0:
            use_noembed = not use_noembed

        # create a bunch of mappings between video IDs, channel IDs, and channel names
        video_id_to_channel_id = layers_to_channel_dict(layers)
        video_id_to_channel_id = {
            node: video_id_to_channel_id[node] for node in tree.nodes()
        }
        video_id_to_channel_info = {}
        for video_id in tree.nodes():
            channel_name = get_channel_name_embed(video_id, use_noembed)
            if channel_name:
                channel_name = re.sub(r"[^\w\s-]", "", channel_name).strip()
                video_id_to_channel_info[video_id] = [
                    channel_name,
                    video_id_to_channel_id[video_id],
                ]
            else:
                video_id_to_channel_info[video_id] = [
                    "Not Found",
                    video_id_to_channel_id[video_id],
                ]
        channel_id_to_channel_name = {
            channel_id: channel_name
            for channel_name, channel_id in video_id_to_channel_info.values()
        }

        # add nodes and edges to the graph for each tree
        for edge in tree.edges():
            u_video_id, v_video_id = edge
            u_channel_name = channel_id_to_channel_name[
                video_id_to_channel_id[u_video_id]
            ]
            v_channel_name = channel_id_to_channel_name[
                video_id_to_channel_id[v_video_id]
            ]
            if (
                not v_channel_name in graph.nodes()
                and u_channel_name == "Not Found"
                and v_channel_name != "Not Found"
            ):
                graph.add_node(v_channel_name, size=1)
                continue
            elif (
                not u_channel_name in graph.nodes()
                and v_channel_name == "Not Found"
                and u_channel_name != "Not Found"
            ):
                graph.add_node(u_channel_name, size=1)
                continue
            elif (
                not (u_channel_name, v_channel_name) in graph.edges()
                and u_channel_name != v_channel_name
            ):
                graph.add_node(u_channel_name, size=1)
                graph.add_node(v_channel_name, size=1)
                graph.add_edge(u_channel_name, v_channel_name, weight=1)
            elif (u_channel_name, v_channel_name) in graph.edges():
                graph.edges[u_channel_name, v_channel_name]["weight"] += 1
            edge_total += 1

        for node in tree.nodes():
            u_channel_name = channel_id_to_channel_name[video_id_to_channel_id[node]]
            if u_channel_name == "Not Found":
                continue
            elif log_line == 0:
                graph.nodes[u_channel_name]["size"] += 0.1
            elif log_line > 0 and node != root:
                graph.nodes[u_channel_name]["size"] += 0.1
            node_total += 1

    file_name = re.sub(r"\s+", "_", file_name)
    file_name = re.sub(r"[^\w\s-]", "", file_name)
    logger.info("Converted tree T with V(T)=%d, E(T)=%d", node_total, edge_total)
    nx.write_graphml(graph, f"./graphs/{file_name}.graphml")
    logger.info("Created graph: ./graphs/%s.graphml", file_name)


def _get_leaf_trees(
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
    """Starting at the line number specified in the start_line parameter, calculates the layers for
    all of the leaf nodes of the tree in the logfile <video_id>.log.

    :param start_line: The line number in the logfile where the calculation should start
    :param current_leaf_index: The index of the current leaf node in the layer
    :param current_leafs: The number of leaf nodes left in the current layer
    :param next_leafs: The number of leaf nodes in the next layer
    :param current_depth: The current overall depth of the tree
    :param youtube: The Youtube Data API object
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :param video_id: The ID of the Youtube video for which the layers should be calculated
    :return: A tuple containing a boolean indicating whether the evaluation should continue,
    the number of current leafs left, and the number of next leafs to be evaluated
    """

    def _save_breakpoint(
        start_line: int,
        leaf_index: int,
        current_leafs: int,
        next_leafs: int,
        current_depth: int,
        leaf_ids: List[str],
        evaluating_root: bool,
    ) -> None:
        """Saves the current state of the calculation to a breakpoint file"""
        with open(f"./data/{video_id}_breakpoint.txt", "w", encoding="utf-8") as file:
            file.write(str(start_line) + "\n")
            file.write(str(leaf_index) + "\n")
            if evaluating_root:
                file.write(str(0) + "\n")
                file.write(str(next_leafs) + "\n")
            else:
                file.write(str(current_leafs) + "\n")
                file.write(str(next_leafs - len(leaf_ids)) + "\n")
            file.write(str(current_depth))
        logger.info("Saved logfile: ./data/%s.log", video_id)
        logger.info("Saved breakpoint: ./data/%s_breakpoint.txt", video_id)

    evaluating_root = False
    with open(f"./data/{video_id}.log", "r", encoding="utf-8") as logfile:
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

    with open(f"./data/{video_id}.log", "a", encoding="utf-8") as logfile:
        for leaf_index, leaf_video_id in enumerate(leaf_layer_video_ids):
            if leaf_index >= current_leaf_index:
                if current_depth >= max_depth:
                    logger.info("Reached maxDepth. Quitting...")
                    _save_breakpoint(
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

                try:
                    layers = get_layers(youtube, leaf_video_id, width, depth)
                    print(layers, file=logfile)
                    logger.info("Saved leafTree: %d", leaf_index)
                except Exception:  #  pylint: disable=broad-except
                    _save_breakpoint(
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
    """Repeatedly calls the function get_leaf_trees until either the API usage limit
    has been exceeded, or max_depth has been reached

    :param start_line: The line number in the logfile where the calculation should start
    :param current_leaf_index: The index of the current leaf node in the layer
    :param current_leafs: The number of leaf nodes left in the current layer
    :param next_leafs: The number of leaf nodes in the next layer
    :param current_depth: The current overall depth of the tree
    :param youtube: The Youtube Data API object
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :param video_id: The ID of the Youtube video for which the layers should be calculated
    :return: None
    """
    continue_eval = True
    while continue_eval:
        logger.info("Calling _get_leaf_trees(%d)...", start_line)
        if current_leafs == 0:
            current_depth += depth
            current_leafs = next_leafs
            next_leafs = 0
        continue_eval, current_leafs, next_leafs = _get_leaf_trees(
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
        # current_leaf_index needs to continue from breakpoint on the first call of get_leaf_trees()
        current_leaf_index = 0
        current_leafs -= 1
        start_line += 1


def force_until_quota(
    youtube: Any,
    video_id: str,
    width: int,
    depth: int,
    max_depth: int,
) -> None:
    """Calculates the layers of related videos until the API usage limit has been exceeded
    or max_depth has been reached. If the logfile for the video_id does not exist,
    it will be created and the layers will be calculated from scratch. If the logfile exists,
    it will continue the calculation from the last saved state in the breakpoint file.

    :param youtube: The Youtube Data API object
    :param video_id: The ID of the Youtube video for which the layers should be calculated
    :param width: The width of one tree (number of related videos per layer)
    :param depth: The depth of one tree (number of layers)
    :param max_depth: The maximum overall depth that should not be exceeded
    :return: None
    """

    def _calc_new_tree() -> None:
        layers = get_layers(youtube, video_id, width, depth)
        with open(f"./data/{video_id}.log", "w", encoding="utf-8") as logfile:
            print(layers, file=logfile)
        _force_until_quota(0, 0, 0, 0, 0, youtube, width, depth, max_depth, video_id)

    def _continue_tree_calc() -> None:
        start_line, current_leaf_index, current_leafs, next_leafs, current_depth = (
            0,
            0,
            0,
            0,
            0,
        )
        with open(f"./data/{video_id}_breakpoint.txt", "r", encoding="utf-8") as file:
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

    if not os.path.isfile(f"./data/{video_id}.log"):
        logger.info("Starting tree calculation...")
        _calc_new_tree()
    elif not os.path.isfile(f"./data/{video_id}_breakpoint.txt"):
        logger.info(
            "Log file exists, but no breakpoint file found. Starting from scratch..."
        )
        _calc_new_tree()
    else:
        logger.info(
            "Log file and breakpoint file found. Continuing tree calculation..."
        )
        _continue_tree_calc()


def calculate_aggressive(
    api_keys: list[str],
    seed: str,
    width: int,
    depth: int,
    max_depth: int,
) -> None:
    """Calculates the layers of related videos for a given seed video using multiple API keys
    in an aggressive manner, meaning it will use all API keys in parallel until the quota is
    exceeded or max_depth is reached. Each API key will be used to start a new process
    that runs the main.py script with the specified parameters.

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


def get_titles(filename: str) -> None:
    """Extracts the titles of every video from a specified logfile in the data
    folder and saves them in the titles folder

    :param filename: The name of the logfile containing the layers
    :return: None
    """
    video_titles = []
    with open(f"./data/{filename}", "r", encoding="utf-8") as file:
        data = file.read()

    items = data.split("}, {")
    for item in items:
        video_info = item.split(": [")[1].split(", ")[1].strip("'")
        video_titles.append(video_info)

    with open(f"./titles/{filename}", "w", encoding="utf-8") as file:
        for title in video_titles:
            file.write(title + "\n")

    logger.info("Extracted titles: ./titles/%s", filename)


def hierarchy_pos(graph, root=None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    """
    if not nx.is_tree(graph):
        raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

    if root is None:
        if isinstance(graph, nx.DiGraph):
            root = next(
                iter(nx.topological_sort(graph))
            )  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(graph.nodes))

    def _hierarchy_pos(
        graph,
        root,
        width=1.0,
        vert_gap=0.2,
        vert_loc=0,
        xcenter=0.5,
        pos=None,
        parent=None,
    ):
        """
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        """

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(graph.neighbors(root))
        if not isinstance(graph, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(
                    graph,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(graph, root, width, vert_gap, vert_loc, xcenter)
