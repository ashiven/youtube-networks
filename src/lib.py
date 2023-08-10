import networkx as nx
import random
import re
import networkx as nx
import matplotlib.pyplot as plt
from typing import *
import requests


def parseVideoId(link: str) -> Optional[str]:
    """Uses a regular expression to extract the video ID  from a Youtube link

    Args:
        link (str): The link of the Youtube video

    Returns:
        Optional[str]: The extracted video ID if the link was valid
    """

    regex = r"(?:youtu\.be\/|youtube\.com\/watch\?v=|youtube\.com\/embed\/)([^?&\/]+)"
    res = re.search(regex, link)

    if res:
        videoId = res.group(1)
        return videoId
    return None


def getVideoInfo(youtube: Any, videoId: str) -> tuple[str, str]:
    """Takes a Youtube video ID and returns the title and channel ID of the video

    Args:
        youtube (Any): The Youtube Data API object
        videoId (str): The ID of the video (retrievable via parseVideoId)

    Returns:
        tuple[str, str]: A tuple containing the title and the channel ID of the video
    """

    response = youtube.videos().list(part="snippet", id=videoId).execute()
    return (
        response["items"][0]["snippet"]["title"],
        response["items"][0]["snippet"]["channelId"],
    )


def getChannelName(youtube: Any, channelId: str) -> str:
    """Takes a Youtube channel ID and returns the name of the channel

    Args:
        youtube (Any): The Youtube Data API object
        channelId (str): The ID of the Youtube channel

    Returns:
        str: The name of the Youtube channel
    """

    response = youtube.channels().list(part="snippet", id=channelId).execute()
    return response["items"][0]["snippet"]["title"]


def getChannelNameEmbed(videoId: str, method: str) -> Optional[str]:
    """Takes a Youtube channel ID and returns the name of the channel without using the Youtube Data API

    Args:
        videoId (str): The ID of the Youtube video (retrievable via parseVideoId)
        method (str): Specify if the channel name should be retrieved via oembed or noembed

    Returns:
        Optional[str]: The name of the Youtube channel
    """

    try:
        if method == "noembed":
            response = requests.get(
                "https://noembed.com/embed?url=https://www.youtube.com/watch?v="
                + videoId
            )
        elif method == "oembed":
            response = requests.get(
                "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v="
                + videoId
            )
        dict = eval(response.text)
        return dict["author_name"]
    except:
        return None


def getRelated(youtube: Any, videoId: str, width: int) -> Dict:
    """Takes a video ID and returns related videos via the Youtube Data API

    Args:
        youtube (Any): The Youtube Data API object
        videoId (str): The ID of the Youtube video (retrievable via ParseVideoId)
        width (int): Specifies how many related videos should be fetched

    Returns:
        Dict: A dictionary with the video ID of the related videos as keys and a list containing the title, parent video ID, and channel ID as values.

    """

    response = (
        youtube.search()
        .list(part="snippet", relatedToVideoId=videoId, maxResults=width, type="video")
        .execute()
    )

    related = {}
    for item in response["items"]:
        title = item["snippet"]["title"]
        id = item["id"]["videoId"]
        channelId = item["snippet"]["channelId"]
        related[id] = [videoId, title, channelId]

    return related


def getLayers(youtube: Any, videoId: str, width: int, depth: int) -> List[Dict]:
    """Calculates the layers of related videos with the help of getRelated

    Args:
        youtube (Any): The Youtube Data API object
        videoId (str): The ID of the Youtube video (retrievable via ParseVideoId)
        width (int): The number of related videos per video
        depth (int): The number of layers to be calculated

    Returns:
        List[Dict]: A list containing one dictionary with video metadata(see getRelated) per layer
    """

    layers = [{} for _ in range(depth + 1)]
    title, channelId = getVideoInfo(youtube, videoId)
    layers[0] = {videoId: [None, title, channelId]}

    for i in range(1, depth + 1):
        if i == 1:
            layers[i] = getRelated(youtube, videoId, width)
        else:
            for video in layers[i - 1]:
                related = getRelated(youtube, video, width)
                layers[i].update(related)

    return layers


