import unittest
from base import app, TORTOISE_ORM
from utils.passwd import get_password_hash
from models import User
from tortoise import run_async, Tortoise


async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    await User.create(
        username="admin2",
        email="admin2@admin.com",
        hashed_password=get_password_hash("admin123456"),
        is_active=True
    )


run_async(main())
