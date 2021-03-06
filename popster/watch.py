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
                              [default: nodate]
  -H, --hostname=<name>       Use this name as hostname instead of the
                              environment's [default: %(hostname)s]
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
  -F, --sender=<user>         The value to be used for the "From:" e-mail
                              field, if we should send them. E.g.:
                              "John Doe <john.doe@example.com>"
  -T, --to=<u1,u2,...>        A comma-separated list of users to send e-mails
                              to, if we should send them. E.g.:
                              "U1 <u1@example.com>,U2 <u2@example.com>"
  -X, --filesystem-timestamp  If set, and if no creation time date is found on
                              the traditional object metadata, then organizes
                              images using the filesystem timestamp - first try
                              the creation time if available, else the
                              last modification time.


Examples:

  1. Test what would do:

     $ %(prog)s -vv --email --sender=joe@example.com --to=alice@example.com --dry-run

  2. Runs the program and e-mails when done:

     $ %(prog)s -vv --email --username=me@gmail.com --password=secret --sender=bob@example.com --to='alice@example.com,jack@example.com'

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
    import socket
    import pkg_resources

    completions = dict(
        prog=os.path.basename(sys.argv[0]),
        version=pkg_resources.require("popster")[0].version,
        hostname=socket.gethostname(),
    )

    args = docopt.docopt(
        __doc__ % completions, argv=argv, version=completions["version"],
    )

    from .sorter import setup_logger, Sorter

    logger = setup_logger("popster", args["--verbose"])

    logger.info(
        "Popster version %s (running on %s)",
        completions["version"],
        args["--hostname"],
    )
    logger.info("Watching for photos/movies on: %s", args["--source"])
    logger.info("Moving photos/movies to: %s", args["--dest"])
    logger.info("Folder format set to: %s", args["--folder-format"])
    logger.info(
        "Default to filesystem timestamps: %s", args["--filesystem-timestamp"]
    )
    logger.info("No-date path set to: %s", args["--no-date-path"])
    logger.info("Checkpoint timeout: %s seconds", args["--check-point"])
    logger.info("Idle time set to: %s seconds", args["--idleness"])
    if args["--email"]:
        logger.info("Sending **real** e-mails")
    else:
        logger.info("Only logging e-mails, **not** sending anything")
    logger.info("E-mail From: %s", args["--sender"])
    logger.info("E-mail To: %s", args["--to"])

    check_point = int(args["--check-point"])
    idleness = int(args["--idleness"])

    if args["--email"]:
        to = [k.strip() for k in args["--to"].split(",")]
    else:
        to = []

    the_sorter = Sorter(
        base=args["--source"],
        dst=args["--dest"],
        fmt=args["--folder-format"],
        timestamp=args["--filesystem-timestamp"],
        nodate=args["--no-date-path"],
        move=not (args["--copy"]),
        dry=args["--dry-run"],
        email=args["--email"],
        hostname=args["--hostname"],
        sender=args["--sender"],
        to=to,
        server=args["--server"],
        port=int(args["--port"]),
        username=args["--username"],
        password=args["--password"],
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