def layersToTitleDict(layers: List[Dict]) -> Dict:
    """Takes the layers returned by getLayers and converts them into a dictionary for quickly converting video IDs to their respective titles

    Args:
        layers (List[Dict]): The layers that were returned by getLayers

    Returns:
        Dict: A dictionary containing video IDs as keys and video titles as values
    """

    d = {}
    for layer in layers:
        for key, value in layer.items():
            d[key] = value[1]
    return d


def layersToChannelDict(layers: List[Dict]) -> Dict:
    """Takes the layers returned by getLayers and converts them into a dictionary for quickly converting video IDs to their respective channel IDs

    Args:
        layers (List[Dict]): The layers that were returned by getLayers

    Returns:
        Dict: A dictionary containing video IDs as keys and channel IDs as values
    """

    d = {}
    for layer in layers:
        for key, value in layer.items():
            d[key] = value[2]
    return d


# takes the dictionary from layersToDict() and uses it to return the matching video Title
def keyToTitle(d: Dict, videoId: str) -> Optional[str]:
    """Returns the title for a given video ID via the dictionary that was generated in layersToDict

    Args:
        dict (Dict): The dictionary generated in layersToDict
        videoId (str): The ID of the Youtube video

    Returns:
        Optional[str]: The title of the Youtube video if it is contained in the dictionary
    """

    if videoId in d:
        return d[videoId]
    return None


def getColors(layers: List[Dict], T: nx.Graph) -> tuple[List[str], Dict]:
    """Takes the layers generated in getLayers and their tree representation and returns a coloring according to the Youtube channels

    Args:
        layers (List[Dict]): The layers generated via getLayers
        T (nx.Graph): The tree representation of layers (retrievable via getTree)

    Returns:
        tuple[List[str], Dict]: A tuple containing the list of colors and a dictionary for converting video IDs to channel IDs
    """

    # convert layers to a dictionary with key: videoId, value: channelId
    dict = layersToChannelDict(layers)
    # give every node its appropriate channelId label, replacing its previous videoId labels
    labels = {}
    for node in T.nodes():
        labels[node] = dict[node]
    # create a list of unique channel Ids and then create a list of colors with one color for each channel Id
    uniqueChannelIds = list(set(dict.values()))
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
        "orange",
        "darkorange",
        "yellow",
        "green",
        "red",
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
        "gold",
        "violet",
        "blue",
        "silver",
        "yellow",
        "green",
        "red",
        "limegreen",
        "orange",
        "darkorange",
    ]

    # map every channelId to a color and after that map every node in the tree to the color corresponding with its channelId
    channelToColor = {
        channelId: colors[count] for count, channelId in enumerate(uniqueChannelIds)
    }
    nodeToColor = {node: channelToColor[labels[node]] for node in T.nodes()}
    # finally, return the list of colors that will be used for the nodes, red being the default color for undefined channelIds
    return [nodeToColor.get(node, "red") for node in T.nodes()], labels


def getTree(layers: List[Dict]) -> tuple[nx.Graph, str]:
    """Converts the layers generated in getLayers to a tree, which can then be visualized

    Args:
        layers (List[Dict]): The layers generated in getLayers

    Returns:
        tuple[nx.Graph, str]: A tuple containing the tree representation of layers as a NetworkX graph, and the name of the root node
    """

    T = nx.Graph()
    # iterate over layers and add edges according to parent node specified in value[0]
    for layer in layers:
        for key, value in layer.items():
            if not T.has_node(key) and value[0] != None:
                T.add_node(key)
                parentKey = value[0]
                T.add_edge(parentKey, key)
    root = next(iter(layers[1].values()))[0]
    return T, root


