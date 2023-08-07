import networkx as nx
import random
import re
import networkx as nx
import matplotlib.pyplot as plt
from typing import *
import requests


# uses a regular expression to extract the videoId parameter from any youtube link
def parseVideoId(link: str) -> Optional[str]:
    # regular expression for extracting videoId
    regex = r"(?:youtu\.be\/|youtube\.com\/watch\?v=|youtube\.com\/embed\/)([^?&\/]+)"
    res = re.search(regex, link)

    if res:
        videoId = res.group(1)
        return videoId
    else:
        return None


# takes a video id and returns the title and channel id for that video
def getVideoInfo(youtube: Any, videoId: str) -> tuple[str, str]:
    response = youtube.videos().list(part="snippet", id=videoId).execute()
    return (
        response["items"][0]["snippet"]["title"],
        response["items"][0]["snippet"]["channelId"],
    )


# takes a channel id and returns the name of the channel
def getChannelName(youtube: Any, channelId: str) -> str:
    response = youtube.channels().list(part="snippet", id=channelId).execute()
    return response["items"][0]["snippet"]["title"]


# does the same starting with a video id and using oembed instead of the data api
def getChannelNameEmbed(videoId: str, method: str) -> str:
    if method == "noembed":
        response = requests.get(
            "https://noembed.com/embed?url=https://www.youtube.com/watch?v=" + videoId
        )
    elif method == "oembed":
        response = requests.get(
            "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v="
            + videoId
        )
    try:
        dict = eval(response.text)
        return dict["author_name"]
    except:
        return None


# takes as input a video Id and based on width returns 'width' amount of related videos
def getRelated(youtube: Any, videoId: str, width: int) -> Dict:
    # query youtube api for related videos
    response = (
        youtube.search()
        .list(part="snippet", relatedToVideoId=videoId, maxResults=width, type="video")
        .execute()
    )

    # store related videos in a dictionary with key: videoId , value: title
    related = {}
    for item in response["items"]:
        title = item["snippet"]["title"]
        id = item["id"]["videoId"]
        channelId = item["snippet"]["channelId"]
        related[id] = [videoId, title, channelId]

    return related


# will calculate our layers of related videos by repeatedly calling getRelated() on every video for every layer
def getLayers(youtube: Any, videoId: str, width: int, depth: int) -> List[Dict]:
    # initialize array that will hold one dictionary per layer
    layers = [{} for _ in range(depth + 1)]
    title, channelId = getVideoInfo(youtube, videoId)
    layers[0] = {videoId: [None, title, channelId]}

    # call getRelated() for retrieving related videos from layer 1 to 'depth'
    for i in range(1, depth + 1):
        if i == 1:
            layers[i] = getRelated(youtube, videoId, width)
        else:
            for video in layers[i - 1]:
                related = getRelated(youtube, video, width)
                layers[i].update(related)

    return layers


# takes our layers and converts them to a dict with key: video Id, value: video Title
def layersToTitleDict(layers: List[Dict]) -> Dict:
    dict = {}
    for layer in layers:
        for key, value in layer.items():
            dict[key] = value[1]

    return dict


# takes our layers and converts them to a dict with key: video Id, value: channel Id
def layersToChannelDict(layers: List[Dict]) -> Dict:
    dict = {}
    for layer in layers:
        for key, value in layer.items():
            dict[key] = value[2]

    return dict


# takes the dictionary from layersToDict() and uses it to return the matching video Title
def keyToTitle(dict: Dict, videoId: str) -> str:
    if videoId in dict:
        return dict[videoId]
    else:
        return None


# takes our layers and tree and so on and returns a list with the colors for the tree according to channelIds and a dict labels for labeling nodes with channelIds
def getColors(layers: List[Dict], T: nx.Graph) -> tuple[List[str], Dict]:
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
        "silver",  # TODO: this is a very shitty and temporary solution and needs to be changed because if we end up needing more colors we're f'd
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

    # now finally we create the list of colors that will be used for the nodes, red being the default color for undefined channelIds
    return [nodeToColor.get(node, "red") for node in T.nodes()], labels


# will convert our layers from a list of dictionaries to a tree which can then be visualized
def getTree(layers: List[Dict]) -> tuple[nx.Graph, str]:
    # create a new graph with undirected edges
    T = nx.Graph()

    # iterate through layers and add edges according to parent node specified in value[0]
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


# imports the trees saved in filename and converts them to a network graph
# this graph will then be saved as import_log.graphml in /graphs
def convertImports(youtube: Any, filename: str) -> None:
    # we basically repeat what we are doing in convertTree() with -D channelName and -g with the trees from the import file
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

        # some stuff we need
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

        # we use the root of the first tree as the filename
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


# takes a rootLine indicating where the tree, whose leafs we are trying to convert into trees, is located in the file
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


# keeps calling getLeafTrees until the quota has been exceded
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


# extracts the video titles from a specified logfile
def getTitles(filename: str) -> None:
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
