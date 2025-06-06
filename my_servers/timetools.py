from loguru import logger

from fastmcp import FastMCP

from datetime import datetime
import pytz

mcp = FastMCP("time_mcp_server")

@mcp.tool()
def get_current_time():
    """
    get current time in ISO 8601 format

    Returns:
        str: time string in ISO 8601 format
    """
    current_time = datetime.now().isoformat()
    return current_time

@mcp.tool()
def transform_timezone(source_time: str, timezone: str) -> str:
    """
    transform the source time string to the target timezone

    Args:
        source_time (str): source time string in ISO 8601 format, e.g. "2023-10-01T12:00:00"
        timezone (str): target timezone string, e.g. "Asia/Shanghai", "America/New_York"
            pytz time zone list: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

    Returns:
        str: transformed time string in ISO 8601 format
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
    

if __name__ == "__main__":
    # mcp.run(
    #     transport="sse",
    #     host="0.0.0.0",
    #     port=8000,
    #     path='/mcp',
    # )
    mcp.run(transport="stdio")