# takes a tree with the node names being video Ids and converts that tree
# into one that is labeled with the respective channel Ids belonging to the video Ids
def convertTree(
    youtube: Any, T: nx.Graph, root: str, layers: List[Dict], display: str, graph: bool
) -> None:
    """Takes the tree retrieved from getTree, the list of colors generated in getColors, and a label specification to further embellish the tree, and then displays it

    Args:
        youtube (Any): The Youtube Data API object
        T (nx.Graph): The tree that was generated in getTree
        root (str): The name of the root node
        layers (List[Dict]): The layers that were generated in getLayers
        display (str): Gives the option to choose whether to display the titles of the Youtube videos, their IDs, their channel IDs, or their channel names
        graph (bool): An option that can be enabled in conjunction with the display option 'channelName' to convert the tree into its network graph representation
    """

    colors, labels = getColors(layers, T)

    if display == "channelId":
        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos, with_labels=False, node_color=colors)
        nx.draw_networkx_labels(T, pos, labels, font_size=9)

        # show plot
        plt.title("Channel Id Tree")
        plt.tight_layout
        plt.show()

    elif display == "title":
        # convert layers to a dictionary with key: videoId, value: title
        dict = layersToTitleDict(layers)

        # give every node its appropriate title label, replacing its previous videoId labels
        labels = {}
        for node in T.nodes():
            labels[node] = dict[node]

        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos, with_labels=False, node_color=colors)
        nx.draw_networkx_labels(T, pos, labels, font_size=9)

        # show plot
        plt.title("Title Tree")
        plt.tight_layout
        plt.show()

    elif display == "channelName":
        # list with unique channel Ids
        channelIdList = list(set(labels.values()))

        # create dict with key: channelId ,value: channelName
        channelDict = {
            channelId: getChannelName(youtube, channelId) for channelId in channelIdList
        }

        # give every node its appropriate channelName label, replacing its previous videoId labels
        channelLabels = {}
        for node in T.nodes():
            channelLabels[node] = channelDict[labels[node]]

        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos, with_labels=False, node_color=colors)
        nx.draw_networkx_labels(T, pos, channelLabels, font_size=9)

        # show plot
        plt.title("Channel Name Tree")
        plt.tight_layout
        plt.show()

        if graph:
            G = nx.Graph()

            for edge in T.edges():
                u, v = edge
                U = channelDict[labels[u]]
                V = channelDict[labels[v]]
                if not (U, V) in G.edges() and U != V:
                    G.add_node(U, size=1)
                    G.add_node(V, size=1)
                    G.add_edge(U, V, weight=1)
                elif (U, V) in G.edges():
                    G.edges[U, V]["weight"] += 1

            for node in T.nodes():
                U = channelDict[labels[node]]
                G.nodes[U]["size"] += 1

            nx.write_graphml(G, f"./graphs/{root}.graphml")
            print(f"Created graph: ./graphs/{root}.graphml")
    return


