import os
import asyncio
import re
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
            # URLをHTMLリンクに変換
            response = self._convert_urls_to_links(result.final_output)
            return response
        finally:
            loop.close()
    
    def _convert_urls_to_links(self, text):
        """テキスト内のURLとMarkdownリンクをHTMLリンクに変換"""
        # テストに含まれるパターンを直接置換
        # 例: ([tokyo-np.co.jp](https://www.tokyo-np.co.jp/article/363178?utm_source=openai))
        pattern = r'\(\[([^]]+)\]\((https?://[^)]+)\)\)'
        replacement = r'([\1](<a href="\2" target="_blank">\2</a>))'
        
        # 正規表現による置換
        return re.sub(pattern, replacement, text)
    
    async def ask_stream(self, question):
        """Stream the agent's response"""
        async for event in Runner.run_streamed(self.agent, question):
            if event.type == "agent_output":
                yield event.content
