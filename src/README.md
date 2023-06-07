Install:

1) open a terminal inside of the /src directory

2) run 'pip install --user -r requirements.txt'


Options:

-s [required] : the initial youtube link e.g. '-s https://www.youtube.com/watch?v=StJremO4_Do'

-d [default = 3] : how deep should the search be e.g. '-d 5' 

-w [default = 2] : how wide should the search be e.g. '-w 3'

-D [default = "title"] : whether to display the video ids or titles as node labels e.g. '-D videoId' '-D channelId' '-D channelName' '-D title'

-l : add this flag to log the calculated layers in output.log 

-g : add this flag to convert the tree to a graph representing the network surrounding the seed video (only works in combination with -D channelName)

-i : use this flag to convert all of the previously calculated trees, that you have logged with the -l flag, into a network graph (use without any other options) e.g. 'python collector.py -i'

-f : use this flag to calculate trees with specified width and depth until the quota of your api key has been exceeded 
        1) with empty output.log file: 'python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -f'
        2) if you have already called 1) and output.log is populated: 'python collector.py -f'