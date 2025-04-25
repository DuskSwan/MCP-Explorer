'''
通过 Ollama API 调用模型
官方仓库 https://github.com/ollama/ollama-python
菜鸟教程 https://www.runoob.com/ollama/ollama-python-sdk.html
可用模型列表 https://ollama.com/search

需要下载Ollama客户端，以及安装库
```bash
pip install ollama
```

顺带一提，Ollama下载时默认安装到C盘，指定下载路径需要安装时在命令行中给出参数
OllamaSetup.exe /DIR="d:\some\location"

另外，Ollama的模型也默认安装在C盘，指定模型下载路径配置环境变量
OLLAMA_MODELS=D:\some\location\models
'''

from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='llama3.3', messages=[
  {
    'role': 'user',
    'content': 'Introduce yourself.',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
# print(response)

'''
print response's structure, it will be a ChatResponse object which is similar to openai's ChatCompletion object.

model='llama3.2' 
created_at='2025-04-21T02:07:02.7276296Z' 
done=True 
done_reason='stop' 
total_duration=16946545200 
load_duration=13800649700 
prompt_eval_count=31 
prompt_eval_duration=349836700 
eval_count=284 
eval_duration=2793554700 
message=Message(
  role='assistant', 
  content="The sky appears blue because of a phenomenon called Rayleigh scattering, named after the British physicist Lord Rayleigh. He discovered that when sunlight enters Earth's atmosphere, it encounters tiny molecules of gases such as nitrogen and oxygen.\n\nThese molecules scatter the light in all directions, but they scatter shorter (blue) wavelengths more than longer (red) wavelengths. This is known as Rayleigh scattering. As a result, the blue light is dispersed throughout the atmosphere, giving the sky its blue color.\n\nHere's a simplified explanation:\n\n1. Sunlight enters Earth's atmosphere and contains all the colors of the visible spectrum.\n2. The shorter wavelengths of light (like blue and violet) are scattered more than the longer wavelengths (like red and orange).\n3. This scattered light is then dispersed throughout the atmosphere in all directions.\n4. Our eyes see this scattered light, which appears as a blue color to us.\n\nIt's worth noting that the sky can appear different colors at different times of day and in different atmospheric conditions. For example:\n\n* During sunrise and sunset, the sky can take on hues of red, orange, and pink due to the scattering of light by atmospheric particles.\n* On cloudy days or during dust storms, the sky can appear gray or hazy due to the scattering of light by larger particles.\n\nHowever, under clear conditions with minimal atmospheric interference, the blue color of the sky is usually the most visible.", 
  images=None, 
  tool_calls=None
)
'''