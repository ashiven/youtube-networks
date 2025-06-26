"""
This script collects related videos from YouTube using the YouTube Data API.
It builds a tree structure of related videos starting from a given video ID,
and allows for various configurations such as args.depth, args.width, and args.display options.
"""

import argparse
import logging

from googleapiclient.discovery import HttpError, build

from helpers import parse_video_id
from lib import (
    calculate_aggressive,
    convert_imports,
    draw_tree,
    force_until_quota,
    get_layers,
    get_titles,
)

logger = logging.getLogger(__name__)


def get_api_keys():
    """
    Retrieve a list of YouTube API keys.

    :return: List of API keys.
    """
    # Add your own API keys here!!!
    api_keys = [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]
    return [key for key in api_keys if key]


def parse_args():
    """
    Parse command line arguments for the YouTube related video collector.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Youtube Related Video Collector")
    parser.add_argument(
        "-s",
        "--seed",
        type=str,
        help="The initial YouTube link (required)",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=2,
        help="The number of depth layers to calculate for the tree",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=3,
        help="The number of related videos per video",
    )
    parser.add_argument(
        "-l",
        "--labels",
        type=str,
        default="title",
        help="Label description of the tree: title, videoId, channelId, channelName",
    )
    parser.add_argument(
        "-g",
        "--graph",
        action="store_true",
        default=False,
        help="Convert the tree into a network graph",
    )
    parser.add_argument(
        "-i",
        "--importtrees",
        type=str,
        default=None,
        help="Path to a logfile (will convert its contents into a network graph)",
    )
    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Calculate a large tree saved in a logfile until API key quota is reached",
    )
    parser.add_argument(
        "-A",
        "--aggressive",
        default=False,
        action="store_true",
        help="Do the same as -f, exhausting all available API keys",
    )
    parser.add_argument(
        "-m",
        "--maxdepth",
        type=int,
        default=10000,
        help="Max depth for tree compilation (must be a multiple of -d)",
    )
    parser.add_argument(
        "-t",
        "--titles",
        type=str,
        default=None,
        help="Path to a logfile (will extract the video titles for further topic analysis)",
    )
    parser.add_argument(
        "-a",
        "--apikey",
        type=str,
        default=None,
        help="The API key to be used (if not provided, the first key from the list will be used)",
    )
    args = parser.parse_args()
    return args


def main():
    """
    Main function to parse arguments and execute the YouTube related video collector.
    It initializes the YouTube API client, retrieves related videos, and processes
    them based on user-defined parameters.
    """
    try:
        args = parse_args()
        api_keys = get_api_keys()
        default_api_key = args.apikey if args.apikey else api_keys[0]
        youtube = build("youtube", "v3", developerKey=default_api_key)
        video_id = parse_video_id(args.seed)

        if not (args.importtrees or args.force or args.aggressive or args.titles):
            layers = get_layers(youtube, video_id, args.width, args.depth)
            with open(f"./data/{video_id}.log", "a", encoding="utf-8") as logfile:
                print(layers, file=logfile)
            draw_tree(layers, args.labels, args.graph)

        elif args.importtrees:
            logfile = args.importtrees
            convert_imports(logfile)

        elif args.force:
            force_until_quota(
                youtube,
                video_id,
                args.width,
                args.depth,
                args.maxdepth,
            )

        elif args.aggressive:
            calculate_aggressive(
                api_keys,
                video_id,
                args.width,
                args.depth,
                args.maxdepth,
            )

        elif args.titles:
            get_titles(args.titles)

        else:
            logger.error(
                "Invalid arguments. Please use -h or --help to see the available options."
            )
    except HttpError as http_error:
        logger.error("An error occurred: %s", http_error)
    except Exception as error:  # pylint: disable=broad-except
        logger.error("An unexpected error occurred: %s", error)


if __name__ == "__main__":
    main()
