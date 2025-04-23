from yacs.config import CfgNode as CN

_C = CN()

_C.MODEL = CN()
# _C.MODEL.TYPE = "openai"  
#     # "openai", "ollama"
#     # Deepseek and Qwen are in openai style
# _C.MODEL.MARK = "DASHSCOPE" 
# _C.MODEL.NAME = "qwen2.5-3b-instruct" 

_C.MODEL.TYPE = "ollama"
_C.MODEL.MARK = "LLAMA"
_C.MODEL.NAME = "llama3.2"

_C.SERVER = CN()
_C.SERVER.LOCAL_SCRIPTS = [
    "D:/GitRepo/MCP-Explorer/my_servers/TimeServer/timetools.py",
    "D:/GitRepo/MCP-Explorer/my_servers/WallpaperServer/Unsplash.py",
]

def get_cfg_defaults():
  """Get a yacs CfgNode object with default values for my_project."""
  # Return a clone so that the defaults will not be altered
  # This is for the "local variable" use pattern
  return _C.clone()
