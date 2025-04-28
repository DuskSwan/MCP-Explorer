from yacs.config import CfgNode as CN

_C = CN()

_C.MODEL = CN()

# _C.MODEL.MARK = "DASHSCOPE" # API KEY name
# _C.MODEL.NAME = "qwen2.5-3b-instruct" 
# _C.MODEL.NAME = "qwen-max-latest"

_C.MODEL.MARK = "DEEPSEEK"
_C.MODEL.NAME = "deepseek-chat"
# _C.MODEL.NAME = "deepseek-reasoner" # 不支持tools调用

# _C.MODEL.MARK = "GEMINI"
# _C.MODEL.NAME =  "gemini-2.0-flash"

# _C.MODEL.MARK = "OLLAMA"
# _C.MODEL.NAME = "llama3.2"

_C.SERVER = CN()
_C.SERVER.LOCAL_SCRIPTS = [
    "D:/GitRepo/MCP-Explorer/my_servers/Timetools.py",
    # "D:/GitRepo/MCP-Explorer/my_servers/Unsplash.py",
    # "D:/GitRepo/MCP-Explorer/my_servers/BraveSearch.py",
    
] # absolute path of local scripts

_C.HOST = CN()
_C.HOST.MAX_MASSAGE_TURNS = 30 
  # max turns of messages in the conversation
# _C.HOST.LOG_FILE = "" 
_C.HOST.LOG_FILE = "logs/.log"
  # log file name, or "" to print to console
_C.HOST.NEED_USER_CONFIRM = False 
  # whether to need user confirm when using tools

def get_cfg_defaults():
  """Get a yacs CfgNode object with default values for my_project."""
  # Return a clone so that the defaults will not be altered
  # This is for the "local variable" use pattern
  return _C.clone()
