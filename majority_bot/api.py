from aiohttp import web
from telegram import Update, User, Message

from majority_bot.db import set_active_connection, get_tg_user
from majority_bot.exceptions import UnexpectedResponseError
from majority_bot.handlers import (
    SetLanguageHandler,
    SetLocationHandler,
    PersonalTaskHandler,
    CommandHandler,
    TakeRestHandler,
    WaitingOrdersHandler,
)
from majority_bot.tg_communication import send_messages_soon
from majority_bot.translate import gettext, set_active


async def bot_test_entry_point(request):
    set_active_connection(is_live=False)
    return web.json_response(await root_handler(request, is_live=False))


async def root_handler(request, *, is_live: bool):
    tg_update = Update.de_json(await request.json(), None)
    if not tg_update.effective_user:
        return {}

    set_active(tg_update.effective_user.language_code)

    handler = await get_handler(tg_update.effective_user.id, tg_update.message)
    try:
        messages = await handler.handle(tg_update.effective_user, tg_update.message)
    except UnexpectedResponseError:
        return {
            'method': 'sendMessage',
            'text': gettext('Unexpected Response'),
        }

    send_messages_soon(messages, tg_update.message.chat_id, is_live=is_live)
    next_messages = await STATE_TO_HANDLER[handler.next_state].get_greeting()
    await handler.switch_state()
    send_messages_soon(next_messages, tg_update.message.chat_id, is_live=is_live)
    return {}


STATE_TO_HANDLER = {
    'language': SetLanguageHandler,
    'location': SetLocationHandler,
    'personal-task': PersonalTaskHandler,
    'take-rest': TakeRestHandler,
    'waiting-orders': WaitingOrdersHandler,
}


async def get_handler(user: User, message: Message) -> 'majority_bot.handlers.BaseHandler':
    if message.text is not None and message.text.startswith('/') and message.text[1:] in CommandHandler.expected:
        return CommandHandler(None)

    db_user = await get_tg_user(user.id)
    if db_user is None:
        raise ValueError(user.id)

    return STATE_TO_HANDLER[db_user.get('state')](db_user)


async def init():
    app = web.Application()

    app.router.add_post('/bot/test/user/', bot_test_entry_point)

    return app