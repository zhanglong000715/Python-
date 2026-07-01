# ==============================================================================
# 【脚本功能介绍 / スクリプト機能紹介 / Script Introduction】
#
# 中文：
#   本脚本是一个纯标准库实现的小说自动排版工具。
#   它能够自动识别小说文件中的"卷"和"章"结构，提取书名、作者、内容简介等元数据，
#   并对正文内容进行智能换行排版（基于标点符号断句），最终输出结构化的 JSON 文件
#   和排版美观的 TXT 文件。支持 UTF-8、GBK、GB18030、UTF-16 多种编码自动检测。
#   无需安装任何第三方依赖，开箱即用。
#
# 日本語：
#   このスクリプトは、標準ライブラリのみで実装された小説自動レイアウトツールです。
#   小説ファイル内の「巻」と「章」の構造を自動的に識別し、書名・著者・内容紹介などの
#   メタデータを抽出します。本文コンテンツに対しては、句読点に基づくインテリジェントな
#   改行処理を行い、構造化されたJSONファイルと整形されたTXTファイルを出力します。
#   UTF-8、GBK、GB18030、UTF-16の複数エンコーディング自動検出に対応しています。
#   サードパーティライブラリのインストール不要で、すぐに使用できます。
#
# English:
#   This script is a novel auto-formatting tool implemented using only the Python
#   standard library. It automatically identifies the "volume" and "chapter" structure
#   in a novel file, extracts metadata such as title, author, and synopsis, and performs
#   intelligent line-wrapping on the body text (breaking at punctuation marks). It outputs
#   both a structured JSON file and a beautifully formatted TXT file. It supports automatic
#   detection of UTF-8, GBK, GB18030, and UTF-16 encodings.
#   No third-party dependencies required — ready to use out of the box.
#
# 作者 / 著者 / Author: 张龙 (Zhang Long)
# ==============================================================================

# 导入操作系统接口模块，用于文件和路径操作
# OSモジュールをインポート、ファイルとパスの操作に使用
# Import the OS module for file and path operations
import os

# 导入正则表达式模块，用于文本模式匹配
# 正規表現モジュールをインポート、テキストパターンマッチングに使用
# Import the regular expression module for text pattern matching
import re

# 导入JSON模块，用于数据序列化和输出
# JSONモジュールをインポート、データのシリアライズと出力に使用
# Import the JSON module for data serialization and output
import json

# ================= 配置区域 / 設定エリア / Configuration Area =================

# 限制最里面"内容"的单行最大字数，超过此长度会自动寻找标点符号换行
# 最も内側の「内容」の1行あたりの最大文字数を制限。この長さを超えると自動的に句読点で改行する
# Maximum number of characters per line for the innermost content; auto-wraps at punctuation if exceeded
MAX_LINE_LENGTH = 40

# 默认卷名（如果小说开头直接是章节，没有写"第X卷"，则归入此卷）
# デフォルト巻名（小説の冒頭が直接「章」で、「第X巻」がない場合、この巻に帰属させる）
# Default volume name (if the novel starts directly with chapters without a "Volume X" header, they go here)
DEFAULT_VOLUME = "未分卷_正文"

# ============================================================================

