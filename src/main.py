"""
This script collects related videos from YouTube using the YouTube Data API.
It builds a tree structure of related videos starting from a given video ID,
and allows for various configurations such as depth, width, and display options.
"""

import argparse
import os
import subprocess

import matplotlib.pyplot as plt
import networkx as nx
from googleapiclient.discovery import HttpError, build

from lib import (
    convert_imports,
    convert_tree,
    force_until_quota,
    get_colors,
    get_layers,
    get_titles,
    get_tree,
    hierarchy_pos,
    parse_video_id,
)


def main():
    """
    Main function to parse arguments and execute the YouTube related video collector.
    It initializes the YouTube API client, retrieves related videos, and processes
    them based on user-defined parameters.
    """
    parser = argparse.ArgumentParser(description="Youtube Related Video Collector")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Search Depth")
    parser.add_argument("-w", "--width", type=int, default=3, help="Search Width")
    parser.add_argument("-s", "--seed", type=str, help="Initial Youtube Video Link")
    parser.add_argument(
        "-a", "--apikey", type=int, default=0, help="Which API key should be used"
    )
    parser.add_argument(
        "-D",
        "--display",
        type=str,
        default="title",
        help="Display Video Titles: 'title' | Video Ids: 'videoId' | Channel Ids: 'channelId'",
    )
    parser.add_argument(
        "-l", "--log", action="store_true", help="Store the tree inside of a log file"
    )
    parser.add_argument(
        "-g",
        "--graph",
        action="store_true",
        help="""Whether to convert the tree to a graph that will be exported to a
 graphML file(only works with -D channelName)""",
    )
    parser.add_argument(
        "-i",
        "--treeimport",
        type=str,
        default=None,
        help="Import the trees for a given file and convert them to a graph",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Keep calculating trees until the quota is exceeded",
    )
    parser.add_argument(
        "-t",
        "--titles",
        type=str,
        default=None,
        help="Extract only the titles from a given file",
    )
    parser.add_argument(
        "-A",
        "--aggressive",
        action="store_true",
        help="Do the same as with -f but cycle through all available api keys",
    )
    parser.add_argument(
        "-m",
        "--maxdepth",
        type=int,
        default=10000,
        help="Total depth of the tree to be built with -f or -A (must be a multiple of depth)",
    )
    args = parser.parse_args()

    seed = args.seed
    width = args.width
    depth = args.depth
    api_index = args.apikey
    display = args.display
    log = args.log
    graph = args.graph
    treeimport = args.treeimport
    force = args.force
    titles = args.titles
    aggressive = args.aggressive
    max_depth = args.maxdepth
    video_id = parse_video_id(seed) if seed else None

    # Add your own API keys here!!!
    api_key0 = ""
    api_key1 = ""
    api_key2 = ""
    api_key3 = ""
    api_key4 = ""
    api_key5 = ""
    api_key6 = ""
    api_key7 = ""
    api_key8 = ""
    api_key9 = ""
    api_key10 = ""
    api_key11 = ""
    api_key12 = ""
    api_key13 = ""
    api_key14 = ""
    api_key15 = ""
    api_key16 = ""
    api_key17 = ""
    api_key18 = ""
    api_key19 = ""

    api_keys = [
        api_key0,
        api_key1,
        api_key2,
        api_key3,
        api_key4,
        api_key5,
        api_key6,
        api_key7,
        api_key8,
        api_key9,
        api_key10,
        api_key11,
        api_key12,
        api_key13,
        api_key14,
        api_key15,
        api_key16,
        api_key17,
        api_key18,
        api_key19,
    ]

    youtube = build("youtube", "v3", developerKey=api_keys[api_index])
    if not (treeimport or force or titles or aggressive):
        layers = get_layers(youtube, video_id, width, depth)
        if log:
            with open(f"./data/{video_id}.log", "a", encoding="utf-8") as logfile:
                print(layers, file=logfile)

    # display video ids as node labels
    if display == "videoId":
        tree, root = get_tree(layers)
        colors = get_colors(layers, tree)[0]

        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(tree, root)
        nx.draw(tree, pos=pos, with_labels=True, font_size=9, node_color=colors)
        plt.title("Related Videos")
        plt.show()

    # display video titles as node labels
    elif (
        display == "title" or display == "channelId" or display == "channelName"
    ) and not (treeimport or force or titles or aggressive):
        tree, root = get_tree(layers)
        convert_tree(youtube, tree, root, layers, display, graph)

    # import/convert trees saved in treeimport
    elif treeimport:
        convert_imports(treeimport)

    # calculate trees until the quota is exceeded
    elif force:
        if not os.path.isfile(f"./data/{video_id}.log"):
            open(f"./data/{video_id}.log", "w", encoding="utf-8").close()

        with open(f"./data/{video_id}.log", "r", encoding="utf-8") as logfile:
            linecount = sum(1 for _ in logfile)

        if linecount == 0:
            layers = get_layers(youtube, video_id, width, depth)
            with open(f"./data/{video_id}.log", "a", encoding="utf-8") as logfile:
                print(layers, file=logfile)
            print("Starting tree calculation...")
            force_until_quota(0, 0, 0, 0, 0, youtube, width, depth, max_depth, video_id)

        else:
            line, leaf, current_leafs, next_leafs, current_depth = 0, 0, 0, 0, 0
            with open(
                f"./data/{video_id}_breakpoint.txt", "r", encoding="utf-8"
            ) as file:
                for i, l in enumerate(file):
                    if i == 0:
                        line = l
                    if i == 1:
                        leaf = l
                    if i == 2:
                        current_leafs = l
                    if i == 3:
                        next_leafs = l
                    if i == 4:
                        current_depth = l
            line = int(line.strip())
            leaf = int(leaf.strip())
            current_leafs = int(current_leafs.strip())
            next_leafs = int(next_leafs.strip())
            current_depth = int(current_depth.strip())
            print(f"Continuing tree calculation from line: {line} - leaf: {leaf}")
            force_until_quota(
                line,
                leaf,
                current_leafs,
                next_leafs,
                current_depth,
                youtube,
                width,
                depth,
                max_depth,
                video_id,
            )

    # extract only the tiles of a given logfile
    elif titles:
        get_titles(titles)

    # call the force option with every available api key
    elif aggressive:
        for i in range(len(api_keys)):
            print(f"Using API-Key: {i}")
            p = subprocess.Popen(
                [
                    "python",
                    "main.py",
                    f"-s {seed}",
                    f"-w {width}",
                    f"-d {depth}",
                    f"-m {max_depth}",
                    "-f",
                    f"-a {i}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            for line in iter(p.stdout.readline, b""):
                print(line.rstrip().decode())

    # invalid arguments
    else:
        parser.print_usage()


if __name__ == "__main__":
    try:
        main()
    except HttpError:
        print("seems like the quota has been exceeded :(")
