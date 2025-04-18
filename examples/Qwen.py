'''
Qwen系列模型的使用
获取API key见 https://help.aliyun.com/zh/model-studio/get-api-key?spm=a2c4g.11186623.0.0.3c726f53PvOJcs
模型价格见 https://help.aliyun.com/zh/model-studio/models
官方使用示例见 https://help.aliyun.com/zh/model-studio/text-generation?spm=a2c4g.11186623.0.0.190d1d1cfxiGi1#bfae0adf88aa2
'''

import os
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

print(f"DASHSCOPE_API_KEY: {DASHSCOPE_API_KEY}")

try:
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': '你是谁？'}
            ]
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"错误信息：{e}")
    print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")

# client = OpenAI(
#     api_key=DASHSCOPE_API_KEY,
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )

# completion = client.chat.completions.create(
#     # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
#     model="qwen-plus",
#     messages=[
#         {'role': 'system', 'content': 'You are a helpful assistant.'},
#         {'role': 'user', 'content': '你是谁？'}
#         ]
# )
# print(completion.choices[0].message.content)