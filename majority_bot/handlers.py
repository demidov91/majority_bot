from typing import Optional

from telegram.user import User
from telegram.message import Message

from majority_bot.db import connection, get_active_messages
from majority_bot.exceptions import UnexpectedResponseError
from majority_bot.tg_utils import message_contains, build_message
from majority_bot.translate import gettext_lazy, gettext


class BaseHandler:
    greeting: Optional[str]
    options: Optional[list]
    next_state: Optional[str]

    def __init__(self, db_user: Optional[dict]):
        self.db_user = db_user

    async def get_greeting(self):
        return build_message(self.greeting, self.options)

    async def handle(self, user: User, message: Message):
        raise NotImplementedError


class SetLanguageHandler:
    greeting = 'Вітанкі. Абярыце мову.'
    options = ['Беларуская', 'Русский']
    next_state = 'location'

    async def handle(self, user: User, message: Message):
        if 'беларуская' in message.text.lower():
            lang = 'be'

        elif 'русский' in message.text.lower():
            lang = 'ru'

        else:
            raise UnexpectedResponseError()

        await connection()['users'].update_one({'tg_id': user.id}, {'language': lang})


class SetLocationHandler(BaseHandler):
    greeting = gettext_lazy('Where are you located?')
    options = [gettext_lazy('In Belarus'), gettext_lazy('Abroad')]
    next_state = 'personal-task'

    async def handle(self, user: User, message: Message):
        if message_contains(message, 'мяжой', 'граніцей'):
            location = 'out-bel'

        elif message_contains(message, 'беларус'):
            location = 'in-bel'

        else:
            raise UnexpectedResponseError()

        await connection()['users'].update_one({'tg_id': user.id}, {'location': location})

        return await get_tg_active_messages(self.db_user)


class PersonalTaskHandler(BaseHandler):
    greeting = gettext_lazy('Choose button or a number.')
    options = [
        gettext_lazy('1 - Ready'),
        gettext_lazy('2 - Contact us'),
        gettext_lazy('3 - Take a rest'),
    ]

    async def handle(self, user: User, message: Message):
        if message_contains(message, 'гатова', 'готово'):
            conn = connection()
            await conn['activity'].insert_one({
                'tg_id': user.id,
                'datetime': user.first_name,
                'location': self.db_user['location'],
            })

            self.next_state = 'waiting-orders'

        if message_contains(message, 'напісаць камандзе', 'написать команде'):
            self.next_state = 'personal-task'

            return {
                'method': 'sendMessage',
                'text': gettext('Here goes information about chat-bot'),
            }

        if message_contains(message, 'адпачынак', 'отдых'):
            await connection().update_one({'tg_id': self.db_user['tg_id']}, {'active': False})
            self.next_state = 'take-rest'


class TakeRestHandler(BaseHandler):
    greeting = gettext_lazy('Push the button to return')
    options = gettext_lazy('Return')

    def handle(self, user: User, message: Message):
        await connection()['users'].update_one({'tg_id': self.db_user['tg_id']}, {'active': True})
        self.next_state = 'personal-task'
        return await get_tg_active_messages(self.db_user)


class WaitingOrdersHandler(BaseHandler):
    """Nothing happens"""

    next_state = None
    greeting = gettext_lazy('Thank you for your activity.')


class CommandHandler(BaseHandler):
    expected = ['start']
    next_state = 'language'

    async def handle(self, user: User, message: Message):
        if message.text == '/start':
            if self.db_user is not None:
                await connection()['users'].update_one({'tg_id': user.id}, {'location': None, 'language': None})

            else:
                await connection()['users'].insert_one({
                    'tg_id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tg_username': user.username,
                })


async def get_tg_active_messages(db_user: dict):
    active_messages = await get_active_messages(db_user['location'], db_user['language'])
    for message in active_messages:
        message['method'] = 'sendMessage'

    return active_messages