# 定义安全读取文件的函数
# ファイルを安全に読み込む関数を定義
# Define a function to safely read a file
def read_file_safely(filepath):
    """
    安全读取文件，自动尝试常见中文网文编码
    ファイルを安全に読み込み、一般的な中国語ネット小説のエンコーディングを自動試行
    Safely read a file, automatically trying common Chinese web novel encodings
    """
    # 定义一个编码列表，按优先级从高到低排列，依次尝试
    # エンコーディングリストを定義、優先度が高い順に並べて順番に試行
    # Define an encoding list ordered by priority, trying each one in sequence
    encodings = ['utf-8', 'gbk', 'gb18030', 'utf-16']

    # 遍历所有编码，逐一尝试读取文件
    # すべてのエンコーディングを順に試行してファイルを読み込む
    # Iterate over all encodings, trying to read the file with each one
    for enc in encodings:
        # 使用 try-except 捕获编码不匹配导致的解码错误
        # try-except でエンコーディング不一致によるデコードエラーを捕捉
        # Use try-except to catch decoding errors caused by encoding mismatch
        try:
            # 以当前编码打开文件并读取全部内容
            # 現在のエンコーディングでファイルを開き、全内容を読み込む
            # Open the file with the current encoding and read all content
            with open(filepath, 'r', encoding=enc) as f:
                # 成功读取，返回文件内容字符串
                # 読み込み成功、ファイル内容の文字列を返す
                # Successfully read, return the file content as a string
                return f.read()
        # 如果当前编码无法解码，捕获异常并继续尝试下一种编码
        # 現在のエンコーディングでデコードできない場合、例外を捕捉して次のエンコーディングを試行
        # If the current encoding fails to decode, catch the exception and try the next one
        except UnicodeDecodeError:
            # 跳过当前编码，继续循环
            # 現在のエンコーディングをスキップしてループを続行
            # Skip the current encoding and continue the loop
            continue

    # 如果所有编码都失败了，抛出一个带有提示信息的值错误
    # すべてのエンコーディングが失敗した場合、ヒント情報付きのValueErrorを発生
    # If all encodings fail, raise a ValueError with a helpful message
    raise ValueError(f"无法使用常见编码读取文件: {filepath}，请检查文件是否损坏。")


