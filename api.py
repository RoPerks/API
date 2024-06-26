import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class Database():

    async def create_db_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                host="DEPRECATED",
                database="RoPerks",
                user="postgres",
                password="e0Hu7AgF*24o7Hf$H&3o",
            )
        except asyncpg.exceptions.InvalidAuthorizationSpecificationError:
            self.pool = await asyncpg.create_pool(
                host="localhost",
                database="RoPerks",
                user="postgres",
                password="e0Hu7AgF*24o7Hf$H&3o",
            )

    async def get_nitro_status(self, api_key, roblox_id):
        guild_id = await self.pool.fetchval(f'SELECT guild_id FROM guild_dump WHERE api_key=$1', api_key)
        if not guild_id:
            return JSONResponse(status_code=403, content={'detail': 'api-key was invalid.'})
        discord_id = await self.pool.fetchval(f'SELECT discord_id FROM user_data WHERE guild_id=$1 AND roblox_id=$2', guild_id, roblox_id)
        if discord_id:
            return {"has_nitro": True}
        return {"has_nitro": False}


def create_app():

    app = FastAPI()
    db = Database()

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        request.state.pool = db.pool
        response = await call_next(request)
        return response

    @app.on_event("startup")
    async def startup():
        await db.create_db_pool()

    @app.get("/nitro_status/{roblox_id}")
    async def nitro_status(request: Request, roblox_id: int, api_key: str):

        nitro_status = await db.get_nitro_status(api_key, roblox_id)
        return nitro_status

    return app

app = create_app()
