import asyncio
import logging
from functools import partial
from urllib.parse import urljoin

from aiohttp import ClientSession

from majority_bot.settings import TG_TOKENS, TEST_SECURE_URL

logger = logging.getLogger(__name__)
_client = None


def create_client():
    return ClientSession('https://api.telegram.org')


def get_client() -> ClientSession:
    global _client
    if _client is None:
        _client = create_client()

    return _client


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
    _key = 'live' if is_live else 'test'
    url = f'/bot{TG_TOKENS[_key]}/{message.pop("method")}'

    logger.info(url)

    async with create_client() as client:
        response = await client.post(url, json=message)
        if response.status != 200:
            logger.error(await response.read())
            if response.status >= 500:
                return None

        return await response.json()


async def set_webhook(url, *, is_live: bool, is_admin: bool):
    if is_live or is_admin:
        raise NotImplementedError

    data = await _send_message({
        'method': 'setWebhook',
        'url': urljoin(url, f'/bot/test/user/{TEST_SECURE_URL}'),
    }, is_live=is_live)

    return data