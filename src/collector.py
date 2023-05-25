from googleapiclient.discovery import build
import re
import networkx as nx
import matplotlib.pyplot as plt
import random
import argparse

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
        channelId = item['snippet']['channelId']
        related[id] = [videoId, title, channelId]

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


def layersToChannelDict(layers):
    dict = {}
    for layer in layers:
        for key, value in layer.items():
            dict[key] = value[2]

    return dict
    

def keyToTitle(dict, videoId):

    # return the fitting title for the videoId
    if videoId in dict:
        return dict[videoId]
    else:
        return None
    

def getGraph(layers, display, rootTitle):

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
        root = rootTitle
        G.add_node(root)
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
    
    return G, root


# this function takes a tree with the nodes names being video Ids and converts that tree
# into one which is labeled with the respective channel Ids belonging to the video Ids
def convertTree(T, root, rootTitle, layers):
    
    # convert layers to a dictionary with key: videoId, value: channelId
    dict = layersToChannelDict(layers)

    labels = {}
    # give every node its appropriate channelId label, replacing its previous videoId labels
    for node in T.nodes():
        if node != root:
            labels[node] = dict[node]
    labels[root] = rootTitle

    # draw the graph
    plt.figure(figsize=(15, 10))
    pos = hierarchy_pos(T, root)
    nx.draw(T, pos=pos,  with_labels=False)

    # draw the previously created channelId labels
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
    parser.add_argument('-s', '--seed', type=str, required=True, help='Initial Youtube Video')
    parser.add_argument('-t', '--title', type=str, default="I'm root", help='Title of Initial Youtube Video / Label for the root node')
    parser.add_argument('-D', '--display', type=str, default='title', help="Display Video Titles: 'title' VideoIds: 'videoId'")
    args = parser.parse_args()

    seed = args.seed 
    seedTitle = args.title  
    videoId = parseVideoId(seed)
    resultSize = args.width
    depth = args.depth

    # here we have a few api keys because the ratelimiting is bad...
    apiKey = '***REMOVED***'
    apiKey2 = '***REMOVED***'
    apiKey3 = '***REMOVED***'
    apiKey4 = '***REMOVED***'
    youtube = build('youtube', 'v3', developerKey=apiKey2)
    layers = getLayers(youtube, videoId, resultSize, depth)

    with open('output.log', 'a', encoding='utf-8') as logFile:
        for count, layer in enumerate(layers):
            print('\n', file=logFile)
            print(f'Layer {count}:\n', file=logFile)
            print(layer, file=logFile)

    # display either video titles or video ids as node labels
    if args.display == 'title':
        T, root = getGraph(layers, 'title', seedTitle)
        
        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos,  with_labels=True, font_size=9)
        plt.title('Related Videos')
        plt.tight_layout
        plt.show()

    elif args.display == 'videoId':
        T, root = getGraph(layers, 'videoId', seedTitle)

        # draw the graph
        plt.figure(figsize=(15, 10))
        pos = hierarchy_pos(T, root)
        nx.draw(T, pos=pos,  with_labels=True, font_size=9)
        plt.title('Related Videos')
        plt.tight_layout
        plt.show()

    elif args.display == 'channelId':
        T, root = getGraph(layers, 'videoId', seedTitle)
        if seedTitle:
            convertTree(T, root, seedTitle, layers)
        else:
            convertTree(T, root, '', layers)


if __name__ == '__main__':
    main()