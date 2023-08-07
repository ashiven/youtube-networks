from googleapiclient.discovery import build, HttpError
import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
from lib import *
from typing import *
import subprocess


def main():
    # parse the arguments supplied by the user
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
        help="Whether to convert the tree to a graph that will be exported to a graphML file(only works with -D channelName)",
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
        help="Keep calculating trees and storing them in the specific file until the quota is exceeded",
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
        "--maxDepth",
        type=int,
        default=10000,
        help="Total depth of the tree to be built with -f or -A (must be a multiple of depth)",
    )
    args = parser.parse_args()

    seed = args.seed
    width = args.width
    depth = args.depth
    apiIndex = args.apikey
    display = args.display
    log = args.log
    graph = args.graph
    treeimport = args.treeimport
    force = args.force
    titles = args.titles
    aggressive = args.aggressive
    maxDepth = args.maxDepth
    videoId = None
    if seed:
        videoId = parseVideoId(seed)

    # TODO: Add your own API keys here!!
    apiKey0 = ""
    apiKey1 = ""
    apiKey2 = ""
    apiKey3 = ""
    apiKey4 = ""
    apiKey5 = ""
    apiKey6 = ""
    apiKey7 = ""
    apiKey8 = ""
    apiKey9 = ""
    apiKey10 = ""
    apiKey11 = ""
    apiKey12 = ""
    apiKey13 = ""
    apiKey14 = ""
    apiKey15 = ""
    apiKey16 = ""
    apiKey17 = ""
    apiKey18 = ""
    apiKey19 = ""

    apiKeys = [
        apiKey0,
        apiKey1,
        apiKey2,
        apiKey3,
        apiKey4,
        apiKey5,
        apiKey6,
        apiKey7,
        apiKey8,
        apiKey9,
        apiKey10,
        apiKey11,
        apiKey12,
        apiKey13,
        apiKey14,
        apiKey15,
        apiKey16,
        apiKey17,
        apiKey18,
        apiKey19,
    ]

    # we create the youtube object for interacting with the API and getLayers() to retrieve the layers of related videos
    youtube = build("youtube", "v3", developerKey=apiKeys[apiIndex])
    if not (treeimport or force or titles or aggressive):
        layers = getLayers(youtube, videoId, width, depth)

        # write the result for layers into a log file
        if log:
            with open(f"./data/{videoId}.log", "a", encoding="utf-8") as logfile:
                print(layers, file=logfile)

    # display video ids as node labels
    if display == "videoId":
        T, root = getTree(layers)
        colors = getColors(layers, T)[0]

        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos, with_labels=True, font_size=9, node_color=colors)
        plt.title("Related Videos")
        plt.tight_layout
        plt.show()

    # display video titles as node labels
    elif (
        display == "title" or display == "channelId" or display == "channelName"
    ) and not (treeimport or force or titles or aggressive):
        T, root = getTree(layers)
        convertTree(youtube, T, root, layers, display, graph)

    # import/convert trees saved in treeimport
    elif treeimport:
        convertImports(youtube, treeimport)

    # calculate trees until the quota is exceeded and save the stopping point in {videoId}_breakpoint.txt
    elif force:
        if not os.path.isfile(f"./data/{videoId}.log"):
            open(f"./data/{videoId}.log", "w", encoding="utf-8").close()

        with open(f"./data/{videoId}.log", "r", encoding="utf-8") as logfile:
            linecount = sum(1 for _ in logfile)

        if linecount == 0:
            layers = getLayers(youtube, videoId, width, depth)
            with open(f"./data/{videoId}.log", "a", encoding="utf-8") as logfile:
                print(layers, file=logfile)
            print("Starting tree calculation...")
            forceUntilQuota(0, 0, 0, 0, 0, youtube, width, depth, maxDepth, videoId)

        else:
            with open(f"./data/{videoId}_breakpoint.txt", "r") as file:
                for i, l in enumerate(file):
                    if i == 0:
                        line = l
                    if i == 1:
                        leaf = l
                    if i == 2:
                        currentLeafs = l
                    if i == 3:
                        nextLeafs = l
                    if i == 4:
                        currentDepth = l
            line = int(line.strip())
            leaf = int(leaf.strip())
            currentLeafs = int(currentLeafs.strip())
            nextLeafs = int(nextLeafs.strip())
            currentDepth = int(currentDepth.strip())
            print(f"Continuing tree calculation from line: {line} - leaf: {leaf}")
            forceUntilQuota(
                line,
                leaf,
                currentLeafs,
                nextLeafs,
                currentDepth,
                youtube,
                width,
                depth,
                maxDepth,
                videoId,
            )

    # extract only the tiles of a given logfile
    elif titles:
        getTitles(titles)

    # call the force option with every available api key
    elif aggressive:
        for i in range(len(apiKeys)):
            print(f"Using API-Key: {i}")
            p = subprocess.Popen(
                [
                    "python",
                    "main.py",
                    f"-s {seed}",
                    f"-w {width}",
                    f"-d {depth}",
                    f"-m {maxDepth}",
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

    # TODO: Add an option to import/convert multiple logfiles into one network-graph


if __name__ == "__main__":
    try:
        main()
    except HttpError:
        print("seems like the quota has been exceeded :(")
