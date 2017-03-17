#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Test units'''

import os
import shutil
import datetime
import tempfile
import pkg_resources

import nose.tools

from .sorter import read_creation_date, copy, rcopy, DateReadoutError


def data_path(f):
  '''Returns a path to a data item inside the package'''

  return pkg_resources.resource_filename(__name__, os.path.join('data', f))


def test_jpeg_readout():

  #Tests one extract the proper exif tag from a jpeg file

  date = read_creation_date(data_path('img_with_exif.jpg'))
  assert date == datetime.datetime(2003, 12, 14, 12, 1, 44)


@nose.tools.raises(DateReadoutError)
def test_exif_failure():

  #Tests it raises a proper exception when the jpeg file has no exif info
  read_creation_date(data_path('img_without_exif.jpg'))


def test_move():

  #Tests if can organize at least the sample photo

  #Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=True, dry=False)
    assert os.path.exists(result)
    assert not os.path.exists(subfolder) #removed
    assert os.path.exists(base) #not removed


def test_move_fails():

  #Tests if can correctly detect moving fails

  #Temporary setup
  src = data_path('img_without_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  # STOPPED HERE!
  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=True, dry=False)
    assert os.path.exists(result)
    assert not os.path.exists(subfolder) #removed
    assert os.path.exists(base) #not removed


def test_move_dry():

  #Tests if can organize at least the sample photo

  #Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=True, dry=True)
    assert os.path.exists(subfolder) #removed
    assert not os.path.exists(result)


def test_copy():

  #Tests if can organize at least the sample photo

  #Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=False, dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder)


def test_copy_dry():

  #Tests if can organize at least the sample photo

  #Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=False, dry=True)
    assert os.path.exists(subfolder)
    assert not os.path.exists(result)
