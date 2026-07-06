################################################################################
# FFmpeg Media Merger v3 - 多语言注释映射文件 (Multilingual Comments Mapping)
# 作者 / Author / 著者: 张龙 (Zhang Long)
# 说明：本文件包含源码中所有中文注释对应的英文(EN)与日文(JP)翻译。
#      请通过 [代码锚点] 定位源码中的具体位置。
################################################################################


======================================================================
[锚点 1] 文件头 Docstring (文件开篇的多行注释)
======================================================================
[中文] 
脚本名称: FFmpeg Media Merger v3 (基于流检测的重构版本)
作者署名: 张龙
脚本介绍:
本脚本是一个基于 Python 编写的高级 FFmpeg 媒体合并工具。其核心创新点在于摒弃了传统仅依赖文件扩展名来判断媒体类型的做法，转而通过调用 ffprobe 对文件内部的实际流（视频流、音频流、字幕流）进行深度检测与解析。这使得工具能够精准识别诸如“包含纯音频的 .webm 文件”或“包含字幕流的 .mkv 文件”等复杂情况，从而实现无损、高效的媒体封装。
主要功能包括：
1. 智能流检测：利用 ffprobe 获取真实的 codec_type，确保分类准确无误。
2. 无损合并：采用 stream copy 模式，将视频、多音轨、多字幕无损封装至 MKV 容器。
3. 降级容错机制：当字幕流直接 copy 失败时，自动尝试重编码为 MKV 兼容格式。
4. 灵活的工作模式：支持交互式命令行选择、自动同名匹配合并以及命令行参数直接指定。
5. 跨平台兼容：自动在系统 PATH 及常见安装目录中查找 ffmpeg/ffprobe 可执行文件。

[EN]
Script Name: FFmpeg Media Merger v3 (Refactored version based on stream detection)
Author: Zhang Long
Introduction:
This script is an advanced FFmpeg media merging tool written in Python. Its core innovation lies in abandoning the traditional method of relying solely on file extensions to determine media types. Instead, it calls ffprobe to deeply detect and parse the actual streams (video, audio, subtitle) inside the file. This allows the tool to accurately identify complex cases such as ".webm files containing pure audio" or ".mkv files containing subtitle streams", thereby achieving lossless and efficient media muxing.
Main features include:
1. Intelligent stream detection: Uses ffprobe to get the real codec_type, ensuring accurate classification.
2. Lossless merging: Uses stream copy mode to losslessly mux video, multiple audio tracks, and multiple subtitles into an MKV container.
3. Fallback fault-tolerance mechanism: Automatically attempts to re-encode subtitles into an MKV-compatible format when direct subtitle copy fails.
4. Flexible working modes: Supports interactive command-line selection, automatic same-name matching merge, and direct specification via command-line arguments.
5. Cross-platform compatibility: Automatically searches for ffmpeg/ffprobe executables in the system PATH and common installation directories.

[JP]
スクリプト名: FFmpeg Media Merger v3 (ストリーム検出に基づくリファクタリング版)
著者: 張龍 (Zhang Long)
スクリプト紹介:
本スクリプトはPythonで記述された高度なFFmpegメディア結合ツールです。その中核となるイノベーションは、メディアタイプを判断するためにファイル拡張子だけに依存する従来の方法を廃止し、代わりにffprobeを呼び出してファイル内部の実際のストリーム（ビデオ、オーディオ、字幕）を深く検出・解析する点にあります。これにより、「純粋なオーディオを含む.webmファイル」や「字幕ストリームを含む.mkvファイル」といった複雑なケースを正確に識別し、無劣化かつ効率的なメディア多重化を実現します。
主な機能は以下の通りです：
1. インテリジェントなストリーム検出：ffprobeを利用して実際のcodec_typeを取得し、正確な分類を保証します。
2. 無劣化結合：ストリームコピーモードを使用し、ビデオ、複数のオーディオトラック、複数の字幕をMKVコンテナに無劣化で多重化します。
3. フォールバックフォールトトレランス機制：字幕ストリームの直接コピーが失敗した場合、MKV互換フォーマットへの再エンコードを自動的に試みます。
4. 柔軟な動作モード：対話型コマンドライン選択、自動同名マッチング結合、およびコマンドライン引数による直接指定をサポートします。
5. クロ스플레이ヤー互換性：システムPATHおよび一般的なインストールディレクトリ内でffmpeg/ffprobeの実行ファイルを自動的に検索します。