# 定义清理文件头部并提取元数据的函数
# ファイルヘッダーをクリーンアップしメタデータを抽出する関数を定義
# Define a function to clean the file header and extract metadata
def clean_header_and_meta(text):
    """
    1. 屏蔽开头的 =*? 和 链接
    2. 提取 名称、作者、内容简介

    1. 冒頭の =*? やリンクを屏蔽する
    2. 名称・著者・内容紹介を抽出する

    1. Block leading lines starting with = or containing links
    2. Extract title, author, and synopsis
    """
    # 将文本按换行符分割为行列表
    # テキストを改行文字で分割して行リストにする
    # Split the text into a list of lines by newline character
    lines = text.split('\n')

    # 创建一个空列表，用于存放清理后的行
    # クリーンアップ後の行を格納する空のリストを作成
    # Create an empty list to store the cleaned lines
    cleaned_lines = []

    # 1. 屏蔽开头的干扰信息（逐行判断，避免正则贪婪匹配误删正文）
    # 1. 冒頭の干渉情報を屏蔽（行ごとに判断し、正規表現の貪欲マッチングによる本文誤削除を防止）
    # 1. Block leading interference info (check line by line to avoid regex greedy matching deleting body text)

    # 设置一个标志位，标记是否还处于文件头部的干扰区域
    # ファイルヘッダーの干渉領域にいるかどうかを示すフラグを設定
    # Set a flag to indicate whether we are still in the header interference zone
    skip_header = True

    # 逐行遍历原始文本的每一行
    # 元のテキストの各行を順に走査
    # Iterate through each line of the original text
    for line in lines:
        # 如果仍处于头部干扰区域，且当前行以"="开头或包含"链接"二字
        # まだヘッダー干渉領域にあり、現在の行が「=」で始まるか「リンク」を含む場合
        # If still in the header zone and the current line starts with '=' or contains '链接' (link)
        if skip_header and (line.strip().startswith('=') or '链接' in line):
            # 跳过该行，不加入清理后的列表
            # その行をスキップし、クリーンアップ後のリストに追加しない
            # Skip this line, do not add it to the cleaned list
            continue

        # 一旦遇到不符合干扰条件的行，关闭头部跳过模式
        # 干渉条件に合わない行に出会ったら、ヘッダースキップモードをオフにする
        # Once a line doesn't match the interference criteria, turn off header skip mode
        skip_header = False

        # 将当前行加入清理后的列表
        # 現在の行をクリーンアップ後のリストに追加
        # Add the current line to the cleaned list
        cleaned_lines.append(line)

    # 将清理后的行列表重新拼接为一个完整字符串
    # クリーンアップ後の行リストを再度結合して完全な文字列にする
    # Rejoin the cleaned lines into a single complete string
    clean_text = '\n'.join(cleaned_lines)

    # 2. 提取元数据
    # 2. メタデータを抽出
    # 2. Extract metadata

    # 创建一个空字典，用于存放提取到的元数据
    # 抽出したメタデータを格納する空の辞書を作成
    # Create an empty dictionary to store the extracted metadata
    meta = {}

    # 匹配 名称/书名：使用正则表达式查找"名称"或"书名"后面的内容
    # 名称/書名をマッチ：正規表現で「名称」または「書名」の後の内容を探す
    # Match title/book name: use regex to find content after "名称" (name) or "书名" (book name)
    name_match = re.search(r'(?:名称|书名)[/：:\s]+([^\n]+)', clean_text)

    # 如果匹配成功则提取第一组内容并去除首尾空格，否则使用默认值
    # マッチ成功なら第1グループの内容を抽出して前後の空白を除去、失敗ならデフォルト値を使用
    # If matched, extract group 1 and strip whitespace; otherwise use a default value
    meta['名称'] = name_match.group(1).strip() if name_match else "未知名称"

    # 匹配 作者：使用正则表达式查找"作者"或"原作者"后面的内容
    # 著者をマッチ：正規表現で「作者」または「原作者」の後の内容を探す
    # Match author: use regex to find content after "作者" (author) or "原作者" (original author)
    author_match = re.search(r'(?:作者|原作者)[/：:\s]+([^\n]+)', clean_text)

    # 如果匹配成功则提取作者名，否则使用默认值
    # マッチ成功なら著者名を抽出、失敗ならデフォルト値を使用
    # If matched, extract the author name; otherwise use a default value
    meta['作者'] = author_match.group(1).strip() if author_match else "未知作者"

    # 匹配 内容简介（可能是多行，直到遇到第一个"第X卷/章"或连续空行或文本末尾）
    # 内容紹介をマッチ（複数行の可能性あり、最初の「第X巻/章」または連続空行またはテキスト末尾まで）
    # Match synopsis (may be multi-line, until the first "Volume/Chapter X", consecutive blank lines, or end of text)
    intro_pattern = r'(?:内容简介|简介|内容)[/：:\s]+([\s\S]*?)(?=\n第[零一二三四五六七八九十百千万\d]+[卷章]|\n\n|\Z)'

    # 使用正则表达式搜索简介内容
    # 正規表現で内容紹介を検索
    # Search for the synopsis content using regex
    intro_match = re.search(intro_pattern, clean_text)

    # 如果匹配成功则提取简介内容，否则使用默认值
    # マッチ成功なら内容紹介を抽出、失敗ならデフォルト値を使用
    # If matched, extract the synopsis; otherwise use a default value
    meta['内容简介'] = intro_match.group(1).strip() if intro_match else "无简介"

    # 返回清理后的文本和元数据字典
    # クリーンアップ後のテキストとメタデータ辞書を返す
    # Return the cleaned text and the metadata dictionary
    return clean_text, meta