def convertImports(youtube: Any, filename: str) -> None:
    """Given the name of a logfile that contains multiple layers derived with getLayers, converts this set of layers into one network graph that will be saved in the graphs folder

    Args:
        youtube (Any): The Youtube Data API object
        filename (str): The name of the logfile (logfiles can be found in the data folder)
    """

    layerList = []
    with open(f"./data/{filename}", "r", encoding="utf-8") as logfile:
        for line in logfile:
            layers = eval(line)
            layerList.append(layers)

    fileName = None
    nodeTotal = 0
    edgeTotal = 0
    methodCounter = 0
    prevMethod = "noembed"
    currentMethod = "oembed"
    G = nx.Graph()
    for count, layers in enumerate(layerList):
        # swap between noembed and oembed every 20 iterations
        if methodCounter == 20:
            temp = prevMethod
            prevMethod = currentMethod
            currentMethod = temp
            methodCounter = 0

        T, root = getTree(layers)
        print(f"Converting subtree: {count} with root: {root}")

        dict = layersToChannelDict(layers)
        labels = {}
        for node in T.nodes():
            labels[node] = dict[node]
        # channelIdList = list(set(labels.values()))
        # channelDict = {channelId: getChannelName(youtube, channelId) for channelId in channelIdList}

        # using the embed version for large graphs that might exhaust the data api in their creation
        videoIdTochannelName = {}
        for videoId in T.nodes():
            channelName = getChannelNameEmbed(videoId, currentMethod)
            if channelName:
                channelName = re.sub(r"[^\w\s-]", "", channelName).strip()
                videoIdTochannelName[videoId] = [channelName, dict[videoId]]
            else:
                videoIdTochannelName[videoId] = ["Not Found", dict[videoId]]

        channelDict = {
            channelId: channelName
            for channelName, channelId in videoIdTochannelName.values()
        }

        # use the root of the first tree as the filename
        if fileName == None:
            fileName = channelDict[labels[root]]

        for edge in T.edges():
            u, v = edge
            U = channelDict[labels[u]]
            V = channelDict[labels[v]]
            if not V in G.nodes() and U == "Not Found" and V != "Not Found":
                G.add_node(V, size=1)
                continue
            elif not U in G.nodes() and V == "Not Found" and U != "Not Found":
                G.add_node(U, size=1)
                continue
            elif not (U, V) in G.edges() and U != V:
                G.add_node(U, size=1)
                G.add_node(V, size=1)
                G.add_edge(U, V, weight=1)
            elif (U, V) in G.edges():
                G.edges[U, V]["weight"] += 1
            edgeTotal += 1

        for node in T.nodes():
            U = channelDict[labels[node]]
            if U == "Not Found":
                continue
            elif count == 0:
                G.nodes[U]["size"] += 0.1
            elif count > 0 and node != root:
                G.nodes[U]["size"] += 0.1
            nodeTotal += 1

        methodCounter += 1

    fileName = re.sub(r"\s+", "_", fileName)
    fileName = re.sub(r"[^\w\s-]", "", fileName)
    print(f"Converted tree T with V(T)={nodeTotal}, E(T)={edgeTotal}")
    nx.write_graphml(G, f"./graphs/{fileName}.graphml")
    print(f"Created graph: ./graphs/{fileName}.graphml")
    return


def getLeafTrees(
    rootLine: int,
    leaf: int,
    currentLeafs: int,
    nextLeafs: int,
    currentDepth: int,
    youtube: Any,
    width: int,
    depth: int,
    maxDepth: int,
    videoId: str,
) -> tuple[bool, Optional[int], Optional[int]]:
    """Starting at the line number specified in the <rootLine> parameter, calculates the layers for all of the leaf nodes of the tree that can be found at <rootLine> in the file: <videoId>.log

    Args:
        rootLine (int): The line in the specified logfile where the layers of the tree, whose leafs will be converted into trees and saved in the logfile, have been logged.
        leaf (int): The line number of the leaf where the calculation has been interrupted due to overleveraging the Youtube Data API
        currentLeafs (int): How many leafs there are left to calculate for the current layer (increases dynamically)
        nextLeafs (int): How many leafs the next layer contains (increases dynamically)
        currentDepth (int): The overall depth that is currently being calculated
        youtube (Any): The Youtube Data API object
        width (int): The width of one tree
        depth (int): The depth of one tree
        maxDepth (int): Once <currentDepth> reaches this threshhold, the calculation of trees terminates
        videoId (str): The ID of the Youtube video, which will also be the name of the logfile: <videoId>.log

    Returns:
        tuple[bool, Optional[int], Optional[int]]: A tuple containing a boolean value that tells the function forceUntilQuota whether the calculation has to be interrupted, <currentLeafs>, and <nextLeafs>
    """

    flag1 = False
    flag2 = False

    # open file in read mode
    with open(f"./data/{videoId}.log", "r", encoding="utf-8") as logfile:
        for i, l in enumerate(logfile):
            # read the tree in rootLine and get the leafs for that tree
            if i == rootLine:
                rootLayers = eval(l)
                leafDict = rootLayers[-1]
                leafIds = list(leafDict.keys())

                if (
                    currentLeafs == 0
                ):  # this only happens for the root node of the total tree
                    currentLeafs = len(leafIds) + 1
                    flag1 = True
                elif currentLeafs != 0:
                    nextLeafs += len(leafIds)
                    flag2 = True

    with open(f"./data/{videoId}.log", "a", encoding="utf-8") as logfile:
        # append the leaf trees to the file
        for count, leafId in enumerate(leafIds):
            if count >= leaf:
                if currentDepth >= maxDepth:
                    print("Reached maxDepth. Quitting...")
                    with open(f"./data/{videoId}_breakpoint.txt", "w") as file:
                        file.write(str(rootLine))
                        file.write("\n")
                        file.write(str(count))
                        file.write("\n")
                        if flag1:
                            file.write(str(0))
                        else:
                            file.write(str(currentLeafs))
                        file.write("\n")
                        if flag2:
                            file.write(str(nextLeafs - len(leafIds)))
                        else:
                            file.write(str(nextLeafs))
                        file.write("\n")
                        file.write(str(currentDepth))
                    print(f"Saved logfile: ./data/{videoId}.log")
                    print(f"Saved breakpoint: ./data/{videoId}_breakpoint.txt")
                    return False, 0, 0

                try:
                    layers = getLayers(youtube, leafId, width, depth)
                    print(layers, file=logfile)
                    print(f"Saved leafTree: {count}")
                except:
                    with open(f"./data/{videoId}_breakpoint.txt", "w") as file:
                        file.write(str(rootLine))
                        file.write("\n")
                        file.write(str(count))
                        file.write("\n")
                        if flag1:
                            file.write(str(0))
                        else:
                            file.write(str(currentLeafs))
                        file.write("\n")
                        if flag2:
                            file.write(str(nextLeafs - len(leafIds)))
                        else:
                            file.write(str(nextLeafs))
                        file.write("\n")
                        file.write(str(currentDepth))
                    print(f"Saved logfile: ./data/{videoId}.log")
                    print(f"Saved breakpoint: ./data/{videoId}_breakpoint.txt")
                    return False, 0, 0
    return True, currentLeafs, nextLeafs