======================================================================
[锚点 2] 导入模块 (Import 语句上方的注释)
======================================================================
[中文] 
导入操作系统接口模块，用于环境变量和路径判断
导入系统特定参数模块，用于退出程序
导入子进程模块，用于调用外部 ffmpeg 和 ffprobe 命令
导入 JSON 模块，用于解析 ffprobe 返回的 JSON 数据
导入 shutil 模块，用于跨平台查找可执行文件
导入 pathlib 模块，用于面向对象的路径操作
导入 typing 模块，用于类型提示，增强代码可读性

[EN]
Import OS interface module for environment variables and path judgments
Import system-specific parameters module for exiting the program
Import subprocess module for calling external ffmpeg and ffprobe commands
Import JSON module for parsing JSON data returned by ffprobe
Import shutil module for cross-platform executable file searching
Import pathlib module for object-oriented path operations
Import typing module for type hinting to enhance code readability

[JP]
環境変数とパスの判定のためにOSインターフェースモジュールをインポート
プログラムを終了するためにシステム固有のパラメータモジュールをインポート
外部のffmpegおよびffprobeコマンドを呼び出すためにサブプロセスモジュールをインポート
ffprobeが返すJSONデータを解析するためにJSONモジュールをインポート
クロスプラットフォームで実行ファイルを検索するためにshutilモジュールをインポート
オブジェクト指向のパス操作のためにpathlibモジュールをインポート
コードの可読性を向上させるための型ヒント用にtypingモジュールをインポート


======================================================================
[锚点 3] 全局变量 ALL_MEDIA_EXTENSIONS
======================================================================
[中文] 
扩展名白名单（仅用于初筛，不作为最终分类依据）
定义支持的媒体文件扩展名集合，用于快速过滤非媒体文件
视频容器 / 纯视频格式
既可能是视频也可能是音频的容器格式
音频格式
原始视频流格式
字幕格式

[EN]
Extension whitelist (used only for initial screening, not as final classification basis)
Define a set of supported media file extensions for quick filtering of non-media files
Video containers / pure video formats
Container formats that can be either video or audio
Audio formats
Raw video stream formats
Subtitle formats

[JP]
拡張子ホワイトリスト（初期スクリーニングのみに使用され、最終的な分類の基準としては使用されません）
非メディアファイルを迅速にフィルタリングするために、サポートされているメディアファイル拡張子のセットを定義
ビデオコンテナ / 純粋なビデオフォーマット
ビデオまたはオーディオのいずれにもなり得るコンテナフォーマット
オーディオフォーマット
生のビデオストリームフォーマット
字幕フォーマット


======================================================================
[锚点 4] 类 StreamInfo 及其方法
======================================================================
[中文] 
定义单个文件的流信息数据类
单个文件的流信息
使用 __slots__ 限制属性，优化内存占用
初始化方法，传入文件路径
保存文件路径对象 / 标记是否包含视频流 / 标记是否包含音频流 / 标记是否包含字幕流
视频流数量 / 音频流数量 / 字幕流数量
存储详细的流信息字典列表
定义对象的字符串表示形式，便于调试打印
初始化标签列表
如果有视频流，添加视频数量标签 / 如果有音频流，添加音频数量标签 / 如果有字幕流，添加字幕数量标签
返回格式化的字符串，包含文件名和流标签

[EN]
Define data class for stream information of a single file
Stream information of a single file
Use __slots__ to restrict attributes and optimize memory usage
Initialization method, passing in the file path
Save file path object / Flag whether it contains video stream / Flag whether it contains audio stream / Flag whether it contains subtitle stream
Video stream count / Audio stream count / Subtitle stream count
Store list of detailed stream information dictionaries
Define string representation of the object for easy debug printing
Initialize tag list
If video stream exists, add video count tag / If audio stream exists, add audio count tag / If subtitle stream exists, add subtitle count tag
Return formatted string containing file name and stream tags

