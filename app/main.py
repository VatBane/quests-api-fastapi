from fastapi import FastAPI

from config import TITLE
from v1.main import v1_app

app = FastAPI(title=TITLE)


app.mount('/v1', v1_app)
