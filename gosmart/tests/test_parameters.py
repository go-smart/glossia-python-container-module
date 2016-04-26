import pytest
import asyncio.coroutines
import asyncio
from unittest.mock import MagicMock
import uuid

import gosmart
gosmart.setup(False)
import gosmart.status
import gosmart.parameters

known_guid = str(uuid.uuid4()).upper()
unknown_guid = str(uuid.uuid4()).upper()


def magic_coro():
    mock = MagicMock()
    return mock, asyncio.coroutine(mock)


@asyncio.coroutine
def wait():
    pending = asyncio.Task.all_tasks()
    relevant_tasks = [t for t in pending if ('test_' not in t._coro.__name__)]
    yield from asyncio.gather(*relevant_tasks)


@pytest.fixture(scope="function")
def param(monkeypatch):
    prefix = MagicMock()
    param = gosmart.parameters.GoSmartParameterLoader(prefix)
    param.model_builder = MagicMock()
    return param


def test_get_parameters(monkeypatch, param):
    param.initiated = True
    param.P = 'aaa'
    param.NP = 'ccc'
    result = param.get_parameters()
    assert(result == ('aaa', 'ccc'))


def test_get_regions(monkeypatch, param):
    param.initiated = MagicMock()
    param.P = MagicMock()
    param.initiated = True
    param.R = 'aaa'
    result = param.get_regions()
    assert(result == 'aaa')


def test_get_region_dict(monkeypatch, param):
    param.initiated = MagicMock()
    param._region_dict = MagicMock()
    param.initiated = True
    param._region_dict = 'aaa'
    result = param.get_region_dict()
    assert(result == 'aaa')


def test_initiate(monkeypatch, param):
    param._load_parameters = MagicMock()
    param._initiate_region_dict = MagicMock()
    param._initiate_parameter_dict = MagicMock()
    param.initiate()
    param._load_parameters.assert_called_with()
    param._initiate_region_dict.assert_called_with()
    param._initiate_parameter_dict.assert_called_with()


def test_initiate_region_dict(monkeypatch, param):
    mock1 = MagicMock()
    monkeypatch.setattr('gosmart.dicts.AttributeDict', lambda p1: mock1)
    monkeypatch.setattr('gosmart.region.Region.group', lambda p1: 'q1')
    monkeypatch.setattr('gosmart.region.Region.meshed_as', lambda p1: 'q1')
    monkeypatch.setattr('gosmart.region.Region.zone', lambda p1: 'q1')
    monkeypatch.setattr('gosmart.region.Region.surface', lambda p1: 'q1')
    param._initiate_region_dict()
    # nothing to assert here ...


def test_initiate_parameter_dict(monkeypatch, param):
    param._parameter_dict = 'ooooooooooooooooooo'
    mock1 = MagicMock()
    mock1.update.return_value = 'q1'
    monkeypatch.setattr('gosmart.dicts.ParameterDict', lambda: mock1)
    param._initiate_parameter_dict()
    # gosmart.dicts.ParameterDict.assert_called_with()
    mock1.update.assert_called_with('ooooooooooooooooooo')
