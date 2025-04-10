from tortoise import fields
from tortoise.models import Model
from datetime import datetime


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "users"


class ChatMessage(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='messages')
    content = fields.TextField()
    role = fields.CharField(max_length=10)  # 'user' or 'assistant'
    with_his = fields.BooleanField(default=False)    # 构造Messages是否携带历史，测试时不携带开发方便些
    # batch_id = fields.IntField()  # 如果要支持多轮对话，增加此字段 方便起见不在这里继续开发了。
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"

    @classmethod
    async def get_his_messages(cls, user, prompt):
        his_msgs = await ChatMessage.filter(user=user).order_by('-id')[:10]
        his_msgs.reverse()
        res = []
        first_chat = [i for i in his_msgs if i.role == 'user'][0]
        index_begin = his_msgs.index(first_chat)
        for i in his_msgs[index_begin:]:
            res.append({"role": i.role, "content": i.content})
        res.append({"role": i.role, "content": prompt})
        return res
