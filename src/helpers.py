"""
This file contains functions to interact with the Youtube Data API
and create trees of related videos.
"""

import logging
import random
import re
from typing import Any, Dict, List, Optional

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
