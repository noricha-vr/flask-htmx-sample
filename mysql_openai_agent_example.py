"""
OpenAI Agent SDK で MySQL に接続するサンプルアプリケーション
このスクリプトは OpenAI Agent SDK を使用して MySQL データベースに接続し、
自然言語クエリをデータベースクエリに変換して実行する AI アシスタントを作成します。
"""

import os
import json
from typing import List, Dict, Any, Optional
import mysql.connector
from agents import Agent, Runner, function_tool, InputGuardrail, GuardrailFunctionOutput

# ========== データベース接続関連の関数 ==========


def get_db_connection():
    """MySQL データベース接続を確立する"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )


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
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        return [{"error": str(e)}]


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
        connection = get_db_connection()
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


@function_tool
def list_tables() -> List[str]:
    """
    データベース内の全テーブルリストを取得します。
    
    Returns:
        テーブル名のリスト
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        connection.close()
        return tables
    except Exception as e:
        return [f"エラー: {str(e)}"]

# ========== セキュリティガードレール ==========


def check_sql_injection(ctx, agent, input_data):
    """
    SQL インジェクションの可能性をチェックするガードレール関数
    """
    dangerous_patterns = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
        "--", "/*", "*/", "@@", "SLEEP(", "BENCHMARK("
    ]

    input_upper = input_data.upper()
    is_safe = True

    for pattern in dangerous_patterns:
        if pattern in input_upper:
            is_safe = False
            break

    return GuardrailFunctionOutput(
        output_info={"is_safe": is_safe},
        tripwire_triggered=not is_safe
    )


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
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        return results
    except Exception as e:
        return [{"error": str(e)}]

# ========== エージェント設定 ==========


# データベースツールを持つエージェントを作成
db_agent = Agent(
    name="Database Assistant",
    instructions="""あなたはデータベースアシスタントです。
    ユーザーからの質問に基づいて適切な SQL クエリを作成し、
    データベースからデータを取得してください。
    
    以下のツールが利用可能です：
    - list_tables: データベース内のすべてのテーブルを一覧表示
    - get_table_schema: 特定のテーブルのスキーマ情報を取得
    - safe_query_mysql: 安全なクエリを実行（推奨）
    - query_mysql: 一般的な SQL クエリを実行（高度なクエリの場合のみ使用）
    
    ユーザーがデータベースについて質問した場合：
    1. まず list_tables を使用してどのテーブルが利用可能か確認
    2. 次に get_table_schema を使用して関連テーブルの構造を理解
    3. safe_query_mysql または query_mysql を使用してデータを取得
    4. 結果をユーザーにわかりやすく説明
    
    必ず安全なクエリのみを実行し、SQL インジェクションを防止してください。
    SQLの文法エラーがある場合は、クエリを修正して再実行してください。
    """,
    tools=[list_tables, get_table_schema, safe_query_mysql, query_mysql],
    input_guardrails=[
        InputGuardrail(guardrail_function=check_sql_injection)
    ]
)

# ========== ストリーミング出力関数 ==========


async def stream_agent_output(prompt):
    """エージェントの出力をストリーミングする"""
    print(f"質問: {prompt}")
    print("\n回答:")

    async for event in Runner.run_streamed(db_agent, prompt):
        if event.type == "agent_output":
            print(event.content, end="", flush=True)
    print("\n" + "-"*50)

# ========== メイン実行部分 ==========


def main():
    """メインのインタラクション関数"""
    print("MySQL データベースアシスタントへようこそ！")
    print("データベースについて質問することができます。終了するには 'exit' と入力してください。")
    print("-"*50)

    while True:
        user_input = input("\nデータベースについての質問を入力してください: ")
        if user_input.lower() in ['exit', 'quit', '終了']:
            break

        # 同期的にエージェントを実行
        result = Runner.run_sync(db_agent, user_input)
        print("\n回答:")
        print(result.final_output)
        print("-"*50)


if __name__ == "__main__":
    import asyncio

    # 非同期処理のサンプル（使用したい場合はコメントを外す）
    # asyncio.run(stream_agent_output("customers テーブルの最初の 5 件を表示してください"))

    # 同期的なインタラクション
    main()
