#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Test units'''

import os
import datetime
import pkg_resources

from .sorter import read_date


def data_path(f):
  '''Returns a path to a data item inside the package'''

  return pkg_resources.resource_filename(__name__, os.path.join('data', f))


def test_exif_readout():
  '''Tests one extract the proper exif tag from a jpeg file'''

  date = read_date(data_path('img1'))
