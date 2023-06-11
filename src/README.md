Install:

-  open a terminal inside of the /src directory

-  run `pip install --user -r requirements.txt`


Options:

- `-s` [required] : The initial youtube link
    - example: `-s https://www.youtube.com/watch?v=StJremO4_Do`

- `-d` [default = 2] : How deep should the search be
    - example: `-d 5` 

- `-w` [default = 3] : How wide should the search be
    - example: `-w 3`

- `-a` [default = 0] : Which api key should be used 
    - example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -a 3`

- `-D` [default = title] : What to display as node labels 
    - options: `title`, `videoId`, `channelId`, `channelName`

- `-l` : Add this flag to log the calculated tree in a logfile
    - example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -l`

- `-g` : Add this flag to convert a single tree into a network graph (only works in combination with `-D channelName`)
    - example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -D channelName -g`

- `-i` : Use this flag to convert all of the trees inside of a logfile, into a network graph 
    - example usage: `python collector.py -i LIVuZqs392k.log`

- `-f` : Use this flag to compile subtrees into a larger tree until the api key quota has been exceeded (You don't need to add `-l` here)
    - example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -f`

- `-t` : Use this flag to extract the titles for a logfile in /data 
    - example usage: `python collector.py -t LIVuZqs392k.log`

- `-A` : Use this flag to do the same as with -f cycling through every available api key 
    - example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -A`

- `-m` [default = 10000] : Use this flag to specify a maximum depth for the tree being compiled with -f or -A (has to be a multiple of depth)
    - example usage: `python collector.py -s https://www.youtube.com/watch?v=StJremO4_Do -A -d 3 -m 6`
