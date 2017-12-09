#!/usr/bin/env python3

import asyncio
import uvloop
import telethon
import config
import os
import socks
from pprint import pprint
import logging


async def auth() -> tuple:
    authLog = logging.StreamHandler()
    authLog.setLevel(logging.DEBUG)
    if os.path.isfile(config.session):
        client = telethon.TelegramClient(config.session)
        if client.is_connected():
            me = await client.get_me()
            return me, client
        else:
            raise Exception('Auth Failed')
    else:
        if config.proxy:
            client = telethon.TelegramClient(config.session, config.api_id, config.api_hash,
                                             (socks.SOCKS5, config.proxyHost, config.proxyPort))
        else:
            client = telethon.TelegramClient(config.session, config.api_id, config.api_hash,
                                             (socks.SOCKS5, config.proxyHost, config.proxyPort))
        await client.connect()
        if client.is_connected():
            await client.send_code_request(config.phone_number)
            me = await client.sign_in(config.phone_number, input('Enter auth code: '))
            return me, client
        else:
            raise Exception('Auth Failed')


async def get_dialogs(client):
    #dialogs = await client.get_dialogs(limit=None)

    dialogs = await client.get_dialogs()
    return dialogs


async def main():
    me, client = await auth()
    pprint(get_dialogs(client))

if __name__ == '__main__':
    logging.getLogger(__name__)
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())