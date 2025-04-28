import os
import sys
import json
from typing import Optional, List
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

from openai import AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.sessions: List[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
        )
        self.model_name = "deepseek-chat"

    async def connect_to_sse_servers(self, server_urls: List[str]):
        """Connect to multiple MCP servers running with SSE transport"""
        self._streams_contexts = []
        self._session_contexts = []
        '''
        这两个列表的意义是保证管理SSE连接的上下文管理器不会终止。
        用完上下文管理器（sse_client）的.__aenter__() 之后，如果不保留对它的引用，
        Python 可能会在后续的某个时刻自动销毁这个对象，并隐式触发 __aexit__()，
        断开连接。此时session就会失效。
        '''
        for server_url in server_urls:
            # Store the context managers so they stay alive
            self._streams_contexts.append(sse_client(url=server_url))
            streams = await self._streams_contexts[-1].__aenter__() # 相当于stdio, write

            self._session_contexts.append(ClientSession(*streams))
            session: ClientSession = await self._session_contexts[-1].__aenter__()
            self.sessions.append(session)

            # Initialize
            await session.initialize()

            # List available tools to verify connection
            print(f"Initialized SSE client for {server_url}...")
            print("Listing tools...")
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to server {server_url} with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        """Properly clean up the sessions and streams"""
        for session_context in self._session_contexts:
            if session_context:
                await session_context.__aexit__(None, None, None)
        for streams_context in self._streams_contexts:
            if streams_context:
                await streams_context.__aexit__(None, None, None)

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

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

        # Initial OpenAI API call
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=available_tools
        )
        
        # Process response and handle tool calls
        tool_results = []
        final_text = []

        message = response.choices[0].message
        final_text.append(message.content or "")

        if message.tool_calls:
            # Handle each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Find the session that has the tool
                for session in self.sessions:
                    response = await session.list_tools()
                    if any(tool.name == tool_name for tool in response.tools):
                        # Execute tool call
                        result = await session.call_tool(tool_name, tool_args)
                        tool_results.append({"call": tool_name, "result": result})
                        final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                        # Add tool call and result to messages
                        messages.append({
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
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result.content)
                })
                

            # Get next response
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=available_tools
            )
            
            message = response.choices[0].message
            if message.content:
                final_text.append(message.content)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <URLs of SSE MCP servers separated by comma (i.e. http://localhost:8080/sse)>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        server_urls = sys.argv[1].split(',')
        await client.connect_to_sse_servers(server_urls=server_urls)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())