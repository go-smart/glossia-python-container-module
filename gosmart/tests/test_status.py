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
def status(monkeypatch):
    update_socket_location = MagicMock()
    status = gosmart.status.StatusUpdater(update_socket_location)
    status.model_builder = MagicMock()
    return status


def test_connect(monkeypatch, status):
    status._update_socket_location = True
    mock1 = MagicMock()
    mock1.return_value = 'oooooo'
    monkeypatch.setattr('os.path.exists', lambda p3: True)
    monkeypatch.setattr('socket.socket', lambda p3, p4: mock1)
    status.connect()
    status._update_socket.connect.assert_called_with(True)


def test_status(monkeypatch, status):
    random_message = MagicMock()
    random_percentage = MagicMock()
    status._update_socket = MagicMock()
    random_percentage = 0.3
    random_message = 'msg1'
    status._update_socket = MagicMock()
    status.status(random_message, random_percentage)
    status._update_socket.sendall.assert_called_with(bytes('0.300000|msg1', encoding='utf-8'))
