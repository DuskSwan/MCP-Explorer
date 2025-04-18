# MCP-Explorer

本项目意在学习创建一个MCP客户端，要实现的内容包括

- 通过API调用远端大模型
- 本地部署大模型
- 建立MCP客户端
- 创建一些本地MCP服务器供使用

## 相关库

### 通用

dotenv: 加载.env文件以获取API（环境变量）

### Gemini

使用 Python 3.9 及更高版本时，请使用以下 pip 命令安装 google-genai 软件包

```bash
pip install -q -U google-genai
```

### hugging face

需要transform和torch

### Ollama

需要下载Ollama客户端，以及

```bash
pip install ollama
```

### OpenAI

很多模型都提供了与 OpenAI 兼容的 API 格式，可以使用 OpenAI SDK 来访问，这需要的库是

```bash
pip install openai
```

## 参考

[Gemini API 使用入门](https://ai.google.dev/gemini-api/docs/text-generation?hl=zh-cn)

[Ollama Python 使用](https://www.runoob.com/ollama/ollama-python-sdk.html)
