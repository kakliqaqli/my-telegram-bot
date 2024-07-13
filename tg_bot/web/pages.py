import os

import aiohttp_jinja2
from aiohttp import web


@aiohttp_jinja2.template('create_order.html')
async def create_order(request: web.Request):
    return {"api_send_order_url": os.environ.get('TELEGRAM_BOT_API_URL') + 'start_search/',}
