from yacs.config import CfgNode as CN

_C = CN()

_C.MODEL = CN()
# _C.MODEL.TYPE = "openai"  # SDK style
#     # "openai", "ollama"
#     # Deepseek and Qwen are in openai style
# _C.MODEL.MARK = "DASHSCOPE" # API KEY name
# _C.MODEL.NAME = "qwen2.5-3b-instruct" 

_C.MODEL.TYPE = "ollama"
_C.MODEL.MARK = "LLAMA"
_C.MODEL.NAME =  "phi4-mini"
    # "llama3.2"

# _C.MODEL.TYPE = "gemini"
# _C.MODEL.MARK = "GEMINI"
# _C.MODEL.NAME =  "gemini-2.0-flash"

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
