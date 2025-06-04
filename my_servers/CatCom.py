import logging
import hashlib

import uvicorn
from mcp.server.fastmcp import FastMCP

# 小猫字符画（纯ASCII，适合在终端打印）
cats = [
    r'''
 /\_/\ 
( o.o )
 > ^ <
''',
    r'''
  |\_/|  
  / @ @ \ 
 ( > º < )
  `»»x««´
  /  O  \
''',
    r'''
      |\      _,,,---,,_
ZZZzz /,`.-'`'    -.  ;-;;,_
     |,4-  ) )-,_..;\ (  `'-'
    '---''(_/--'  `-'\_)
''',
    r'''
 ,_     _
 |\\_,-~/
 / _  _ |    ,--.
(  @  @ )   / ,-'
 \  _T_/-._( (
 /         `. \
|         _  \ |
 \ \ ,  /      |
  || |-_\__   /
 ((_/`(____,-'
''',
]


def select_cat(signal: str) -> str:
    """根据输入的 signal 生成 hash 并选取一只小猫 ASCII 画。"""
    hash_bytes = hashlib.md5(signal.encode("utf-8")).digest()
    hash_int = int.from_bytes(hash_bytes, byteorder="big")
    idx = hash_int % len(cats)
    return cats[idx]


# 设置日志
MCP_SERVER_NAME = "CatCom"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(MCP_SERVER_NAME)

# 创建 FastMCP 实例，启用 Streamable HTTP 模式
mcp = FastMCP(MCP_SERVER_NAME, json_response=False, stateless_http=False)


@mcp.tool()
def summon_cat(signal: str) -> str:
    """
    每次调用，在服务端打印一只小猫字符画。

    Args:
        signal (str): 任意提示内容。

    Returns:
        str: 返回确认消息。
    """
    logger.info(f"收到召唤小猫的信号: {signal}")
    try:
        selected = select_cat(signal)
        print("\n😺 收到召唤小猫指令!")
        print(selected)
        return "小猫出现在了服务端！"
    except Exception as e:
        logger.error(f"召唤小猫失败: {e}")
        return "小猫召唤失败！"


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8081

    print(f"CatCom 启动，监听 {HOST}:{PORT}，使用 Streamable HTTP 连接方式")
    uvicorn.run(mcp.streamable_http_app, host=HOST, port=PORT)