[JP]
単一ファイルのストリーム情報データクラスを定義
単一ファイルのストリーム情報
__slots__を使用して属性を制限し、メモリ使用量を最適化
初期化メソッド、ファイルパスを渡す
ファイルパスオブジェクトを保存 / ビデオストリームを含むかどうかをマーク / オーディオストリームを含むかどうかをマーク / 字幕ストリームを含むかどうかをマーク
ビデオストリーム数 / オーディオストリーム数 / 字幕ストリーム数
詳細なストリーム情報辞書のリストを保存
デバッグ印刷を容易にするためにオブジェクトの文字列表現を定義
タグリストを初期化
ビデオストリームがある場合、ビデオ数タグを追加 / オーディオストリームがある場合、オーディオ数タグを追加 / 字幕ストリームがある場合、字幕数タグを追加
ファイル名とストリームタグを含むフォーマットされた文字列を返す


======================================================================
[锚点 5] 类 FFmpegMediaMerger 初始化 (__init__)
======================================================================
[中文] 
定义 FFmpeg 媒体合并器主类
FFmpeg 媒体合并器 — 基于 ffprobe 流检测
初始化方法，可选传入工作目录
解析并保存工作目录的绝对路径，默认为当前目录
设置详细输出模式为 True
查找 ffmpeg 可执行文件路径 / 查找 ffprobe 可执行文件路径
如果找不到 ffmpeg，抛出运行时错误并提示安装方法

[EN]
Define main class for FFmpeg media merger
FFmpeg Media Merger — based on ffprobe stream detection
Initialization method, optionally passing in working directory
Parse and save absolute path of working directory, default to current directory
Set verbose output mode to True
Find ffmpeg executable path / Find ffprobe executable path
If ffmpeg is not found, raise runtime error and prompt installation methods

[JP]
FFmpegメディアマージャーのメインクラスを定義
FFmpegメディアマージャー — ffprobeストリーム検出に基づく
初期化メソッド、オプションで作業ディレクトリを渡す
作業ディレクトリの絶対パスを解析して保存、デフォルトは現在のディレクトリ
詳細出力モードをTrueに設定
ffmpeg実行ファイルパスを検索 / ffprobe実行ファイルパスを検索
ffmpegが見つからない場合、ランタイムエラーをスローしインストール方法を促す


======================================================================
[锚点 6] 方法 _locate_binary
======================================================================
[中文] 
工具方法
静态方法：在 PATH 和常见位置中查找可执行文件
1. 使用 shutil.which 跨平台查找 / 如果找到了，直接返回路径
2. 定义常见安装路径列表
如果是 Windows 系统 (Program Files / WinGet / Scoop 目录)
如果是 macOS 或 Linux 系统 (系统级二进制 / Homebrew / 用户级目录)
根据操作系统确定可执行文件后缀名
遍历所有常见路径 / 拼接完整的候选文件路径 / 如果文件存在，返回其字符串路径
如果都没找到，返回 None

[EN]
Utility methods
Static method: Find executable in PATH and common locations
1. Use shutil.which for cross-platform search / If found, return path directly
2. Define list of common installation paths
If Windows system (Program Files / WinGet / Scoop directories)
If macOS or Linux system (system-level binary / Homebrew / user-level directories)
Determine executable suffix based on operating system
Iterate through all common paths / Concatenate full candidate file path / If file exists, return its string path
If none found, return None

[JP]
ユーティリティメソッド
静的メソッド：PATHおよび一般的な場所で実行ファイルを検索
1. shutil.whichを使用してクロスプラットフォーム検索 / 見つかった場合、パスを直接返す
2. 一般的なインストールパスのリストを定義
Windowsシステムの場合 (Program Files / WinGet / Scoop ディレクトリ)
macOSまたはLinuxシステムの場合 (システムレベルバイナリ / Homebrew / ユーザーレベルディレクトリ)
オペレーティングシステムに基づいて実行ファイルのサフィックスを決定
すべての一般的なパスをループ / 完全な候補ファイルパスを結合 / ファイルが存在する場合、その文字列パスを返す
どれもが見つからない場合、Noneを返す


======================================================================
[锚点 7] 方法 _run_ffprobe
======================================================================
[中文] 
实例方法：用 ffprobe 获取文件流信息
用 ffprobe 获取文件流信息，返回 JSON dict
如果 ffprobe 路径不存在，直接返回 None
构建 ffprobe 命令参数列表 (静默模式 / 输出JSON / 显示流和格式 / 目标文件)
执行子进程命令 (捕获标准输出和错误 / 文本模式 / 30秒超时)
如果返回码为 0 且标准输出不为空，解析 JSON 并返回字典
捕获所有异常，忽略错误 / 失败时返回 None

