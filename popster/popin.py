#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


"""Watches and imports photos recursively from an SD card reader

Usage: %(prog)s [-v...] [options] <source> <dest>
       %(prog)s --help
       %(prog)s --version


Arguments:
  <source>  Name of the device to watch for photographs
  <dest>    Destination directory where to place sorted photographs/videos


Options:
  -h, --help                  Shows this help message and exits
  -V, --version               Prints the version and exits
  -v, --verbose               Increases the output verbosity level
  -f, --folder-format=<fmt>   How to format (using date formatters), the
                              destination folder where the photos/videos are
                              going to be stored [default: %Y/%b/
  -n, --dry-run
  -e, --email=<dest>



Examples:

  1. Specify a different criteria (only mhter, mwer or eer accepted):

     $ %(prog)s --criterium=mhter scores.txt

  2. Calculate the threshold that minimizes the weither HTER for a cost of 0.4:

    $ %(prog)s --criterium=mwer --cost=0.4 scores.txt

  3. Parse your input using a 5-column format

    $ %(prog)s scores.txt

"""


import os
import sys


def apthres(neg, pos, thres):
  """Prints a single output line that contains all info for the threshold"""

  from .. import farfrr

  far, frr = farfrr(neg, pos, thres)
  hter = (far + frr)/2.0

  ni = neg.shape[0] #number of impostors
  fa = int(round(far*ni)) #number of false accepts
  nc = pos.shape[0] #number of clients
  fr = int(round(frr*nc)) #number of false rejects

  print("FAR : %.3f%% (%d/%d)" % (100*far, fa, ni))
  print("FRR : %.3f%% (%d/%d)" % (100*frr, fr, nc))
  print("HTER: %.3f%%" % (100*hter,))


def calculate(neg, pos, crit, cost):
  """Returns the threshold given a certain criteria"""

  if crit == 'eer':
    from .. import eer_threshold
    return eer_threshold(neg, pos)
  elif crit == 'mhter':
    from .. import min_hter_threshold
    return min_hter_threshold(neg, pos)

  # defaults to the minimum of the weighter error rate
  from .. import min_weighted_error_rate_threshold
  return min_weighted_error_rate_threshold(neg, pos, cost)


def main(user_input=None):

  if user_input is not None:
    argv = user_input
  else:
    argv = sys.argv[1:]

  import docopt
  import pkg_resources

  completions = dict(
      prog=os.path.basename(sys.argv[0]),
      version=pkg_resources.require('bob.measure')[0].version
      )

  args = docopt.docopt(
      __doc__ % completions,
      argv=argv,
      version=completions['version'],
      )

  # validates criterium
  valid_criteria = ('eer', 'mhter', 'mwer')
  if args['--criterium'] not in valid_criteria:
    raise docopt.DocoptExit("--criterium must be one of %s" % \
        ', '.join(valid_criteria))

  # handles cost validation
  try:
    args['--cost'] = float(args['--cost'])
  except:
    raise docopt.DocoptExit("cannot convert %s into float for cost" % \
        args['--cost'])

  if args['--cost'] < 0.0 or args['--cost'] > 1.0:
    docopt.DocoptExit("cost should lie between 0.0 and 1.0")

  from ..load import load_score, get_negatives_positives
  neg, pos = get_negatives_positives(load_score(args['<scores>']))

  t = calculate(neg, pos, args['--criterium'], args['--cost'])
  print("Threshold:", t)
  apthres(neg, pos, t)

  return 0
