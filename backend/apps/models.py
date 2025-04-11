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


# class Theme(Model):
#     id = fields.IntField(pk=True)
#     user = fields.ForeignKeyField('models.User', related_name='themes')
#     title = fields.CharField(max_length=100)  # 主题标题，默认使用第一条用户消息的前N个字符
#     created_at = fields.DatetimeField(auto_now_add=True)
#     updated_at = fields.DatetimeField(auto_now=True)  # 最后一次对话时间
#     is_active = fields.BooleanField(default=True)  # 是否有效（支持软删除）

#     class Meta:
#         table = "themes"

#     @classmethod
#     async def create_with_first_message(cls, user, first_message):
#         """
#         创建新主题，并根据第一条消息生成标题
#         """
#         # 使用第一条消息的前20个字符作为标题
#         title = first_message[:20] + ('...' if len(first_message) > 20 else '')
#         return await cls.create(user=user, title=title)


class ChatMessage(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='messages')
    # theme = fields.ForeignKeyField('models.Theme', related_name='messages')  # 关联到主题
    content = fields.TextField()
    role = fields.CharField(max_length=10)  # 'user' or 'assistant'
    with_his = fields.BooleanField(default=False)    # 构造Messages是否携带历史，测试时不携带开发方便些
    # batch_id = fields.IntField()  # 如果要支持多轮对话，增加此字段 方便起见不在这里继续开发了。
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"

    # @classmethod
    # async def get_theme_messages(cls, theme_id: int):
    #     """
    #     获取指定主题的所有对话消息
    #     按时间顺序返回消息列表
    #     """
    #     messages = await cls.filter(theme_id=theme_id).order_by('created_at')
    #     return [{"role": msg.role, "content": msg.content} for msg in messages]

    # @classmethod
    # async def get_recent_messages(cls, theme_id: int, limit: int = 10):
    #     """
    #     获取指定主题的最近N条消息
    #     用于构建上下文
    #     """
    #     messages = await cls.filter(theme_id=theme_id).order_by('-created_at').limit(limit)
    #     messages_list = [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]
    #     return messages_list

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