[EN]
Instance method: Get file stream info using ffprobe
Get file stream info using ffprobe, return JSON dict
If ffprobe path does not exist, return None directly
Build ffprobe command argument list (quiet mode / output JSON / show streams and format / target file)
Execute subprocess command (capture stdout and stderr / text mode / 30s timeout)
If return code is 0 and stdout is not empty, parse JSON and return dictionary
Catch all exceptions, ignore errors / Return None on failure

[JP]
インスタンスメソッド：ffprobeを使用してファイルストリーム情報を取得
ffprobeを使用してファイルストリーム情報を取得し、JSON dictを返す
ffprobeパスが存在しない場合、直接Noneを返す
ffprobeコマンド引数リストを構築 (静黙モード / JSON出力 / ストリームとフォーマット表示 / 対象ファイル)
サブプロセスコマンドを実行 (標準出力とエラーをキャプチャ / テキストモード / 30秒タイムアウト)
リターンコードが0で標準出力が空でない場合、JSONを解析して辞書を返す
すべての例外をキャプチャし、エラーを無視 / 失敗時にNoneを返す


======================================================================
[锚点 8] 方法 probe_file
======================================================================
[中文] 
实例方法：检测文件实际包含的流类型
检测文件实际包含的流类型。优先使用 ffprobe；若不可用则退回到扩展名猜测。
初始化 StreamInfo 对象 / 调用 ffprobe 获取探测结果
如果探测成功且包含 streams 字段，保存详细流信息
遍历每一个流，获取流的类型并转为小写
如果是视频流，视频计数加 1 / 音频流加 1 / 字幕流加 1
根据计数更新布尔标记，返回探测结果
ffprobe 不可用时的退路：按扩展名猜测
获取文件扩展名，去除点号并转为小写
定义常见的视频/音频/字幕扩展名集合
如果扩展名在视频集合中，标记包含视频，容器格式通常也含音频，默认标记包含音频
如果扩展名在音频集合中，标记包含音频 / 字幕集合标记包含字幕
webm/ogg 在退路里两边都算（可能包含音频） / 返回猜测结果

[EN]
Instance method: Detect actual stream types contained in the file
Detect actual stream types contained in the file. Prioritize ffprobe; fallback to extension guessing if unavailable.
Initialize StreamInfo object / Call ffprobe to get probe results
If probe is successful and contains streams field, save detailed stream info
Iterate through each stream, get stream type and convert to lowercase
If video stream, increment video count by 1 / audio by 1 / subtitle by 1
Update boolean flags based on counts, return probe results
Fallback when ffprobe is unavailable: guess by extension
Get file extension, strip dot and convert to lowercase
Define sets of common video/audio/subtitle extensions
If extension is in video set, flag contains video, container formats usually contain audio, default flag contains audio
If extension is in audio set, flag contains audio / subtitle set flag contains subtitle
webm/ogg count as both in fallback (may contain audio) / Return guessed results

[JP]
インスタンスメソッド：ファイルに実際に含まれるストリームタイプを検出
ファイルに実際に含まれるストリームタイプを検出。ffprobeを優先し、利用できない場合は拡張子推測にフォールバック。
StreamInfoオブジェクトを初期化 / ffprobeを呼び出して検出結果を取得
検出が成功しstreamsフィールドを含む場合、詳細なストリーム情報を保存
各ストリームをループし、ストリームタイプを取得して小文字に変換
ビデオストリームならビデオカウントを1増やす / オーディオなら1増やす / 字幕なら1増やす
カウントに基づいてブールフラグを更新し、検出結果を返す
ffprobeが利用できない場合のフォールバック：拡張子による推測
ファイル拡張子を取得し、ドットを除去して小文字に変換
一般的なビデオ/オーディオ/字幕拡張子のセットを定義
拡張子がビデオセットにある場合、ビデオを含むとマーク、コンテナフォーマットは通常オーディオも含むためデフォルトでオーディオを含むとマーク
拡張子がオーディオセットにある場合、オーディオを含むとマーク / 字幕セットは字幕を含むとマーク
webm/oggはフォールバックでは両方とみなす（オーディオを含む可能性あり） / 推測結果を返す


