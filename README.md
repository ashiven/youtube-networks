<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/ashiven/youtube-networks)](https://github.com/ashiven/youtube-networks/releases)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/ashiven/youtube-networks)](https://github.com/ashiven/youtube-networks/issues)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/ashiven/youtube-networks)](https://github.com/ashiven/youtube-networks/pulls)
![GitHub Repo stars](https://img.shields.io/github/stars/ashiven/youtube-networks)

</div>

## About

This script can be used to map out the channel landscape surrounding specific **YouTube** videos. It was developed as part of a programming project at TU Berlin. If you want to learn more about the project and how the generated graphs were evaluated, you may read the [project report](docs/Projektbericht.pdf).

<p align="center">
   <img src="https://github.com/user-attachments/assets/7b36596e-34ed-4bbe-bcb0-ba8bcbdbf142" />
</p>

## Getting Started

### Prerequisites

-  Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/).
-  Register for the [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) and retrieve your API key.

### Setup

1. Clone the repository to your local machine as follows:
   ```bash
   git clone https://github.com/ashiven/youtube-networks.git
   ```
2. Navigate to the **youtube-networks** directory.

   ```bash
   cd ./youtube-networks
   ```

3. Install the necessary dependencies.

   ```bash
   pip install --user -r requirements.txt
   ```

4. Insert your API key(s) into the script.

   ```bash
   nano ./src/main.py
   ```

### Usage

-  Enter the following command to run the script:

   ```bash
   python ./src/main.py -s <link to a youtube video>
   ```

   |    parameter    | alias |  type   | description                                                                        | default |
   | :-------------: | :---: | :-----: | :--------------------------------------------------------------------------------- | :-----: |
   |    `--help`     | `-h`  | Boolean | Shows argument usage                                                               |         |
   |    `--seed`     | `-s`  | String  | The initial YouTube link                                                           |  None   |
   |    `--depth`    | `-d`  | Integer | The number of depth layers to calculate for the tree                               |    2    |
   |    `--width`    | `-w`  | Integer | The number of related videos per video                                             |    3    |
   |   `--apikey`    | `-a`  | String  | The API key to be used (if not provided, the first key from the list will be used) |  None   |
   |   `--labels`    | `-l`  | String  | Label description of the tree: `title`, `videoId`, `channelId`, `channelName`      | `title` |
   |    `--graph`    | `-g`  | Boolean | Convert the tree into a network graph                                              |  False  |
   |    `--force`    | `-f`  | Boolean | Calculate a large tree saved in a logfile until API key quota is reached           |  False  |
   | `--aggressive`  | `-A`  | Boolean | Do the same as `-f`, exhausting all available API keys                             |  False  |
   |  `--maxdepth`   | `-m`  | Integer | Max depth for tree compilation (must be a multiple of `-d`)                        |  10000  |
   | `--importtrees` | `-i`  | String  | Path to a logfile (will convert its contents into a network graph)                 |  None   |
   |   `--titles`    | `-t`  | String  | Path to a logfile (will extract the video titles for further topic analysis)       |  None   |

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
