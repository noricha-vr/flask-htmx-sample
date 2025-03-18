OpenAI Agent SDKの使い方ガイド

## 概要

OpenAI Agent SDKは、AIエージェントを簡単に作成・管理するためのツールキットです。このSDKを使用することで、ウェブ検索、カスタム機能、複数エージェントのワークフローなどを実装できます。

## インストールと設定

### インストール方法

```bash
pip install openai-agents
```

### API設定

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

### 基本的なインポート

```python
from agents import Agent, Runner, WebSearchTool, function_tool
```

## 基本的なエージェントの作成

```python
agent = Agent(
    name="Assistant",
    instructions="あなたは役立つアシスタントです。",
    model="gpt-4"
)

result = Runner.run_sync(agent, "フランスの首都は何ですか？")
print(result.final_output)
```

## ツールの追加

### ウェブ検索ツール

```python
web_search_agent = Agent(
    name="Web Searcher",
    instructions="情報を検索できるウェブ検索アシスタントです。",
    tools=[WebSearchTool()]
)

result = Runner.run_sync(web_search_agent, "AIの最新動向は何ですか？")
print(result.final_output)
```

### カスタム関数ツール

```python
@function_tool
def calculate_area(length: float, width: float) -> float:
    return length * width

math_agent = Agent(
    name="Math Assistant",
    instructions="数学的な計算を実行できるアシスタントです。",
    tools=[calculate_area]
)

result = Runner.run_sync(math_agent, "長さ5、幅3の長方形の面積を計算してください")
print(result.final_output)
```

## マルチエージェントワークフロー

```python
support_agent = Agent(
    name="Support Agent",
    instructions="カスタマーサポートの問い合わせを処理します。"
)

sales_agent = Agent(
    name="Sales Agent",
    instructions="販売に関する質問を処理します。"
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="ユーザークエリに基づいて適切なエージェントにルーティングします。",
    handoffs=[support_agent, sales_agent]
)

result = Runner.run_sync(triage_agent, "製品に問題があります")
print(result.final_output)
```

## ガードレールの実装

```python
from agents import InputGuardrail, GuardrailFunctionOutput

def check_appropriate_content(ctx, agent, input_data):
    # コンテンツチェックロジックを実装
    is_appropriate = True  # 実際のチェックに置き換える
    return GuardrailFunctionOutput(
        output_info={"is_appropriate": is_appropriate},
        tripwire_triggered=not is_appropriate
    )

safe_agent = Agent(
    name="Safe Assistant",
    instructions="適切なクエリにのみ応答する役立つアシスタントです。",
    input_guardrails=[
        InputGuardrail(guardrail_function=check_appropriate_content)
    ]
)

result = Runner.run_sync(safe_agent, "科学について教えてください")
print(result.final_output)
```

## ストリーミング出力

```python
async def stream_agent_output():
    async for event in Runner.run_streamed(agent, "量子コンピューティングについて説明してください"):
        if event.type == "agent_output":
            print(event.content, end="", flush=True)

import asyncio
asyncio.run(stream_agent_output())
```

## デバッグ用トレースへのアクセス

```python
result = Runner.run_sync(agent, "今日の天気はどうですか？")
for trace in result.traces:
    print(f"Trace: {trace}")
```

## 応用例

1. **カスタマーサポートボット**：Web検索ツールと製品データベースツールを組み合わせて、顧客の質問に回答するエージェント

2. **データ分析アシスタント**：データ処理ツールを追加して、データセットを分析・可視化するエージェント

3. **コンテンツ作成支援**：画像生成APIやテキスト要約ツールを組み合わせたコンテンツ制作エージェント

4. **スマートホーム管理**：IoTデバイス制御ツールを追加して、家庭内のデバイスを管理するエージェント

## 注意点

- エージェントのメモリ管理：長期的な会話履歴を管理するには、カスタムストレージソリューションが必要な場合があります
- レート制限：OpenAI APIのレート制限に注意してエージェントを設計する
- セキュリティ：機密情報を扱う場合は、適切なセキュリティ対策を実装する

## 参考リソース

- [公式ドキュメント](https://openai.github.io/openai-agents-python/)
- [クイックスタートガイド](https://openai.github.io/openai-agents-python/quickstart/)
- [OpenAI Platform Docs](https://platform.openai.com/docs/guides/agents-sdk)
