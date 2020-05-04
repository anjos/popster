#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Checks the date on a particular media asset

Usage: %(prog)s [-v...] [options] <path> [<path>...]
       %(prog)s --help
       %(prog)s --version


Arguments:
  <path>  Path to asset to check date from


Options:
  -h, --help                  Shows this help message and exits
  -V, --version               Prints the version and exits
  -v, --verbose               Increases the output verbosity level. May be used
                              multiple times


Examples:

  1. Check date on an image

     $ %(prog)s -vv /path/to/image.jpg

  2. Check date on a movie

     $ %(prog)s -vv /path/to/image.mov

"""


import os
import sys


def main(user_input=None):

    if user_input is not None:
        argv = user_input
    else:
        argv = sys.argv[1:]

    import docopt
    import pkg_resources

    completions = dict(
        prog=os.path.basename(sys.argv[0]),
        version=pkg_resources.require("popster")[0].version,
    )

    args = docopt.docopt(
        __doc__ % completions, argv=argv, version=completions["version"],
    )

    from .sorter import setup_logger

    logger = setup_logger("popster", args["--verbose"])

    from .sorter import read_creation_date, file_timestamp, DateReadoutError

    for path in args["<path>"]:
        try:
            date = read_creation_date(path)
        except DateReadoutError:
            logger.warn(
                "no date metadata at %s - returning creation date" % path
            )
            date = file_timestamp(path)
        print("%s: %s" % (path, date))
