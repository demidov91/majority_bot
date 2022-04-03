import asyncio
import logging
from functools import partial

from aiohttp import ClientSession

from majority_bot.settings import TG_TOKENS

logger = logging.getLogger(__name__)
_clients = {}


def get_client(*, is_live) -> ClientSession:
    key = 'live' if is_live else 'test'
    if key not in _clients:
        base_url = f'https://api.telegram.org/bot{TG_TOKENS[key]}/'
        _clients[key] = ClientSession(base_url)

    return _clients[key]


def send_messages_soon(messages, chat_id, *, is_live):
    if messages is None:
        return

    if isinstance(messages, dict):
        messages = [messages]

    for msg in messages:
        msg['chat_id'] = chat_id
        send_message_soon(msg, is_live=is_live)


def send_message_soon(message, *, is_live):
    asyncio.get_event_loop().call_soon(partial(_send_message, message, is_live=is_live))


async def _send_message(message: dict, is_live: bool):
    method = message.pop('method')
    response = await get_client(is_live=is_live).post(method, json=message)
    if response.status != 200:
        logger.error(await response.read())


async def set_webhook(url, *, is_live: bool, is_admin: bool):
    await _send_message({
        'method': 'setWebhook',
        'url': url,
    }, is_live=is_live)