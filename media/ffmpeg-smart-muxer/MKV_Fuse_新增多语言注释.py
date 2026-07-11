#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
脚本名称: FFmpeg Media Merger v3 (基于流检测的重构版本)
Script Name: FFmpeg Media Merger v3 (Refactored version based on stream detection)
スクリプト名: FFmpeg Media Merger v3 (ストリーム検出に基づくリファクタリング版)

作者署名: 张龙
Author: Zhang Long
著者: 張龍 (Zhang Long)
================================================================================
脚本介绍: / Introduction: / スクリプト紹介:
本脚本是一个基于 Python 编写的高级 FFmpeg 媒体合并工具.
其核心创新点在于摒弃了传统仅依赖文件扩展名来判断媒体类型的做法,转而通过调用 ffprobe对文件内部的实际流 ( 视频流、音频流、字幕流) 进行深度检测与解析.
这使得工具能够精准识别诸如"包含纯音频的 .webm 文件"或"包含字幕流的 .mkv 文件"等复杂情况,从而实现无损、高效的媒体封装.

This script is an advanced FFmpeg media merging tool written in Python.
Its core innovation lies in abandoning the traditional method of relying solely on file extensions to determine media types. Instead, it calls ffprobe to deeply detect and parse the actual streams (video, audio, subtitle) inside the file.
This allows the tool to accurately identify complex cases such as ".webm files containing pure audio" or ".mkv files containing subtitle streams", thereby achieving lossless and efficient media muxing.

本スクリプトはPythonで記述された高度なFFmpegメディア結合ツールです.
その中核となるイノベーションは、メディアタイプを判断するためにファイル拡張子だけに依存する従来の方法を廃止し、代わりにffprobeを呼び出してファイル内部の実際のストリーム ( ビデオ、オーディオ、字幕) を深く検出・解析する点にあります.
これにより、「純粋なオーディオを含む.webmファイル」や「字幕ストリームを含む.mkvファイル」といった複雑なケースを正確に識別し、無劣化かつ効率的なメディア多重化を実現します.

主要功能包括 : 
Main features include:
主な機能は以下の通りです : 

1. 智能流检测 : 利用 ffprobe 获取真实的 codec_type,确保分类准确无误.
1. Intelligent stream detection: Uses ffprobe to get the real codec_type, ensuring accurate classification.
1. インテリジェントなストリーム検出 : ffprobeを利用して実際のcodec_typeを取得し、正確な分類を保証します.

2. 无损合并 : 采用 stream copy 模式,将视频、多音轨、多字幕无损封装至 MKV 容器.
2. Lossless merging: Uses stream copy mode to losslessly mux video, multiple audio tracks, and multiple subtitles into an MKV container.
2. 無劣化結合 : ストリームコピーモードを使用し、ビデオ、複数のオーディオトラック、複数の字幕をMKVコンテナに無劣化で多重化します.

3. 降级容错机制 : 当字幕流直接 copy 失败时,自动尝试重编码为 MKV 兼容格式.
3. Fallback fault-tolerance mechanism: Automatically attempts to re-encode subtitles into an MKV-compatible format when direct subtitle copy fails.
3. フォールバックフォールトトレランス機制 : 字幕ストリームの直接コピーが失敗した場合、MKV互換フォーマットへの再エンコードを自動的に試みます.

4. 灵活的工作模式 : 支持交互式命令行选择、自动同名匹配合并以及命令行参数直接指定.
4. Flexible working modes: Supports interactive command-line selection, automatic same-name matching merge, and direct specification via command-line arguments.
4. 柔軟な動作モード : 対話型コマンドライン選択、自動同名マッチング結合、およびコマンドライン引数による直接指定をサポートします.

