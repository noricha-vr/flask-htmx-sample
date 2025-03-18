import os
import asyncio
import re
import mysql.connector
from typing import List, Dict, Any, Optional
from agents import Agent, Runner, WebSearchTool, function_tool

class MySQLTools:
    @staticmethod
    def get_db_connection():
        """MySQL データベース接続を確立する"""
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            database=os.getenv("DB_DATABASE", "")
        )
    
    @staticmethod
    @function_tool
    def query_mysql(query: str) -> List[Dict[str, Any]]:
        """
        MySQL データベースにクエリを実行し、結果を返します。
        
        Args:
            query: 実行する SQL クエリ
            
        Returns:
            クエリ結果の辞書のリスト
        """
        try:
            connection = MySQLTools.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    @function_tool
    def get_table_schema(table_name: str) -> Dict[str, Any]:
        """
        指定されたテーブルのスキーマ情報を取得します。
        
        Args:
            table_name: スキーマを取得するテーブル名
            
        Returns:
            テーブルのスキーマ情報を含む辞書
        """
        try:
            connection = MySQLTools.get_db_connection()
            cursor = connection.cursor(dictionary=True)

            # テーブル構造の取得
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            # サンプルデータの取得
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()

            cursor.close()
            connection.close()

            return {
                "table_name": table_name,
                "columns": columns,
                "sample_data": sample_data
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    @function_tool
    def list_tables() -> List[str]:
        """
        データベース内の全テーブルリストを取得します。
        
        Returns:
            テーブル名のリスト
        """
        try:
            connection = MySQLTools.get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            connection.close()
            return tables
        except Exception as e:
            return [f"エラー: {str(e)}"]
    
    @staticmethod
    @function_tool
    def safe_query_mysql(table_name: str, columns: Optional[List[str]] = None,
                        where_clause: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        安全な MySQL クエリを実行します。テーブル名、列、where 句、制限を指定できます。
        
        Args:
            table_name: クエリするテーブルの名前
            columns: 取得する列のリスト（指定がない場合は全列）
            where_clause: WHERE 句（オプション）
            limit: 結果の最大行数（指定がない場合は100）
            
        Returns:
            クエリ結果
        """
        try:
            # 列のリストを構築
            cols = "*"
            if columns and len(columns) > 0:
                cols = ", ".join(columns)

            # クエリを構築
            query = f"SELECT {cols} FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"

            # limitのデフォルト値をコード内で設定
            actual_limit = 100 if limit is None else limit
            query += f" LIMIT {actual_limit}"

            # クエリ実行
            connection = MySQLTools.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()

            return results
        except Exception as e:
            return [{"error": str(e)}]

class SearchAgent:
    def __init__(self, api_key=None, enable_mysql=True):
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key must be provided or set as environment variable")
        
        tools = [WebSearchTool()]
        
        # MySQLツールを有効化する場合
        if enable_mysql:
            tools.extend([
                MySQLTools.list_tables,
                MySQLTools.get_table_schema,
                MySQLTools.safe_query_mysql,
                MySQLTools.query_mysql
            ])
            
            instructions = """You are a helpful assistant that can search the web for information and 
            interact with MySQL databases. You can answer questions using both web search results and database queries.
            
            When working with databases:
            1. Use list_tables to see available tables
            2. Use get_table_schema to understand table structure
            3. Use safe_query_mysql for most queries (preferred)
            4. Use query_mysql only for complex queries
            
            Provide concise, informative responses.
            """
        else:
            instructions = "You are a helpful assistant that can search the web for information and answer questions accurately. Provide concise, informative responses."
        
        # Create an agent with specified tools
        self.agent = Agent(
            name="Search and Database Assistant",
            instructions=instructions,
            model="gpt-4o-mini",
            tools=tools
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
        """テキスト内のMarkdown形式をHTMLに変換"""
        try:
            # Markdownモジュールをインポート、なければインストールを促す
            import markdown
            from markdown.extensions.extra import ExtraExtension
            
            # Markdownをベースにして完全なHTMLに変換
            # ExtensionでMarkdownの拡張機能（テーブルなど）も処理可能に
            html = markdown.markdown(text, extensions=[ExtraExtension()])
            
            return html
            
        except Exception as e:
            print(e)
            return text
    
    async def ask_stream(self, question):
        """Stream the agent's response"""
        async for event in Runner.run_streamed(self.agent, question):
            if event.type == "agent_output":
                yield event.content

# 使用例
if __name__ == "__main__":
    # MySQLを有効にしたエージェントを作成
    agent = SearchAgent(enable_mysql=True)
    response = agent.ask("データベース内のテーブル一覧を教えてください")
    print(response)
