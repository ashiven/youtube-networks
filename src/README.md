Install:

- `1)` open a terminal inside of the /src directory

- `2)` run 'pip install --user -r requirements.txt'


Options:

- `-s` [required] : The initial youtube link, e.g. '-s https://www.youtube.com/watch?v=StJremO4_Do'

- `-d` [default = 3] : How deep should the search be, e.g. '-d 5' 

- `-w` [default = 2] : How wide should the search be, e.g. '-w 3'

- `-D` [default = 'title'] : What to display as node labels - options: 'title', 'videoId', 'channelId', 'channelName'

- `-l` : Add this flag to log the calculated layers in output.log 

- `-g` : Add this flag to convert the tree to a network graph (only works in combination with -D channelName)

- `-i` : Use this flag to convert all of the trees(layers) inside of output.log, into a network graph e.g. 'python collector.py -i'

- `-f` : Use this flag to calculate trees with specified width and depth until the quota of your api key has been exceeded 
1. With an empty output.log file: 'python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -f'
2. Continue fetching more data where the script left off: 'python collector.py -f'