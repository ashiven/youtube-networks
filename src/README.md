Install:

- `1.` open a terminal inside of the /src directory

- `2.` run `pip install --user -r requirements.txt`


Options:

- `-s` [required] : The initial youtube link, e.g. `-s https://www.youtube.com/watch?v=StJremO4_Do`

- `-d` [default = 3] : How deep should the search be, e.g. `-d 5` 

- `-w` [default = 2] : How wide should the search be, e.g. `-w 3`

- `-D` [default = title] : What to display as node labels - options: - `title`, `videoId`, `channelId`, `channelName`

- `-l` : Add this flag to log the calculated tree in a logfile saved in /data
    1. example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -l`

- `-g` : Add this flag to convert the tree to a network graph (only works in combination with -D channelName)
    1. example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -D channelName -g`

- `-i` : Use this flag to convert all of the trees inside of a logfile, into a network graph 
    1. example usage: `python collector.py -i LIVuZqs392k.log`

- `-f` : Use this flag to calculate trees with specified width and depth until the quota of your api key has been exceeded (You don't need to add `-l` here)
    1. example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -f`

- `-t` : Use this flag to extract only the titles for a file in /data 
    1. example usage: `python collector.py -t LIVuZqs392k.log`