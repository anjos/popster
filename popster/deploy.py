#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dumb (optionless) script that just deployes all our containers"""

import os
from . import qnap, utils


def _delete_create(session, server, name, existing, options):

    if name in existing:
        if existing[name]["state"] == "running":
            qnap.stop_container(session, server, existing[name]["id"])
        qnap.remove_container(session, server, existing[name]["id"])

    retval = qnap.create_container(session, server, name, options)
    if options.get("autostart", True) == False:
        qnap.stop_container(session, server, retval["id"])


def main():

    from popster import sorter

    logger = sorter.setup_logger("popster", 3)

    common_command = utils.retrieve_json_secret("popster/deploy.json")
    common_options = []
    for k, v in common_command.items():
        if v is not None:
            common_options.append('%s="%s"' % (k, v))
        else:
            common_options.append("%s" % (k,))
    common_command = " ".join(common_options)
    nas = utils.retrieve_json_secret("nas/info.json")
    server = nas["server"]

    volumes = {
        "host": {
            "/Pictures/Importar Aqui": dict(bind="/imported", rw=True),
            "/Pictures/Para Organizar": dict(bind="/organized", rw=True),
        },
    }

    with qnap.session(server, nas["username"], nas["password"]) as session:

        existing = qnap.get_containers(session, server)
        existing = dict([(k["name"], k) for k in existing])

        # Use this one for tests
        options = dict(volume=volumes, autostart=False, command="-vvv --help",)
        # _delete_create(session, server, 'popster-help', existing, options)

        #### RECURRENT ACTIONS ####

        options = dict(volume=volumes, autostart=True, command=common_command,)
        _delete_create(session, server, "popster", existing, options)


if __name__ == "__main__":
    main()