# 定义解析小说卷章结构的函数
# 小説の巻・章構造を解析する関数を定義
# Define a function to parse the novel's volume/chapter structure
def parse_novel_structure(text):
    """
    解析卷和章，构建多层嵌套字典。
    使用 finditer 获取标题索引，通过字符串切片获取内容，确保内容100%不漏字。

    巻と章を解析し、多層ネスト辞書を構築する。
    finditerを使用してタイトルインデックスを取得し、文字列スライスで内容を取得して、内容の100%漏れなさを保証する。

    Parse volumes and chapters, building a multi-level nested dictionary.
    Uses finditer to get title indices and string slicing to extract content, ensuring 100% content integrity.
    """
    # 编译正则表达式：匹配"第X卷"或"第X章"格式的标题行
    # 正規表現をコンパイル：「第X巻」または「第X章」形式のタイトル行にマッチ
    # Compile regex: match title lines in the format "第X卷" (Volume X) or "第X章" (Chapter X)
    # 其中数字部分支持中文数字和阿拉伯数字，^和MULTILINE确保匹配行首
    # 数字部分は中国語数字とアラビア数字をサポート、^とMULTILINEで行頭マッチを保証
    # The number part supports both Chinese numerals and Arabic digits; ^ with MULTILINE ensures line-start matching
    title_pattern = re.compile(r'^[ \t]*(第[零一二三四五六七八九十百千万\d]+[卷章][^\n]*)', re.MULTILINE)

    # 使用 finditer 获取所有匹配的标题及其在文本中的位置索引
    # finditerを使用してすべてのマッチするタイトルとそのテキスト内の位置インデックスを取得
    # Use finditer to get all matching titles and their positional indices in the text
    matches = list(title_pattern.finditer(text))

    # 创建一个空字典，用于存放解析后的小说结构
    # 解析後の小説構造を格納する空の辞書を作成
    # Create an empty dictionary to store the parsed novel structure
    novel_content = {}

    # 初始化当前卷名为默认卷名
    # 現在の巻名をデフォルト巻名に初期化
    # Initialize the current volume name to the default volume name
    current_volume = DEFAULT_VOLUME

    # 如果没有匹配到任何卷或章标题
    # 巻や章のタイトルが一つもマッチしなかった場合
    # If no volume or chapter titles were matched at all
    if not matches:
        # 将整篇文本作为一章存入默认卷下
        # テキスト全体を1つの章としてデフォルト巻の下に格納
        # Store the entire text as a single chapter under the default volume
        novel_content[DEFAULT_VOLUME] = {"全文内容": text.strip()}
        # 直接返回结果
        # 結果を直接返す
        # Return the result directly
        return novel_content

    # 遍历所有匹配到的标题
    # すべてのマッチしたタイトルを走査
    # Iterate over all matched titles
    for i, match in enumerate(matches):
        # 提取标题文本并去除首尾空格
        # タイトルテキストを抽出して前後の空白を除去
        # Extract the title text and strip leading/trailing whitespace
        title = match.group(1).strip()

        # 记录当前标题结束位置（即正文内容的起始位置）
        # 現在のタイトルの終了位置（すなわち本文内容の開始位置）を記録
        # Record the end position of the current title (i.e., the start position of the body content)
        start_idx = match.end()

        # 截取当前标题到下一个标题之间的所有内容作为正文
        # 現在のタイトルから次のタイトルまでのすべての内容を本文として切り出す
        # Slice all content between the current title and the next title as body text
        # 如果是最后一个标题，则截取到文本末尾
        # 最後のタイトルの場合、テキスト末尾まで切り出す
        # If it's the last title, slice to the end of the text
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)

        # 提取正文内容并去除首尾空格
        # 本文内容を抽出して前後の空白を除去
        # Extract the body content and strip leading/trailing whitespace
        content = text[start_idx:end_idx].strip()

        # 判断当前标题是"卷"还是"章"
        # 現在のタイトルが「巻」か「章」かを判断
        # Determine whether the current title is a "volume" or a "chapter"

        # 如果匹配到"第X卷"格式
        # 「第X巻」形式にマッチした場合
        # If it matches the "Volume X" format
        if re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', title):
            # 更新当前卷名为该卷标题
            # 現在の巻名をその巻タイトルに更新
            # Update the current volume name to this volume's title
            current_volume = title
            # 如果该卷尚未在字典中，初始化一个空字典
            # その巻がまだ辞書にない場合、空の辞書で初期化
            # If this volume is not yet in the dictionary, initialize an empty dict
            if current_volume not in novel_content:
                novel_content[current_volume] = {}

        # 如果匹配到"第X章"格式
        # 「第X章」形式にマッチした場合
        # If it matches the "Chapter X" format
        elif re.match(r'^第[零一二三四五六七八九十百千万\d]+章', title):
            # 确保当前卷在字典中存在
            # 現在の巻が辞書に存在することを確認
            # Ensure the current volume exists in the dictionary
            if current_volume not in novel_content:
                novel_content[current_volume] = {}

            # 防止作者写错导致章节名重复覆盖，若重复则追加序号
            # 著者の書き間違いによる章名の重複上書きを防止、重複すれば番号を追加
            # Prevent duplicate chapter names from overwriting each other; append a counter if duplicated
            base_title = title
            # 初始化重复计数器
            # 重複カウンターを初期化
            # Initialize the duplicate counter
            counter = 1
            # 当章节名已存在时，循环追加"重复_X"后缀
            # 章名が既に存在する場合、「重複_X」サフィックスを追加するループ
            # While the chapter name already exists, loop to append a "(duplicate_X)" suffix
            while title in novel_content[current_volume]:
                title = f"{base_title} (重复_{counter})"
                # 计数器递增
                # カウンターをインクリメント
                # Increment the counter
                counter += 1

            # 将章节名和对应正文内容存入当前卷的字典中
            # 章名と対応する本文内容を現在の巻の辞書に格納
            # Store the chapter name and its corresponding body content in the current volume's dictionary
            novel_content[current_volume][title] = content

    # 返回完整的小说结构字典
    # 完全な小説構造辞書を返す
    # Return the complete novel structure dictionary
    return novel_content


