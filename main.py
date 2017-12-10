#!/usr/bin/env python3

import asyncio
import uvloop
import telethon
import config
import os
import socks
from pprint import pprint
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
authLog = logging.StreamHandler()
authLog.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
authLog.setFormatter(formatter)
logger.addHandler(authLog)


async def auth() -> tuple:
    if os.path.isfile(config.session):
        client = telethon.TelegramClient(config.session)
        await client.connect()
        if client.is_connected():
            logger.debug("Assuming client is connected and good to go, returning.")
            me = await client.get_me()
            return me, client
        else:
            raise Exception('Auth Failed')
    else:
        if config.proxy:
            logger.debug("Connecting with proxy...")
            client = telethon.TelegramClient(session=config.session, api_id=config.api_id, api_hash=config.api_hash,
                                             proxy=(socks.SOCKS5, config.proxyHost, config.proxyPort))
        else:
            logger.debug("Connecting...")
            client = telethon.TelegramClient(config.session, config.api_id, config.api_hash)
        await client.connect()
        if client.is_connected():
            logger.debug("Sending auth code...")
            await client.send_code_request(config.phone_number)
            logger.debug("Code sent!")
            me = await client.sign_in(config.phone_number, input('Enter auth code: '))
            return me, client
        else:
            raise Exception('Auth Failed')


async def get_dialogs(client) -> tuple:
    # dialogs = await client.get_dialogs(limit=None)
    logger.debug("Getting dialogs...")
    dialogs, entities = await client.get_dialogs()
    return dialogs, entities


async def get_history(client, entries, offset_id=0):
    logger.debug("Starting to gather history messages...")
    history = []
    for i in entries:
        logger.debug("Getting history for id " + repr(i.id))
        history.append(await client.get_message_history(entity=i, offset_id=offset_id))
    return history


async def main():
    me, client = await auth()
    _, entries = await get_dialogs(client)
    pprint(await get_history(client, entries))


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