======================================================================
[锚点 9] 目录扫描方法 (scan_directory, scan_all_for_audio, scan_all_for_subtitles)
======================================================================
[中文] 
扫描工作目录，返回 (视频文件, 音频文件, 字幕文件) 三个列表。分类依据是 ffprobe 检测到的实际流类型，而非扩展名。
初始化三个空列表 / 如果工作目录不是有效目录，直接返回空列表
遍历目录下的所有文件，按文件名小写排序 / 跳过非文件、不在白名单的扩展名、隐藏/临时文件、0字节文件
探测文件流信息
纯字幕文件（只有字幕流，没有音视频）放入字幕列表
含视频流放入视频列表 / 含音频流（且无视频流）放入音频列表
扫描所有含音频流的文件（包括同时含视频的文件），用于音频选择步骤。只要包含音频流，就加入结果列表
扫描所有含字幕流或为纯字幕格式的文件。纯字幕扩展名直接收入，其他扩展名但含字幕流（且无音视频）也收入

[EN]
Scan working directory, return three lists: (video files, audio files, subtitle files). Classification is based on actual stream types detected by ffprobe, not extensions.
Initialize three empty lists / If working directory is invalid, return empty lists directly
Iterate through all files in directory, sort by lowercase filename / Skip non-files, extensions not in whitelist, hidden/temp files, 0-byte files
Probe file stream info
Pure subtitle files (only subtitle streams, no audio/video) go to subtitle list
Files with video streams go to video list / Files with audio streams (and no video) go to audio list
Scan all files containing audio streams (including those with video) for audio selection step. Add to result list as long as it contains audio streams
Scan all files containing subtitle streams or pure subtitle formats. Pure subtitle extensions are included directly, other extensions with subtitle streams (and no audio/video) are also included

[JP]
作業ディレクトリをスキャンし、(ビデオファイル、オーディオファイル、字幕ファイル)の3つのリストを返す。分類は拡張子ではなく、ffprobeによって検出された実際のストリームタイプに基づく。
3つの空のリストを初期化 / 作業ディレクトリが無効な場合、直接空のリストを返す
ディレクトリ内のすべてのファイルをループし、小文字のファイル名でソート / 非ファイル、ホワイトリストにない拡張子、隠し/一時ファイル、0バイトファイルをスキップ
ファイルストリーム情報を検出
純粋な字幕ファイル（字幕ストリームのみ、オーディオ/ビデオなし）は字幕リストに入れる
ビデオストリームを含むファイルはビデオリストに入れる / オーディオストリームを含む（ビデオなし）ファイルはオーディオリストに入れる
オーディオ選択ステップのために、オーディオストリームを含むすべてのファイル（ビデオを含むものも含む）をスキャン。オーディオストリームを含む限り結果リストに追加
字幕ストリームを含む、または純粋な字幕フォーマットのすべてのファイルをスキャン。純粋な字幕拡張子は直接含め、他の拡張子でも字幕ストリームを含む（オーディオ/ビデオなし）ものは含める


======================================================================
[锚点 10] FFmpeg 命令构建 (_build_command 及 fallback)
======================================================================
[中文] 
构建精确的 FFmpeg 命令。视频文件提取视频流及自带音视频字幕；外部音频只提取音频；外部字幕只提取字幕。全部使用 copy 模式（无损）。
初始化命令列表，包含 ffmpeg 路径和全局参数 (-y, -hide_banner, -loglevel warning)
添加主视频文件作为第 0 个输入 / 遍历外部音频和字幕文件依次添加为输入
Map 映射：从视频文件中提取视频流(必须)、自带音频(可选?)、自带字幕(可选?)
从外部音频/字幕文件中只提取对应流
编码器：全部 copy（无损） / MKV 特定选项：强制输出格式为 matroska (MKV) / 添加输出文件路径
备用命令：当 -c:s copy 失败时，将字幕重编码为 srt/ass。视频和音频保持 copy，不使用 -c:s copy，让 ffmpeg 自动选择 MKV 兼容的字幕编码器。

