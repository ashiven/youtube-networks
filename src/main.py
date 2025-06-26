"""
This script collects related videos from YouTube using the YouTube Data API.
It builds a tree structure of related videos starting from a given video ID,
and allows for various configurations such as args.depth, args.width, and args.display options.
"""

import argparse
import logging

from googleapiclient.discovery import HttpError, build

from lib import (
    calculate_aggressive,
    convert_imports,
    draw_tree,
    force_until_quota,
    get_layers,
    get_titles,
    parse_video_id,
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
        "-s", "--seed", type=str, help="Initial Youtube Video Link", required=True
    )
    parser.add_argument("-d", "--depth", type=int, default=2, help="Search args.depth")
    parser.add_argument("-w", "--width", type=int, default=3, help="Search args.width")
    parser.add_argument(
        "-l",
        "--labels",
        type=str,
        default="title",
        help="""Display Video Titles: 'title' | Video Ids: 'videoId'
 | Channel Ids: 'channelId'  | Channel Names: 'channelName'""",
    )
    parser.add_argument(
        "-g",
        "--graph",
        action="store_true",
        help="""Whether to convert the tree to a graph that will be exported to a
 graphML file(only works with -D channelName)""",
    )
    parser.add_argument(
        "-i",
        "--import_trees",
        type=str,
        default=None,
        help="Import the trees for a given logfile and convert them to a graph",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Keep calculating trees until the quota is exceeded",
    )
    parser.add_argument(
        "-A",
        "--aggressive",
        action="store_true",
        help="Do the same as with -f but cycle through all available api keys",
    )
    parser.add_argument(
        "-m",
        "--maxdepth",
        type=int,
        default=10000,
        help="Total depth of the tree to be built with -f or -A (must be a multiple of depth)",
    )
    parser.add_argument(
        "-t",
        "--titles",
        type=str,
        default=None,
        help="Extract only the titles from a given file",
    )
    parser.add_argument(
        "-a",
        "--api_key",
        type=str,
        default=None,
        help="Use a specific API key instead of the default one in the file",
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
        default_api_key = args.api_key if args.api_key else api_keys[0]
        youtube = build("youtube", "v3", developerKey=default_api_key)
        video_id = parse_video_id(args.seed)

        if not (args.import_trees or args.force or args.aggressive or args.titles):
            layers = get_layers(youtube, video_id, args.width, args.depth)
            with open(f"./data/{video_id}.log", "a", encoding="utf-8") as logfile:
                print(layers, file=logfile)
            draw_tree(youtube, layers, args.labels, args.graph)

        elif args.import_trees:
            logfile = args.import_trees
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
