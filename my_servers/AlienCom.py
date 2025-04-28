import argparse
import logging
import hashlib

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server

import uvicorn

# 外星人字符画（纯ASCII，适合cmd）
aliens = [
    r'''
      .-""""-.
     / -   -  \
    |  .-. .- |
    |  \o| |o (
    \     ^    \
     '.  )--'  /
       '-...-'`
    ''',
    r'''
     .-""""-.
    / -   -  \
   |   o   o  |
   |     ^    |
    \  '---' /
     '-.__.-'
    ''',
    r'''
      .-.
     (o o)  
     |=|=|
    __| |__
   /       \
  / /|   |\ \
 /_/ |   | \_\
    _|   |_
   (___|___)
    ''',
    r'''
       .     .
        \.-./
       (o o)
    ooO--(_)--Ooo
      UFO above
    ''',
    r'''
    .-"      "-.
   /            \
  |  .-.    .-.  |
  |  |o|    |o|  |
  |     /\\      |
  \    (__)    /
   '-.        .-'
      '------'
    ''',
    r'''
      ___
    .='   '=.
   /         \
  |           |
  |  .-" "-.  |
  | /       \ |
   \/       \/
   (|  o o  |)
    |   ^   |
    |  '-'  |
    |_______|
 .-'/       '\-.
(_.-'       '-._)
    '''
]

def select_alien(signal: str) -> str:
    hash_bytes = hashlib.md5(signal.encode('utf-8')).digest()
    hash_int = int.from_bytes(hash_bytes, byteorder='big')
    idx = hash_int % len(aliens)
    return aliens[idx]

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
    每次调用，在服务端打印一只外星人字符画。

    Args:
        signal (str): 任意提示内容。

    Returns:
        str: 返回确认消息。
    """
    logger.info(f"收到召唤外星人的信号: {signal}")
    try:
        selected = select_alien(signal)
        print("\n👾 收到召唤外星人指令!")
        print(selected)
        return "外星人出现在了服务端！"
    except Exception as e:
        logger.error(f"召唤外星人失败: {e}")
        return "外星人召唤失败！"

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
    HOST = "0.0.0.0"
    PORT = 8080

    mcp_server = mcp._mcp_server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    print(f"AlienCom 启动，监听 {HOST}:{PORT}")
    uvicorn.run(starlette_app, host=HOST, port=PORT)