[EN]
Build precise FFmpeg command. Video file extracts video stream and built-in audio/subtitles; external audio extracts only audio; external subtitles extract only subtitles. All use copy mode (lossless).
Initialize command list with ffmpeg path and global parameters (-y, -hide_banner, -loglevel warning)
Add main video file as 0th input / Iterate external audio and subtitle files and add as inputs sequentially
Map mapping: Extract video stream (mandatory), built-in audio (optional?), built-in subtitles (optional?) from video file
Extract only corresponding streams from external audio/subtitle files
Encoders: all copy (lossless) / MKV specific options: force output format to matroska (MKV) / Add output file path
Fallback command: When -c:s copy fails, re-encode subtitles to srt/ass. Keep video and audio as copy, do not use -c:s copy, let ffmpeg automatically choose MKV-compatible subtitle encoder.

[JP]
正確なFFmpegコマンドを構築。ビデオファイルはビデオストリームおよび内蔵のオーディオ/字幕を抽出、外部オーディオはオーディオのみ、外部字幕は字幕のみを抽出。すべてcopyモード（無劣化）を使用。
ffmpegパスとグローバルパラメータ (-y, -hide_banner, -loglevel warning) を含むコマンドリストを初期化
メインビデオファイルを0番目の入力として追加 / 外部オーディオおよび字幕ファイルをループして順次入力として追加
Mapマッピング：ビデオファイルからビデオストリーム(必須)、内蔵オーディオ(オプション?)、内蔵字幕(オプション?)を抽出
外部オーディオ/字幕ファイルから対応するストリームのみを抽出
エンコーダー：すべてcopy（無劣化） / MKV固有オプション：出力フォーマットをmatroska (MKV)に強制 / 出力ファイルパスを追加
予備コマンド：-c:s copyが失敗した場合、字幕をsrt/assに再エンコード。ビデオとオーディオはcopyを維持し、-c:s copyを使用せず、ffmpegにMKV互換の字幕エンコーダーを自動選択させる。


======================================================================
[锚点 11] 合并执行与辅助方法 (merge_files, _check_file, _execute)
======================================================================
[中文] 
执行合并，返回是否成功。解析所有输入输出路径为绝对路径。验证视频文件存在性，过滤有效的音频和字幕文件。
确定输出路径（默认 视频名_merged.mkv），确保扩展名为 .mkv，创建输出目录。
打印合并任务摘要。第一次尝试：全部 copy。如果失败且存在字幕，第二次尝试：字幕不 copy（降级重编码）。
检查文件是否有效：不存在、为空（0字节）、不可访问则跳过并返回 False。
执行 FFmpeg 命令：使用 Popen 启动子进程，等待结束（1小时超时）。返回码为 0 表示成功。
过滤出包含关键错误词汇的行并打印，超时则强制杀死进程。

[EN]
Execute merge, return whether successful. Parse all input/output paths to absolute paths. Validate video file existence, filter valid audio and subtitle files.
Determine output path (default video_name_merged.mkv), ensure extension is .mkv, create output directory.
Print merge task summary. First attempt: all copy. If fails and subtitles exist, second attempt: subtitles not copy (fallback re-encoding).
Check if file is valid: skip and return False if not exists, empty (0 bytes), or inaccessible.
Execute FFmpeg command: Start subprocess using Popen, wait for completion (1 hour timeout). Return code 0 indicates success.
Filter and print lines containing key error vocabulary, force kill process on timeout.

[JP]
結合を実行し、成功したかどうかを返す。すべての入出力パスを絶対パスに解析。ビデオファイルの存在を検証し、有効なオーディオおよび字幕ファイルをフィルタリング。
出力パスを決定（デフォルト video_name_merged.mkv）、拡張子が.mkvであることを確認し、出力ディレクトリを作成。
結合タスクの要約を印刷。1回目の試行：すべてcopy。失敗して字幕が存在する場合、2回目の試行：字幕はcopyしない（フォールバック再エンコード）。
ファイルが有効かチェック：存在しない、空（0バイト）、アクセス不可の場合はスキップしてFalseを返す。
FFmpegコマンドを実行：Popenを使用してサブプロセスを開始し、完了を待つ（1時間タイムアウト）。リターンコード0は成功を示す。
重要なエラー語彙を含む行をフィルタリングして印刷、タイムアウト時はプロセスを強制キル。


