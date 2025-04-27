# MCP-Explorer

本项目意在学习创建一个MCP客户端，要实现的内容包括

- 通过API调用远端大模型
- 本地部署大模型
- 建立MCP客户端
- 创建一些本地MCP服务器供使用

## 依赖环境

使用`pip install -r requirements.txt`或者`uv add -r requirements.txt`安装所需环境

## 结构说明

- host.py: 自己搭建的MCP host，里面实际上是一个Client负责接入本地（将来或许支持远端）的Server。其配置文件为config.py，模型与一些功能选择需要通过修改config.py来进行。

- LLM_examples: 各个模型的调用方法。
  - Gemini: Google Gemini系列模型。
  - HuggingFace: Hugging Face的开源模型。（不支持OpenAI SDK调用，暂不考虑）
  - OpenAI: 兼容OpenAI API 格式的模型，目前包括Deepseek和Qwen系列。
  - Ollama: Ollama上可用的模型。

- my_servers: 自己写的MCP Server脚本。
  - timetools: 提供时间查询和时区转换功能。
  - Unsplash: 提供壁纸查询、壁纸下载和设置壁纸功能。

- client_examples: 自己写的MCP Client脚本。
  - stdio_client: 以stdio为输入输出方式，在本地启动服务脚本。
  - sse_client: 以sse为输入输出方式，通过指定的端口连接到已经启动的服务。想要试用的话，将my_servers/timetools中的运行方式由`run_server(mode='stdio')`改成`run_server(mode='sse', port=8000)`然后运行，再运行`uv run sse_client.py http://localhost:8000/sse`即可。

## 使用方法

在项目目录下创建.env文件，在其中设置API

```txt
UNSPLASH_API="xxx"
BRAVE_API_KEY="xxx"

GEMINI_API_KEY="xxx"
DASHSCOPE_API_KEY="xxx" 
DEEPSEEK_API_KEY="xxx"
OLLAMA_API_KEY="ollama"
```

Unsplash是获取壁纸的工具，申请Unsplash的API key参见[这里](https://unsplash.com/documentation#getting-started)。

Brave search是一个搜索工具，申请API点击[这里](https://brave.com/search/api/)。

Ollama用于本地部署大模型，并不需要API key，但为了符合OpenAI调用规则还是给一个字符串。
