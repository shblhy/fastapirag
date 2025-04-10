import copy
import json
import logging
import requests
from openai import OpenAI
from config import conf
logger = logging.getLogger('task')

CHAT_MODELS = {
    'deepseek-llm-67b-chat':
        {'api_key': conf.aimlapi_api_key, 'base_url': "https://api.aimlapi.com/v1",
         'model': 'deepseek-ai/deepseek-llm-67b-chat'},
    'deepseek-chat': {
        'api_key': conf.deepseek_api_key, 'base_url': "https://api.deepseek.com",
         'model': 'deepseek-chat'
    },
    'deepseek-v3-volcengine': { # 火山引擎/字节跳动 deepseek
        'api_key': conf.toutiao_api_key, 'base_url': "https://ark.cn-beijing.volces.com/api/v3",
         'model': "ep-20250214153206-rjxkd", # 'deepseek-v3'
    },
    'deepseek-r1-volcengine': { # 火山引擎/字节跳动 deepseek
        'api_key': conf.toutiao_api_key, 'base_url': "https://ark.cn-beijing.volces.com/api/v3",
         'model': "ep-20250307112429-p2bnk", # 'deepseek-v3' #
    },
}
# DEFAULT_ENGINE = 'deepseek-v3-volcengine'
DEFAULT_ENGINE = 'local-gemma3:12b'
# 'local-deepseek-r1:32b'


def gen_messages(prompt: str):
    return [{"role": "user", "content": prompt}]


def get_completion(prompt, engine=DEFAULT_ENGINE, stream=False):
    if engine.startswith('local-'):
        return get_completion_local(prompt, engine.replace('local-', ''))
    if engine not in CHAT_MODELS:
        raise Exception('不可用的模型')
    model_info = copy.copy(CHAT_MODELS[engine])
    model = model_info.pop('model')
    client = OpenAI(**model_info)
    messages = gen_messages(prompt) if type(prompt) is not list else prompt
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, #0.3,
        stream=stream,
    )
    if not stream:
        optimized_description = response.choices[0].message.content.strip()
        logger.info(optimized_description)
        return optimized_description
    return response


def get_completion_local(prompt, model='gemma3:12b'):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {'model': model, 'prompt': prompt, 'stream': False}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        try:
            return response.json()['response']
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error:{response.status_code}  {response.text}")
            return
    else:
        logger.error(f"Error:{response.status_code}  {response.text}")
        return
