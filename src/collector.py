from googleapiclient.discovery import build
import re

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

def main():
    apiKey = '***REMOVED***'
    apiKey2 = '***REMOVED***'
    youtube = build('youtube', 'v3', developerKey=apiKey2)

    # insert youtube link here
    seed = 'https://www.youtube.com/watch?v=lpFXlkjAurc'
    videoId = parseVideoId(seed)
    resultSize = 2
    depth = 3

    layers = getLayers(youtube, videoId, resultSize, depth)

    for count, layer in enumerate(layers):
        print('\n')
        print(f'Layer {count}:\n')
        print(layer)

if __name__ == '__main__':
    main()