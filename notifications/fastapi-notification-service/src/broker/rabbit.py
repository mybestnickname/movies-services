from typing import Optional
from aio_pika import Channel

rabbit_channel: Optional[Channel] = None


async def get_rabbit_chanel() -> rabbit_channel:
    return rabbit_channel