5. 跨平台兼容 : 自动在系统 PATH 及常见安装目录中查找 ffmpeg/ffprobe 可执行文件.
5. Cross-platform compatibility: Automatically searches for ffmpeg/ffprobe executables in the system PATH and common installation directories.
5. クロスプラットフォーム互換性 : システムPATHおよび一般的なインストールディレクトリ内でffmpeg/ffprobeの実行ファイルを自動的に検索します.
================================================================================
"""

# 导入操作系统接口模块,用于环境变量和路径判断
# Import OS interface module for environment variables and path judgments
# 環境変数とパスの判定のためにOSインターフェースモジュールをインポート
import os

# 导入系统特定参数模块,用于退出程序
# Import system-specific parameters module for exiting the program
# プログラムを終了するためにシステム固有のパラメータモジュールをインポート
import sys

# 导入子进程模块,用于调用外部 ffmpeg 和 ffprobe 命令
# Import subprocess module for calling external ffmpeg and ffprobe commands
# 外部のffmpegおよびffprobeコマンドを呼び出すためにサブプロセスモジュールをインポート
import subprocess

# 导入 JSON 模块,用于解析 ffprobe 返回的 JSON 数据
# Import JSON module for parsing JSON data returned by ffprobe
# ffprobeが返すJSONデータを解析するためにJSONモジュールをインポート
import json

# 导入 shutil 模块,用于跨平台查找可执行文件
# Import shutil module for cross-platform executable file searching
# クロスプラットフォームで実行ファイルを検索するためにshutilモジュールをインポート
import shutil

# 导入 pathlib 模块,用于面向对象的路径操作
# Import pathlib module for object-oriented path operations
# オブジェクト指向のパス操作のためにpathlibモジュールをインポート
from pathlib import Path

# 导入 typing 模块,用于类型提示,增强代码可读性
# Import typing module for type hinting to enhance code readability
# コードの可読性を向上させるための型ヒント用にtypingモジュールをインポート
from typing import List, Dict, Optional, Tuple, Union

# ─────────────────────────────────────────────
# 扩展名白名单 ( 仅用于初筛,不作为最终分类依据) 
# Extension whitelist (used only for initial screening, not as final classification basis)
# 拡張子ホワイトリスト ( 初期スクリーニングのみに使用され、最終的な分類の基準としては使用されません) 
# ─────────────────────────────────────────────
# 定义支持的媒体文件扩展名集合,用于快速过滤非媒体文件
# Define a set of supported media file extensions for quick filtering of non-media files
# 非メディアファイルを迅速にフィルタリングするために、サポートされているメディアファイル拡張子のセットを定義
ALL_MEDIA_EXTENSIONS = {
    # 视频容器 / 纯视频格式
    # Video containers / pure video formats
    # ビデオコンテナ / 純粋なビデオフォーマット
    'mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mpg', 'mpeg',
    'mts', 'm2ts', 'ts', 'vob', 'rm', 'rmvb', 'asf',
    '3gp', '3g2', 'divx', 'f4v', 'ogv', 'dv',
    # 既可能是视频也可能是音频的容器格式
    # Container formats that can be either video or audio
    # ビデオまたはオーディオのいずれにもなり得るコンテナフォーマット
    'webm', 'ogg', 'ogx', 'm4v',
    # 音频格式
    # Audio formats
    # オーディオフォーマット
    'mp3', 'wav', 'aac', 'm4a', 'flac', 'oga', 'opus',
    'wma', 'ac3', 'dts', 'eac3', 'mka', 'aiff', 'aif',
    'm4b', 'ape', 'tta', 'mp2', 'amr', 'mpc', 'wv',
    'spx', 'ra', 'ram', 'caf',
    # 原始视频流格式
    # Raw video stream formats
    # 生のビデオストリームフォーマット
    'h264', 'h265', 'hevc', 'avc', 'vp9', 'ivf',
    # 字幕格式
    # Subtitle formats
    # 字幕フォーマット
    'srt', 'ass', 'ssa', 'sub', 'idx', 'vtt',
    'ttml', 'dfxp', 'smi', 'sami', 'mpl', 'pjs',
    'stl', 'sup', 'pgs', 'sbv', 'lrc', 'rt', 'txt',
}

# 定义单个文件的流信息数据类
# Define data class for stream information of a single file
# 単一ファイルのストリーム情報データクラスを定義
class StreamInfo:

    """
    单个文件的流信息
    Stream information of a single file
    単一ファイルのストリーム情報
    """
    # 使用 __slots__ 限制属性,优化内存占用
    # Use __slots__ to restrict attributes, optimize memory usage
    # __slots__を使用して属性を制限し、メモリ使用量を最適化
    __slots__ = ('path', 'has_video', 'has_audio', 'has_subtitle',
                 'video_count', 'audio_count', 'subtitle_count', 'streams')
    
    # 初始化方法,传入文件路径
    # Initialization method, passing in the file path
    # 初期化メソッド、ファイルパスを渡す
    def __init__(self, path: Path):

        # 保存文件路径对象
        # Save file path object
        # ファイルパスオブジェクトを保存
        self.path = path

        # 标记是否包含视频流
        # Flag whether it contains video stream
        # ビデオストリームを含むかどうかをマーク
        self.has_video = False

        # 标记是否包含音频流
        # Flag whether it contains audio stream
        # オーディオストリームを含むかどうかをマーク
        self.has_audio = False

        # 标记是否包含字幕流
        # Flag whether it contains subtitle stream
        # 字幕ストリームを含むかどうかをマーク
        self.has_subtitle = False

        # 视频流数量
        # Video stream count
        # ビデオストリーム数
        self.video_count = 0

        # 音频流数量
        # Audio stream count
        # オーディオストリーム数
        self.audio_count = 0

        # 字幕流数量
        # Subtitle stream count
        # 字幕ストリーム数
        self.subtitle_count = 0

        # 存储详细的流信息字典列表
        # Store list of detailed stream information dictionaries
        # 詳細なストリーム情報辞書のリストを保存
        self.streams: List[dict] = []

        
    # 定义对象的字符串表示形式,便于调试打印
    # Define string representation of the object for easy debug printing
    # デバッグ印刷を容易にするためにオブジェクトの文字列表現を定義
    def __repr__(self):

        # 初始化标签列表
        # Initialize tag list
        # タグリストを初期化
        tags = []

        # 如果有视频流,添加视频数量标签
        # If video stream exists, add video count tag
        # ビデオストリームがある場合、ビデオ数タグを追加
        if self.has_video:
            tags.append(f'V×{self.video_count}')

        # 如果有音频流,添加音频数量标签
        # If audio stream exists, add audio count tag
        # オーディオストリームがある場合、オーディオ数タグを追加
        if self.has_audio:
            tags.append(f'A×{self.audio_count}')

        # 如果有字幕流,添加字幕数量标签
        # If subtitle stream exists, add subtitle count tag
        # 字幕ストリームがある場合、字幕数タグを追加
        if self.has_subtitle:
            tags.append(f'S×{self.subtitle_count}')

        # 返回格式化的字符串,包含文件名和流标签
        # Return formatted string containing file name and stream tags
        # ファイル名とストリームタグを含むフォーマットされた文字列を返す
        return f"<{self.path.name} [{', '.join(tags)}]>"


# 定义 FFmpeg 媒体合并器主类
# Define main class for FFmpeg media merger
# FFmpegメディアマージャーのメインクラスを定義
class FFmpegMediaMerger:

    """
    FFmpeg 媒体合并器 — 基于 ffprobe 流检测
    FFmpeg Media Merger — based on ffprobe stream detection
    FFmpegメディアマージャー — ffprobeストリーム検出に基づく
    """
    
    # 初始化方法,可选传入工作目录
    # Initialization method, optionally passing in working directory
    # 初期化メソッド、オプションで作業ディレクトリを渡す
    def __init__(self, working_dir: Optional[str] = None):

        # 解析并保存工作目录的绝对路径,默认为当前目录
        # Parse and save absolute path of working directory, default to current directory
        # 作業ディレクトリの絶対パスを解析して保存、デフォルトは現在のディレクトリ
        self.working_dir = Path(working_dir).resolve() if working_dir else Path.cwd()

        # 设置详细输出模式为 True
        # Set verbose output mode to True
        # 詳細出力モードをTrueに設定
        self.verbose = True

        # 查找 ffmpeg 可执行文件路径
        # Find ffmpeg executable path
        # ffmpeg実行ファイルパスを検索
        self.ffmpeg_path = self._locate_binary('ffmpeg')

        # 查找 ffprobe 可执行文件路径
        # Find ffprobe executable path
        # ffprobe実行ファイルパスを検索
        self.ffprobe_path = self._locate_binary('ffprobe')

        # 如果找不到 ffmpeg,抛出运行时错误并提示安装方法
        # If ffmpeg is not found, raise runtime error and prompt installation methods
        # ffmpegが見つからない場合、ランタイムエラーをスローしインストール方法を促す
        if not self.ffmpeg_path:
            raise RuntimeError(
                "未找到 ffmpeg,请安装或将其加入 PATH.\n"
                "  Windows: https://www.gyan.dev/ffmpeg/builds/\n"
                "  macOS  : brew install ffmpeg\n"
                "  Linux  : sudo apt install ffmpeg"
            )

            
    # ────────────── 工具方法 ──────────────
    # ────────────── Utility methods ──────────────
    # ────────────── ユーティリティメソッド ──────────────
    
    # 静态方法 : 在 PATH 和常见位置中查找可执行文件
    # Static method: Find executable in PATH and common locations
    # 静的メソッド : PATHおよび一般的な場所で実行ファイルを検索
    @staticmethod
    def _locate_binary(name: str) -> Optional[str]:

        """
        在 PATH 和常见位置中查找可执行文件
        Find executable in PATH and common locations
        PATHおよび一般的な場所で実行ファイルを検索
        """
        # 1. 使用 shutil.which 跨平台查找
        # 1. Use shutil.which for cross-platform search
        # 1. shutil.whichを使用してクロスプラットフォーム検索
        found = shutil.which(name)

        # 如果找到了,直接返回路径
        # If found, return path directly
        # 見つかった場合、パスを直接返す
        if found:
            return found

            
        # 2. 定义常见安装路径列表
        # 2. Define list of common installation paths
        # 2. 一般的なインストールパスのリストを定義
        extras = []

        # 如果是 Windows 系统
        # If Windows system
        # Windowsシステムの場合
        if os.name == 'nt':
            extras = [
                # Program Files 目录下的 ffmpeg
                # (Program Files directory)
                # (Program Files ディレクトリ)
                Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'ffmpeg' / 'bin',

                # Program Files (x86) 目录下的 ffmpeg
                # (Program Files (x86) directory)
                # (Program Files (x86) ディレクトリ)
                Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'ffmpeg' / 'bin',

                # WinGet 安装目录
                # (WinGet directory)
                # (WinGet ディレクトリ)
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Links',

                # Scoop 安装目录
                # (Scoop directory)
                # (Scoop ディレクトリ)
                Path.home() / 'scoop' / 'shims',

            ]

        # 如果是 macOS 或 Linux 系统
        # If macOS or Linux system
        # macOSまたはLinuxシステムの場合
        else:
            extras = [
                # 常见的系统级二进制目录
                # (Common system-level binary directory)
                # (一般的なシステムレベルバイナリディレクトリ)
                Path('/usr/local/bin'),
                Path('/usr/bin'),

                # macOS Homebrew (Apple Silicon) 目录
                # (macOS Homebrew directory)
                # (macOS Homebrew ディレクトリ)
                Path('/opt/homebrew/bin'),

                # 用户级二进制目录
                # (User-level binary directory)
                # (ユーザーレベルバイナリディレクトリ)
                Path.home() / '.local' / 'bin',
            ]

        # 根据操作系统确定可执行文件后缀名
        # Determine executable suffix based on operating system
        # オペレーティングシステムに基づいて実行ファイルのサフィックスを決定
        suffix = '.exe' if os.name == 'nt' else ''

        # 遍历所有常见路径
        # Iterate through all common paths
        # すべての一般的なパスをループ
        for d in extras:

            # 拼接完整的候选文件路径
            # Concatenate full candidate file path
            # 完全な候補ファイルパスを結合
            candidate = d / f'{name}{suffix}'

            # 如果文件存在,返回其字符串路径
            # If file exists, return its string path
            # ファイルが存在する場合、その文字列パスを返す
            if candidate.exists():
                return str(candidate)

        # 如果都没找到,返回 None
        # If none found, return None
        # どれもが見つからない場合、Noneを返す
        return None
        
    # 实例方法 : 用 ffprobe 获取文件流信息
    # Instance method: Get file stream info using ffprobe
    # インスタンスメソッド : ffprobeを使用してファイルストリーム情報を取得
    def _run_ffprobe(self, file_path: Path) -> Optional[dict]:

        """
        用 ffprobe 获取文件流信息,返回 JSON dict
        Get file stream info using ffprobe, return JSON dict
        ffprobeを使用してファイルストリーム情報を取得し、JSON dictを返す
        """

        # 如果 ffprobe 路径不存在,直接返回 None
        # If ffprobe path does not exist, return None directly
        # ffprobeパスが存在しない場合、直接Noneを返す
        if not self.ffprobe_path:
            return None

        try:
            # 构建 ffprobe 命令参数列表
            # Build ffprobe command argument list (quiet mode / output JSON / show streams and format / target file)
            # ffprobeコマンド引数リストを構築 (静黙モード / JSON出力 / ストリームとフォーマット表示 / 対象ファイル)
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',             # 静默模式,不输出冗余信息 / Quiet mode, no redundant output / 静黙モード、冗長な出力なし
                '-print_format', 'json',   # 输出格式为 JSON / Output format as JSON / 出力形式をJSON
                '-show_streams',           # 显示流信息 / Show stream info / ストリーム情報を表示
                '-show_format',            # 显示容器格式信息 / Show container format info / コンテナフォーマット情報を表示
                str(file_path),            # 目标文件路径 / Target file path / 対象ファイルパス
            ]

            # 执行子进程命令
            # Execute subprocess command (capture stdout and stderr / text mode / 30s timeout)
            # サブプロセスコマンドを実行 (標準出力とエラーをキャプチャ / テキストモード / 30秒タイムアウト)
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,    # 捕获标准输出 / Capture stdout / 標準出力をキャプチャ
                stderr=subprocess.PIPE,    # 捕获标准错误 / Capture stderr / 標準エラーをキャプチャ
                text=True,                 # 以文本模式返回 / Return in text mode / テキストモードで返す
                timeout=30,                # 设置 30 秒超时 / Set 30s timeout / 30秒タイムアウトを設定
            )

            # 如果返回码为 0 且标准输出不为空
            # If return code is 0 and stdout is not empty, parse JSON and return dictionary
            # リターンコードが0で標準出力が空でない場合、JSONを解析して辞書を返す
            if result.returncode == 0 and result.stdout.strip():

                # 解析 JSON 并返回字典
                # Parse JSON and return dictionary
                # JSONを解析して辞書を返す
                return json.loads(result.stdout)
        except Exception:

            # 捕获所有异常,忽略错误
            # Catch all exceptions, ignore errors
            # すべての例外をキャプチャし、エラーを無視
            pass

        # 失败时返回 None
        # Return None on failure
        # 失敗時にNoneを返す
        return None
        
    # 实例方法 : 检测文件实际包含的流类型
    # Instance method: Detect actual stream types contained in the file
    # インスタンスメソッド : ファイルに実際に含まれるストリームタイプを検出
    def probe_file(self, file_path: Path) -> StreamInfo:

        """
        检测文件实际包含的流类型.
        优先使用 ffprobe ; 若不可用则退回到扩展名猜测.
        Detect actual stream types contained in the file.
        Prioritize ffprobe; fallback to extension guessing if unavailable.
        ファイルに実際に含まれるストリームタイプを検出.
        ffprobeを優先し、利用できない場合は拡張子推測にフォールバック.
        """

        # 初始化 StreamInfo 对象
        # Initialize StreamInfo object
        # StreamInfoオブジェクトを初期化
        info = StreamInfo(file_path)

        # 调用 ffprobe 获取探测结果
        # Call ffprobe to get probe results
        # ffprobeを呼び出して検出結果を取得
        probe = self._run_ffprobe(file_path)

        # 如果探测成功且包含 streams 字段
        # If probe is successful and contains streams field, save detailed stream info
        # 検出が成功しstreamsフィールドを含む場合、詳細なストリーム情報を保存
        if probe and 'streams' in probe:

            # 保存详细流信息
            # Save detailed stream info
            # 詳細なストリーム情報を保存
            info.streams = probe['streams']

            # 遍历每一个流
            # Iterate through each stream, get stream type and convert to lowercase
            # 各ストリームをループし、ストリームタイプを取得して小文字に変換
            for stream in probe['streams']:

                # 获取流的类型并转为小写
                # Get stream type and convert to lowercase
                # ストリームタイプを取得して小文字に変換
                codec_type = stream.get('codec_type', '').lower()

                # 如果是视频流,视频计数加 1
                # If video stream, increment video count by 1
                # ビデオストリームならビデオカウントを1増やす
                if codec_type == 'video':
                    info.video_count += 1

                # 如果是音频流,音频计数加 1
                # Audio by 1
                # オーディオなら1増やす
                elif codec_type == 'audio':
                    info.audio_count += 1

                # 如果是字幕流,字幕计数加 1
                # Subtitle by 1
                # 字幕なら1増やす
                elif codec_type == 'subtitle':
                    info.subtitle_count += 1

            # 根据计数更新布尔标记
            # Update boolean flags based on counts, return probe results
            # カウントに基づいてブールフラグを更新し、検出結果を返す
            info.has_video = info.video_count > 0
            info.has_audio = info.audio_count > 0
            info.has_subtitle = info.subtitle_count > 0

            # 返回探测结果
            # Return probe results
            # 検出結果を返す
            return info
            
        # ── ffprobe 不可用时的退路 : 按扩展名猜测 ──
        # ── Fallback when ffprobe is unavailable: guess by extension ──
        # ── ffprobeが利用できない場合のフォールバック : 拡張子による推測 ──
        # 获取文件扩展名,去除点号并转为小写
        # Get file extension, strip dot and convert to lowercase
        # ファイル拡張子を取得し、ドットを除去して小文字に変換
        ext = file_path.suffix.lstrip('.').lower()

        # 定义常见的视频扩展名集合
        # Define sets of common video/audio/subtitle extensions
        # 一般的なビデオ/オーディオ/字幕拡張子のセットを定義
        video_exts = {
            'mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mpg', 'mpeg',
            'mts', 'm2ts', 'ts', 'vob', 'rm', 'rmvb', 'asf',
            '3gp', '3g2', 'divx', 'f4v', 'ogv', 'dv', 'webm', 'm4v',
        }

        # 定义常见的音频扩展名集合
        # Define sets of common video/audio/subtitle extensions
        # 一般的なビデオ/オーディオ/字幕拡張子のセットを定義
        audio_exts = {
            'mp3', 'wav', 'aac', 'm4a', 'flac', 'ogg', 'oga', 'opus',
            'wma', 'ac3', 'dts', 'eac3', 'mka', 'aiff', 'aif',
            'm4b', 'ape', 'tta', 'mp2', 'amr', 'mpc', 'wv',
            'spx', 'ra', 'ram', 'caf',
        }

        # 定义常见的字幕扩展名集合
        # Define sets of common video/audio/subtitle extensions
        # 一般的なビデオ/オーディオ/字幕拡張子のセットを定義
        subtitle_exts = {
            'srt', 'ass', 'ssa', 'sub', 'idx', 'vtt',
            'ttml', 'dfxp', 'smi', 'sami', 'mpl', 'pjs',
            'stl', 'sup', 'pgs', 'sbv', 'lrc',
        }

        # 如果扩展名在视频集合中
        # If extension is in video set, flag contains video, container formats usually contain audio, default flag contains audio
        # 拡張子がビデオセットにある場合、ビデオを含むとマーク、コンテナフォーマットは通常オーディオも含むためデフォルトでオーディオを含むとマーク
        if ext in video_exts:

            # 标记包含视频
            # Flag contains video
            # ビデオを含むとマーク
            info.has_video = True
            info.video_count = 1

            # 容器格式通常也含音频,默认标记包含音频
            # Container formats usually contain audio, default flag contains audio
            # コンテナフォーマットは通常オーディオも含むためデフォルトでオーディオを含むとマーク
            info.has_audio = True
            info.audio_count = 1

        # 如果扩展名在音频集合中
        # If extension is in audio set, flag contains audio
        # 拡張子がオーディオセットにある場合、オーディオを含むとマーク
        elif ext in audio_exts:

            # 标记包含音频
            # Flag contains audio
            # オーディオを含むとマーク
            info.has_audio = True
            info.audio_count = 1

        # 如果扩展名在字幕集合中
        # Subtitle set flag contains subtitle
        # 字幕セットは字幕を含むとマーク
        elif ext in subtitle_exts:

            # 标记包含字幕
            # Subtitle set flag contains subtitle
            # 字幕セットは字幕を含むとマーク
            info.has_subtitle = True
            info.subtitle_count = 1

        # webm/ogg 在退路里两边都算 ( 可能包含音频) 
        # Webm/ogg count as both in fallback (may contain audio)
        # webm/oggはフォールバックでは両方とみなす ( オーディオを含む可能性あり) 
        if ext in ('webm', 'ogg', 'ogx'):
            info.has_audio = True
            info.audio_count = 1

        # 返回猜测结果
        # Return guessed results
        # 推測結果を返す
        return info


    # 实例方法 : 扫描工作目录,分类文件
    # Scan working directory, return three lists: (video files, audio files, subtitle files).
    # Classification is based on actual stream types detected by ffprobe, not extensions.
    # 作業ディレクトリをスキャンし、(ビデオファイル、オーディオファイル、字幕ファイル)の3つのリストを返す.
    # 分類は拡張子ではなく、ffprobeによって検出された実際のストリームタイプに基づく.
    def scan_directory(self) -> Tuple[List[StreamInfo], List[StreamInfo], List[StreamInfo]]:

        """
        扫描工作目录,返回 (视频文件, 音频文件, 字幕文件) 三个列表.

        分类依据是 ffprobe 检测到的实际流类型,而非扩展名.
        Classification is based on actual stream types detected by ffprobe, not extensions.
        分類は拡張子ではなく、ffprobeによって検出された実際のストリームタイプに基づく.

        一个文件可以同时出现在多个列表中 ( 如含视频+音频的 mkv) .
        A file can appear in multiple lists simultaneously (such as mkv with video+audio).
        ファイルは複数のリストに同時に出現することができる ( ビデオ+オーディオを含むmkvなど) .
        """

        # 初始化三个空列表
        # Initialize three empty lists
        # 3つの空のリストを初期化
        video_files: List[StreamInfo] = []
        audio_files: List[StreamInfo] = []
        subtitle_files: List[StreamInfo] = []

        # 如果工作目录不是有效目录,直接返回空列表
        # If working directory is invalid, return empty lists directly
        # 作業ディレクトリが無効な場合、直接空のリストを返す
        if not self.working_dir.is_dir():
            return video_files, audio_files, subtitle_files

        # 遍历目录下的所有文件,按文件名小写排序
        # Iterate through all files in directory, sort by lowercase filename
        # ディレクトリ内のすべてのファイルをループし、小文字のファイル名でソート
        for entry in sorted(self.working_dir.iterdir(), key=lambda p: p.name.lower()):\

            # 如果不是文件,跳过
            # Skip non-files
            # 非ファイルをスキップ
            if not entry.is_file():
                continue

            # 获取扩展名
            # Get extension
            # 拡張子を取得
            ext = entry.suffix.lstrip('.').lower()

            # 如果扩展名不在白名单中,跳过
            # Skip extensions not in whitelist
            # ホワイトリストにない拡張子をスキップ
            if ext not in ALL_MEDIA_EXTENSIONS:
                continue

            # 跳过隐藏文件、临时文件
            # Skip hidden/temp files
            # 隠し/一時ファイルをスキップ
            if entry.name.startswith('.') or entry.name.startswith('~'):
                continue
            try:

                # 跳过 0 字节文件
                # Skip 0-byte files
                # 0バイトファイルをスキップ
                if entry.stat().st_size == 0:
                    continue
            except OSError:

                # 如果无法获取文件状态,跳过
                # Skip if unable to access file status
                # ファイルステータスにアクセスできない場合スキップ
                continue

            # 探测文件流信息
            # Probe file stream info
            # ファイルストリーム情報を検出
            info = self.probe_file(entry)

            # 纯字幕文件 ( 只有字幕流,没有音视频) 
            # Pure subtitle files (only subtitle streams, no audio/video) go to subtitle list
            # 純粋な字幕ファイル ( 字幕ストリームのみ、オーディオ/ビデオなし) は字幕リストに入れる
            if info.has_subtitle and not info.has_video and not info.has_audio:
                subtitle_files.append(info)
                continue

            # 含视频流 → 放入视频列表
            # Files with video streams go to video list
            # ビデオストリームを含むファイルはビデオリストに入れる
            if info.has_video:
                video_files.append(info)

            # 含音频流 ( 且无视频流) → 放入音频列表
            # 注意 : 如果文件同时有视频和音频,它已经在视频列表了,不重复放入音频列表
            # Files with audio streams (and no video) go to audio list
            # Note: If file has both video and audio, it's already in video list, don't duplicate in audio list
            # オーディオストリームを含む ( ビデオなし) ファイルはオーディオリストに入れる
            # 注 : ファイルがビデオとオーディオの両方を持つ場合、すでにビデオリストにあるため、オーディオリストに重複して入れない
            if info.has_audio and not info.has_video:
                audio_files.append(info)

        # 返回分类后的三个列表
        # Return classified three lists
        # 分類後の3つのリストを返す
        return video_files, audio_files, subtitle_files
        
    # 实例方法 : 扫描所有含音频流的文件
    # Scan all files containing audio streams (including those with video) for audio selection step.
    # Add to result list as long as it contains audio streams
    # オーディオ選択ステップのために、オーディオストリームを含むすべてのファイル ( ビデオを含むものも含む) をスキャン.
    # オーディオストリームを含む限り結果リストに追加
    def scan_all_for_audio(self) -> List[StreamInfo]:

        """
        扫描所有含音频流的文件 ( 包括同时含视频的文件) ,用于音频选择步骤.
        For audio selection step.
        オーディオ選択ステップ用.
        """

        # 初始化结果列表
        # Initialize result list
        # 結果リストを初期化
        result: List[StreamInfo] = []

        # 如果工作目录无效,返回空列表
        # Return empty list if working directory is invalid
        # 作業ディレクトリが無効な場合、空のリストを返す
        if not self.working_dir.is_dir():
            return result

        # 遍历目录文件
        # Iterate through directory files
        # ディレクトリファイルをループ
        for entry in sorted(self.working_dir.iterdir(), key=lambda p: p.name.lower()):
            if not entry.is_file():
                continue
            ext = entry.suffix.lstrip('.').lower()
            if ext not in ALL_MEDIA_EXTENSIONS:
                continue
            if entry.name.startswith('.') or entry.name.startswith('~'):
                continue
            try:
                if entry.stat().st_size == 0:
                    continue
            except OSError:
                continue

            # 探测文件
            # Probe file
            # ファイルを検出
            info = self.probe_file(entry)

            # 只要包含音频流,就加入结果列表
            # Add to result list as long as it contains audio streams
            # オーディオストリームを含む限り結果リストに追加
            if info.has_audio:
                result.append(info)
        return result

        
    # 实例方法 : 扫描所有含字幕流或为纯字幕格式的文件
    # Scan all files containing subtitle streams or pure subtitle formats.
    # Pure subtitle extensions are included directly, other extensions with subtitle streams (and no audio/video) are also included
    # 字幕ストリームを含む、または純粋な字幕フォーマットのすべてのファイルをスキャン.
    # 純粋な字幕拡張子は直接含め、他の拡張子でも字幕ストリームを含む ( オーディオ/ビデオなし) ものは含める
    def scan_all_for_subtitles(self) -> List[StreamInfo]:

        """
        扫描所有含字幕流或为纯字幕格式的文件
        Scan all files containing subtitle streams or pure subtitle formats
        字幕ストリームを含む、または純粋な字幕フォーマットのすべてのファイルをスキャン
        """

        result: List[StreamInfo] = []
        if not self.working_dir.is_dir():
            return result

        # 定义纯字幕扩展名集合
        # Define pure subtitle extension set
        # 純粋な字幕拡張子セットを定義
        subtitle_exts = {
            'srt', 'ass', 'ssa', 'sub', 'idx', 'vtt',
            'ttml', 'dfxp', 'smi', 'sami', 'mpl', 'pjs',
            'stl', 'sup', 'pgs', 'sbv', 'lrc', 'rt', 'txt',
        }
        for entry in sorted(self.working_dir.iterdir(), key=lambda p: p.name.lower()):
            if not entry.is_file():
                continue
            ext = entry.suffix.lstrip('.').lower()
            if entry.name.startswith('.') or entry.name.startswith('~'):
                continue
            try:
                if entry.stat().st_size == 0:
                    continue
            except OSError:
                continue

            # 纯字幕扩展名直接收入
            # Pure subtitle extensions are included directly
            # 純粋な字幕拡張子は直接含める
            if ext in subtitle_exts:
                info = self.probe_file(entry)
                if info.has_subtitle or ext in subtitle_exts:
                    result.append(info)
                    continue

            # 其他扩展名但含字幕流 ( 且无音视频) 
            # Other extensions but contain subtitle streams (and no audio/video)
            # 他の拡張子でも字幕ストリームを含む ( オーディオ/ビデオなし) 
            if ext in ALL_MEDIA_EXTENSIONS:
                info = self.probe_file(entry)
                if info.has_subtitle and not info.has_video and not info.has_audio:
                    result.append(info)
        return result


    # FFmpeg 命令构建
    # Build precise FFmpeg command. Video file extracts video stream and built-in audio/subtitles; external audio extracts only audio; external subtitles extract only subtitles. All use copy mode (lossless).
    #　正確なFFmpegコマンドを構築.ビデオファイルはビデオストリームおよび内蔵のオーディオ/字幕を抽出、外部オーディオはオーディオのみ、外部字幕は字幕のみを抽出.すべてcopyモード ( 無劣化) を使用.
    
    # 实例方法 : 构建精确的 FFmpeg 命令
    # Build precise FFmpeg command. Video file extracts video stream and built-in audio/subtitles; external audio extracts only audio; external subtitles extract only subtitles. All use copy mode (lossless).
    # 正確なFFmpegコマンドを構築.ビデオファイルはビデオストリームおよび内蔵のオーディオ/字幕を抽出、外部オーディオはオーディオのみ、外部字幕は字幕のみを抽出.すべてcopyモード ( 無劣化) を使用.
    def _build_command(
        self,
        video_file: Path,
        audio_files: List[Path],
        subtitle_files: List[Path],
        output_file: Path,
    ) -> List[str]:

        """
        构建精确的 FFmpeg 命令.
        - 视频文件 : 提取视频流 ( 以及其自带的音频/字幕流) 
        - 外部音频文件 : 只提取音频流
        - 外部字幕文件 : 只提取字幕流
        全部使用 copy 模式 ( 无损) .

        Build precise FFmpeg command.
        Video file extracts video stream (and its built-in audio/subtitle streams)
        External audio files extract only audio streams
        External subtitle files extract only subtitle streams.
        All use copy mode (lossless).

        正確なFFmpegコマンドを構築.
        ビデオファイル : ビデオストリーム ( およびその内蔵オーディオ/字幕ストリーム) を抽
        外部オーディオファイル : オーディオストリームのみ抽
        外部字幕ファイル : 字幕ストリームのみ抽出.
        すべてcopyモード ( 無劣化) を使用.
        """

        # 初始化命令列表,包含 ffmpeg 路径和全局参数
        # Initialize command list with ffmpeg path and global parameters (-y, -hide_banner, -loglevel warning)
        # ffmpegパスとグローバルパラメータ (-y, -hide_banner, -loglevel warning) を含むコマンドリストを初期化
        cmd: List[str] = [self.ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'warning']
        
        # ── 输入文件
        # Input files
        # 入力ファイル ──
        # 添加主视频文件作为第 0 个输入
        # Add main video file as 0th input
        # メインビデオファイルを0番目の入力として追加
        cmd.extend(['-i', str(video_file)])          # input 0: 视频 / Video / ビデオ

        # 记录当前输入索引
        # Record current input index
        # 現在の入力インデックスを記録
        input_index = 1

        # 遍历外部音频文件,依次添加为输入
        # Iterate external audio files and add as inputs sequentially
        # 外部オーディオファイルをループし、順次入力として追加
        for af in audio_files:
            cmd.extend(['-i', str(af)])
            input_index += 1

        # 遍历外部字幕文件,依次添加为输入
        # Iterate external subtitle files and add as inputs sequentially
        # 外部字幕ファイルをループし、順次入力として追加
        for sf in subtitle_files:
            cmd.extend(['-i', str(sf)])
            input_index += 1
            
        # ── Map 映射
        # ── Map mapping: Extract video stream (mandatory), built-in audio (optional?), built-in subtitles (optional?) from video file
        # ── Mapマッピング : ビデオファイルからビデオストリーム(必須)、内蔵オーディオ(オプション?)、内蔵字幕(オプション?)を抽出

        # 从视频文件中提取 : 视频流 + 自带音频流 + 自带字幕流
        # Extract from video file: video stream + built-in audio stream + built-in subtitle stream
        # ビデオファイルから抽出 : ビデオストリーム + 内蔵オーディオストリーム + 内蔵字幕ストリーム
        cmd.extend(['-map', '0:v'])         # 视频流 ( 必须)  / Video stream (mandatory) / ビデオストリーム ( 必須) 
        cmd.extend(['-map', '0:a?'])        # 自带音频 ( 可选,?表示没有也不报错)  / Built-in audio (optional, ? means no error if not present) / 内蔵オーディオ ( オプション、?は存在しなくてもエラーにならない) 
        cmd.extend(['-map', '0:s?'])        # 自带字幕 ( 可选)  / Built-in subtitles (optional) / 内蔵字幕 ( オプション) 
        
        # 从外部音频文件中只提取音频流
        # Extract only audio streams from external audio files
        # 外部オーディオファイルからオーディオストリームのみ抽出
        for i in range(len(audio_files)):
            idx = i + 1
            cmd.extend(['-map', f'{idx}:a'])
            
        # 从外部字幕文件中只提取字幕流
        # Extract only subtitle streams from external subtitle files
        # 外部字幕ファイルから字幕ストリームのみ抽出
        sub_start = 1 + len(audio_files)
        for i in range(len(subtitle_files)):
            idx = sub_start + i
            cmd.extend(['-map', f'{idx}:s'])
            
        # ── 编码器 : 全部 copy ( 无损)  ──
        # ── Encoders: all copy (lossless) ──
        # ── エンコーダー : すべてcopy ( 無劣化)  ──
        cmd.extend(['-c:v', 'copy'])
        cmd.extend(['-c:a', 'copy'])
        cmd.extend(['-c:s', 'copy'])
        
        # ── MKV 特定选项 ──
        # ── MKV specific options: force output format to matroska (MKV) ──
        # ── MKV固有オプション : 出力フォーマットをmatroska (MKV)に強制 ──

        # 强制输出格式为 matroska (MKV)
        # Force output format to matroska (MKV)
        # 出力フォーマットをmatroska (MKV)に強制
        cmd.extend(['-f', 'matroska'])
        
        # ── 输出 ──
        # ── Output ──
        # ── 出力 ──

        # 添加输出文件路径
        # Add output file path
        # 出力ファイルパスを追加
        cmd.append(str(output_file))
        return cmd
        
    # 实例方法 : 构建备用命令 ( 字幕降级重编码) 
    # Fallback command: When -c:s copy fails, re-encode subtitles to srt/ass.
    # Keep video and audio as copy, do not use -c:s copy, let ffmpeg automatically choose MKV-compatible subtitle encoder.
    # 予備コマンド : -c:s copyが失敗した場合、字幕をsrt/assに再エンコード.
    # ビデオとオーディオはcopyを維持し、-c:s copyを使用せず、ffmpegにMKV互換の字幕エンコーダーを自動選択させる.
    def _build_command_with_subtitle_fallback(
        self,
        video_file: Path,
        audio_files: List[Path],
        subtitle_files: List[Path],
        output_file: Path,
    ) -> List[str]:

        """
        备用命令 : 当 -c:s copy 失败时,将字幕重编码为 srt/ass.
        MKV 原生支持 srt 和 ass,这是有损的字幕转换但几乎不影响使用.

        Fallback command: When -c:s copy fails, re-encode subtitles to srt/ass.
        MKV natively supports srt and ass, this is a lossy subtitle conversion but hardly affects usage.

        予備コマンド : -c:s copyが失敗した場合、字幕をsrt/assに再エンコード.
        MKVはsrtとassをネイティブサポートしており、これは劣化した字幕変換だが使用にはほとんど影響しない.
        """

        # 初始化命令列表
        # Initialize command list
        # コマンドリストを初期化
        cmd: List[str] = [self.ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'warning']

        # 添加视频输入
        # Add video input
        # ビデオ入力を追加
        cmd.extend(['-i', str(video_file)])

        # 添加音频输入
        # Add audio input
        # オーディオ入力を追加
        for af in audio_files:
            cmd.extend(['-i', str(af)])

        # 添加字幕输入
        # Add subtitle input
        # 字幕入力を追加
        for sf in subtitle_files:
            cmd.extend(['-i', str(sf)])

        # 映射视频、音频、字幕流
        # Map video, audio, subtitle streams
        # ビデオ、オーディオ、字幕ストリームをマッピング
        cmd.extend(['-map', '0:v'])
        cmd.extend(['-map', '0:a?'])
        cmd.extend(['-map', '0:s?'])
        for i in range(len(audio_files)):
            cmd.extend(['-map', f'{i + 1}:a'])
        sub_start = 1 + len(audio_files)
        for i in range(len(subtitle_files)):
            cmd.extend(['-map', f'{sub_start + i}:s'])

        # 视频和音频保持 copy
        # Keep video and audio as copy
        # ビデオとオーディオはcopyを維持
        cmd.extend(['-c:v', 'copy'])
        cmd.extend(['-c:a', 'copy'])

        # 不使用 -c:s copy,让 ffmpeg 自动选择 MKV 兼容的字幕编码器
        # 强制输出格式为 matroska

        # Do not use -c:s copy, let ffmpeg automatically choose MKV-compatible subtitle encoder
        # Force output format to matroska

        # 出力フォーマットをmatroskaに強制
        # -c:s copyを使用せず、ffmpegにMKV互換の字幕エンコーダーを自動選択させる
        cmd.extend(['-f', 'matroska'])

        # 添加输出文件
        # Add output file
        # 出力ファイルを追加
        cmd.append(str(output_file))
        return cmd

        
    # 合并执行
    # Execute merge, return whether successful. Parse all input/output paths to absolute paths.
    # Validate video file existence, filter valid audio and subtitle files.
    # 結合を実行し、成功したかどうかを返す.すべての入出力パスを絶対パスに解析.
    # ビデオファイルの存在を検証し、有効なオーディオおよび字幕ファイルをフィルタリング.
    
    # 实例方法 : 执行合并操作
    # Execute merge, return whether successful
    # 結合を実行し、成功したかどうかを返す
    def merge_files(
        self,
        video_file: Union[str, Path],
        audio_files: Optional[List[Union[str, Path]]] = None,
        subtitle_files: Optional[List[Union[str, Path]]] = None,
        output_file: Optional[Union[str, Path]] = None,
    ) -> bool:

        """
        执行合并,返回是否成功
        Execute merge, return whether successful
        結合を実行し、成功したかどうかを返す
        """
        try:

            # 解析所有输入输出路径为绝对路径
            # Parse all input/output paths to absolute paths
            # すべての入出力パスを絶対パスに解析
            video_path = Path(video_file).resolve()
            audio_paths = [Path(f).resolve() for f in (audio_files or [])]
            subtitle_paths = [Path(f).resolve() for f in (subtitle_files or [])]
            
            # 验证视频文件存在性
            # Validate video file existence
            # ビデオファイルの存在を検証
            if not video_path.is_file():
                print(f"  [错误] 视频文件不存在: {video_path}")
                return False

            # 验证并过滤有效的音频和字幕文件
            # Filter valid audio and subtitle files
            # 有効なオーディオおよび字幕ファイルをフィルタリング
            audio_paths = [p for p in audio_paths if self._check_file(p, '音频')]
            subtitle_paths = [p for p in subtitle_paths if self._check_file(p, '字幕')]
            
            # 确定输出路径
            # Determine output path (default video_name_merged.mkv), ensure extension is .mkv, create output directory
            # 出力パスを決定 ( デフォルト video_name_merged.mkv) 、拡張子が.mkvであることを確認し、出力ディレクトリを作成
            if output_file:
                output_path = Path(output_file).resolve()
            else:

                # 默认输出文件名为 视频名_merged.mkv
                # Default output filename video_name_merged.mkv
                # デフォルト出力ファイル名 video_name_merged.mkv
                output_path = video_path.parent / f"{video_path.stem}_merged.mkv"

            # 确保输出扩展名为 .mkv
            # Ensure output extension is .mkv
            # 出力拡張子が.mkvであることを確認
            if not output_path.suffix.lower() == '.mkv':
                output_path = output_path.with_suffix('.mkv')

            # 创建输出目录 ( 如果不存在) 
            # Create output directory (if not exists)
            # 出力ディレクトリを作成 ( 存在しない場合) 
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 打印合并任务摘要
            # Print merge task summary
            # 結合タスクの要約を印刷
            print(f"\n{'─' * 60}")
            print(f"  视频 : {video_path.name}")
            print(f"  音频 : {[p.name for p in audio_paths] or '无 ( 保留原音轨) '}")
            print(f"  字幕 : {[p.name for p in subtitle_paths] or '无 ( 保留原字幕) '}")
            print(f"  输出 : {output_path.name}")
            print(f"{'─' * 60}")
            
            # ── 第一次尝试 : 全部 copy
            # First attempt: all copy
            # 1回目の試行 : すべてcopy ──
            cmd = self._build_command(video_path, audio_paths, subtitle_paths, output_path)
            if self.verbose:
                print(f"\n  [命令] {' '.join(cmd)}\n")

            # 执行命令
            # Execute command
            # コマンドを実行
            success = self._execute(cmd)
            
            # 第二次尝试 : 字幕不 copy ( 降级) 
            # Second attempt: subtitles not copy (fallback re-encoding)
            # 2回目の試行 : 字幕はcopyしない ( フォールバック再エンコード) 

            # 如果第一次失败且存在字幕文件,尝试降级重编码字幕
            # If first attempt fails and subtitles exist, try fallback re-encoding subtitles
            # 1回目の試行が失敗して字幕が存在する場合、フォールバック再エンコード字幕を試す
            if not success and subtitle_paths:
                print("  [重试] 字幕 copy 失败,尝试自动编码字幕...")
                cmd2 = self._build_command_with_subtitle_fallback(
                    video_path, audio_paths, subtitle_paths, output_path
                )
                if self.verbose:
                    print(f"  [命令] {' '.join(cmd2)}\n")
                success = self._execute(cmd2)
                
            # 打印最终结果
            # Print final result
            # 最終結果を印刷
            if success:
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"\n  [成功] {output_path}  ({size_mb:.1f} MB)")
            else:
                print(f"\n  [失败] 合并未成功,请检查输入文件.")
            return success
        except Exception as e:

            # 捕获并打印异常堆栈
            # Catch and print exception stack
            # 例外スタックをキャッチして印刷
            print(f"  [异常] {e}")
            import traceback
            traceback.print_exc()
            return False
            
    # 静态方法 : 检查文件是否有效
    # Check if file is valid: skip and return False if not exists, empty (0 bytes), or inaccessible.
    # ファイルが有効かチェック : 存在しない、空 ( 0バイト) 、アクセス不可の場合はスキップしてFalseを返す.
    @staticmethod
    def _check_file(path: Path, label: str) -> bool:

        # 如果文件不存在,打印提示并返回 False
        # Skip and return False if file does not exist
        # ファイルが存在しない場合、スキップしてFalseを返す
        if not path.is_file():
            print(f"  [跳过] {label}文件不存在: {path}")
            return False
        try:

            # 如果文件为空 ( 0字节) ,打印提示并返回 False
            # Skip and return False if file is empty (0 bytes)
            # ファイルが空 ( 0バイト) の場合、スキップしてFalseを返す
            if path.stat().st_size == 0:
                print(f"  [跳过] {label}文件为空: {path}")
                return False
        except OSError:

            # 如果无法访问文件,打印提示并返回 False
            # Skip and return False if file is inaccessible
            # ファイルにアクセスできない場合、スキップしてFalseを返す
            print(f"  [跳过] {label}文件不可访问: {path}")
            return False
        return True
        
    # 静态方法 : 执行 FFmpeg 命令
    # Execute FFmpeg command: Start subprocess using Popen, wait for completion (1 hour timeout). Return code 0 indicates success.
    # FFmpegコマンドを実行 : Popenを使用してサブプロセスを開始し、完了を待つ ( 1時間タイムアウト) .リターンコード0は成功を示す.
    @staticmethod
    def _execute(cmd: List[str]) -> bool:

        """
        执行 FFmpeg 命令
        Execute FFmpeg command
        FFmpegコマンドを実行
        """
        try:

            # 使用 Popen 启动子进程
            # Start subprocess using Popen
            # Popenを使用してサブプロセスを開始
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # 等待进程结束,设置 1 小时超时
            # Wait for process to complete, set 1 hour timeout
            # プロセスの完了を待つ、1時間タイムアウトを設定
            _, stderr = process.communicate(timeout=3600)  # 1 小时超时 / 1 hour timeout / 1時間タイムアウト

            # 如果返回码为 0,表示成功
            # Return code 0 indicates success
            # リターンコード0は成功を示す
            if process.returncode == 0:
                return True

            # 打印精简的错误信息
            # Print concise error message
            # 簡潔なエラーメッセージを印刷
            if stderr:
                lines = stderr.strip().splitlines()

                # 过滤出包含关键错误词汇的行
                # Filter and print lines containing key error vocabulary
                # 重要なエラー語彙を含む行をフィルタリングして印刷
                error_lines = [
                    l for l in lines
                    if any(kw in l.lower() for kw in ('error', 'fail', 'invalid', 'not'))
                ]
                if error_lines:
                    print("  [FFmpeg 错误]:")

                    # 最多打印前 10 行错误
                    # Print up to first 10 error lines
                    # 最大最初の10行エラーを印刷
                    for el in error_lines[:10]:
                        print(f"    {el.strip()}")
                else:

                    # 如果没有匹配的关键错误,打印最后 5 行输出
                    # Print last 5 lines if no matching key errors
                    # 一致する重要なエラーがない場合、最後の5行を印刷
                    print(f"  [FFmpeg 退出码] {process.returncode}")
                    for l in lines[-5:]:
                        print(f"    {l.strip()}")
            return False
        except subprocess.TimeoutExpired:

            # 超时处理 : 强制杀死进程
            # Timeout handling: Force kill process
            # タイムアウト処理 : プロセスを強制キル
            process.kill()
            print("  [超时] FFmpeg 执行超时")
            return False
        except Exception as e:
            print(f"  [执行异常] {e}")
            return False
            
    # 交互模式
    # Interactive file selection. Core improvement: Detect actual stream types via ffprobe, no longer relying on extension classification.
    # 対話型ファイル選択.中核となる改善点 : ffprobeを通じて実際のストリームタイプを検出し、拡張子分類に依存しない.
    
    # 实例方法 : 交互式文件选择
    # Interactive file selection
    # 対話型ファイル選択
    def interactive(self) -> bool:

        """
        交互式文件选择.
        核心改进 : 通过 ffprobe 检测实际流类型,
        .webm ( 纯音频) 会出现在音频列表中,
        不再依赖扩展名分类.

        Interactive file selection.
        Core improvement: Detect actual stream types via ffprobe,
        .webm (pure audio) will appear in audio list,
        no longer rely on extension classification.

        対話型ファイル選択.
        中核となる改善点 : ffprobeを通じて実際のストリームタイプを検出し、
        .webm ( 純粋なオーディオ) はオーディオリストに表示され、
        拡張子分類に依存しない.
        """
        try:

            # 打印交互模式欢迎信息
            # Print welcome info for interactive mode
            # 対話モードの歓迎情報を印刷
            print(f"\n{'═' * 60}")
            print("  FFmpeg 媒体合并器 — 交互模式")
            print(f"  工作目录: {self.working_dir}")
            print(f"{'═' * 60}")
            
            # 扫描
            # Scan
            # スキャン
            print("\n  正在扫描目录并检测文件流类型...")
            video_list, _, _ = self.scan_directory()
            audio_list = self.scan_all_for_audio()
            subtitle_list = self.scan_all_for_subtitles()
            
            # 步骤 1: 选择视频
            # Step 1: Select video
            # ステップ1 : ビデオ選択
            if not video_list:
                print("  [错误] 目录中未找到含视频流的文件")
                return False
            print(f"\n  [步骤 1/3] 选择视频文件 ( 共 {len(video_list)} 个) ")
            print(f"  {'─' * 50}")

            # 打印视频列表及流信息
            # Print video list and stream info
            # ビデオリストとストリーム情報を印刷
            for i, v in enumerate(video_list, 1):
                size_mb = v.path.stat().st_size / (1024 * 1024)
                tag = f"V×{v.video_count}"
                if v.has_audio:
                    tag += f" A×{v.audio_count}"
                if v.has_subtitle:
                    tag += f" S×{v.subtitle_count}"
                print(f"    {i:3d}. {v.path.name}  [{tag}]  {size_mb:.1f} MB")

            # 获取用户选择的视频
            # Get user-selected video
            # ユーザー選択ビデオを取得
            video_info = self._pick_one(video_list, "视频")
            if not video_info:
                return False
            print(f"  -> 已选: {video_info.path.name}\n")
            
            # 步骤 2: 选择音频
            # Step 2: Select audio (exclude selected video)
            # ステップ2 : オーディオ選択 ( 選択したビデオを除外) 

            # 排除已选的视频文件本身
            # Exclude selected video file itself
            # 選択したビデオファイル自体を除外
            audio_candidates = [a for a in audio_list if a.path != video_info.path]
            print(f"  [步骤 2/3] 选择音频文件 ( 共 {len(audio_candidates)} 个,可多选) ")
            print(f"  {'─' * 50}")
            if audio_candidates:
                for i, a in enumerate(audio_candidates, 1):
                    size_mb = a.path.stat().st_size / (1024 * 1024)
                    tag = f"A×{a.audio_count}"
                    ext = a.path.suffix.lower()
                    print(f"    {i:3d}. {a.path.name}  [{tag}] ({ext})  {size_mb:.1f} MB")

                # 获取用户多选音频
                # Get user multi-select audio
                # ユーザー複数選択オーディオを取得
                selected_audio = self._pick_multiple(audio_candidates, "音频")
            else:
                print("     ( 目录中无可用音频文件) ")
                selected_audio = []

            # 打印选择结果
            # Print selection results
            # 選択結果を印刷
            if selected_audio:
                print(f"  -> 已选 {len(selected_audio)} 个音频:")
                for a in selected_audio:
                    print(f"       {a.path.name}")
            else:
                print("  -> 未选择外部音频 ( 将保留视频原音轨) ")
            print()
            
            # 步骤 3: 选择字幕
            # Step 3: Select subtitles
            # ステップ3 : 字幕選択

            # 排除已选的视频文件本身
            # Exclude selected video file itself
            # 選択したビデオファイル自体を除外
            subtitle_candidates = [s for s in subtitle_list if s.path != video_info.path]
            print(f"  [步骤 3/3] 选择字幕文件 ( 共 {len(subtitle_candidates)} 个,可多选) ")
            print(f"  {'─' * 50}")
            if subtitle_candidates:
                for i, s in enumerate(subtitle_candidates, 1):
                    size_kb = s.path.stat().st_size / 1024
                    ext = s.path.suffix.lower()
                    print(f"    {i:3d}. {s.path.name}  ({ext})  {size_kb:.1f} KB")

                # 获取用户多选字幕
                # Get user multi-select subtitles
                # ユーザー複数選択字幕を取得
                selected_subs = self._pick_multiple(subtitle_candidates, "字幕")
            else:
                print("     ( 目录中无可用字幕文件) ")
                selected_subs = []

            # 打印选择结果
            # Print selection results
            # 選択結果を印刷
            if selected_subs:
                print(f"  -> 已选 {len(selected_subs)} 个字幕:")
                for s in selected_subs:
                    print(f"       {s.path.name}")
            else:
                print("  -> 未选择外部字幕")
            print()
            
            # 确认
            # Confirm
            # 確認
            print(f"{'═' * 60}")
            print(f"  视频: {video_info.path.name}")
            print(f"  音频: {[a.path.name for a in selected_audio] or '保留原音轨'}")
            print(f"  字幕: {[s.path.name for s in selected_subs] or '无'}")
            print(f"{'═' * 60}")

            # 等待用户确认
            # Wait for user confirmation
            # ユーザー確認を待つ
            confirm = input("\n  确认执行？(Y/n): ").strip().lower()
            if confirm == 'n':
                print("  已取消.")
                return False
                
            # 输出文件名
            # Output filename
            # 出力ファイル名
            default_name = f"{video_info.path.stem}_merged.mkv"
            out_input = input(f"  输出文件名 (回车使用 {default_name}): ").strip()
            if not out_input:
                out_input = default_name
            if not out_input.lower().endswith('.mkv'):
                out_input += '.mkv'
            output_path = self.working_dir / out_input
            
            # 执行
            # Execute
            # 実行

            # 调用 merge_files 执行实际合并
            # Call merge_files to execute actual merge
            # merge_filesを呼び出して実際の結合を実行
            return self.merge_files(
                video_info.path,
                [a.path for a in selected_audio],
                [s.path for s in selected_subs],
                output_path,
            )
        except KeyboardInterrupt:

            # 捕获 Ctrl+C 中断
            # Catch Ctrl+C interrupt
            # Ctrl+C割り込みをキャッチ
            print("\n\n  操作已取消.")
            return False
        except Exception as e:

            # 捕获其他异常
            # Catch other exceptions
            # 他の例外をキャッチ
            print(f"\n  [错误] {e}")
            import traceback
            traceback.print_exc()
            return False
            
    # 静态方法 : 从列表中选择单个文件
    # Pick one from list: Supports numeric index or filename keyword matching.
    # リストから1つ選択 : 数字インデックスまたはファイル名キーワードマッチングをサポート.
    @staticmethod
    def _pick_one(items: List[StreamInfo], label: str) -> Optional[StreamInfo]:

        """
        从列表中选一个
        Pick one from list
        リストから1つ選択
        """
        while True:
            # 获取用户输入
            # Get user input
            # ユーザー入力を取得
            raw = input(f"  请输入编号 (1-{len(items)}) 或文件名关键字: ").strip()
            if not raw:
                continue

            # 如果输入的是数字
            # If input is number
            # 入力が数字の場合
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(items):
                    return items[idx]
                print(f"  编号超出范围,请重试")
                continue

            # 如果是关键字匹配
            # If keyword matching
            # キーワードマッチングの場合
            keyword = raw.lower()
            matches = [it for it in items if keyword in it.path.name.lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"  匹配到 {len(matches)} 个文件,请更精确:")
                for m in matches:
                    print(f"    {m.path.name}")
                continue
            else:

                # 尝试作为完整路径解析
                # Try parsing as full path
                # 完全パスとして解析を試みる
                p = Path(raw)
                if p.is_file():
                    dummy = StreamInfo(p)
                    dummy.has_video = True
                    return dummy
                print(f"  未匹配到任何文件,请重试")
                
    # 静态方法 : 从列表中多选文件
    # Pick multiple from list: Supports comma/space separation, supports 'all' keyword for select all, Enter to skip.
    # リストから複数選択 : カンマ/スペース区切りをサポートし、'all'キーワードで全選択をサポート、Enterでスキップ.
    @staticmethod
    def _pick_multiple(items: List[StreamInfo], label: str) -> List[StreamInfo]:

        """
        从列表中多选 ( 逗号/空格分隔) ,支持 all 关键字
        Multi-select from list (comma/space separated), supports 'all' keyword
        リストから複数選択 ( カンマ/スペース区切り) 、'all'キーワードをサポート
        """
        while True:
            raw = input(
                f"  请输入编号 (逗号分隔, 'all'=全选, 回车=跳过): "
            ).strip()

            # 回车跳过
            # Enter to skip
            # Enterでスキップ
            if not raw:
                return []

            # 全选
            # Select all
            # 全選択
            if raw.lower() == 'all':
                return list(items)

            # 支持逗号和空格分隔
            # Support comma and space separation
            # カンマとスペース区切りをサポート
            parts = raw.replace(',', ' ').split()
            selected = []
            valid = True
            for part in parts:
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(items):
                        if items[idx] not in selected:
                            selected.append(items[idx])
                    else:
                        print(f"  编号 {part} 超出范围")
                        valid = False
                else:

                    # 关键字匹配
                    # Keyword matching
                    # キーワードマッチング
                    keyword = part.lower()
                    matches = [it for it in items if keyword in it.path.name.lower()]
                    for m in matches:
                        if m not in selected:
                            selected.append(m)
            if not selected and valid:
                print("  未匹配到有效文件")
                continue
            return selected
            
    # 自动模式
    # Automatically match same-name files and merge.
    # Determine output directory, scan directory to get all media lists.
    # 同名ファイルを自動的にマッチングして結合.
    # 出力ディレクトリを決定し、ディレクトリをスキャンしてすべてのメディアリストを取得.
    
    # 实例方法 : 自动匹配同名文件并合并
    # Automatically match same-name files and merge
    # 同名ファイルを自動的にマッチングして結合
    def auto_merge(self, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, bool]:

        """
        自动匹配同名文件并合并
        Automatically match same-name files and merge
        同名ファイルを自動的にマッチングして結合
        """
        results: Dict[str, bool] = {}

        # 确定输出目录
        # Determine output directory
        # 出力ディレクトリを決定
        out_dir = Path(output_dir).resolve() if output_dir else self.working_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        # 扫描目录
        # Scan directory
        # ディレクトリをスキャン
        video_list, _, _ = self.scan_directory()
        all_audio = self.scan_all_for_audio()
        all_subs = self.scan_all_for_subtitles()
        if not video_list:
            print("  [错误] 目录中未找到含视频流的文件")
            return results
        print(f"  找到 {len(video_list)} 个视频文件\n")

        # 遍历每个视频文件
        # Iterate through each video file
        # 各ビデオファイルをループ
        for v in video_list:
            stem = v.path.stem.lower()

            # 匹配同名的外部音频 ( 排除视频文件自身) 
            # Match external audio with same name (exclude video file itself)
            # 同名の外部オーディオをマッチング ( ビデオファイル自体を除外) 
            matched_audio = [
                a for a in all_audio
                if a.path != v.path and stem in a.path.stem.lower()
            ]

            # 匹配同名的外部字幕 ( 排除视频文件自身) 
            # Match external subtitles with same name (exclude video file itself)
            # 同名の外部字幕をマッチング ( ビデオファイル自体を除外) 
            matched_subs = [
                s for s in all_subs
                if s.path != v.path and stem in s.path.stem.lower()
            ]
            output_path = out_dir / f"{v.path.stem}_merged.mkv"
            print(f"  处理: {v.path.name}")
            print(f"    音频: {[a.path.name for a in matched_audio] or '无'}")
            print(f"    字幕: {[s.path.name for s in matched_subs] or '无'}")

            # 执行合并
            # Execute merge
            # 結合を実行
            success = self.merge_files(
                v.path,
                [a.path for a in matched_audio],
                [s.path for s in matched_subs],
                output_path,
            )
            results[v.path.stem] = success
            print()
        return results

# 入口
# Entry point
# エントリーポイント

# 定义主函数
# Define main function
# メイン関数を定義
def main():

    # 导入命令行参数解析模块
    # Import command-line argument parsing module (argparse)
    # コマンドライン引数解析モジュール (argparse) をインポート
    import argparse

    # 创建解析器对象
    # Create parser object and add arguments (working dir, auto mode, interactive mode, manual file specification, etc.)
    # パーサーオブジェクトを作成して引数を追加 ( 作業ディレクトリ、自動モード、対話モード、手動ファイル指定など) 
    parser = argparse.ArgumentParser(
        description='FFmpeg 媒体合并器 v3 — 基于 ffprobe 流类型检测 / FFmpeg Media Merger v3 — Based on ffprobe stream type detection / FFmpegメディアマージャー v3 — ffprobeストリームタイプ検出に基づく'
    )

    # 添加命令行参数
    # Add command-line arguments
    # コマンドライン引数を追加
    parser.add_argument('-d', '--dir', help='工作目录 ( 默认当前目录)  / Working directory (default current directory) / 作業ディレクトリ ( デフォルト現在のディレクトリ) ')
    parser.add_argument('-a', '--auto', action='store_true', help='自动匹配模式 / Auto-match mode / 自動マッチングモード')
    parser.add_argument('-o', '--output-dir', help='输出目录 ( 自动模式)  / Output directory (auto mode) / 出力ディレクトリ ( 自動モード) ')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式 / Interactive mode / 対話モード')
    parser.add_argument('-q', '--quiet', action='store_true', help='安静模式 / Quiet mode / 静かなモード')
    parser.add_argument('-v', '--video', help='手动指定视频文件 / Manually specify video file / 手動でビデオファイルを指定')
    parser.add_argument('-A', '--audio', nargs='*', help='手动指定音频文件 / Manually specify audio files / 手動でオーディオファイルを指定')
    parser.add_argument('-S', '--subtitle', nargs='*', help='手动指定字幕文件 / Manually specify subtitle files / 手動で字幕ファイルを指定')
    parser.add_argument('-O', '--output', help='手动指定输出文件 / Manually specify output file / 手動で出力ファイルを指定')
    parser.add_argument('-I', '--info', help='显示文件流信息 / Display file stream info / ファイルストリーム情報を表示')

    # 解析参数
    # Parse arguments
    # 引数を解析
    args = parser.parse_args()
    try:

        # 初始化合并器实例
        # Initialize merger instance
        # マージャーインスタンスを初期化
        merger = FFmpegMediaMerger(args.dir)
        merger.verbose = not args.quiet

        # 处理 --info 参数 : 仅显示文件流信息
        # Handle --info argument: Only display file stream info
        # --info 引数を処理 : ファイルストリーム情報のみを表示
        if args.info:
            info = merger.probe_file(Path(args.info).resolve())
            print(f"\n  文件: {info.path.name}")
            print(f"  视频流: {info.video_count}")
            print(f"  音频流: {info.audio_count}")
            print(f"  字幕流: {info.subtitle_count}")
            if info.streams:
                print(f"\n  详细流信息:")
                for i, s in enumerate(info.streams):
                    ct = s.get('codec_type', '?')
                    cn = s.get('codec_name', '?')
                    print(f"    [{i}] {ct} / {cn}")
            return

        # 处理手动指定视频参数 : 直接合并
        # Handle manual video argument: Merge directly
        # 手動ビデオ引数を処理 : 直接結合
        if args.video:
            merger.merge_files(args.video, args.audio, args.subtitle, args.output)
            return

        # 处理自动模式参数
        # Handle auto mode argument: Execute auto-matching and print success rate
        # 自動モード引数を処理 : 自動マッチングを実行し成功率を印刷
        if args.auto:
            results = merger.auto_merge(args.output_dir)
            print(f"\n{'═' * 60}")
            ok = sum(1 for v in results.values() if v)
            total = len(results)
            print(f"  自动合并完成: {ok}/{total} 成功")
            for name, success in results.items():
                print(f"    {'[OK]' if success else '[FAIL]'} {name}")
            return

        # 默认进入交互模式
        # Default to interactive mode
        # デフォルトに対話モード
        merger.interactive()
    except Exception as e:

        # 捕获致命错误并退出
        # Catch fatal errors and exit
        # 致命的なエラーをキャッチして終了
        print(f"  [致命错误] {e}")
        sys.exit(1)

# 脚本入口点判断
# Script entry point check, call main function
# スクリプトエントリポイントチェック、メイン関数を呼び出す
if __name__ == '__main__':
    # 调用主函数
    # Call main function
    # メイン関数を呼び出す
    main()
