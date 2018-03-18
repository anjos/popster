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
  -f, --folder-format=<fmt>   How to format (using date formatters), the
                              destination folder where the photos/videos are
                              going to be stored [default: %%Y/%%B/%%d.%%m.%%Y]


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
      version=pkg_resources.require('popster')[0].version
      )

  args = docopt.docopt(
      __doc__ % completions,
      argv=argv,
      version=completions['version'],
      )


  from .sorter import read_creation_date

  for path in args['<path>']:
    date = read_creation_date(path)
    print('%s: %s' % (path, date))
