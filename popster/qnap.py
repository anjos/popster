#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities to use the QNAP Container Station API

See documentation here: http://qnap-dev.github.io/container-station-api/index.html
"""


import os
import sys
import pickle
import requests
import getpass
import warnings
import contextlib

import logging

logger = logging.getLogger(__name__)

import pkg_resources


SESSION_FILE = os.path.expanduser("~/.qnap-auth.pickle")


@contextlib.contextmanager
def no_ssl_warnings(verify):
    if not verify:
        warnings.filterwarnings("ignore", "Unverified HTTPS request")
    yield
    if not verify:
        warnings.resetwarnings()


def api(session, server, url, verb="get", data=None, json=None, verify=False):
    """Calls the container station API with a given url and data dictionary


    Parameters:

      session (requests.Session): A previously opened session with the
        authentication cookies to use

      server (str): The server to reach

      url (str): The URL to call on the container station API, relative to the
        the address ``/container-station/api/v1", which is always
        prepended.

      verb (str, Optional): One of the HTTP verbs to query the URL with. If not
        specified, defaults to ``get``. Any verb available in
        :py:class:`requests.Session` is acceptable.

      data (dict, Optional): A dictionary containing parameters to pass to the
        API

      verify (bool, Optional): If should use ``verify=True`` for requests calls


    Returns:

      int: The returned status code

      requests.Result: An object that contains the reply from the HTTP API call

    """

    url = server + "/container-station/api/v1" + url
    logger.debug(f"{verb.upper()} {url}")
    with no_ssl_warnings(verify):
        return getattr(session, verb)(url, data=data, json=json, verify=verify)


def login(server, username, password, verify=False):
    """Logs-in the server, if a session file is not available yet.


  Parameters:

    server (str): The server to reach

    username (str): The user identifier to use for login

    password (str): The user password for login

    verify (bool, Optional): If should use ``verify=True`` for requests calls


  Returns:

    requests.Session: A restored or new session after successfuly
    authenticating to the server

  """

    if os.path.exists(SESSION_FILE):
        logger.debug(f"Session file ({SESSION_FILE}) exists - trying to use it")
        with open(SESSION_FILE, "rb") as f:
            session = pickle.load(f)
        result = api(session, server, "/login_refresh", verify=verify)
        if "error" in result.json():
            logout(server, verify=verify)

    if not os.path.exists(SESSION_FILE):
        logger.debug(f"Session file ({SESSION_FILE}) does not exist - logging-in")

        session = requests.Session()
        data = dict(username=username, password=password)
        result = api(
            session, server, "/login", verb="post", json=data, verify=verify
        )

    if result.status_code != 200:
        raise RuntimeError(
            "Login request failed with status code %d" % result.status_code
        )
    response = result.json()
    if response.get("username") != username:
        raise RuntimeError(
            "Login request for user %s failed (%s is "
            "logged in)" % (username, response.get("username"))
        )

    with open(SESSION_FILE, "wb") as f:
        pickle.dump(session, f)

    return session


def logout(server, verify=False):
    """Logs the user out


  Parameters:

    server (str): The server to reach

    verify (bool, Optional): If should use ``verify=True`` for requests calls

  """

    if not os.path.exists(SESSION_FILE):
        logger.error(f"No session file exists at {SESSION_FILE} - not logging out")
        return

    logger.debug("Logging out...")

    with open(SESSION_FILE, "rb") as f:
        session = pickle.load(f)

    result = api(session, server, "/logout", verb="put", verify=verify)
    response = result.json()

    if os.path.exists(SESSION_FILE):
        logger.debug(f"Removing {SESSION_FILE}...")
        os.unlink(SESSION_FILE)

    session.close()  # close all connections


@contextlib.contextmanager
def session(server, username, password, verify=False):
    """Context manager that opens and closes a connection to the NAS"""

    yield login(server, username, password, verify=verify)
    logout(server, verify=verify)


def system(server, session=None, verify=False):
    """Checks system information


  Parameters:

    server (str): The server to reach

    session (requests.Session): A previously opened session you'd like to close

    verify (bool, Optional): If should use ``verify=True`` for requests calls


  Returns:

    dict: A valid JSON object, decoded into Python

  """

    return api(session, server, "/system", verify=verify).json()


def get_containers(session, server, verify=False):
    """Gets all information on available containers


  Parameters:

    session (requests.Session): A previously opened session you'd like to close

    server (str): The server to reach

    verify (bool, Optional): If should use ``verify=True`` for requests calls


  Returns:

    list of dict: Containing information about all running containers

  """

    return api(session, server, "/container", verify=verify).json()


def inspect_container(session, server, id_, verify=False):
    """Gets all information on the container with the given identifier


  Parameters:

    session (requests.Session): A previously opened session you'd like to close

    server (str): The server to reach

    id_ (str): The identify of the container to inspect

    verify (bool, Optional): If should use ``verify=True`` for requests calls


  Returns:

    list: A valid JSON object, decoded into Python

  """

    return api(
        session, server, "/container/docker/%s/inspect" % id_, verify=verify
    ).json()


def stop_container(session, server, id_, verify=False):
    """Stops the container with the given identifier


  Parameters:

    session (requests.Session): A previously opened session you'd like to close

    server (str): The server to reach

    id_ (str): The identify of the container to stop

    verify (bool, Optional): If should use ``verify=True`` for requests calls


  Returns:

    list: A valid JSON object, decoded into Python

  """

    return api(
        session,
        server,
        "/container/docker/%s/stop" % id_,
        verb="put",
        verify=verify,
    ).json()


def remove_container(session, server, id_, verify=False):
    """Removes the container with the given identifier


  Parameters:

    session (requests.Session): A previously opened session you'd like to close

    server (str): The server to reach

    id_ (str): The identify of the container to be removed

    verify (bool, Optional): If should use ``verify=True`` for requests calls


  Returns:

    list: A valid JSON object, decoded into Python

  """

    return api(
        session,
        server,
        "/container/docker/%s" % id_,
        verb="delete",
        verify=verify,
    ).json()


def create_container(
    session,
    server,
    name,
    options,
    image="anjos/popster",
    tag="v%s" % pkg_resources.require("popster")[0].version,
    verify=False,
):
    """Creates a container with an existing image


  Parameters:

    session (requests.Session): A previously opened session you'd like to close

    server (str): The server to reach

    name (str): The name of the container to update

    image (str): The name of the image to use for the update (e.g.:
      'anjos/popster')

    tag (str): Tag to be used for the above image (e.g.: 'v1.2.3')

    options (dict): A dictionary of options that will be passed to the API

    verify (bool, Optional): If should use ``verify=True`` for requests calls

  """

    info = dict(type="docker", name=name, image=image, tag=tag,)

    # prepares new container information
    info.update(options)

    response = api(
        session, server, "/container", verb="post", json=info, verify=verify
    )
    return response.json()


def retrieve_logs(session, server, id_, tail=1000, verify=False):
    """Retrieves the logs from container


  Parameters:

    session (requests.Session): A previously opened session you'd like to close

    server (str): The server to reach

    id_ (str): The identifier of the container to retrieve logs from

    verify (bool, Optional): If should use ``verify=True`` for requests calls

  """

    return api(
        session,
        server,
        "/container/docker/%s/logs?tail=%d" % (id_, tail),
        verify=verify,
    ).json()
