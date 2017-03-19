#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Watches and imports photos recursively from a folder

Usage: %(prog)s [-v...] [options]
       %(prog)s --help
       %(prog)s --version


Options:
  -h, --help                  Shows this help message and exits
  -V, --version               Prints the version and exits
  -v, --verbose               Increases the output verbosity level. May be used
                              multiple times
  -f, --folder-format=<fmt>   How to format (using date formatters), the
                              destination folder where the photos/videos are
                              going to be stored [default: %%Y/%%B/%%d.%%m.%%Y]
  -n, --dry-run               If set, just tell what it would do instead of
                              doing it. This flag is good for testing.
  -e, --email                 If set, e-mail agents responsible every minute
                              about status
  -s, --source=<path>         Path leading to the folder to watch for
                              photographs to import
                              [default: /share/Download/SmartImport]
  -d, --dest=<path>           Path leading to the folder to dump photos to
                              [default: /share/Pictures/Para Organizar]
  -c, --copy                  Copy instead of moving files from the source
                              folder (this will be a bit slower).
  -i, --idleness=<secs>       Number of seconds to wait until no more activity
                              is registered and before it can dispatch summary
                              e-mails [default: 60]


Examples:

  1. Test what would do:

     $ %(prog)s -vv --email --dry-run

  2. Runs the program and e-mails when done:

     $ %(prog)s -vv --email

"""


import os
import sys
import time

import logging
logger = logging.getLogger(__name__)


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

  # setup logging
  if args['--verbose'] == 1: logger.setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logger.setLevel(logging.DEBUG)

  from .sorter import Sorter
  the_sorter = Sorter(
      base=args['--source'],
      dst=args['--dest'],
      fmt=args['--folder-format'],
      move=not(args['--copy']),
      dry=args['--dry-run'],
      email=args['--email'],
      idleness=int(args['--idleness']),
      )

  the_sorter.start()
  try:
    while True:
      time.sleep(1)
      the_sorter.email_check()
  except KeyboardInterrupt:
    the_sorter.stop()
  the_sorter.join()
