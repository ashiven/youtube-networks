## Options
- There are several functionalities included with this script.
- Below is a short description and an example for every option.

#### `-s` : The initial Youtube link.
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do
```

#### `-d` : What depth should the tree have?
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -d 5
```

#### `-w` : What width should the tree have?
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -w 3
```

#### `-a` : Which API key should be used?
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -a 3
```

#### `-D` [ `title`, `videoId`, `channelId`, `channelName` ] : What should be displayed for the tree nodes?
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -D title
```

#### `-l` : Should the calculated tree be saved in a log file?
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -l
```

#### `-g` : Should the tree be converted into a network graph? ( this only works in combination with `-D channelName` )
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -D channelName -g
```

#### `-f` : Compile trees into a larger tree until the API key quota has been exceeded. The result will be saved in a log file in the **data** folder, named after the specified Youtube video's ID.
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -f
```

#### `-A` : Do the same as with `-f`, exhausting every available API key.
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -A
```

#### `-m` : Use in conjunction with `-f` or `-A` to specify a maximum depth for the tree being compiled. ( it has to be a multiple of `-d` )
```bash
python main.py -s https://www.youtube.com/watch?v=StJremO4_Do -A -d 3 -m 6
```

#### `-i` : Convert all of the trees inside a log file in the **data** folder into a network graph.
```bash
python main.py -i LIVuZqs392k.log
```

#### `-t` : Extract the titles for a log file in the **data** folder.
```bash
python main.py -t LIVuZqs392k.log
```
