from googleapiclient.discovery import build
import re
import networkx as nx
import matplotlib.pyplot as plt
import random
from typing import Optional


# [I didn't write this function!!!] had to use this function from stackoverflow because there is no way to get pygraphviz working on windows
def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
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
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''
    
        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos

            
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def parseVideoId(link):

    # regular expression for extracting videoId
    regex = r"(?:youtu\.be\/|youtube\.com\/watch\?v=|youtube\.com\/embed\/)([^?&\/]+)"
    res = re.search(regex, link)

    if res:
        videoId = res.group(1)
        return videoId
    else:
        return None


def getRelated(youtube, videoId, resultSize):
    
    # query youtube api for related videos 
    response = youtube.search().list(
        part = 'snippet',
        relatedToVideoId = videoId,
        maxResults = resultSize,
        type = 'video'
    ).execute()

    # store related videos in a dictionary with key: videoId , value: title
    related = {}
    for item in response['items']:
        title = item['snippet']['title']
        id = item['id']['videoId']
        related[id] = [videoId, title]

    return related


def getLayers(youtube, videoId, resultSize, depth):

    # initialize a two dimensional array that will hold one dictionary per layer
    layers = [{} for _ in range(depth + 1)]

    # call getRelated() for retrieving related videos from layer 1 to 'depth'
    for i in range(1, depth + 1):
        if(i == 1):
            layers[i] = getRelated(youtube, videoId, resultSize)
        else:
            for video in layers[i - 1]:
                related = getRelated(youtube, video, resultSize)
                layers[i].update(related)

    return layers


def layersToDict(layers):

    # merge the dictionaries of layers to one dictionary
    dict = {}
    for layer in layers:
        for key, value in layer.items():
            dict[key] = value[1]
    return dict


def keyToTitle(dict, videoId):

    # return the fitting title for the videoId
    if videoId in dict:
        return dict[videoId]
    else:
        return None


def plotGraph(layers, display, rootTitle):

    # create a new graph with undirected edges
    G = nx.Graph()

    # iterate through layers and add edges according to parent node specified in value[0]
    if display == 'videoId':
        for layer in layers:
            for key, value in layer.items():
                if not G.has_node(key):
                    G.add_node(key)
                    parentKey = value[0]
                    G.add_edge(parentKey, key)
        root = next(iter(layers[1].values()))[0]
                
    elif display == 'title':
        dict = layersToDict(layers)
        if rootTitle:
            root = rootTitle
            G.add_node(rootTitle)
        else:
            root = 'seed'
            G.add_node('seed')
        for count, layer in enumerate(layers):
            for key, value in layer.items():
                if count <= 1:
                    if count == 1 and not G.has_node(value[1]):
                        G.add_node(value[1])
                        G.add_edge(root, value[1])
                elif not G.has_node(value[1]):
                    G.add_node(value[1])
                    parentKey = value[0]
                    G.add_edge(keyToTitle(dict, parentKey), value[1])

    # draw the graph
    plt.figure(figsize=(15, 10))
    pos = hierarchy_pos(G, root)
    nx.draw(G, pos=pos,  with_labels=True, font_size=9)
    plt.title('Related Videos')
    plt.tight_layout
    plt.show()


def main():

    # here we have two api keys because the ratelimiting is bad...
    apiKey = '***REMOVED***'
    apiKey2 = '***REMOVED***'
    youtube = build('youtube', 'v3', developerKey=apiKey2)

    seed = 'https://www.youtube.com/watch?v=cr1KaZ11KCo'    # insert youtube video link here
    seedTitle = "I'm root"                                  # insert title of youtube video here
    videoId = parseVideoId(seed)
    resultSize = 2
    depth = 3

    layers = getLayers(youtube, videoId, resultSize, depth)
    #layersTest = [{},{'X9oSdf_7XsM': ['vV-LIOSAWzY', 'Another Failure of a Review...'], '1SMLQiwt9n4': ['vV-LIOSAWzY', "Wendy's NEW Ghost Pepper Ranch Chicken Sandwich Review!"]},{'vV-LIOSAWzY': ['1SMLQiwt9n4', "Burger King's NEW Spider-Verse Whopper Review!"], '1SMLQiwt9n4': ['X9oSdf_7XsM', "Wendy's NEW Ghost Pepper Ranch Chicken Sandwich Review!"], 'X9oSdf_7XsM': ['1SMLQiwt9n4', 'Another Failure of a Review...']},{'X9oSdf_7XsM': ['1SMLQiwt9n4', 'Another Failure of a Review...'], '1SMLQiwt9n4': ['X9oSdf_7XsM', "Wendy's NEW Ghost Pepper Ranch Chicken Sandwich Review!"], 'vV-LIOSAWzY': ['X9oSdf_7XsM', "Burger King's NEW Spider-Verse Whopper Review!"]}]


    with open('output.log', 'a', encoding='utf-8') as logFile:
        for count, layer in enumerate(layers):
            print('\n', file=logFile)
            print(f'Layer {count}:\n', file=logFile)
            print(layer, file=logFile)

    # specify either 'title' or 'videoId' for node labels
    plotGraph(layers, 'title', seedTitle)


if __name__ == '__main__':
    main()