import os
import sys
import uvicorn
import logging
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(BASE_DIR)

from base import app
from views.user_auth import router as auth_router
from views.chat_ai import router
app.include_router(auth_router)
app.include_router(router)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn")


def start_webserver():
    uvicorn.run("base:app", host="0.0.0.0", port=8798, reload=True)


if __name__ == '__main__':
    start_webserver()
