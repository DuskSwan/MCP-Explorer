# TimeServer

这是一个提供与时间相关的工具的MCP Server。

创建该Server的目的主要是测试通过SSE连接MCP Client与Server，脚本会启动MCP服务器，并创建一个Starlette应用，监听SSE请求。

所需环境：

```bash
uv add mcp[cli]
```
