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
                              going to be stored [default: %%Y/%%m/%%d.%%m.%%Y]
  -N, --no-date-path=<str>    A string with the name of a directory that will
                              be used verbatim in case a date cannot be
                              retrieved from the source filename
                              [default: Sem Data]
  -n, --dry-run               If set, just tell what it would do instead of
                              doing it. This flag is good for testing.
  -e, --email                 If set, e-mail agents responsible every time
                              action occurs
  -s, --source=<path>         Path leading to the folder to watch for
                              photographs to import [default: /imported]
  -d, --dest=<path>           Path leading to the folder to dump photos to
                              [default: /organized]
  -c, --copy                  Copy instead of moving files from the source
                              folder (this will be a bit slower).
  -p, --check-point=<secs>    Number of seconds to wait before each check. This
                              number should be smaller than the idleness
                              setting. [default: 10]
  -i, --idleness=<secs>       Number of seconds to wait until no more activity
                              is registered and before it can dispatch summary
                              e-mails [default: 30]
  -S, --server=<host>         Name of the SMTP server to use for sending the
                              message [default: smtp.gmail.com]
  -P, --port=<port>           Port to use on the server [default: 587]
  -u, --username=<name>       Username for the SMTP authentication
  -w, --password=<pwd>        Password for the SMTP authentication


Examples:

  1. Test what would do:

     $ %(prog)s -vv --email --dry-run

  2. Runs the program and e-mails when done:

     $ %(prog)s -vv --email --username=me@gmail.com --password=secret

"""


import os
import sys
import time


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

  from .sorter import setup_logger, Sorter
  logger = setup_logger('popster', args['--verbose'])

  logger.info("Watching for photos/movies on: %s", args['--source'])
  logger.info("Moving photos/movies to: %s", args['--dest'])
  logger.info("Folder format set to: %s", args['--folder-format'])
  logger.info("No-date path set to: %s", args['--no-date-path'])
  logger.info("Checkpoint timeout: %s seconds", args['--check-point'])
  logger.info("Idle time set to: %s seconds", args['--idleness'])
  if args['--email']:
    logger.info("Sending **real** e-mails")
  else:
    logger.info("Only logging e-mails, **not** sending anthing")

  check_point = int(args['--check-point'])
  idleness = int(args['--idleness'])

  the_sorter = Sorter(
      base=args['--source'],
      dst=args['--dest'],
      fmt=args['--folder-format'],
      nodate=args['--no-date-path'],
      move=not(args['--copy']),
      dry=args['--dry-run'],
      email=args['--email'],
      server=args['--server'],
      port=int(args['--port']),
      username=args['--username'],
      password=args['--password'],
      idleness=idleness,
      )

  the_sorter.start()
  try:
    while True:
      time.sleep(check_point)
      the_sorter.check_point()
  except KeyboardInterrupt:
    the_sorter.stop()
  the_sorter.join()