# 定义文本自动换行函数
# テキスト自動改行関数を定義
# Define a text auto-wrapping function
def wrap_text_content(content, max_len):
    """
    限制单行字数，达到限制值时智能换行（仅处理最里面的内容）

    1行の文字数を制限し、制限値に達したらインテリジェントに改行（最も内側の内容のみ処理）

    Limit characters per line; intelligently wrap when the limit is reached (only processes innermost content)
    """
    # 将内容按换行符分割为行列表
    # 内容を改行文字で分割して行リストにする
    # Split the content into a list of lines by newline
    lines = content.split('\n')

    # 创建一个空列表，用于存放处理后的行
    # 処理後の行を格納する空のリストを作成
    # Create an empty list to store the processed lines
    wrapped_lines = []

    # 逐行遍历处理
    # 行ごとに走査して処理
    # Iterate through each line for processing
    for line in lines:
        # 如果当前行为空行（去除空格后为空），直接保留
        # 現在の行が空行の場合（空白除去後が空）、そのまま保持
        # If the current line is blank (empty after stripping), keep it as is
        if not line.strip():
            # 将空行原样加入结果列表
            # 空行をそのまま結果リストに追加
            # Append the blank line to the result list as is
            wrapped_lines.append(line)
            # 跳过后续处理，进入下一行
            # 後続の処理をスキップして次の行へ
            # Skip further processing and move to the next line
            continue

        # 如果当前行长度未超过最大限制，直接保留
        # 現在の行の長さが最大制限を超えていない場合、そのまま保持
        # If the current line length does not exceed the maximum limit, keep it as is
        if len(line) <= max_len:
            # 将未超限的行加入结果列表
            # 制限を超えていない行を結果リストに追加
            # Append the within-limit line to the result list
            wrapped_lines.append(line)
        # 如果当前行超长，需要进行折行处理
        # 現在の行が長すぎる場合、折り返し処理が必要
        # If the current line is too long, it needs wrapping
        else:
            # 超长行进行折行处理：循环直到剩余部分不再超长
            # 長すぎる行の折り返し処理：残り部分が制限を超えなくなるまでループ
            # Wrapping for overly long lines: loop until the remaining part is within the limit
            while len(line) > max_len:
                # 初始切割位置设为最大长度
                # 初期カット位置を最大長に設定
                # Set the initial cut position to the maximum length
                cut_idx = max_len
                # 定义中英文标点符号集合，用于寻找合适的断句位置
                # 中国語と英語の句読点集合を定義、適切な改行位置を探すために使用
                # Define a set of Chinese and English punctuation marks for finding suitable break points
                punctuations = "，。！？；：、,.!?;:""'】）"
                # 从最大长度位置向前搜索（最多回退10个字符），寻找标点符号
                # 最大長の位置から前方に検索（最大10文字まで戻す）、句読点を探す
                # Search backwards from the max length position (up to 10 characters) for punctuation
                for i in range(max_len, max(0, max_len - 10), -1):
                    # 如果在搜索范围内找到标点符号
                    # 検索範囲内で句読点を見つけた場合
                    # If a punctuation mark is found within the search range
                    if line[i] in punctuations:
                        # 将切割位置设在标点符号之后（保留标点在上一行末尾）
                        # カット位置を句読点の後に設定（句読点を前の行の末尾に保持）
                        # Set the cut position right after the punctuation (keep punctuation at end of previous line)
                        cut_idx = i + 1
                        # 找到后立即跳出搜索循环
                        # 見つかったら直ちに検索ループを抜ける
                        # Break out of the search loop immediately once found
                        break
                # 将切割出的这一段加入结果列表
                # カットした部分を結果リストに追加
                # Append the sliced segment to the result list
                wrapped_lines.append(line[:cut_idx])
                # 更新剩余未处理的文本
                # 残りの未処理テキストを更新
                # Update the remaining unprocessed text
                line = line[cut_idx:]
            # 循环结束后，如果还有剩余文本（不为空）
            # ループ終了後、まだ残りテキストがある場合（空でない）
            # After the loop ends, if there is remaining text (not empty)
            if line:
                # 将最后剩余的文本加入结果列表
                # 最後に残ったテキストを結果リストに追加
                # Append the last remaining text to the result list
                wrapped_lines.append(line)

    # 将所有处理后的行重新用换行符拼接并返回
    # すべての処理済み行を改行文字で再結合して返す
    # Rejoin all processed lines with newline characters and return
    return '\n'.join(wrapped_lines)


