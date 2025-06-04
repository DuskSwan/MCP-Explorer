from yacs.config import CfgNode as CN

_C = CN()

_C.MODEL = CN()

# _C.MODEL.MARK = "DASHSCOPE" # API KEY name
# _C.MODEL.NAME = "qwen2.5-3b-instruct" 
# _C.MODEL.NAME = "qwen-max-latest"

# _C.MODEL.MARK = "DEEPSEEK"
# _C.MODEL.NAME = "deepseek-chat"
# _C.MODEL.NAME = "deepseek-reasoner" # 不支持tools调用

# _C.MODEL.MARK = "GEMINI"
# _C.MODEL.NAME =  "gemini-2.0-flash"

# _C.MODEL.MARK = "OLLAMA"
# _C.MODEL.NAME = "llama3.2"

_C.MODEL.MARK = "HUNYUAN"
_C.MODEL.NAME = "hunyuan-turbos-latest"

_C.SERVER = CN()
_C.SERVER.ACCESS_PATHS = [
    "D:/GitRepo/MCP-Explorer/my_servers/Timetools.py",
    "D:/GitRepo/MCP-Explorer/my_servers/Unsplash.py",
    "D:/GitRepo/MCP-Explorer/my_servers/BraveSearch.py",
    # "http://localhost:8080/sse", # 使用SSE连接的server前必须先将其启动，并一直挂着
    "http://localhost:8081/mcp", # 使用Streamable HTTP连接的server可以在需要时启动，使用后可以关闭
] 

_C.HOST = CN()
_C.HOST.MAX_MASSAGE_TURNS = 20
    # HOST所记录的message数目上限，由于每次都会将全部message传递给模型，所以过多的message会导致token数过多
    # 注意，除了消息，工具调用也会被记录在message中，所以每新增一轮对话可能增加两条或更多message
# _C.HOST.LOG_FILE = "" 
_C.HOST.LOG_FILE = "logs/.log"
    # 日志保存路径, 留空则将日志输出到控制台
_C.HOST.NEED_USER_CONFIRM = False 
    # 调用工具时是否需要用户确认

def get_cfg_defaults():
    """Get a yacs CfgNode object with default values for my_project."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    return _C.clone()
