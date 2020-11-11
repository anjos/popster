#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Identifies and removes duplicate (backups) from one or multiple directories

Usage: %(prog)s [-v...] [options] <path> [<path>...]
       %(prog)s --help
       %(prog)s --version


Arguments:
  <path>  Directory that should be considered when searching for duplicates


Options:
  -h, --help                  Shows this help message and exits
  -V, --version               Prints the version and exits
  -v, --verbose               Increases the output verbosity level. May be used
                              multiple times
  -o <path>, --output=<path>  Writes actions to a shell script you can review
                              and execute later


Examples:

  1. Finds and reports duplicates in two distinct directories.  Print
     action recommendations:

     $ %(prog)s -vv /path/dir1 /path/dir2

  2. The same as above, but records actions in a shell script to be executed in
     batch, later:

     $ %(prog)s -vv /path/dir1 /path/dir2 --output=actions.sh

"""


import os
import sys
import shutil


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

    from .dedup import check_duplicates, recommend_action

    dups = check_duplicates(args["<path>"])
    erase, check = recommend_action(dups)

    if args["--output"]:  #write to file instead of screen
        with open(args["--ouptut"], "wt") as f:

            f.write(f"#!/usr/bin/env bash\n\n")
            f.write(f"## Recommending removal of {len(erase)} files...\n")
            for k in erase:
                f.write(f"rm -f \"{k}\"\n")

            f.write(f"## Should be checking {len(check)} duplications...\n")
            for k in check:
                p = [f"\"{l}\"" for l in k]
                f.write(f"## check: {p[0]}\n")
                for i in p[1:]:
                    f.write(f"##  - {i}\n")
                f.write("\n")

    else:
        print(f"Recommend removal of {len(erase)} file(s):")
        for k in erase:
            print(f"Remove: \"{k}\"")
        print("")

        print(f"Check {len(check)} duplication(s):")
        for k in check:
            p = [f"\"{l}\"" for l in k]
            print(f"check: {p[0]}")
            for i in p[1:]:
                print(f"  - {i}\n")
            print("")
