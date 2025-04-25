'''
deepseek系列模型的使用
获取API与调用示例 https://api-docs.deepseek.com/zh-cn/
模型价格见 https://api-docs.deepseek.com/zh-cn/quick_start/pricing/
'''
import os
from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

from openai import OpenAI

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

'''
print response, it will be a ChatCompletion object.
The object contains the following structure:

ChatCompletion(
    id='e5f9f99e-67b1-4e25-93e2-1d154a87d7e6', 
    choices=[
        Choice(
            finish_reason='stop', 
            index=0, 
            logprobs=None, 
            message=ChatCompletionMessage(
                content='Hello! How can I assist you today? ', 
                refusal=None, 
                role='assistant', 
                annotations=None, 
                audio=None, 
                function_call=None, 
                tool_calls=[
                    ChatCompletionMessageToolCall(
                        id='call_0_a2fda85a-7b8c-4b4e-afef-603481ec00ab',
                        function=Function(
                            arguments='{"image_url":"C:\\Users\\kyland\\Desktop\\abstract_blue_art.jpg"}', 
                            name='show_img'
                        ),
                        type='function',
                        index=0
                    )
                ]
            )
        )
    ], 
    created=1745199811, 
    model='deepseek-chat', 
    object='chat.completion', 
    service_tier=None, 
    system_fingerprint='fp_3d5141a69a_prod0225', 
    usage=CompletionUsage(
        completion_tokens=11, 
        prompt_tokens=9, 
        total_tokens=20, 
        completion_tokens_details=None, 
        prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0), 
        prompt_cache_hit_tokens=0, 
        prompt_cache_miss_tokens=9
    )
)
'''