# 定义保存输出文件的函数
# 出力ファイルを保存する関数を定義
# Define a function to save the output files
def save_outputs(final_dict, directory, base_name):
    """
    先保存为JSON，再转换为排版好的TXT

    まずJSONとして保存し、次に整形されたTXTに変換

    First save as JSON, then convert to a formatted TXT
    """

    # 1. 保存为 JSON（保证数据结构绝对正确，无冲突）
    # 1. JSONとして保存（データ構造の絶対的な正確性を保証、衝突なし）
    # 1. Save as JSON (ensures data structure is absolutely correct, no conflicts)

    # 拼接 JSON 文件的完整路径
    # JSONファイルの完全なパスを結合
    # Concatenate the full path for the JSON file
    json_path = os.path.join(directory, f"{base_name}_parsed.json")

    # 以 UTF-8 编码打开（创建）JSON 文件进行写入
    # UTF-8エンコーディングでJSONファイルを開く（作成）して書き込み
    # Open (create) the JSON file with UTF-8 encoding for writing
    with open(json_path, 'w', encoding='utf-8') as f:
        # 将最终字典序列化为 JSON 格式写入文件
        # 最終辞書をJSON形式にシリアライズしてファイルに書き込む
        # Serialize the final dictionary to JSON format and write to file
        # ensure_ascii=False 保证中文等非ASCII字符正常显示
        # ensure_ascii=False で中国語などの非ASCII文字が正常に表示されることを保証
        # ensure_ascii=False ensures non-ASCII characters like Chinese display correctly
        # indent=4 设置缩进为4个空格，便于人类阅读
        # indent=4 でインデントを4スペースに設定、人間が読みやすくする
        # indent=4 sets indentation to 4 spaces for human readability
        json.dump(final_dict, f, ensure_ascii=False, indent=4)

    # 打印 JSON 保存成功的信息
    # JSON保存成功の情報を出力
    # Print the JSON save success message
    print(f"[成功] 结构化数据已保存至: {json_path}")

    # 2. 转换为人类可读的 TXT
    # 2. 人間が読めるTXTに変換
    # 2. Convert to a human-readable TXT

    # 拼接 TXT 文件的完整路径
    # TXTファイルの完全なパスを結合
    # Concatenate the full path for the TXT file
    txt_path = os.path.join(directory, f"{base_name}_formatted.txt")

    # 以 UTF-8 编码打开（创建）TXT 文件进行写入
    # UTF-8エンコーディングでTXTファイルを開く（作成）して書き込み
    # Open (create) the TXT file with UTF-8 encoding for writing
    with open(txt_path, 'w', encoding='utf-8') as f:
        # 写入书名标题行
        # 書名タイトル行を書き込む
        # Write the book title line
        f.write(f"《{final_dict['名称']}》\n")
        # 写入作者信息行
        # 著者情報行を書き込む
        # Write the author information line
        f.write(f"作者：{final_dict['作者']}\n")
        # 写入内容简介标题和内容
        # 内容紹介のタイトルと内容を書き込む
        # Write the synopsis title and content
        f.write(f"内容简介：\n{final_dict['内容简介']}\n\n")
        # 写入一条由50个等号组成的分隔线
        # 50個の等号からなる区切り線を書き込む
        # Write a separator line consisting of 50 equal signs
        f.write("=" * 50 + "\n\n")

        # 写入正文：遍历每一卷及其包含的章节
        # 本文を書き込む：各巻とその章を走査
        # Write the body: iterate over each volume and its chapters
        for vol, chapters in final_dict['正文'].items():
            # 写入卷标题，用等号和方括号装饰
            # 巻タイトルを書き込む、等号と角括弧で装飾
            # Write the volume title, decorated with equal signs and brackets
            f.write(f"{'='*20} 【{vol}】 {'='*20}\n\n")
            # 遍历当前卷下的每一章
            # 現在の巻の各章を走査
            # Iterate over each chapter in the current volume
            for chap, content in chapters.items():
                # 写入章节标题，前面加两个空格缩进
                # 章タイトルを書き込む、前に2スペースのインデントを追加
                # Write the chapter title with a two-space indent
                f.write(f"  {chap}\n")
                # 对章节正文内容进行智能换行排版
                # 章の本文内容にインテリジェントな改行レイアウトを適用
                # Apply intelligent line-wrapping formatting to the chapter body content
                formatted_content = wrap_text_content(content, MAX_LINE_LENGTH)
                # 为每一行添加两个空格的首行缩进（空行保持为空）
                # 各行に2スペースの先頭インデントを追加（空行は空のまま）
                # Add a two-space indent to each line (blank lines remain blank)
                indented_content = '\n'.join(['  ' + line if line.strip() else '' for line in formatted_content.split('\n')])
                # 将缩进后的章节内容写入文件，末尾加两个换行符作为章节间距
                # インデント付きの章内容をファイルに書き込む、末尾に2つの改行で章間スペースを追加
                # Write the indented chapter content to the file, with two trailing newlines as chapter spacing
                f.write(f"{indented_content}\n\n")

    # 打印 TXT 保存成功的信息
    # TXT保存成功の情報を出力
    # Print the TXT save success message
    print(f"[成功] 排版后的文本已保存至: {txt_path}")


