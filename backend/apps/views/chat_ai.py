import time
import asyncio
import logging
import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from utils.openai.chat import get_completion
from utils.auth import get_current_user
from models import User, ChatMessage    #, Theme

router = APIRouter()
logger = logging.getLogger('default')
logger.setLevel(logging.INFO)


@router.get("/ping")
async def ping():
    time.sleep(1)
    return {"pong": True}


async def status_event_generator(response, callback):
    collected_chunks = []
    try:
        for chunk_ in response:
            chunk = chunk_.choices[0].delta.content if type(chunk_).__name__ == 'ChatCompletionChunk' else ''
            # logger.debug(chunk)
            if chunk:
                collected_chunks.append(str(chunk))
                # 使用正确的 SSE 格式
                yield {
                    "event": "message",
                    "data": chunk
                }
            await asyncio.sleep(0.05)
        
        # 发送完成标记
        yield {
            "event": "done",
            "data": "[DONE]"
        }
        
        # 处理完整响应
        res = ''.join(collected_chunks)
        await callback(res)
        
    except Exception as e:
        logger.error(f"Error in stream: {str(e)}")
        yield {
            "event": "error",
            "data": str(e)
        }


class Item(BaseModel):
    prompt: str
    with_his: bool = True
    # theme: int = None


@router.get("/v1/chat/completions")
async def gen_text_v1(prompt, with_his=True, current_user: User = Depends(get_current_user)):
    # prompt = item.prompt  # 改成了form表单中的参数，以适应前端打字机效果所需的fetch EventSource
    # with_his = item.with_his
    await ChatMessage.create(
        user=current_user,
        content=prompt,
        with_his=with_his,
        role='user',
    )

    async def after_reply(reply):
        logger.debug(reply)
        await ChatMessage.create(
            user=current_user,
            content=reply,
            role='assistant',
        )
    # if item.theme:
    #     theme = await Theme.get(item.theme)
    #     messages = await ChatMessage.get_theme_messages(theme)
    # else:
    #     theme = await Theme.create_with_first_message(current_user, item.prompt)
    #     messages = await ChatMessage.get_his_messages(current_user, item.prompt) if item.with_his else item.prompt
    messages = await ChatMessage.get_his_messages(current_user, prompt) if with_his else prompt
    event_generator = status_event_generator(
        get_completion(messages, engine='deepseek-v3-volcengine', stream=True), 
        callback=after_reply
    )
    
    return EventSourceResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/easy_chat")
async def easy_text(item: Item, current_user: User = Depends(get_current_user)):
    prompt = item.prompt
    await ChatMessage.create(
        user=current_user,
        content=json.dumps(item.prompt),
        with_his=item.with_his,
        role='user',
    )
    messages = await ChatMessage.get_his_messages(current_user, item.prompt) if item.with_his else prompt
    res = get_completion(messages, engine='deepseek-v3-volcengine', stream=False)
    await ChatMessage.create(
        user=current_user,
        content=res,
        role='assistant',
    )
    return {"data": res}


@router.get("/v1/chat/history")
async def get_chat_history(current_user: User = Depends(get_current_user)):
    # 获取最近的聊天记录，按时间倒序排列
    messages = await ChatMessage.filter(user=current_user).order_by('-created_at').limit(50)
    messages.reverse()  # 转换为正序，便于显示
    
    # 将消息按对话分组
    chat_groups = []
    current_group = []
    
    for msg in messages:
        current_group.append({
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        # 每两条消息（用户+助手）形成一组对话
        if len(current_group) == 2:
            chat_groups.append(current_group)
            current_group = []
    
    # 处理可能的剩余消息
    if current_group:
        chat_groups.append(current_group)
    
    return {"history": chat_groups}
