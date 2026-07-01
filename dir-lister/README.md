================================================================================
                        dir-lister.py  README
================================================================================

【中文】

一、脚本简介
--------------------------------------------------------------------------------
dir-lister.py 是一个轻量级的目录文件列表生成工具。它会自动扫描脚本自身所在的
目录及其所有子目录，收集全部文件的路径信息（不包含文件夹），并将结果以格式化
的文本文件输出，方便用户快速了解当前目录结构。

二、运行环境
--------------------------------------------------------------------------------
  - Python 3.x
  - 仅依赖标准库 os 模块，无需安装任何第三方包

三、使用方法
--------------------------------------------------------------------------------
  将 dir-lister.py 放置到你想扫描的目录中，然后在终端/命令行中执行：

      python dir-lister.py

  脚本执行完成后，会在当前工作目录下生成名为「test_文件列表.txt」的文本文件。

四、核心功能
--------------------------------------------------------------------------------
  1. 递归目录扫描
     脚本以自身所在目录为起点，通过递归方式遍历所有子文件夹，收集每一个文件的
     完整绝对路径。自动跳过无法访问的目录（异常安全处理）。

  2. 路径规范化处理
     将扫描到的所有路径中的反斜杠（\）统一替换为正斜杠（/），确保在不同操作
     系统下输出格式一致。

  3. 格式化文本输出
     将文件列表写入「test_文件列表.txt」文件，内容包括：
       - 标题与分隔线
       - 每个文件以「[文件] 文件名」的格式逐行记录
       - 底部统计汇总：总项目数、文件数量、文件夹数量
     使用 UTF-8 编码，支持中文文件名。每次运行会覆盖上一次的结果。

  4. 控制台摘要输出
     运行结束后，在终端显示：
       - 文件保存位置（绝对路径）
       - 扫描到的总项目数
       - 文件与文件夹的分别计数

五、函数说明
--------------------------------------------------------------------------------
  get_current_folder_files()
    → 递归获取脚本所在目录及所有子目录下的文件路径列表（排除文件夹）。
    → 返回值：包含所有文件绝对路径的列表。

  write_to_txt(items)
    → 将文件列表写入 txt 文本文件。
    → 参数 items：包含文件路径的列表。
    → 返回值：生成的 txt 文件的绝对路径。

  main()
    → 主控制函数，协调调用上述函数，完成路径处理、文件写入及控制台输出。

六、输出示例
--------------------------------------------------------------------------------
  test_文件列表.txt 内容示例：

      文件内容列表
      ==============================
      [文件] index.html
      [文件] style.css
      [文件] script.js
      [文件] logo.png

      ==============================
      总计: 4 个项目
      文件数量: 4
      文件夹数量: 0

  控制台输出示例：

      请等待
      脚本已工作完成,文件列表已保存至: /home/user/test_文件列表.txt
      共扫描到 4 个项目
      其中文件: 4 个，文件夹: 0 个


================================================================================

【日本語】

一、スクリプト概要
--------------------------------------------------------------------------------
dir-lister.py は、軽量なディレクトリファイルリスト生成ツールです。スクリプト
自身が配置されているディレクトリおよびそのすべてのサブディレクトリを自動的に
スキャンし、ファイルのパス情報を収集して（フォルダは除外）、整形されたテキスト
ファイルとして出力します。

二、動作環境
--------------------------------------------------------------------------------
  - Python 3.x
  - 標準ライブラリ os モジュールのみ使用。サードパーティパッケージのインストール不要

三、使用方法
--------------------------------------------------------------------------------
  dir-lister.py をスキャンしたいディレクトリに配置し、ターミナルまたはコマンド
  プロンプトで以下を実行します：

      python dir-lister.py

  実行完了後、現在の作業ディレクトリに「test_文件列表.txt」というテキストファイル
  が生成されます。

四、コア機能
--------------------------------------------------------------------------------
  1. 再帰的ディレクトリスキャン
     スクリプト自身のディレクトリを起点として、再帰的にすべてのサブフォルダを
     走査し、各ファイルの完全な絶対パスを収集します。アクセスできないディレクトリ
     は自動的にスキップされます（例外安全処理）。

  2. パス正規化処理
     スキャンされたすべてのパスに含まれるバックスラッシュ（\）をスラッシュ（/）
     に統一置換し、異なるOS環境でも一貫した出力フォーマットを保証します。

  3. 整形テキスト出力
     ファイルリストを「test_文件列表.txt」ファイルに書き込みます。内容は以下の通り：
       - タイトルと区切り線
       - 各ファイルは「[文件] ファイル名」の形式で1行ずつ記録
       - 下部に統計サマリー：総項目数、ファイル数、フォルダ数
     UTF-8 エンコーディングを使用し、日本語や中国語のファイル名にも対応。
     実行のたびに前回結果を上書きします。

  4. コンソールサマリー出力
     実行終了後、ターミナルに以下を表示：
       - ファイル保存場所（絶対パス）
       - スキャンした総項目数
       - ファイルとフォルダの個別カウント

