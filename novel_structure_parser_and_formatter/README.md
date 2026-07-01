# 📚 Novel Auto-Formatter / 小説自動フォーマッター / 小说自动排版工具

**Author / 著者 / 作者**: 张龙 (Zhang Long)  
**Dependencies / 依存関係 / 依赖**: None (Pure Python Standard Library / 純Python標準ライブラリ / 纯Python标准库)

---

## 🇬🇧 English

### Introduction
**Novel Auto-Formatter** is a lightweight, zero-dependency Python script designed to automatically parse, structure, and beautifully format raw novel text files (especially Chinese web novels). It transforms messy, unstructured text dumps into highly readable, professionally formatted documents.

### Core Features
- **Auto Encoding Detection**: Automatically detects and reads files in UTF-8, GBK, GB18030, or UTF-16 encodings, eliminating manual encoding headaches.
- **Header Cleaning & Metadata Extraction**: Utilizes **Regular Expressions (Regex)** to strip out header junk (e.g., `===` lines, spam links) and accurately extracts metadata such as the Book Title, Author, and Synopsis.
- **Intelligent Structure Parsing**: Uses advanced Regex matching to automatically identify and build a multi-level nested dictionary of "Volumes" (卷) and "Chapters" (章). It guarantees 100% content integrity with zero text loss.
- **JSON to TXT with Beautiful Formatting**: 
  - Exports the parsed structure into a clean **JSON** file for programmatic use.
  - Converts the JSON structure into a **beautifully formatted TXT** file.
  - **Smart Line-Wrapping**: Intelligently breaks long paragraphs at appropriate punctuation marks (e.g., `，`, `。`, `！`) rather than cutting words in half.
  - **Visual Layout**: Adds elegant volume separators, chapter indents, and proper line spacing for an optimal reading experience.

### How to Use
1. Ensure you have Python 3.x installed.
2. Run the script in your terminal: `python novel_auto_formatter.py`
3. Follow the prompts to input the directory path and the novel's filename.
4. Find the generated `_parsed.json` and `_formatted.txt` files in the same directory.

---

## 🇨🇳 中文

### 简介
**小说自动排版工具** 是一个轻量级、零依赖的 Python 脚本，专为自动解析、结构化和精美排版原始小说文本文件（尤其是中文网文）而设计。它能将杂乱无章的纯文本转化为结构清晰、排版专业的阅读文档。

### 核心功能
- **自动编码检测**：自动识别并读取 UTF-8、GBK、GB18030 或 UTF-16 编码的文件，彻底告别乱码烦恼。
- **头部清理与元数据提取**：利用**正则表达式 (Regex)** 自动屏蔽文件头部的干扰信息（如 `===` 符号、推广链接等），并精准提取“书名”、“作者”和“内容简介”。
- **智能卷章结构解析**：通过正则匹配自动识别“第X卷”和“第X章”，构建多层嵌套的字典结构。采用索引切片技术提取正文，确保内容 100% 完整，绝不漏字。
- **JSON 转 TXT 与精美排版**：
  - 将解析后的数据导出为结构化的 **JSON** 文件，方便后续程序调用。
  - 将 JSON 数据转换为**排版精美的 TXT** 文件。
  - **智能断句换行**：当单行字数超限时，自动向前寻找合适的标点符号（如 `，`、`。`、`！`）进行断句换行，避免生硬截断。
  - **视觉美化**：自动添加卷名分隔线、章节首行缩进和合理的段落间距，打造沉浸式阅读体验。

### 使用方法
1. 确保已安装 Python 3.x 环境。
2. 在终端中运行脚本：`python novel_auto_formatter.py`
3. 根据提示输入小说文件所在的目录路径和文件名。
4. 运行结束后，在原目录下即可找到生成的 `_parsed.json` 和 `_formatted.txt` 文件。

---

## 🇯🇵 日本語

### 概要
**小説自動フォーマッター** は、軽量で依存関係ゼロの Python スクリプトであり、生の小説テキストファイル（特に中国語ウェブ小説）を自動的に解析、構造化、美しくレイアウトするために設計されています。雑然とした構造化されていないテキストを、非常に読みやすくプロフェッショナルなフォーマットのドキュメントに変換します。

### コア機能
- **自動エンコーディング検出**：UTF-8、GBK、GB18030、UTF-16 エンコーディングを自動的に検出して読み込み、文字化けの悩みを解消します。
- **ヘッダークリーンアップとメタデータ抽出**：**正規表現 (Regex)** を使用して、ヘッダーのジャンクデータ（`===` 行やスパムリンクなど）を除去し、「書名」、「著者」、「内容紹介」などのメタデータを正確に抽出します。
- **インテリジェントな構造解析**：高度な正規表現マッチングを使用して、「巻」と「章」の多層ネスト辞書を自動的に識別・構築します。文字列スライスにより内容の100%完全性を保証し、テキストの欠落をゼロにします。
- **JSONからTXTへの変換と美しいレイアウト**：
  - 解析された構造をクリーンな **JSON** ファイルとしてエクスポートし、プログラムでの利用を容易にします。
  - JSON 構造を**美しくフォーマットされた TXT** ファイルに変換します。
  - **スマートな改行処理**：長い段落を適切な句読点（`，`、`。`、`！` など）でインテリジェントに改行し、単語の途中での不自然な分断を防ぎます。
  - **ビジュアルレイアウト**：優雅な巻の区切り線、章のインデント、適切な行間を追加し、最適な読書体験を提供します。

### 使い方
1. Python 3.x がインストールされていることを確認してください。
2. ターミナルでスクリプトを実行します：`python novel_auto_formatter.py`
3. プロンプトに従って、ディレクトリパスと小説のファイル名を入力します。
4. 実行後、同じディレクトリ内に生成された `_parsed.json` と `_formatted.txt` ファイルを確認できます。

---

### 📄 License / ライセンス / 开源协议
MIT License - Feel free to use, modify, and distribute! / 自由に使用、改変、配布してください！ / 欢迎自由使用、修改和分发！
