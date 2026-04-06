from aiogram import BaseMiddleware

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool):
        self.pool = pool

    async def __call__(self, handler, event, data):
        data["pool"] = self.pool
        return await handler(event, data)