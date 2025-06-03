import os
import sys
import json
from typing import Optional, List
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        # self.sessions: List[ClientSession] = []
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
        self.model_name = "deepseek-chat"
        # self.model_name = "qwen2.5-3b-instruct"
        

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an local MCP server

        Args:
            server_script_path: Path to the server script (for me only .py)
        """
        is_python = server_script_path.endswith('.py')
        if not is_python:
            raise ValueError("Server script must be a .py file")

        command = "python"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        """Properly clean up the sessions and streams"""
        await self.exit_stack.aclose()

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        known_tools = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            },
        } for tool in known_tools.tools]

        '''
        respoense = self.session.list_tools() :
            meta=None,
            nextCursor=None,
            tools=[
                Tool(
                    name, 
                    dexcripstion,
                    inputSchema={
                        'properties': {'image_url': {'title': 'Image Url', 'type': 'string'}}
                        'required': ['image_url'], 
                        'title': 'show_imgArguments', 
                        'type': 'object'
                    }
                ),
                Tools...
            ]
        '''

        # Initial OpenAI API call
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            # tools=available_tools,
            tools=available_tools
        )

        '''
        ChatCompletion(
            id='a1d06dad-9071-4e1b-abab-87258664d912', 
            choices=[
                Choice(
                    finish_reason='tool_calls', 
                    index=0, 
                    logprobs=None, 
                    message=ChatCompletionMessage(
                        content='', 
                        refusal=None, 
                        role='assistant', 
                        annotations=None, 
                        audio=None, 
                        function_call=None, 
                        tool_calls=[
                            ChatCompletionMessageToolCall(
                                id='call_0_a2fda85a-7b8c-4b4e-afef-603481ec00ab', 
                                function=Function(
                                    arguments='{"image_url":"C:\\Users\\kyland\\Desktop\\abstract_blue_art.jpg"}', name='show_img'
                                ), 
                                type='function', 
                                index=0
                            )
                        ]
                    )
                )
            ], 
            created=1745222131, 
            model='deepseek-chat', 
            object='chat.completion', 
            service_tier=None, 
            system_fingerprint='fp_3d5141a69a_prod0225', 
            usage=CompletionUsage(
                completion_tokens=33, 
                prompt_tokens=167, 
                total_tokens=200, 
                completion_tokens_details=None, 
                prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=128), 
                prompt_cache_hit_tokens=128, 
                prompt_cache_miss_tokens=39
            )
        )
        '''
        
        # Process response and handle tool calls
        tool_results = []
        final_text = []

        assistant_message = response.choices[0].message
        final_text.append(assistant_message.content or "")

        if assistant_message.tool_calls:
            # Handle each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Find the session that has the tool
                response = await self.session.list_tools()
                if any(tool.name == tool_name for tool in response.tools):
                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    '''
                    result = ToolResult(
                        meta=None ,
                        content=[TextContent(type='text', text='2025-04-23T11:37:17.760668', annotations=None)] ,
                        isError=False ,
                    )
                    '''
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

            # Get next response from OpenAI
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=available_tools
            )
            
            assistant_message = response.choices[0].message
            if assistant_message.content:
                final_text.append(assistant_message.content)

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
        print("Usage: python client.py <path to server script> ")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())