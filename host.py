# -*- coding: utf-8 -*-

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
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from dotenv import load_dotenv
load_dotenv()

from loguru import logger
from config import get_cfg_defaults

model_info = {
    "DEEPSEEK": {"base_url": "https://api.deepseek.com",},
    "DASHSCOPE": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",},
    "GEMINI": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",},
    "OLLAMA": {"base_url": "http://localhost:11434/v1",},
    "HUNYUAN": {"base_url": "https://api.hunyuan.cloud.tencent.com/v1",},
}

class MyMCPClient:
    def __init__(self, cfg):
        # Initialize session and client objects
        self.cfg = cfg
        self.model_name = cfg.MODEL.NAME

        self.sessions: List[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self._streams_contexts = []
        self._session_contexts = []
        self.tools = []

        self.init_messages = [{
            "role": "system",
            "content": "You are a helpful assistant. If you have not called any tool, answer the question. Otherwise, call the appropriate tool."
        }]
        self.messages = self.init_messages.copy()
    
    async def cleanup(self):
        """Properly clean up the sessions and streams"""
        await self.exit_stack.aclose()
        for session_context in self._session_contexts:
            if session_context:
                await session_context.__aexit__(None, None, None)
        for streams_context in self._streams_contexts:
            if streams_context:
                await streams_context.__aexit__(None, None, None)

    async def connect_to_servers(self):
        """
        Connect to local MCP server by stdio or sse transport. Servers defined in config.py.
        """
        for server_command in self.cfg.SERVER.ACCESS_PATHS:
            if server_command.startswith("http://localhost:"):
                await self.connect_sse_servers(server_command)
            else:
                await self.connect_stdio_server(server_command)
        
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
        self.tools = available_tools
        

    async def connect_sse_servers(self, server_url: str):
        """
        Connect to a local MCP server using SSE transport

        Args:
            server_url: url of the server (such as http://localhost:8000/messages/)
        """
        # Store the context managers so they stay alive
        self._streams_contexts.append(sse_client(url=server_url))
        try:
            streams = await self._streams_contexts[-1].__aenter__() # streams相当于(stdio, write)
        except Exception as e:
            logger.error(f"Failed to connect to SSE server: {e}")
            logger.error(f"Please check if the server is running at {server_url}")
            print(f"**Failed to connect to SSE server: {e}**")
            print(f"**Please check if the server is running at {server_url}**")
            self._streams_contexts.pop()
            return

        self._session_contexts.append(ClientSession(*streams))
        session: ClientSession = await self._session_contexts[-1].__aenter__()
        self.sessions.append(session)
        await session.initialize()

        logger.info(f"Connecting to sse server {server_url}")
        response = await session.list_tools()
        tools = response.tools
        logger.info(f"\nConnected to server {server_url} with tools{[tool.name for tool in tools]}")
    
    async def connect_stdio_server(self, server_script_path: str):
        """
        Connect to a local MCP server script using stdio transport

        Args:
            server_script_path: path to the server script (for me only .py)
        """
        is_python = server_script_path.endswith('.py')
        if not is_python:
            logger.error("Server script must be a .py , but got: {}".format(server_script_path))
            return

        command = "python"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        self.sessions.append(session)
        await session.initialize()
        logger.info("Connecting to server script: {}".format(server_script_path))

        # List available tools
        response = await session.list_tools()
        tools = response.tools
        logger.info(f"Connected to server with tools:{[tool.name for tool in tools]}")


    async def get_response_message(self) -> ChatCompletionMessage:
        """Get response from OpenAI API"""
        client = AsyncOpenAI(
            api_key=os.getenv("{}_API_KEY".format(self.cfg.MODEL.MARK.upper())),
            base_url=model_info[self.cfg.MODEL.MARK]["base_url"],
        )
        response = await client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            tools=self.tools,
        )

        return response.choices[0].message

    async def process_query(self, query: str) -> None:
        """Process a query using OpenAI and available tools"""
        logger.info("Processing a  query...")
        
        self.messages += [{
            "role": "user",
            "content": query
        }]

        await self.send_messages()
    
    def log_all_messages(self):
        """Show all messages in the conversation"""
        logger.info("All messages in the conversation:")
        formatted_messages = ''
        for message in self.messages:
            for key, value in message.items():
                formatted_messages += f"{key}: {value}\n"
            formatted_messages += "\n"
        logger.info("Formatted messages: \n{}".format(formatted_messages))
    
    def user_confirm_tool_call(self, tool_name: str, tool_args: dict) -> bool:
        print(f"\n[Calling tool {tool_name} with args {tool_args}]")
        if not self.cfg.HOST.NEED_USER_CONFIRM:
            return True
        # Ask user for confirmation
        cmd = input("Do you want to call this tool? ('n' to cancel, any other key to continue): ").strip().lower()
        if cmd == 'n':
            print(f"Skipping tool call [{tool_name}]")
            return False
        return True
    
    async def send_messages(self) -> None:
        """Send messages to the server and get a response"""
        logger.info("Sending messages to the model...")

        assistant_message = await self.get_response_message()
        if assistant_message.content: 
            print('\nAnswer:',assistant_message.content)

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
                        # user check
                        if not self.user_confirm_tool_call(tool_name, tool_args):
                            continue

                        # Execute tool call
                        tool_call_result = await session.call_tool(tool_name, tool_args)
                        result_txt = tool_call_result.content[0].text
                        print(f'[Tool result]: {result_txt}')

                        logger.info(f"calling tool [{tool_name}] with args [{tool_args}], got result:[{result_txt}]")

                        # Add tool call and result to messages
                        self.messages.append({
                            "role": "assistant",
                            "tool_calls": [{
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": json.dumps(tool_args)
                                }
                            }]
                        })
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_txt
                        })
            
            await self.send_messages()

    def self_check(self):
        """Check if everything is ok"""
        if len(self.messages) > self.cfg.HOST.MAX_MASSAGE_TURNS:
            logger.warning("Message length exceeds the limit. Cleaning up...")
            self.clean_dialogue(command="touch_max")

    async def chat_loop(self):
        """Run an interactive chat loop"""
        logger.info("Starting chat loop. Model: {}".format(self.model_name))
        print("\nMCP Client Started! (model: {})".format(self.model_name))

        help_text = """
        Type your queries or command

        Commands:
          - 'quit': Exit the program
          - 'restart': Restart the dialogue and clean up memory
          - 'help': Show help message
        """
        help_text = textwrap.dedent(help_text)
        print(help_text)

        print(f"Available tools: { [tool['function']['name'] for tool in self.tools] } ")
        
        while True:
            self.self_check()
            self.log_all_messages()
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                if query.lower() == 'restart':
                    print("Restarting dialogue...")
                    self.clean_dialogue(command="user_restart")
                    continue
                if query.lower() == 'help':
                    print(help_text)
                    continue
                await self.process_query(query)
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        print("\nExited.")
    
    def clean_dialogue(self, command: str):
        """Clean up memory and restart dialogue"""
        if command == "user_restart":
            self.messages = self.init_messages.copy()
            logger.info("Memory cleaned.")
        if command == "touch_max":
            self.messages = self.messages[-self.cfg.HOST.MAX_MASSAGE_TURNS:]
            logger.info("Memory touch max, auto clean.")

async def main():
    cfg = get_cfg_defaults()
    if cfg.HOST.LOG_FILE:
        logger.remove() # 移除控制台输出
        logger.add(cfg.HOST.LOG_FILE, rotation="1 MB", retention="7 days", level="DEBUG")
    client = MyMCPClient(cfg)
    try:
        await client.connect_to_servers()
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())