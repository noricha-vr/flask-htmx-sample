import os
import asyncio
from agents import Agent, Runner, WebSearchTool

class SearchAgent:
    def __init__(self, api_key=None):
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key must be provided or set as environment variable")
        
        # Create an agent with web search capability
        self.agent = Agent(
            name="Search Assistant",
            instructions="You are a helpful assistant that can search the web for information and answer questions accurately. Provide concise, informative responses.",
            model="gpt-4o-mini",
            tools=[WebSearchTool()]
        )
    
    def ask(self, question):
        """Ask a question to the agent and get a response"""
        # 新しいイベントループを作成して使用
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(Runner.run(self.agent, question))
            return result.final_output
        finally:
            loop.close()
    
    async def ask_stream(self, question):
        """Stream the agent's response"""
        async for event in Runner.run_streamed(self.agent, question):
            if event.type == "agent_output":
                yield event.content