======================================================================
[锚点 12] 交互模式与用户输入 (interactive, _pick_one, _pick_multiple)
======================================================================
[中文] 
交互式文件选择。核心改进：通过 ffprobe 检测实际流类型，不再依赖扩展名分类。
打印欢迎信息，扫描目录。步骤 1: 选择视频 / 步骤 2: 选择音频（排除已选视频） / 步骤 3: 选择字幕。
打印选择结果，等待用户确认，确定输出文件名，调用 merge_files 执行实际合并。捕获 Ctrl+C 中断。
从列表中选一个：支持数字编号或文件名关键字匹配。
从列表中多选：支持逗号/空格分隔，支持 all 关键字全选，回车跳过。

[EN]
Interactive file selection. Core improvement: Detect actual stream types via ffprobe, no longer relying on extension classification.
Print welcome info, scan directory. Step 1: Select video / Step 2: Select audio (exclude selected video) / Step 3: Select subtitles.
Print selection results, wait for user confirmation, determine output filename, call merge_files to execute actual merge. Catch Ctrl+C interrupt.
Pick one from list: Supports numeric index or filename keyword matching.
Pick multiple from list: Supports comma/space separation, supports 'all' keyword for select all, Enter to skip.

[JP]
対話型ファイル選択。中核となる改善点：ffprobeを通じて実際のストリームタイプを検出し、拡張子分類に依存しない。
歓迎情報を印刷し、ディレクトリをスキャン。ステップ1：ビデオ選択 / ステップ2：オーディオ選択（選択したビデオを除外） / ステップ3：字幕選択。
選択結果を印刷し、ユーザーの確認を待ち、出力ファイル名を決定し、merge_filesを呼び出して実際の結合を実行。Ctrl+C割り込みをキャプチャ。
リストから1つ選択：数字インデックスまたはファイル名キーワードマッチングをサポート。
リストから複数選択：カンマ/スペース区切りをサポートし、'all'キーワードで全選択をサポート、Enterでスキップ。


======================================================================
[锚点 13] 自动模式 (auto_merge)
======================================================================
[中文] 
自动匹配同名文件并合并。确定输出目录，扫描目录获取所有媒体列表。
遍历每个视频文件，匹配同名的外部音频和字幕（排除视频文件自身）。执行合并并记录结果。

[EN]
Automatically match same-name files and merge. Determine output directory, scan directory to get all media lists.
Iterate through each video file, match external audio and subtitles with the same name (excluding the video file itself). Execute merge and record results.

[JP]
同名ファイルを自動的にマッチングして結合。出力ディレクトリを決定し、ディレクトリをスキャンしてすべてのメディアリストを取得。
各ビデオファイルをループし、同名の外部オーディオと字幕をマッチング（ビデオファイル自体を除外）。結合を実行し結果を記録。


======================================================================
[锚点 14] 主入口 (main 函数)
======================================================================
[中文] 
定义主函数。导入命令行参数解析模块 (argparse)，创建解析器对象并添加命令行参数（工作目录、自动模式、交互模式、手动指定文件等）。
解析参数，初始化合并器实例。
处理 --info 参数：仅显示文件流信息。
处理手动指定视频参数：直接合并。
处理自动模式参数：执行自动匹配并打印成功率。
默认进入交互模式。捕获致命错误并退出。
脚本入口点判断，调用主函数。

[EN]
Define main function. Import command-line argument parsing module (argparse), create parser object and add arguments (working dir, auto mode, interactive mode, manual file specification, etc.).
Parse arguments, initialize merger instance.
Handle --info argument: Only display file stream info.
Handle manual video argument: Merge directly.
Handle auto mode argument: Execute auto-matching and print success rate.
Default to interactive mode. Catch fatal errors and exit.
Script entry point check, call main function.

[JP]
メイン関数を定義。コマンドライン引数解析モジュール (argparse) をインポートし、パーサーオブジェクトを作成して引数を追加（作業ディレクトリ、自動モード、対話モード、手動ファイル指定など）。
引数を解析し、マージャーインスタンスを初期化。
--info 引数を処理：ファイルストリーム情報のみを表示。
手動ビデオ引数を処理：直接結合。
自動モード引数を処理：自動マッチングを実行し成功率を印刷。
デフォルト是对話モード。致命的なエラーをキャプチャして終了。
スクリプトエントリポイントチェック、メイン関数を呼び出す。