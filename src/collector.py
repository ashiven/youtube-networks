from googleapiclient.discovery import build
import re
import networkx as nx
import matplotlib.pyplot as plt
import random
import argparse
from library import hierarchy_pos
from typing import *


# this function uses a regular expression to extract the videoId parameter from any youtube link
def parseVideoId(link: str) -> Optional[str]:

    # regular expression for extracting videoId
    regex = r"(?:youtu\.be\/|youtube\.com\/watch\?v=|youtube\.com\/embed\/)([^?&\/]+)"
    res = re.search(regex, link)

    if res:
        videoId = res.group(1)
        return videoId
    else:
        return None


def getVideoInfo(youtube: Any, videoId: str) -> tuple[str, str]:
    response = youtube.videos().list(part='snippet', id=videoId).execute()
    
    return response['items'][0]['snippet']['title'], response['items'][0]['snippet']['channelId']


def getChannelName(youtube: Any, channelId: str) -> str:
    response = youtube.channels().list(part='snippet', id=channelId).execute()
    
    return response['items'][0]['snippet']['title']


# this function takes as input a video Id and based on width returns 'width' amount of related videos 
def getRelated(youtube: Any, videoId: str, width: int) -> Dict:
    
    # query youtube api for related videos 
    response = youtube.search().list(
        part = 'snippet',
        relatedToVideoId = videoId,
        maxResults = width,
        type = 'video'
    ).execute()

    # store related videos in a dictionary with key: videoId , value: title
    related = {}
    for item in response['items']:
        title = item['snippet']['title']
        id = item['id']['videoId']
        channelId = item['snippet']['channelId']
        related[id] = [videoId, title, channelId]

    return related


# this function will calculate our layers of related videos by repeatedly calling getRelated() on every video for every layer 
def getLayers(youtube: Any, videoId: str, width: int, depth: int) -> List[Dict]:

    # initialize array that will hold one dictionary per layer
    layers = [{} for _ in range(depth + 1)]
    title, channelId = getVideoInfo(youtube, videoId)
    layers[0] = { videoId : [None, title, channelId] }

    # call getRelated() for retrieving related videos from layer 1 to 'depth'
    for i in range(1, depth + 1):
        if(i == 1):
            layers[i] = getRelated(youtube, videoId, width)
        else:
            for video in layers[i - 1]:
                related = getRelated(youtube, video, width)
                layers[i].update(related)

    return layers


# this function takes our layers and converts them to a dict with key: video Id, value: video Title
def layersToDict(layers: List[Dict]) -> Dict:
    dict = {}
    for layer in layers:
        for key, value in layer.items():
            dict[key] = value[1]

    return dict


# this function takes our layers and converts them to a dict with key: video Id, value: channel Id
def layersToChannelDict(layers: List[Dict]) -> Dict:
    dict = {}
    for layer in layers:
        for key, value in layer.items():
            dict[key] = value[2]

    return dict
    

# this function takes the dictionary from layersToDict() and uses it to return the matching video Title 
def keyToTitle(dict: Dict, videoId: str) -> str:
    if videoId in dict:
        return dict[videoId]
    else:
        return None
    

# this function takes our layers and tree and so on and returns a list with the colors for the tree according to channelIds and a dict labels for labeling nodes with channelIds
def getColors(layers: List[Dict], T: nx.Graph) -> tuple[List[str], Dict]:

    # convert layers to a dictionary with key: videoId, value: channelId
    dict = layersToChannelDict(layers)

    # give every node its appropriate channelId label, replacing its previous videoId labels
    labels = {}
    for node in T.nodes():
        labels[node] = dict[node]

    # create a list of unique channel Ids and then create a list of colors with one color for each channel Id
    uniqueChannelIds = list(set(dict.values()))
    colors = ["gold", "violet", "blue", "silver", #TODO: this is a very shitty and temporary solution and needs to be changed because if we end up needing more colors we're f'd
              "limegreen", "orange", "darkorange",
              "yellow", "green"]

    # map every channelId to a color and after that map every node in the tree to the color corresponding with its channelId
    channelToColor = {channelId: colors[count] for count, channelId in enumerate(uniqueChannelIds)}
    nodeToColor = {node: channelToColor[labels[node]] for node in T.nodes()}

    # now finally we create the list of colors that will be used for the nodes, red being the default color for undefined channelIds aka the root node
    return [nodeToColor.get(node, 'red') for node in T.nodes()], labels


