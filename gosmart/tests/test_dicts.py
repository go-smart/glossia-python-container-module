import pytest
import asyncio.coroutines
import asyncio
from unittest.mock import MagicMock
import uuid

import gosmart
gosmart.setup(False)
import gosmart.dicts
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
def dicts(monkeypatch):
    update_socket_location = MagicMock()
    dicts = gosmart.dicts.ParameterDict(update_socket_location)
    dicts.model_builder = MagicMock()
    return dicts


def test__getattr__(monkeypatch, dicts):
    random_attr = MagicMock()
    dicts.__getitem__ = MagicMock()
    dicts.__getitem__.return_value = 12345
    result = dicts.__getattr__(random_attr)
    assert(result == 12345)
