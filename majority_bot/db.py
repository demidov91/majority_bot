from contextvars import ContextVar

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from majority_bot.settings import TEST_CONNECTION_STRING

_connections = {}
_connection = ContextVar('connection')


def get_connection(*, is_live: bool):
    if is_live:
        raise NotImplementedError

    conn_string = TEST_CONNECTION_STRING

    if conn_string not in _connections:
        _connections[conn_string] = AsyncIOMotorClient(conn_string)['test_db']

    return _connections[conn_string]


def set_active_connection(*, is_live: bool):
    _connection.set(get_connection(is_live=is_live))


def connection() -> 'motor.core.AgnosticDatabase':
    return _connection.get()


async def get_tg_user(user_id: int):
    return await connection()['users'].find_one({'tg_id': user_id})


async def get_active_messages(location: str, language: str):
    record = await connection()['tasks'].find_one({'location': location, 'language': language}, sort=[('created_at', DESCENDING)])
    return record and record.get('data')
