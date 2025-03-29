from fastapi import FastAPI

from config import TITLE


v1_app = FastAPI(title=TITLE, version="1")
