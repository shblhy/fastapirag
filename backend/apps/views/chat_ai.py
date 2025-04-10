import time
import asyncio
import logging
import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from utils.openai.chat import get_completion
from utils.auth import get_current_user
from models import User, ChatMessage

router = APIRouter()
logger = logging.getLogger('default')
# logger.setLevel(logging.DEBUG)


@router.get("/ping")
async def ping():
    time.sleep(1)
    return {"pong": True}


async def status_event_generator(response, callback):
    collected_chunks = []
    for chunk_ in response:
        chunk = chunk_.choices[0].delta.content if type(chunk_).__name__ == 'ChatCompletionChunk' else ''
        # logger.debug(chunk)
        if chunk:
            collected_chunks.append(str(chunk))
            yield chunk
        await asyncio.sleep(0.001)
    res = ''.join(collected_chunks)
    callback(res)


class Item(BaseModel):
    prompt: str
    with_his: bool = True


@router.post("/v1/chat/completions")
async def gen_text_v1(item: Item, current_user: User = Depends(get_current_user)):
    prompt = item.prompt

    await ChatMessage.create(
        user=current_user,
        content=prompt,
        with_his=item.with_his,
        role='user',
    )

    async def after_reply(reply):
        logger.debug(reply)
        await ChatMessage.create(
            user=current_user,
            content=reply,
            role='assistant',
        )

    messages = await ChatMessage.get_his_messages(current_user, item.prompt) if item.with_his else prompt
    event_generator = status_event_generator(get_completion(messages, engine='deepseek-v3-volcengine', stream=True), callback=after_reply)
    return EventSourceResponse(event_generator, media_type="application/x-ndjson")


@router.post("/easy_chat")
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
