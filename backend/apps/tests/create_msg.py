import unittest
import json
from base import app, TORTOISE_ORM
from utils.passwd import get_password_hash
from models import ChatMessage, User
from tortoise import run_async, Tortoise


async def test_save_message():
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    try:
        # 获取管理员用户
        user = await User.get_or_none(username='admin')
            
        # 创建聊天消息
        # content = [{"role": "user", "content": "你好"}]
        await ChatMessage.create(
            user=user,
            content='你好',# json.dumps(content),
            role='user',
        )
        print("聊天消息创建成功！")
        
    except Exception as e:
        print(f"创建消息时出错：{str(e)}")
        raise e
        
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()


async def test_get_messages():
    await Tortoise.init(config=TORTOISE_ORM)
    user = await User.get_or_none(username='admin')
    messages = await ChatMessage.get_his_messages(user, '快回复快回复')
    print(messages)


if __name__ == "__main__":
    # run_async(test_save_message())
    run_async(test_get_messages())
