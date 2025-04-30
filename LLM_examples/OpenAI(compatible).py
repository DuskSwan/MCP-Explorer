'''
很多模型都提供了与 OpenAI 兼容的 API 格式，可以使用 OpenAI SDK 来访问，这需要的库是
pip install openai
'''

import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


def deepseek():
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY, 
        base_url="https://api.deepseek.com"
        )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)
    print(response.choices[0].message.tool_calls)

def qwen():
    '''
    Qwen系列模型的使用
    获取API key见 https://help.aliyun.com/zh/model-studio/get-api-key?spm=a2c4g.11186623.0.0.3c726f53PvOJcs
    模型价格见 https://help.aliyun.com/zh/model-studio/models
    官方使用示例见 https://help.aliyun.com/zh/model-studio/text-generation?spm=a2c4g.11186623.0.0.190d1d1cfxiGi1#bfae0adf88aa2
    '''
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    try:
        client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        completion = client.chat.completions.create(
            # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen-turbo",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': '你是谁？'}
                ]
        )
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"错误信息：{e}")
        print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")

'''回复结构：
ChatCompletion(
    id='chatcmpl-47bdf91a-960b-94cc-a9d1-ce9ca1b1c086', 
    choices=[
        Choice(
            finish_reason='stop', 
            index=0, 
            logprobs=None, 
            message=ChatCompletionMessage(
                content='我是语言模型。我被设计用来生成各种各样的文本，包括回答问题、创作故事、编写代码等等。有什么可以帮助你的吗？', 
                refusal=None, 
                role='assistant', 
                annotations=None, 
                audio=None, 
                function_call=None, 
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id='call_0_a2fda85a',
                        function=Function(
                            arguments='{"image_url":"C:\\Users\\User\\Desktop\\abstract_blue_art.jpg"}', 
                            name='show_img'
                        ),
                        type='function',
                        index=0
                    )
                ]
            )
        )
    ], 
    created=1745200371, 
    model='qwen2.5-3b-instruct', 
    object='chat.completion', 
    service_tier=None, 
    system_fingerprint=None, 
    usage=CompletionUsage(
        completion_tokens=52, 
        prompt_tokens=22, 
        total_tokens=74, 
        completion_tokens_details=None, 
        prompt_tokens_details=None
    )
)
'''

def hunyuan():
    '''
    Hunyuan系列模型的使用
    获取API key见 https://console.cloud.tencent.com/hunyuan/start
    模型价格见 https://cloud.tencent.com/document/product/1729/97731
    官方使用示例见 https://cloud.tencent.com/document/product/1729/111007
    '''
    pass

if __name__ == "__main__":
    qwen()
    # deepseek()