#!/usr/bin/env python3

import asyncio
import uvloop
import telethon
import config
import os
import socks
from pprint import pprint
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

logger.setLevel(logging.DEBUG)


async def auth() -> tuple:
    if os.path.isfile(config.session):
        client = telethon.TelegramClient(config.session)
        await client.connect()
        if client.is_connected():
            logger.debug("Assuming client is connected and good to go, returning...")
            me = await client.get_me()
            return me, client
        else:
            raise Exception('Auth Failed')
    else:
        if config.proxy:
            logger.info("Connecting with proxy...")
            client = telethon.TelegramClient(session=config.session, api_id=config.api_id, api_hash=config.api_hash,
                                             proxy=(socks.SOCKS5, config.proxyHost, config.proxyPort))
        else:
            logger.info("Connecting...")
            client = telethon.TelegramClient(config.session, config.api_id, config.api_hash)
        await client.connect()
        if client.is_connected():
            logger.info("Sending auth code...")
            await client.send_code_request(config.phone_number)
            logger.info("Code sent!")
            me = await client.sign_in(config.phone_number, input('Enter auth code: '))
            return me, client
        else:
            raise Exception('Auth Failed')


async def get_dialogs(client) -> tuple:
    # dialogs = await client.get_dialogs(limit=None)
    logger.info("Getting dialogs...")
    dialogs, entities = await client.get_dialogs()
    return dialogs, entities


async def get_history(client, entries, offset_id=0):
    logger.info("Starting to gather history messages...")
    history = []
    for i in entries:
        logger.debug("Getting history for id " + repr(i.id))
        history.append(await client.get_message_history(entity=i, offset_id=offset_id))
    logger.info("Mission success!")
    return history


async def main():
    me, client = await auth()
    _, entries = await get_dialogs(client)
    pprint(await get_history(client, entries))


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
