'''
通过 Ollama API 调用模型
官方仓库 https://github.com/ollama/ollama-python
菜鸟教程 https://www.runoob.com/ollama/ollama-python-sdk.html
可用模型列表 https://ollama.com/search
'''

from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='llama3.2', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)