def forceUntilQuota(
    line: int,
    leaf: int,
    currentLeafs: int,
    nextLeafs: int,
    currentDepth: int,
    youtube: Any,
    width: int,
    depth: int,
    maxDepth: int,
    videoId: str,
) -> None:
    """Repeatedly calls the function getLeafTrees until either the API usage limit has been exceeded, or <maxDepth> has been reached

    Args:
        line (int): The line number in the logfile where the calculation has previously been interrupted
        leaf (int): The number of the leaf of the current tree where the calculation has previously been interrupted
        currentLeafs (int): The number of leaves left in the current depth layer
        nextLeafs (int): The number of leaves coming up for the next depth layer
        currentDepth (int): The current overall depth
        youtube (Any): The Youtube Data API object
        width (int): The width of one tree
        depth (int): The depth of one tree
        maxDepth (int): The maximum overall depth that should not be exceeded
        videoId (str): The ID of the Youtube video
    """

    loop = True
    while loop:
        print(f"Calling getLeafTrees({line})...")
        if currentLeafs == 0:
            currentDepth += depth
            currentLeafs = nextLeafs
            nextLeafs = 0
        loop, currentLeafs, nextLeafs = getLeafTrees(
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
        leaf = 0  # we only need leaf to continue from breakpoint on the first call of gLT()
        currentLeafs -= 1
        line += 1


def getTitles(filename: str) -> None:
    """Extracts the titles of every video from a specified logfile in the data folder and saves them in the titles folder

    Args:
        filename (str): The name of the file whose titles should be extracted
    """
    video_titles = []

    # Load the file
    with open(f"./data/{filename}", "r", encoding="utf-8") as file:
        data = file.read()

    items = data.split("}, {")
    for item in items:
        video_info = item.split(": [")[1].split(", ")[1].strip("'")
        video_titles.append(video_info)

    # Save the titles to titles.log
    with open(f"./titles/{filename}", "w", encoding="utf-8") as file:
        for title in video_titles:
            file.write(title + "\n")

    print(f"Extracted titles: ./titles/{filename}")
    return


def hierarchy_pos(G, root=None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
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
    if not nx.is_tree(G):
        raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(
                iter(nx.topological_sort(G))
            )  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(
        G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None
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
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
