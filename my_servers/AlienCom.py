import argparse
import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server

import uvicorn

# 外星人字符画（纯ASCII，适合cmd）
def print_alien():
    alien = r'''
         .-"      "-.
        /            \
       |              |
       |,  .-.  .-.  ,|
       | )(_o/  \o_)( |
       |/     /\     \|
       (_     ^^     _)
        \__|IIIIII|__/
         | \IIIIII/ |
         \          /
          `--------`
    '''
    print(alien)

# 设置日志
MCP_SERVER_NAME = "AlienCom"
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(MCP_SERVER_NAME)

# 创建FastMCP实例
mcp = FastMCP(MCP_SERVER_NAME)

# 注册一个工具
@mcp.tool()
def summon_alien(signal: str):
    """
    每次调用，打印一只外星人字符画。

    Args:
        signal (str): 任意提示内容。

    Returns:
        str: 返回确认消息。
    """
    logger.info(f"收到召唤外星人的信号: {signal}")
    print("\n收到召唤外星人指令!")
    print_alien()
    return "外星人出现了！"

# 创建Starlette应用

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description='Run AlienCom MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # 绑定SSE请求处理到MCP Server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    print(f"AlienCom 启动，监听 {args.host}:{args.port}")

    uvicorn.run(starlette_app, host=args.host, port=args.port)
