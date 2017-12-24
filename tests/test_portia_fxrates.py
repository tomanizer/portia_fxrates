#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_portia_fxrates
----------------------------------

Tests for `portia_fxrates` module.
"""

import pytest
from pytest import *
import pandas as pd
from datetime import datetime

from portia_fxrates import getFX

def test_getfx():
    assert isinstance(getFX(), pd.DataFrame)

def test_getFX_EUR():
    assert isinstance(getFX(currlist=["EUR"]), pd.DataFrame)

def test_getFX_Cob():
    mycobdate = datetime.strftime(datetime.now(), format="%Y%m%d")
    assert isinstance(getFX(cobdate=mycobdate), pd.DataFrame)

