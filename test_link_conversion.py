import pytest
import re
from my_agent import SearchAgent
import markdown
from markdown.extensions.extra import ExtraExtension

@pytest.fixture
def search_agent():
    return SearchAgent()

def test_url_conversion(search_agent):
    # 画像のサンプルテキスト
    sample_text = """2024年10月28日、トヨタ自動車とNTTは、車の自動運転向けソフトウェアの開発で協業することを発表しました。このシステムは、走行中のデータからAIが事故の可能性を予測し、車両を自動で制御することを目指しています。研究開発には数千億円規模を投じ、2028年をめどに実用化を目指しています。([tokyo-np.co.jp](https://www.tokyo-np.co.jp/article/363178?utm_source=openai)) また、東芝は、生体画像などの限定的なデータから高精度の画像解析を可能にするAI技術を開発しました。従来、数万枚以上のデータが必要とされていましたが、この手法では最小40枚の画像から解析が可能となり、産業分野でのAI導入を促進することが期待されています。([news.yahoo.co.jp](https://news.yahoo.co.jp/articles/8c3a3ebfd7d193005a98d37ecf994edd7b348137?utm_source=openai)) さらに、AI技術の高度化に伴い、国際競争が激化していることが、2024年版の「科学技術・イノベーション白書」で指摘されています。特に、米国と中国が技術革新を先導しており、国内では人材や研究資金の確保が課題となっています。([hokkoku.co.jp](https://www.hokkoku.co.jp/articles/-/1425711?utm_source=openai)) これらの動向は、AI技術の進展とその社会への影響を示しており、今後の展開が注目されます。"""
    
    # カスタムパターンの変換
    pattern = r'\(\[([^]]+)\]\((https?://[^)]+)\)\)'
    replacement = r'([\1](<a href="\2" target="_blank">\2</a>))'
    expected_text_with_patterns = re.sub(pattern, replacement, sample_text)
    expected_html = markdown.markdown(expected_text_with_patterns, extensions=[ExtraExtension()])
    
    # _convert_urls_to_linksメソッドを直接テスト
    result = search_agent._convert_urls_to_links(sample_text)
    
    print("\n--- 実際の結果 ---")
    print(result)
    print("\n--- 期待した結果 ---")
    print(expected_html)
    
    assert result == expected_html

def test_newline_conversion(search_agent):
    # 改行を含むテキスト
    sample_text = """これは1行目です。
これは2行目です。
これは3行目です。

これは空行の後の行です。"""
    
    # Markdownライブラリを使用した期待値
    expected_html = markdown.markdown(sample_text, extensions=[ExtraExtension()])
    
    # _convert_urls_to_linksメソッドを直接テスト
    result = search_agent._convert_urls_to_links(sample_text)
    
    print("\n--- 改行テスト: 実際の結果 ---")
    print(result)
    print("\n--- 改行テスト: 期待した結果 ---")
    print(expected_html)
    
    # Markdownの変換結果を比較
    assert result == expected_html

def test_markdown_conversion(search_agent):
    # Markdownの様々な要素を含むテキスト
    sample_text = """# マークダウンのテスト

これは**太字**と*斜体*のテストです。

## 箇条書き
- 項目1
- 項目2
  - ネストした項目

## コードブロック
```python
def hello():
    print("Hello, world!")
```

[リンク](https://example.com)もテストします。"""
    
    # 期待される結果 - markdownライブラリの出力と一致するはず
    expected_html = markdown.markdown(sample_text, extensions=[ExtraExtension()])
    
    # _convert_urls_to_linksメソッドを直接テスト
    result = search_agent._convert_urls_to_links(sample_text)
    
    print("\n--- Markdown変換テスト: 実際の結果 ---")
    print(result)
    print("\n--- Markdown変換テスト: 期待した結果 ---")
    print(expected_html)
    
    # Markdownの変換結果を比較
    assert result == expected_html
