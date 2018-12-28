#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Converts HEIF/HEIC image files to JPEG, preserving all metadata

Usage: %(prog)s [-v...] [options] <path> [<path>...]
       %(prog)s --help
       %(prog)s --version


Arguments:
  <path>  Path to asset to convert to JPEG (from HEIF)


Options:
  -h, --help                  Shows this help message and exits
  -V, --version               Prints the version and exits
  -v, --verbose               Increases the output verbosity level. May be used
                              multiple times


Examples:

  1. Converts a single image

     $ %(prog)s -vv /path/to/image.heic

  2. Converts multiple images

     $ %(prog)s -vv /path/to/*.heic

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

  from .sorter import setup_logger
  logger = setup_logger('popster', args['--verbose'])

  from .utils import which, heic_to_jpeg
  from .sorter import read_creation_date

  sips = which('sips')
  if sips is None:
    logger.critical('Cannot find "sips" application on your $PATH ' \
        '- are you on a (recent) macOS machine?')
    return 1

  for k, path in enumerate(args['<path>']):
    output = heic_to_jpeg(sips, path)
    date = read_creation_date(output)
    logger.info('%s: %s [%d/%d]', output, date, k+1, len(args['<path>']))