# this function will convert our layers from a list of dictionaries to a tree which can then be visualized 
def getTree(layers: List[Dict], display: str) -> tuple[nx.Graph, str]:

    # create a new graph with undirected edges
    T = nx.Graph()

    # iterate through layers and add edges according to parent node specified in value[0]
    if display == 'videoId':
        for count, layer in enumerate(layers):
            for key, value in layer.items():
                if not T.has_node(key) and value[0] != None:
                    T.add_node(key)
                    parentKey = value[0]
                    T.add_edge(parentKey, key)
        root = next(iter(layers[1].values()))[0]
                
    elif display == 'title':
        dict = layersToDict(layers)
        root = next(iter(layers[0].values()))[1]
        T.add_node(root)
        for count, layer in enumerate(layers):
            for key, value in layer.items():
                if count <= 1:
                    if count == 1 and not T.has_node(value[1]):
                        T.add_node(value[1])
                        T.add_edge(root, value[1])
                elif not T.has_node(value[1]):
                    T.add_node(value[1])
                    parentKey = value[0]
                    T.add_edge(keyToTitle(dict, parentKey), value[1])
    
    return T, root


# this function takes a tree with the node names being video Ids and converts that tree
# into one that is labeled with the respective channel Ids belonging to the video Ids
def convertTree(T: nx.Graph, root: str, layers: List[Dict]) -> None:
    
    colors, labels = getColors(layers, T)

    # draw the graph
    plt.figure(figsize=(15, 10))
    pos = hierarchy_pos(T, root)
    nx.draw(T, pos=pos,  with_labels=False, node_color=colors)
    nx.draw_networkx_labels(T, pos, labels, font_size=9)

    # show plot
    plt.title('Channel Tree')
    plt.tight_layout
    plt.show()


def main():

    # parse the arguments supplied by the user
    parser = argparse.ArgumentParser(description='Youtube Related Video Collector')
    parser.add_argument('-d', '--depth', type=int, default=3, help='Search Depth')
    parser.add_argument('-w', '--width', type=int, default=2, help='Search Width')
    parser.add_argument('-s', '--seed', type=str, required=True, help='Initial Youtube Video Link')
    parser.add_argument('-D', '--display', type=str, default='title', help="Display Video Titles: 'title' | Video Ids: 'videoId' | Channel Ids: 'channelId'")
    args = parser.parse_args()

    seed = args.seed 
    videoId = parseVideoId(seed)
    width = args.width
    depth = args.depth
    display = args.display

    # here we have a few api keys because the ratelimiting is bad...
    apiKey = '***REMOVED***'
    apiKey2 = '***REMOVED***'
    apiKey3 = '***REMOVED***'
    apiKey4 = '***REMOVED***'

    # we create the youtube object for interacting with the API and getLayers() to retrieve the layers of related videos
    youtube = build('youtube', 'v3', developerKey=apiKey3)
    layers = getLayers(youtube, videoId, width, depth)

    '''
    # write the result for layers into a log file 
    with open('output.log', 'a', encoding='utf-8') as logFile:
        for count, layer in enumerate(layers):
            print('\n', file=logFile)
            print(f'Layer {count}:\n', file=logFile)
            print(layer, file=logFile)
    '''
            
    # display video titles as node labels
    if display == 'title':
        T, root = getTree(layers, 'title') # TODO: gotta make colors work for this one
        
        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos,  with_labels=True, font_size=9)
        plt.title('Related Videos')
        plt.tight_layout
        plt.show()

    # display video ids as node labels
    elif display == 'videoId':
        T, root = getTree(layers, 'videoId')
        colors = getColors(layers, T)[0]

        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos,  with_labels=True, font_size=9, node_color=colors)
        plt.title('Related Videos')
        plt.tight_layout
        plt.show()

    # display channel ids as node labels
    elif display == 'channelId':
        T, root = getTree(layers, 'videoId')
        convertTree(T, root, layers)


if __name__ == '__main__':
    main()