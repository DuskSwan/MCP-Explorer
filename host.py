import os
import json
import asyncio
import textwrap
from typing import List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from openai import AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
# DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

from loguru import logger
from config import get_cfg_defaults

model_info = {
    "DEEPSEEK": {"base_url": "https://api.deepseek.com",},
    "DASHSCOPE": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",},
    "GEMINI": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",},
    "OLLAMA": {"base_url": "http://localhost:11434/v1",},
}

class MyMCPClient:
    def __init__(self, cfg):
        # Initialize session and client objects
        self.cfg = cfg
        self.sessions: List[ClientSession] = []
        # self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            api_key=os.getenv("{}_API_KEY".format(cfg.MODEL.MARK.upper())),
            base_url=model_info[cfg.MODEL.MARK]["base_url"],
        )
        self.model_name = cfg.MODEL.NAME
        self.messages = [{
            "role": "system",
            "content": "You are a helpful assistant. If you have not called any tool, answer the question. Otherwise, call the appropriate tool."
        }]
        

    async def connect_to_servers(self, server_script_paths: List[str]):
        """
        Connect to local MCP server scripts

        Args:
            server_script_paths: list of path to the server script (for me only .py)
        """
        self.sessions = []
        for server_script_path in server_script_paths:
            is_python = server_script_path.endswith('.py')
            if not is_python:
                logger.error("Server script must be a .py , but got: {}".format(server_script_path))
                continue

            command = "python"
            server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env=None
            )
            logger.info("Connecting to server script: {}".format(server_script_path))

            stdio, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
            session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
            self.sessions.append(session)

            await session.initialize()
            logger.info("Initialized session.")

            # List available tools
            response = await session.list_tools()
            tools = response.tools
            logger.info("Connected to server with tools:{}".format( [tool.name for tool in tools] ))

    async def cleanup(self):
        """Properly clean up the sessions and streams"""
        await self.exit_stack.aclose()

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        logger.info("Processing a  query...")
        
        self.messages += [{
            "role": "user",
            "content": query
        }]

        available_tools = []
        for session in self.sessions:
            response = await session.list_tools()
            available_tools.extend([{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in response.tools])
        
        tool_names = [tool["function"]["name"] for tool in available_tools]
        logger.info("Available tools: {}".format(tool_names))

        formatted_messages = ''
        for message in self.messages:
            for key, value in message.items():
                formatted_messages += f"{key}: {value}\n"
        logger.info("Formatted messages: \n{}".format(formatted_messages))

        # Initial OpenAI API call
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        # tool_results = []
        final_text = []

        assistant_message = response.choices[0].message
        final_text.append(assistant_message.content or "")

        if not assistant_message.tool_calls:
            logger.info("No tool calls found in the response.")
            self.messages.append({
                "role": "assistant",
                "content": assistant_message.content
            })
        else:
            logger.info("Assistant call tools:{}".format([tool_call.function.name for tool_call in assistant_message.tool_calls]))
            # Handle each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Find the session that has the tool
                for session in self.sessions:
                    response = await session.list_tools()
                    if any(tool.name == tool_name for tool in response.tools):
                        # Execute tool call
                        result = await session.call_tool(tool_name, tool_args)

                        logger.info(f"calling tool [{tool_name}] with args [{tool_args}], got result:[{result.content}]")
                        
                        # tool_results.append({"call": tool_name, "result": result})
                        final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                        # Add tool call and result to messages
                        self.messages.append({
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": json.dumps(tool_args)
                                    }
                                }
                            ]
                        })
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result.content)
                        })

            # Get next response from OpenAI
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                tools=available_tools
            )
            
            assistant_message = response.choices[0].message
            if assistant_message.content:
                final_text.append(assistant_message.content)
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message.content
                })

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        logger.info("Starting chat loop. Model: {}".format(self.model_name))
        print("\nMCP Client Started!")

        help_text = """
        Type your queries or command

        Commands:
          - 'quit': Exit the program
          - 'restart': Restart the dialogue and clean up memory
          - 'help': Show this help message
        """
        help_text = textwrap.dedent(help_text)
        print(help_text)
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                if query.lower() == 'restart':
                    print("Restarting dialogue...")
                    self.clean_dialogue()
                    continue
                if query.lower() == 'help':
                    print(help_text)
                    continue
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        print("\nExited.")
    
    def clean_dialogue(self):
        """Clean up memory and restart dialogue"""
        self.messages = [{
            "role": "system",
            "content": "You are a helpful assistant."
        }]
        logger.info("Memory cleaned.")

async def main():
    cfg = get_cfg_defaults()
    client = MyMCPClient(cfg)
    try:
        await client.connect_to_servers(cfg.SERVER.LOCAL_SCRIPTS)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())