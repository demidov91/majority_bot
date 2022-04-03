import argparse
import sys
import asyncio
import logging

import pymongo

from majority_bot.db import get_connection
from majority_bot.tg_communication import set_webhook


async def setup_db(is_live):
    connection = get_connection(is_live=is_live)
    await connection['users'].create_index('tg_id', unique=True)
    await connection['tasks'].create_index([('language', pymongo.ASCENDING), ('location', pymongo.ASCENDING)])
    await connection['tasks'].create_index([('created_at', pymongo.DESCENDING)])


def run():
    logging.basicConfig(level=logging.INFO)

    argparser = argparse.ArgumentParser()
    argparser.add_argument('command', choices=['setup_db', 'set_webhook'])
    argparser.add_argument('--test', action='store_true')
    argparser.add_argument('--live', action='store_true')
    argparser.add_argument('value', nargs='?')

    args = argparser.parse_args()

    is_live = args.live

    if args.command == 'setup_db':
        asyncio.run(setup_db(is_live=is_live))
        return

    if args.command == 'set_webhook':
        data = asyncio.run(set_webhook(args.value, is_live=is_live, is_admin=False))
        print(data)
        return

    raise ValueError(sys.argv)


if __name__ == '__main__':
    run()