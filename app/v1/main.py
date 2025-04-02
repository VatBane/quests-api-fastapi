from fastapi import FastAPI

from config import TITLE
from v1.routers.quests.router import quest_router

v1_app = FastAPI(title=TITLE, version="1",
                 openapi_url='/openapi.json',
                 docs_url='/docs')


v1_app.include_router(quest_router, prefix='/quests')
