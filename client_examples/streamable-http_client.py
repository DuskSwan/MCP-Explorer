import os
import json
from typing import Optional, List
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

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

    async def connect_to_streamable_http_server(
        self, server_url: str, headers: Optional[dict] = None
    ):
        """Connect to an MCP server running with HTTP Streamable transport"""
        self._streams_context = streamablehttp_client(
            url=server_url,
            headers=headers or {},
        )
        read_stream, write_stream, _ = await self._streams_context.__aenter__()

        self._session_context = ClientSession(read_stream, write_stream)
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        available_tools = []
        response = await self.session.list_tools()
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
                
                response = await self.session.list_tools()
                if any(tool.name == tool_name for tool in response.tools):
                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
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
            # try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n" + response)
            # except Exception as e:
            #     print(f"\nError: {str(e)}")

async def main():
    PORT = 8081
    server_url = f"http://localhost:{PORT}/mcp"
        
    client = MCPClient()
    try:
        await client.connect_to_streamable_http_server(server_url=server_url)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())