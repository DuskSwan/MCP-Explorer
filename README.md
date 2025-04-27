# MCP-Explorer

本项目意在学习创建一个MCP客户端，要实现的内容包括

- 通过API调用远端大模型
- 本地部署大模型
- 建立MCP客户端
- 创建一些本地MCP服务器供使用

## 依赖环境

使用`pip install -r requirements.txt`或者`uv add -r requirements.txt`安装所需环境

## 结构说明

host.py 是我为自己搭建的MCP host，里面实际上是一个Client负责接入本地（将来或许支持远端）的Server。其配置文件为config.py，模型与一些功能选择需要通过修改config.py来进行。

LLM_examples下是各个模型的调用方法。

my_servers下是我自己写的MCP server脚本。

client_examples下是MCP client的示例。

## 使用方法

在项目目录下创建.env文件，在其中设置API

```txt
UNSPLASH_API='xxx'

GEMINI_API_KEY="xxx"
DASHSCOPE_API_KEY="xxx" 
DEEPSEEK_API_KEY="xxx"
OLLAMA_API_KEY='ollama'
```

UNSPLASH是获取壁纸的工具。
