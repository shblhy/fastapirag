from utils.unittest import TestCase
from utils.siliconflow.chat import MODELS, gen_text
from exlib.widgets.decorators import func_timer
from openai import OpenAI
from config import conf
from utils.openai.chat import get_completion


class ChatApiTest(TestCase):
    @func_timer
    def test_chat_deepseek_aiml(self):
        prompt = '你好，自我介绍一下'
        engine = 'deepseek-llm-67b-chat'
        resp = get_completion(prompt, engine, stream=False)
        print(resp)

    @func_timer
    def test_chat_deepseek_chat(self):
        prompt = '你好，自我介绍一下'
        engine = 'deepseek-chat'
        resp = get_completion(prompt, engine, stream=False)
        print(resp)

    @func_timer
    def test_chat_deepseek_olcengine(self):
        prompt = '你好，自我介绍一下'
        engine = 'deepseek-v3-volcengine'
        resp = get_completion(prompt, engine, stream=False)
        print(resp)
