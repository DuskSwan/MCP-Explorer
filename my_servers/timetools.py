import argparse

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

import logging
import uvicorn

from datetime import datetime
import pytz

MCP_SERVER_NAME = "time_mcp_server"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool()
def get_time():
    """
    获取当前时间

    Returns:
        str: 当前时间字符串 (ISO 8601 格式)
    """
    current_time = datetime.now().isoformat()
    return current_time

@mcp.tool()
def transform_timezone(source_time: str, timezone: str) -> str:
    """
    将源时间转换为指定时区的时间

    Args:
        source_time (str): 源时间字符串,格式为 ISO 8601，例如: "2023-10-01T12:00:00+00:00"
        timezone (str): 时区字符串,例如 "Asia/Shanghai" 或 "America/New_York"，可用pytz.all_timezones查看
            参考 pytz 时区列表: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

    Returns:
        str: 转换后的时间字符串
    """
    try:
        # 解析源时间字符串为 datetime 对象
        source_time_dt = datetime.fromisoformat(source_time)
    except ValueError:
        logger.error(f"Invalid source time format: {source_time}")
        return "Invalid source time format"

    # 获取指定时区对象
    try:
        target_timezone = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        logger.error(f"Unknown timezone: {timezone}")
        return "Unknown timezone"

    # 转换为目标时区的时间
    target_time_dt = source_time_dt.astimezone(target_timezone)

    # 格式化为 ISO 8601 字符串
    target_time_str = target_time_dt.isoformat()
    return target_time_str
    

def create_starlette_app(mcp_server: Server) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
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
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def run_server(mode='stdio'):
    """Run the MCP server."""
    if mode == 'stdio':
        mcp.run(transport="stdio")
    elif mode == 'sse':
        mcp_server = mcp._mcp_server

        PORT = 8000
        print(f"Starting SSE server on port {PORT}...")

        parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
        parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
        parser.add_argument('--port', type=int, default=PORT, help='Port to listen on')
        args = parser.parse_args()

        # Bind SSE request handling to MCP server
        starlette_app = create_starlette_app(mcp_server)

        uvicorn.run(starlette_app, host=args.host, port=args.port)

if __name__ == "__main__":
    # run_server(mode='sse')
    run_server(mode='stdio')