五、関数説明
--------------------------------------------------------------------------------
  get_current_folder_files()
    → スクリプト所在ディレクトリおよび全サブディレクトリ下のファイルパスリストを
       再帰的に取得（フォルダは除外）。
    → 戻り値：全ファイルの絶対パスを含むリスト。

  write_to_txt(items)
    → ファイルリストを txt テキストファイルに書き込み。
    → 引数 items：ファイルパスを含むリスト。
    → 戻り値：生成された txt ファイルの絶対パス。

  main()
    → メイン制御関数。上記関数の呼び出しを調整し、パス処理、ファイル書き込み、
       コンソール出力を完了させます。

六、出力例
--------------------------------------------------------------------------------
  test_文件列表.txt の内容例：

      文件内容列表
      ==============================
      [文件] index.html
      [文件] style.css
      [文件] script.js
      [文件] logo.png

      ==============================
      总计: 4 个项目
      文件数量: 4
      文件夹数量: 0

  コンソール出力例：

      请等待
      脚本已工作完成,我文件列表已保存至: /home/user/test_文件列表.txt
      共扫描到 4 个项目
      其中文件: 4 个，文件夹: 0 个


================================================================================

【English】

1. Script Overview
--------------------------------------------------------------------------------
dir-lister.py is a lightweight directory file listing tool. It automatically
scans the directory where the script itself is located, along with all of its
subdirectories, collects file path information (excluding folders), and outputs
the results as a formatted text file for quick review of the directory structure.

2. Requirements
--------------------------------------------------------------------------------
  - Python 3.x
  - Only uses the standard library "os" module; no third-party packages required

3. Usage
--------------------------------------------------------------------------------
  Place dir-lister.py into the directory you want to scan, then run the
  following in your terminal or command prompt:

      python dir-lister.py

  After execution, a text file named "test_文件列表.txt" will be generated in
  the current working directory.

4. Core Features
--------------------------------------------------------------------------------
  1. Recursive Directory Scanning
     Starting from the script's own directory, the tool recursively traverses
     all subfolders and collects the full absolute path of every file.
     Inaccessible directories are automatically skipped (exception-safe handling).

  2. Path Normalization
     All backslashes (\) in scanned paths are uniformly replaced with forward
     slashes (/), ensuring consistent output formatting across different
     operating systems.

  3. Formatted Text Output
     The file list is written to "test_文件列表.txt" with the following content:
       - A title and separator line
       - Each file recorded line by line in the format "[文件] filename"
       - A summary section at the bottom: total items, file count, folder count
     UTF-8 encoding is used, supporting Chinese/Japanese filenames.
     Each run overwrites the previous result file.

  4. Console Summary Output
     Upon completion, the terminal displays:
       - File save location (absolute path)
       - Total number of scanned items
       - Separate counts for files and folders

5. Function Reference
--------------------------------------------------------------------------------
  get_current_folder_files()
    → Recursively retrieves a list of file paths from the script's directory
      and all subdirectories (folders are excluded).
    → Returns: A list containing absolute paths of all files.

  write_to_txt(items)
    → Writes the file list into a txt text file.
    → Parameter items: A list containing file paths.
    → Returns: The absolute path of the generated txt file.

  main()
    → Main control function that coordinates the above functions, performing
      path processing, file writing, and console output.

6. Output Example
--------------------------------------------------------------------------------
  Example content of test_文件列表.txt:

      文件内容列表
      ==============================
      [文件] index.html
      [文件] style.css
      [文件] script.js
      [文件] logo.png

      ==============================
      总计: 4 个项目
      文件数量: 4
      文件夹数量: 0

  Example console output:

      请等待
      脚本已工作完成,我文件列表已保存至: /home/user/test_文件列表.txt
      共扫描到 4 个项目
      其中文件: 4 个，文件夹: 0 个

================================================================================