# 定义主函数，程序执行的入口
# メイン関数を定義、プログラム実行のエントリポイント
# Define the main function, the entry point of program execution
def main():
    # 打印一条由40个等号组成的装饰线
    # 40個の等号からなる装飾線を出力
    # Print a decorative line of 40 equal signs
    print("="*40)
    # 打印工具标题
    # ツールタイトルを出力
    # Print the tool title
    print(" 小说文本解析与排版工具 (纯标准库版) ")
    # 打印另一条装饰线
    # もう一本の装飾線を出力
    # Print another decorative line
    print("="*40)

    # 获取用户输入的目录路径，去除首尾空格和引号
    # ユーザーが入力したディレクトリパスを取得、前後の空白と引用符を除去
    # Get the directory path from user input, strip whitespace and quotes
    directory = input("请输入小说文件所在的目录路径 (例如 D:\\novels): ").strip().strip('"')
    # 获取用户输入的文件名，去除首尾空格和引号
    # ユーザーが入力したファイル名を取得、前後の空白と引用符を除去
    # Get the filename from user input, strip whitespace and quotes
    filename = input("请输入小说文件名 (例如 novel.txt): ").strip().strip('"')

    # 将目录和文件名拼接为完整的文件路径
    # ディレクトリとファイル名を結合して完全なファイルパスにする
    # Concatenate the directory and filename into a full file path
    filepath = os.path.join(directory, filename)

    # 检查文件是否存在于指定路径
    # ファイルが指定パスに存在するか確認
    # Check if the file exists at the specified path
    if not os.path.exists(filepath):
        # 如果文件不存在，打印错误信息
        # ファイルが存在しない場合、エラー情報を出力
        # If the file does not exist, print an error message
        print(f"\n[错误] 找不到文件: {filepath}")
        # 直接返回，终止主函数执行
        # 直接リターンしてメイン関数の実行を終了
        # Return immediately, terminating the main function
        return

    # 打印步骤1的提示信息
    # ステップ1のヒント情報を出力
    # Print the prompt message for step 1
    print("\n[1/4] 正在读取文件并检测编码...")
    # 调用安全读取函数，读取文件原始文本
    # 安全読み込み関数を呼び出し、ファイルの元テキストを読み込む
    # Call the safe read function to read the raw text of the file
    raw_text = read_file_safely(filepath)

    # 打印步骤2的提示信息
    # ステップ2のヒント情報を出力
    # Print the prompt message for step 2
    print("[2/4] 正在清理头部干扰信息并提取元数据...")
    # 调用清理函数，获取清理后的文本和元数据字典
    # クリーンアップ関数を呼び出し、クリーンアップ後のテキストとメタデータ辞書を取得
    # Call the clean function to get the cleaned text and metadata dictionary
    cleaned_text, meta_data = clean_header_and_meta(raw_text)

    # 打印步骤3的提示信息
    # ステップ3のヒント情報を出力
    # Print the prompt message for step 3
    print("[3/4] 正在解析卷/章结构并提取内容 (绝不漏字)...")
    # 调用结构解析函数，获取小说的卷章嵌套字典
    # 構造解析関数を呼び出し、小説の巻・章ネスト辞書を取得
    # Call the structure parsing function to get the novel's volume/chapter nested dictionary
    novel_structure = parse_novel_structure(cleaned_text)

    # 组装最终字典，将元数据和正文结构合并
    # 最終辞書を組み立て、メタデータと本文構造を統合
    # Assemble the final dictionary, merging metadata and body structure
    final_dict = {
        # 书名
        # 書名
        # Book title
        "名称": meta_data['名称'],
        # 作者
        # 著者
        # Author
        "作者": meta_data['作者'],
        # 内容简介
        # 内容紹介
        # Synopsis
        "内容简介": meta_data['内容简介'],
        # 正文结构（卷-章嵌套字典）
        # 本文構造（巻-章ネスト辞書）
        # Body structure (volume-chapter nested dictionary)
        "正文": novel_structure
    }

    # 打印步骤4的提示信息
    # ステップ4のヒント情報を出力
    # Print the prompt message for step 4
    print("[4/4] 正在保存 JSON 与 TXT 文件...")
    # 获取不含扩展名的文件基本名，用作输出文件的前缀
    # 拡張子なしのファイル基本名を取得、出力ファイルのプレフィックスとして使用
    # Get the base filename without extension, used as a prefix for output files
    base_name = os.path.splitext(filename)[0]
    # 调用保存函数，输出 JSON 和 TXT 两个文件
    # 保存関数を呼び出し、JSONとTXTの2つのファイルを出力
    # Call the save function to output both JSON and TXT files
    save_outputs(final_dict, directory, base_name)

    # 打印全部任务完成的提示信息
    # 全タスク完了のヒント情報を出力
    # Print a message indicating all tasks are complete
    print("\n[完成] 所有任务执行完毕！")
    # 打印统计信息：共解析出多少卷、多少章
    # 統計情報を出力：合計何巻、何章を解析したか
    # Print statistics: how many volumes and chapters were parsed in total
    print(f"共解析出 {len(novel_structure)} 卷，总计 {sum(len(chaps) for chaps in novel_structure.values())} 章。")


# Python 标准入口检查：仅在脚本被直接运行时执行 main()
# Python標準エントリチェック：スクリプトが直接実行された場合のみmain()を実行
# Python standard entry check: only execute main() when the script is run directly
if __name__ == "__main__":
    # 调用主函数，启动程序
    # メイン関数を呼び出し、プログラムを開始
    # Call the main function to start the program
    main()
