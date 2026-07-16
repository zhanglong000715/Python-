#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================================
脚本名称: AV_Stream_Splitter.py
作者: 张龙 (zhang_long)
============================================================================

==========================
中文 (Chinese)
==========================

[脚本简介]

本脚本是一个基于 FFmpeg / FFprobe 的自动化音视频流分离工具.

它会自动扫描脚本所在目录下的所有文件, 利用 FFprobe 探测每个文件的

媒体流信息(音频轨、视频轨、字幕轨), 然后将每一条音频轨从原始容器中

无损提取(-c copy, 不涉及重新编码)并导出为独立的文件.

核心特性 : 

1. 无损提取 : 全程使用 stream copy 模式, 保证音轨和字幕零质量损失.

2. 智能容器选择 : 优先使用原始容器格式 ; 若音频编码为 FLAC 则优先

导出为 .flac ; 当文件包含字幕时, 优先选择支持内嵌字幕的容器格式

(如 .mkv / .mka / .mp4 / .mov / .webm).

3. 字幕处理 : 如果可以将字幕封装进音频容器, 则一并封装 ; 否则单独

提取字幕为独立文件(.srt / .ass / .sup 等).

4. 自动容错 : 当首选容器封装失败时, 自动尝试备选容器格式, 采用

"最佳努力"策略确保尽可能成功导出.

5. 文件命名 : 输出文件名包含来源文件名、流类型、流索引、编码名称、

语言标签和标题信息, 自动避免文件名冲突.

6. 支持格式广泛 : 涵盖 mp4、mkv、avi、mov、flv、wmv、ts、webm、

mp3、wav、flac 等数十种常见音视频及字幕格式.

使用方式 : 

将本脚本放置于包含媒体文件的目录中, 直接运行即可.

系统需预先安装 ffmpeg 和 ffprobe 并将其加入 PATH 环境变量.

==========================
日本語 (Japanese)
==========================

日本語: 
このスクリプトは、FFmpeg / FFprobe を基盤とした自動化された音声・映像ストリーム分離ツールです.

スクリプトが置かれたディレクトリ内の対象ファイルを自動的に走査し、FFprobe で各ファイルのメディア情報を検出します.

メディアストリーム情報(音声トラック、映像トラック、字幕トラック)を取得し、その後各音声トラックを元のコンテナから抽出します.

その際、-c copy を用いて再エンコードなしの無劣化抽出を行い、個別のファイルとして出力します.

主要な特徴は、無劣化抽出・柔軟なコンテナ選択・字幕の扱い・失敗時の代替手段・命名の整理にあります.

1. 無劣化抽出: すべての処理で stream copy モードを用い、音声と字幕の品質劣化を防ぎます.

2. インテリジェントなコンテナ選択: まず元のコンテナ形式を優先し、音声コーデックが FLAC の場合は .flac を優先します.

さらに、字幕を含む入力では、字幕を埋め込めるコンテナ形式(例: .mkv / .mka / .mp4 / .mov / .webm)を優先的に選びます.

(例: .mkv / .mka / .mp4 / .mov / .webm)

3. 字幕処理: 字幕を音声出力に同梱できる場合は一緒に封入し、できない場合は別に抽出します.

その場合、字幕は .srt / .ass / .sup などの独立ファイルとして出力します.

4. 自動フォールバック: 優先したコンテナでの封入に失敗した場合、代替フォーマットを自動的に試し、可能な限り成功を狙います.

「ベストエフォート」戦略により、可能な限り成功するように処理を進めます.

5. ファイル命名: 出力ファイル名には、元ファイル名・ストリーム種別・ストリーム番号・コーデック名が含まれます.

さらに、言語タグやタイトル情報も反映され、重複ファイル名を避けるための自動的な調整も行われます.

6. 幅広い対応形式: mp4、mkv、avi、mov、flv、wmv、ts、webm、

mp3、wav、flac など、数十種類の一般的な音声・映像・字幕形式を扱えます.

使い方:

このスクリプトをメディアファイルを含むディレクトリに置き、直接実行してください.

システムには ffmpeg と ffprobe をあらかじめインストールし、PATH に登録しておく必要があります.

==========================
English
==========================

English: 
This script is an automated audio/video stream separation tool based on FFmpeg and FFprobe.

It automatically scans files in the directory where the script is located and probes each file with FFprobe.

It reads stream information such as audio, video, and subtitle tracks, then extracts each audio track from the original container.

In this process, it uses -c copy for lossless extraction without re-encoding and exports each track as a separate file.

Its core features include lossless extraction, flexible container selection, subtitle handling, fallback behavior on failure, and structured naming.

1. Lossless extraction: The workflow uses stream copy mode throughout to prevent any quality loss in audio and subtitles.

2. Smart container selection: It prefers the original container format first, and if the audio codec is FLAC, it prioritizes .flac.

When the source file contains subtitles, it also prioritizes container formats that support embedded subtitles, such as .mkv, .mka, .mp4, .mov, and .webm.

(for example, .mkv / .mka / .mp4 / .mov / .webm)

3. Subtitle handling: If subtitles can be muxed into the audio output, they are bundled together; otherwise, they are extracted separately.

In that case, subtitles are exported as standalone files such as .srt, .ass, or .sup.

4. Automatic fallback: If the preferred container fails to mux, the script automatically tries alternative formats and follows a best-effort strategy.

It uses a best-effort strategy to maximize the chance of a successful export.

5. File naming: Output filenames contain the source filename, stream type, stream index, and codec name.

Language tags and title metadata are also included, and the script automatically avoids filename conflicts.

6. Broad format support: It covers mp4, mkv, avi, mov, flv, wmv, ts, webm,

mp3, wav, flac, and dozens of other common audio, video, and subtitle formats.

Usage:

Place this script in a directory containing media files and run it directly.

The system must have ffmpeg and ffprobe installed and available in the PATH environment variable.

============================================================================

"""


# 导入操作系统相关模块, 用于文件和路径操作
# 日本語: ファイルやディレクトリの操作に必要な標準ライブラリを読み込みます.
# English: Import the standard library modules needed for file and path operations.
import os
# 导入系统相关模块, 用于退出程序和访问命令行参数
# 日本語: プログラムの終了やコマンドライン引数の取得に関する機能を読み込みます.
# English: Import the module used to exit the program and access command-line arguments.
import sys
# 导入JSON模块, 用于解析FFprobe输出的JSON格式数据
# 日本語: FFprobe の出力を JSON として解析するためのモジュールを読み込みます.
# English: Import the JSON module used to parse FFprobe output.
import json
# 导入shutil模块, 用于检测系统命令是否可用(which功能)
# 日本語: システム上のコマンドが利用可能かを確認するためのモジュールを読み込みます.
# English: Import the shutil module used to check whether a system command is available.
import shutil
# 导入subprocess模块, 用于调用外部程序(ffmpeg/ffprobe)
# 日本語: ffmpeg や ffprobe などの外部コマンドを実行するためのモジュールを読み込みます.
# English: Import the subprocess module used to invoke external programs such as ffmpeg and ffprobe.
import subprocess

# 获取当前脚本文件所在的绝对目录路径, 所有输入输出文件都基于此目录
# 日本語: スクリプト自身のあるディレクトリを基準パスとして取得し、入出力ファイルの配置先に用います.
# English: Get the absolute directory of the script so all input and output files are handled relative to it.
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

# 定义已知媒体文件格式的集合(包含视频、音频、纯音频、裸流、字幕等格式)
# 日本語: 音声・映像・字幕など、スクリプトが扱えるメディア形式の拡張子をまとめた集合です.
# English: This set collects the media extensions, including video, audio, raw streams, and subtitles, that the script can handle.
# 用于判断一个文件的扩展名是否属于本脚本可处理的媒体格式
# 日本語: これにより、入力ファイルの拡張子がこのスクリプトの処理対象に含まれるかを判断できます.
# English: It is used to determine whether a given file extension belongs to the formats supported by this script.

KNOWN_FORMATS = {
    # 常见视频容器格式 | Common video container formats / 一般的なビデオコンテナフォーマット
    'mp4','mkv','avi','mov','flv','wmv','mpg','mpeg','mts','m2ts','ts','vob','rm','rmvb','asf',
    
    # 移动端及其他视频格式 | Mobile and other video formats / モバイルおよびその他のビデオフォーマット
    '3gp','3g2','divx','f4v','ogv','dv',
    
    # Web媒体格式 | Web media formats / Webメディアフォーマット
    'webm','ogg','ogx','m4v',
    
    # 常见音频格式 | Common audio formats / 一般的なオーディオフォーマット
    'mp3','wav','aac','m4a','flac','oga','opus','wma','ac3','dts','eac3','mka','aiff','aif',
    
    # 无损/有损压缩音频及有声书等格式 | Lossless/lossy compressed audio and audiobook formats / 可逆・非可逆圧縮オーディオおよびオーディオブックフォーマット
    'm4b','ape','tta','mp2','amr','mpc','wv','spx','ra','ram','caf',
    
    # 裸视频编码流格式 | Raw video codec stream formats / 裸のビデオコーデックストリームフォーマット
    'h264','h265','hevc','avc','vp9','ivf',
    
    # 常见字幕文件格式 | Common subtitle file formats / 一般的な字幕ファイルフォーマット
    'srt','ass','ssa','sub','idx','vtt','ttml','dfxp','smi','sami','mpl','pjs','stl','sup','pgs','sbv','lrc','rt','txt'
}

# 音频编解码器名称到推荐输出文件扩展名的映射字典
# 日本語: 音声コーデック名から、出力時に適した拡張子を割り当てるための対応表です.
# English: This mapping associates audio codec names with the file extension that is most suitable for export.
# 当从容器中提取音轨时, 根据编码类型决定保存为什么格式的文件
# 日本語: コンテナから音声トラックを抽出する際、コーデックの種類に応じて保存形式を決めるために使います.
# English: When extracting an audio track from a container, it is used to decide which file format to save it as based on the codec type.

AUDIO_CODEC_TO_EXT = {
    'flac': '.flac',                                          # FLAC无损音频 -> .flac文件 | FLAC lossless audio -> .flac file / FLAC可逆圧縮オーディオ -> .flacファイル
    'mp3': '.mp3',                                            # MP3有损音频 -> .mp3文件 | MP3 lossy audio -> .mp3 file / MP3非可逆圧縮オーディオ -> .mp3ファイル
    'aac': '.m4a',                                            # AAC音频 -> .m4a文件 | AAC audio -> .m4a file / AACオーディオ -> .m4aファイル
    'adts': '.m4a',                                           # ADTS格式的AAC音频 -> .m4a文件 | ADTS-framed AAC audio -> .m4a file / ADTSフレームAACオーディオ -> .m4aファイル
    'aac_latm': '.m4a',                                       # LATM传输格式的AAC音频 -> .m4a文件 | LATM transport AAC audio -> .m4a file / LATMトランスポートAACオーディオ -> .m4aファイル
    'opus': '.ogg',                                           # Opus音频 -> .ogg文件 | Opus audio -> .ogg file / Opusオーディオ -> .oggファイル
    'vorbis': '.ogg',                                          # Vorbis音频 -> .ogg文件 | Vorbis audio -> .ogg file / Vorbisオーディオ -> .oggファイル
    'pcm_s16le': '.wav', 'pcm_s24le': '.wav',                 # PCM 16位/24位有符号小端 -> .wav文件 | PCM 16/24-bit signed little-endian -> .wav file / PCM 16/24ビット符号付きリトルエンディアン -> .wavファイル
    'pcm_u8': '.wav', 'pcm_s16be': '.wav',                    # PCM 8位无符号/16位大端 -> .wav文件 | PCM 8-bit unsigned / 16-bit big-endian -> .wav file / PCM 8ビット符号なし・16ビットビッグエンディアン -> .wavファイル
    'alac': '.m4a',                                           # Apple无损音频 -> .m4a文件 | Apple Lossless audio -> .m4a file / Apple可逆圧縮オーディオ -> .m4aファイル
    'ac3': '.ac3', 'eac3': '.eac3', 'dts': '.dts',           # AC3/EAC3/DTS环绕声音频 -> 对应扩展名 | AC3/EAC3/DTS surround audio -> corresponding extensions / AC3/EAC3/DTSサラウンドオーディオ -> 対応する拡張子
    'wavpack': '.wv', 'tta': '.tta', 'ape': '.ape',          # WavPack/TTA/APE无损音频 -> 对应扩展名 | WavPack/TTA/APE lossless audio -> corresponding extensions / WavPack/TTA/APE可逆圧縮オーディオ -> 対応する拡張子
    'mp2': '.mp2', 'amr': '.amr', 'wma': '.wma'              # MP2/AMR/WMA音频 -> 对应扩展名 | MP2/AMR/WMA audio -> corresponding extensions / MP2/AMR/WMAオーディオ -> 対応する拡張子
}

# 字幕编解码器名称到推荐输出文件扩展名的映射字典
# 日本語: 字幕コーデック名から、出力時に適した拡張子を割り当てるための対応表です.
# English: This mapping associates subtitle codec names with the file extension that is most suitable for export.
# 当从容器中提取字幕流时, 根据编码类型决定保存为什么格式的文件
# 日本語: コンテナから字幕ストリームを抽出する際、コーデックの種類に応じて保存形式を決めるために使います.
# English: When extracting a subtitle stream from a container, it is used to decide which file format to save it as based on the codec type.

SUB_CODEC_TO_EXT = {
    'subrip': '.srt', 'srt': '.srt',                          # SubRip字幕 -> .srt文件 | SubRip subtitles -> .srt file / SubRip字幕 -> .srtファイル
    'ass': '.ass', 'ssa': '.ass',                             # ASS/SSA高级字幕 -> .ass文件 | ASS/SSA advanced subtitles -> .ass file / ASS/SSA高度な字幕 -> .assファイル
    'webvtt': '.vtt', 'vtt': '.vtt',                          # WebVTT网页字幕 -> .vtt文件 | WebVTT web subtitles -> .vtt file / WebVTTウェブ字幕 -> .vttファイル
    'hdmv_pgs_subtitle': '.sup', 'pgs': '.sup',               # 蓝光PGS图形字幕 -> .sup文件 | Blu-ray PGS graphic subtitles -> .sup file / Blu-ray PGSグラフィック字幕 -> .supファイル
    'dvd_subtitle': '.sub',                                    # DVD VobSub字幕 -> .sub文件 | DVD VobSub subtitles -> .sub file / DVD VobSub字幕 -> .subファイル
    'mov_text': '.txt',                                        # QuickTime/MOV文本字幕 -> .txt文件 | QuickTime/MOV text subtitles -> .txt file / QuickTime/MOVテキスト字幕 -> .txtファイル
    'xsub': '.sub'                                             # XSUB字幕(DivX) -> .sub文件 | XSUB subtitles (DivX) -> .sub file / XSUB字幕(DivX) -> .subファイル
}

# 定义支持内嵌字幕流的容器格式集合
# 日本語: 字幕をコンテナ内に埋め込める形式の集合です.
# English: This set lists container formats that can embed subtitle streams.
# 当源文件包含字幕时, 优先尝试将音频和字幕一起封装到这些容器中
# 日本語: 元ファイルに字幕が含まれている場合は、まずこれらの形式で音声と字幕をまとめて封入しようとします.
# English: When the source file contains subtitles, the script first tries to mux audio and subtitles together into these container formats.

SUBTITLE_CAPABLE = {'.mkv', '.mka', '.mp4', '.mov', '.webm', '.ogg'}

# ======================== 工具函数定义 ========================

def check_tools():
    """
    检查系统是否已安装 ffmpeg 和 ffprobe 命令行工具.
    日本語: システムに ffmpeg と ffprobe のコマンドがインストールされているか確認し、どちらかが欠けていれば終了します.
    English: Check whether the ffmpeg and ffprobe command-line tools are installed on the system; if either is missing, exit the program.
    如果任一工具不可用, 则打印提示信息并退出程序.
    日本語: いずれかが利用できない場合は、メッセージを表示して終了します.
    English: If either tool is unavailable, print a message and terminate the program.
    """
    # 使用shutil.which检测ffmpeg命令是否在系统PATH中可用
    # 日本語: shutil.which を使って、ffmpeg と ffprobe が PATH 上で実行可能か確認します.
    # English: Use shutil.which to check whether ffmpeg and ffprobe are executable via the PATH environment.
    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        # 如果ffmpeg或ffprobe未找到, 打印错误提示信息
        # 日本語: ffmpeg または ffprobe が見つからない場合、エラーメッセージを表示します.
        # English: If ffmpeg or ffprobe is not found, print an error message.
        print('需要系统已安装 ffmpeg 和 ffprobe 并在 PATH 中.')
        # 以退出码1终止程序, 表示异常退出
        # 日本語: 終了コード 1 でプログラムを異常終了させます.
        # English: Exit the program with code 1 to indicate an abnormal termination.
        sys.exit(1)

def ffprobe_json(path):
    """
    调用 ffprobe 探测指定媒体文件, 获取所有流的详细信息并以字典形式返回.
    日本語: 指定されたメディアファイルを ffprobe で解析し、全ストリームの詳細情報を辞書として返します.
    English: Probe the target media file with ffprobe and return a dictionary containing detailed stream information.
    参数 path: 待探测的媒体文件的完整路径.
    日本語: path: 調査対象のメディアファイルの絶対パス.
    English: path: The full path of the media file to probe.
    返回值: 解析后的JSON字典, 包含streams等信息 ; 探测失败时返回None.
    日本語: 戻り値: 解析済みの JSON 辞書で、streams などの情報を含む.失敗時は None を返す.
    English: Return value: A parsed JSON dictionary containing stream information such as streams; returns None if probing fails.
    """
    # 构建ffprobe命令行参数列表 : 
    # 日本語: ffprobe に渡す引数を組み立てます.
    # English: Build the argument list for ffprobe.
    # -v error: 只输出错误级别的日志(减少干扰信息)
    # 日本語: -v error: エラーレベルのログだけを出力し、余分な情報を抑えます.
    # English: -v error: Only output error-level logs to reduce noise.
    # -print_format json: 以JSON格式输出结果
    # 日本語: -print_format json: 結果を JSON 形式で出力します.
    # English: -print_format json: Output the result in JSON format.
    # -show_streams: 显示所有媒体流的详细信息
    # 日本語: -show_streams: すべてのメディアストリームの詳細を表示します.
    # English: -show_streams: Show detailed information for all media streams.
    cmd = ['ffprobe','-v','error','-print_format','json','-show_streams',path]
    try:
        # 执行ffprobe命令, 捕获标准输出和标准错误输出, check=True表示非零退出码时抛出异常
        # 日本語: ffprobe を実行し、標準出力と標準エラーを取得します.check=True により、失敗時は例外になります.
        # English: Run ffprobe and capture both stdout and stderr; check=True raises an exception on a non-zero exit code.
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # 将标准输出从字节流解码为UTF-8字符串(忽略无法解码的字符), 然后解析为JSON字典并返回
        # 日本語: 標準出力を UTF-8 としてデコードし、JSON として解析して返します.
        # English: Decode stdout as UTF-8, ignoring undecodable characters, parse it as JSON, and return the resulting dictionary.
        return json.loads(p.stdout.decode('utf-8', errors='ignore'))
    except subprocess.CalledProcessError as e:
        # 如果ffprobe执行失败(返回非零退出码), 捕获异常并打印错误信息
        # 日本語: ffprobe が失敗した場合、例外を捕捉してエラー内容を表示します.
        # English: If ffprobe fails with a non-zero exit code, catch the exception and print the error message.
        print('ffprobe 错误 for {}:'.format(os.path.basename(path)), e.stderr.decode('utf-8', errors='ignore'))
        # 返回None表示探测失败
        # 日本語: 失敗を示すために None を返します.
        # English: Return None to indicate probing failure.
        return None

def classify_streams(info):
    """
    将 ffprobe 返回的流信息按类型分类为音频流、视频流和字幕流.
    日本語: ffprobe の結果を、音声・映像・字幕の各ストリームに分けて整理します.
    English: Categorize the ffprobe stream information into audio, video, and subtitle streams.
    参数 info: ffprobe_json() 返回的字典.
    日本語: info: ffprobe_json() が返した辞書.
    English: info: The dictionary returned by ffprobe_json().
    返回值: 四元组 (音频流列表, 视频流列表, 字幕流列表, 全部流列表).
    日本語: 戻り値: 4要素のタプル (音声ストリーム一覧, 映像ストリーム一覧, 字幕ストリーム一覧, 全ストリーム一覧).
    English: Return value: A 4-tuple of (audio stream list, video stream list, subtitle stream list, full stream list).
    """
    # 从info字典中获取'streams'列表, 如果info为None或不存在该键则返回空列表
    # 日本語: info が None でない場合は 'streams' を取得し、そうでなければ空リストにします.
    # English: Retrieve the 'streams' list from info if present; otherwise use an empty list.
    streams = info.get('streams', []) if info else []
    # 筛选出所有codec_type为'audio'的流, 即音频轨道
    # 日本語: codec_type が 'audio' のものを抽出し、音声トラックとして扱います.
    # English: Filter out streams whose codec_type is 'audio' and treat them as audio tracks.
    audios = [s for s in streams if s.get('codec_type')=='audio']
    # 筛选出所有codec_type为'video'的流, 即视频轨道
    # 日本語: codec_type が 'video' のものを抽出し、映像トラックとして扱います.
    # English: Filter out streams whose codec_type is 'video' and treat them as video tracks.
    videos = [s for s in streams if s.get('codec_type')=='video']
    # 筛选出所有codec_type为'subtitle'的流, 即字幕轨道
    # 日本語: codec_type が 'subtitle' のものを抽出し、字幕トラックとして扱います.
    # English: Filter out streams whose codec_type is 'subtitle' and treat them as subtitle tracks.
    subs = [s for s in streams if s.get('codec_type')=='subtitle']
    # 返回分类后的四个列表
    # 日本語: 分類済みの 4 つの一覧を返します.
    # English: Return the four categorized lists.
    return audios, videos, subs, streams

def sanitize(name):
    """
    清理字符串, 使其适合用作文件名的一部分.
    日本語: 文字列を整え、ファイル名に使える形に変換します.
    English: Clean a string so it can be safely used as part of a filename.
    只保留字母、数字和'-', '_', '.'字符, 并去除首尾的分隔符.
    日本語: 英数字と '-', '_', '.' だけを残し、前後の区切り文字を取り除きます.
    English: Keep only letters, numbers, and the characters '-', '_', and '.', then remove leading and trailing separators.
    参数 name: 待清理的原始字符串.
    日本語: name: 整理前の文字列.
    English: name: The raw string to sanitize.
    返回值: 清理后的字符串 ; 如果输入为空或清理后为空则返回None.
    日本語: 戻り値: 整理後の文字列.空または空文字だった場合は None を返します.
    English: Return value: The sanitized string; returns None if the input is empty or becomes empty after cleaning.
    """
    # 如果输入为空值(None或空字符串), 直接返回None
    # 日本語: 入力が None や空文字なら、そのまま None を返します.
    # English: If the input is None or an empty string, return None immediately.
    if not name: return None
    # 遍历每个字符, 只保留字母数字和'-'、'_'、'.'字符
    # 日本語: 各文字を順に見て、英数字と指定記号だけを残します.
    # English: Iterate through each character and keep only alphanumeric characters and the allowed separators.
    out = ''.join(c for c in name if c.isalnum() or c in ('-','_','.')).strip('._-')
    # 如果清理后字符串不为空则返回, 否则返回None
    # 日本語: 整理後に文字が残っていれば返し、なければ None を返します.
    # English: Return the cleaned string if it is not empty; otherwise return None.
    return out or None

def audio_pref_ext_from_codec(codec):
    """
    根据音频编解码器名称获取推荐的文件扩展名.
    日本語: 音声コーデック名に応じて、出力に適した拡張子を返します.
    English: Return a recommended file extension based on the audio codec name.
    参数 codec: 编解码器名称字符串(如'flac'、'aac'等).
    日本語: codec: 音声コーデック名(例: 'flac', 'aac').
    English: codec: The codec name string, such as 'flac' or 'aac'.
    返回值: 对应的文件扩展名(如'.flac'、'.m4a') ; 未知编码返回None.
    日本語: 戻り値: 対応する拡張子(例: '.flac', '.m4a').未登録のコーデックは None を返します.
    English: Return value: The matching extension, such as '.flac' or '.m4a'; returns None for unknown codecs.
    """
    # 如果编码名称为空, 返回None
    # 日本語: codec が空文字なら None を返します.
    # English: If the codec name is empty, return None.
    if not codec: return None
    # 将编码名称转为小写后, 在AUDIO_CODEC_TO_EXT字典中查找对应的扩展名
    # 日本語: コーデック名を小文字に変換し、対応表から拡張子を検索します.
    # English: Convert the codec name to lowercase and look up the extension in AUDIO_CODEC_TO_EXT.
    return AUDIO_CODEC_TO_EXT.get(codec.lower())

def subtitle_ext_for_codec(codec):
    """
    根据字幕编解码器名称获取对应的文件扩展名.
    日本語: 字幕コーデック名に応じて、適切な拡張子を返します.
    English: Return the appropriate extension for a subtitle codec name.
    参数 codec: 字幕编解码器名称字符串.
    日本語: codec: 字幕コーデック名の文字列.
    English: codec: The subtitle codec name string.
    返回值: 对应的文件扩展名(如'.srt') ; 未知编码返回默认值'.subtitle'.
    日本語: 戻り値: 対応する拡張子(例: '.srt').未登録のコーデックは既定値 '.subtitle' を返します.
    English: Return value: The matching extension, such as '.srt'; returns the default '.subtitle' for unknown codecs.
    """
    # 如果编码名称为空, 返回默认扩展名'.subtitle'
    # 日本語: codec が空なら、既定の '.subtitle' を返します.
    # English: If the codec name is empty, return the default '.subtitle'.
    if not codec: return '.subtitle'
    # 在SUB_CODEC_TO_EXT字典中查找, 找不到时返回默认值'.subtitle'
    # 日本語: 対応表から検索し、見つからなければ '.subtitle' を返します.
    # English: Look up the extension in SUB_CODEC_TO_EXT; if not found, return '.subtitle'.
    return SUB_CODEC_TO_EXT.get(codec.lower(), '.subtitle')

def unique_path(path):
    """
    生成唯一的文件路径, 避免覆盖已有文件.
    日本語: 既存ファイルと衝突しないように、重複しない出力パスを生成します.
    English: Create a unique file path that avoids overwriting existing files.
    如果目标路径已存在, 则在文件名末尾追加递增数字后缀直到找到可用路径.
    日本語: 目標パスがすでに存在する場合は、末尾に連番を付けて利用可能なものを探します.
    English: If the target path already exists, append an incrementing numeric suffix until a free path is found.
    参数 path: 期望的文件完整路径.
    日本語: path: 作成したい出力ファイルの完全なパス.
    English: path: The full path that is intended for the output file.
    返回值: 确保不冲突的唯一文件路径.
    日本語: 戻り値: 衝突しないように調整された一意なファイルパス.
    English: Return value: A unique file path that will not collide with existing files.
    """
    # 将路径拆分为不含扩展名的基础部分和扩展名部分
    # 日本語: パスを拡張子なしの基本部分と拡張子部分に分けます.
    # English: Split the path into the base name and the file extension.
    base, ext = os.path.splitext(path)
    # 初始化数字后缀计数器从1开始
    # 日本語: 連番の初期値を 1 に設定します.
    # English: Initialize the numeric suffix counter at 1.
    i = 1
    # 初始尝试使用原始路径
    # 日本語: 最初は元のパスを試します.
    # English: Start by trying the original path.
    out = path
    # 循环检测 : 如果当前路径已存在文件, 则追加数字后缀
    # 日本語: そのパスが既に存在する間、連番付きの名前へ変更し続けます.
    # English: Keep checking whether the current path exists and append a numeric suffix if it does.
    while os.path.exists(out):
        # 格式化为"基础路径.数字.扩展名"的形式
        # 日本語: 基本名.番号.拡張子 の形式で新しいパスを作ります.
        # English: Format the new path as base_name.number.extension.
        out = "{}.{}{}".format(base, i, ext)
        # 计数器递增
        # 日本語: 番号を 1 つ増やします.
        # English: Increment the counter.
        i += 1
    # 返回找到的第一个不存在的路径
    # 日本語: まだ存在しない最初のパスを返します.
    # English: Return the first path that does not exist yet.
    return out

def build_audio_name(input_path, a_stream, ext):
    """
    为导出的音频文件构建输出文件路径.
    日本語: 抽出した音声ファイルの出力パスを、元ファイル名やトラック情報をもとに組み立てます.
    English: Build the output path for an exported audio file based on the source filename and stream information.
    文件名格式: 源文件名.audio.流索引.编码名[.语言][.标题].扩展名
    日本語: 命名形式は、元ファイル名.audio.ストリーム番号.コーデック名[.言語][.タイトル].拡張子 です.
    English: The filename format is source_name.audio.stream_index.codec_name[.language][.title].extension.
    参数 input_path: 源媒体文件路径.
    日本語: input_path: 元のメディアファイルのパス.
    English: input_path: The path of the source media file.
    参数 a_stream: 音频流的详细信息字典(来自ffprobe).
    日本語: a_stream: ffprobe から得た音声ストリームの詳細情報辞書.
    English: a_stream: The detailed audio stream dictionary from ffprobe.
    参数 ext: 输出文件的扩展名(如'.flac').
    日本語: ext: 出力ファイルの拡張子(例: '.flac').
    English: ext: The output file extension, such as '.flac'.
    返回值: 唯一的输出文件完整路径.
    日本語: 戻り値: 重複しないように調整された出力ファイルの完全パス.
    English: Return value: The full output path with uniqueness guaranteed.
    """
    # 提取源文件的基本名称(不含扩展名)
    # 日本語: 元ファイル名から拡張子を除いた基本名を取り出します.
    # English: Extract the source filename without its extension.
    base = os.path.splitext(os.path.basename(input_path))[0]
    # 获取音频编码名称, 如果不存在则默认为'audio'
    # 日本語: 音声コーデック名を取得し、なければ 'audio' を使います.
    # English: Get the audio codec name, or use 'audio' if missing.
    codec = a_stream.get('codec_name') or 'audio'
    # 获取该音频流在源文件中的索引号
    # 日本語: この音声ストリームの元ファイル内でのインデックスを取得します.
    # English: Get the stream index of this audio stream in the source file.
    idx = a_stream.get('index')
    # 获取流的标签信息字典(包含语言、标题等元数据), 不存在则为空字典
    # 日本語: 言語やタイトルなどのタグ情報を取得し、存在しなければ空辞書にします.
    # English: Get the stream tags dictionary, including language and title metadata; use an empty dict if absent.
    tags = a_stream.get('tags') or {}
    # 尝试从标签中获取语言代码(兼容大小写两种键名)
    # 日本語: language / LANGUAGE のいずれかから言語コードを取得しようとします.
    # English: Try to read the language code from either 'language' or 'LANGUAGE'.
    lang = tags.get('language') or tags.get('LANGUAGE') or ''
    # 尝试从标签中获取标题信息
    # 日本語: title タグからタイトル情報を取得しようとします.
    # English: Try to read title information from the 'title' tag.
    title = tags.get('title') or ''
    # 构建文件名的各个组成部分列表 : 源文件名、'audio'标识、流索引、编码名称
    # 日本語: 元ファイル名・'audio'・ストリーム番号・コーデック名を並べた要素を作ります.
    # English: Build the filename parts from the source name, 'audio', stream index, and codec name.
    parts = [base, 'audio', str(idx), sanitize(codec) or 'audio']
    # 如果有语言标签, 追加经过清理的语言代码到文件名组成部分中
    # 日本語: 言語タグがあれば、整形した言語コードを追加します.
    # English: If there is a language tag, append the sanitized language code to the name parts.
    if lang: parts.append(sanitize(lang))
    # 如果有标题标签, 追加经过清理的标题到文件名组成部分中
    # 日本語: タイトルタグがあれば、整形したタイトルを追加します.
    # English: If there is a title tag, append the sanitized title to the name parts.
    if title: parts.append(sanitize(title))
    # 用点号将所有非空部分连接为完整的文件名(不含扩展名)
    # 日本語: 空でない要素だけを '.' でつなげて、拡張子なしのファイル名を作ります.
    # English: Join all non-empty parts with dots to form the base filename without the extension.
    name = '.'.join([p for p in parts if p])
    # 拼接脚本目录、文件名和扩展名, 得到完整的输出路径
    # 日本語: スクリプト置き場のディレクトリと結合して、完全な出力パスを作ります.
    # English: Join the script directory with the name and extension to create the full output path.
    out = os.path.join(SCRIPT_DIR, name + ext)
    # 调用unique_path确保输出路径不与已有文件冲突
    # 日本語: unique_path を呼び出して、既存ファイルと重ならないようにします.
    # English: Call unique_path to ensure the output path does not collide with existing files.
    return unique_path(out)

def build_sub_name(input_path, s_stream):
    """
    为导出的字幕文件构建输出文件路径.
    日本語: 抽出した字幕ファイルの出力パスを、元ファイル名や字幕情報をもとに組み立てます.
    English: Build the output path for an exported subtitle file based on the source filename and subtitle stream information.
    文件名格式: 源文件名.sub.流索引.编码名[.语言][.标题].扩展名
    日本語: 命名形式は、元ファイル名.sub.ストリーム番号.コーデック名[.言語][.タイトル].拡張子 です.
    English: The filename format is source_name.sub.stream_index.codec_name[.language][.title].extension.
    参数 input_path: 源媒体文件路径.
    日本語: input_path: 元のメディアファイルのパス.
    English: input_path: The path of the source media file.
    参数 s_stream: 字幕流的详细信息字典(来自ffprobe).
    日本語: s_stream: ffprobe から得た字幕ストリームの詳細情報辞書.
    English: s_stream: The detailed subtitle stream dictionary from ffprobe.
    返回值: 唯一的输出文件完整路径.
    日本語: 戻り値: 重複しないように調整された出力ファイルの完全パス.
    English: Return value: The full output path with uniqueness guaranteed.
    """
    # 提取源文件的基本名称(不含扩展名)
    # 日本語: 元ファイル名から拡張子を除いた基本名を取り出します.
    # English: Extract the source filename without its extension.
    base = os.path.splitext(os.path.basename(input_path))[0]
    # 获取字幕编码名称, 如果不存在则默认为'subtitle'
    # 日本語: 字幕コーデック名を取得し、なければ 'subtitle' を使います.
    # English: Get the subtitle codec name, or use 'subtitle' if missing.
    codec = s_stream.get('codec_name') or 'subtitle'
    # 获取该字幕流在源文件中的索引号
    # 日本語: この字幕ストリームの元ファイル内でのインデックスを取得します.
    # English: Get the stream index of this subtitle stream in the source file.
    idx = s_stream.get('index')
    # 获取流的标签信息字典
    # 日本語: 言語やタイトルなどのタグ情報を取得します.
    # English: Get the stream tags dictionary, including metadata such as language and title.
    tags = s_stream.get('tags') or {}
    # 尝试从标签中获取语言代码
    # 日本語: language / LANGUAGE から言語コードを取得しようとします.
    # English: Try to read the language code from either 'language' or 'LANGUAGE'.
    lang = tags.get('language') or tags.get('LANGUAGE') or ''
    # 尝试从标签中获取标题信息
    # 日本語: title タグからタイトル情報を取得しようとします.
    # English: Try to read title information from the 'title' tag.
    title = tags.get('title') or ''
    # 构建文件名的各个组成部分列表
    # 日本語: 元ファイル名・'sub'・ストリーム番号・コーデック名を並べた要素を作ります.
    # English: Build the filename parts from the source name, 'sub', stream index, and codec name.
    parts = [base, 'sub', str(idx), sanitize(codec) or 'sub']
    # 如果有语言标签则追加
    # 日本語: 言語タグがあれば、整形した言語コードを追加します.
    # English: If there is a language tag, append the sanitized language code.
    if lang: parts.append(sanitize(lang))
    # 如果有标题标签则追加
    # 日本語: タイトルタグがあれば、整形したタイトルを追加します.
    # English: If there is a title tag, append the sanitized title.
    if title: parts.append(sanitize(title))
    # 用点号连接所有非空部分
    # 日本語: 空でない要素だけを '.' でつなげて、拡張子なしのファイル名を作ります.
    # English: Join all non-empty parts with dots to form the base filename without the extension.
    name = '.'.join([p for p in parts if p])
    # 根据字幕编码类型确定文件扩展名
    # 日本語: 字幕コーデックに応じて適切な拡張子を決めます.
    # English: Determine the file extension according to the subtitle codec type.
    ext = subtitle_ext_for_codec(s_stream.get('codec_name'))
    # 拼接脚本目录、文件名和扩展名
    # 日本語: スクリプト置き場のディレクトリと結合して、完全な出力パスを作ります.
    # English: Join the script directory with the name and extension to create the full output path.
    out = os.path.join(SCRIPT_DIR, name + ext)
    # 确保输出路径唯一
    # 日本語: unique_path を使って、既存ファイルと重ならないようにします.
    # English: Use unique_path to ensure the output path does not collide with existing files.
    return unique_path(out)

def run_ffmpeg(cmd):
    """
    执行 ffmpeg 命令并实时输出其运行日志.
    日本語: ffmpeg を実行し、そのログをリアルタイムで表示します.
    English: Execute an ffmpeg command and display its log output in real time.
    参数 cmd: ffmpeg命令行参数列表.
    日本語: cmd: ffmpeg に渡す引数のリスト.
    English: cmd: The ffmpeg command-line argument list.
    返回值: ffmpeg进程的退出码(0表示成功, 非0表示失败).
    日本語: 戻り値: ffmpeg プロセスの終了コード(0 は成功、0 以外は失敗).
    English: Return value: The ffmpeg process exit code (0 for success, non-zero for failure).
    """
    # 打印即将执行的完整命令行, 方便调试和追踪
    # 日本語: 実行するコマンド全体を表示し、デバッグしやすくします.
    # English: Print the full command to be executed for easier debugging and tracking.
    print('运行:', ' '.join(cmd))
    # 以Popen方式启动ffmpeg进程, 捕获标准输出和标准错误, universal_newlines=True使输出为字符串
    # 日本語: Popen で ffmpeg を起動し、標準出力と標準エラーを取得します.universal_newlines=True により文字列として扱います.
    # English: Start ffmpeg via Popen, capturing stdout and stderr; universal_newlines=True makes them text streams.
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    try:
        # 逐行读取ffmpeg的标准错误输出(ffmpeg将日志信息输出到stderr)
        # 日本語: ffmpeg の標準エラー出力を1行ずつ読み取り、表示します.
        # English: Read ffmpeg's stderr output line by line and print it.
        for line in p.stderr:
            # 去除行尾换行符后打印到控制台
            # 日本語: 末尾の改行を取り除いてコンソールに表示します.
            # English: Remove the trailing newline and print the line to the console.
            print(line.rstrip())
        # 等待ffmpeg进程执行完毕
        # 日本語: ffmpeg の終了を待ちます.
        # English: Wait until the ffmpeg process finishes.
        p.wait()
    except KeyboardInterrupt:
        # 如果用户按下Ctrl+C中断, 强制杀死ffmpeg子进程
        # 日本語: Ctrl+C で中断された場合、ffmpeg を強制終了します.
        # English: If interrupted with Ctrl+C, force-kill the ffmpeg subprocess.
        p.kill()
        # 重新抛出KeyboardInterrupt异常, 让上层处理
        # 日本語: KeyboardInterrupt を再送出し、呼び出し元で処理できるようにします.
        # English: Re-raise the KeyboardInterrupt so the caller can handle it.
        raise
    # 返回ffmpeg进程的退出码
    # 日本語: ffmpeg の終了コードを返します.
    # English: Return the ffmpeg process exit code.
    return p.returncode

def try_mux(input_path, audio_idx, sub_indices, out_path):
    """
    尝试将指定的音频轨和所有字幕轨封装(mux)到一个输出容器中.
    日本語: 指定した音声トラックと字幕トラックを、1つの出力コンテナにまとめて封入しようとします.
    English: Try to mux the selected audio track and all subtitle tracks into a single output container.
    使用 stream copy 模式, 不进行重新编码.
    日本語: stream copy モードを使い、再エンコードなしで処理します.
    English: Use stream copy mode so no re-encoding is performed.
    参数 input_path: 源媒体文件路径.
    日本語: input_path: 元のメディアファイルのパス.
    English: input_path: The path of the source media file.
    参数 audio_idx: 要提取的音频流索引号.
    日本語: audio_idx: 抽出対象の音声ストリーム番号.
    English: audio_idx: The index of the audio stream to extract.
    参数 sub_indices: 要封装的字幕流索引号列表.
    日本語: sub_indices: 封入対象の字幕ストリーム番号の一覧.
    English: sub_indices: The list of subtitle stream indices to mux.
    参数 out_path: 输出文件的完整路径.
    日本語: out_path: 出力ファイルの完全パス.
    English: out_path: The full path of the output file.
    返回值: ffmpeg进程的退出码.
    日本語: 戻り値: ffmpeg プロセスの終了コード.
    English: Return value: The ffmpeg process exit code.
    """
    # 构建ffmpeg基础命令 : 隐藏版本信息、自动覆盖输出文件、指定输入文件
    # 日本語: ffmpeg の基本コマンドを組み立てます.バナーを隠し、出力を上書きし、入力ファイルを指定します.
    # English: Build the base ffmpeg command, hiding the banner, overwriting output files, and specifying the input file.
    cmd = ['ffmpeg','-hide_banner','-y','-i',input_path]
    # 添加-map参数, 选择指定索引的音频流
    # 日本語: -map を追加して、指定した音声ストリームだけを選びます.
    # English: Add -map to select the specified audio stream.
    cmd += ['-map','0:{}'.format(audio_idx)]
    # 遍历所有字幕流索引, 为每条字幕添加-map参数
    # 日本語: すべての字幕ストリーム番号について、-map を追加します.
    # English: For each subtitle stream index, add a -map entry.
    for si in sub_indices:
        cmd += ['-map','0:{}'.format(si)]
    # 添加-c copy参数(流复制模式, 不重编码)和输出文件路径
    # 日本語: -c copy を指定してストリームコピーで出力し、保存先を追加します.
    # English: Add -c copy to perform stream copy without re-encoding and specify the output path.
    cmd += ['-c','copy', out_path]
    # 调用run_ffmpeg执行命令并返回退出码
    # 日本語: run_ffmpeg を呼び出して実行し、終了コードを返します.
    # English: Call run_ffmpeg to execute the command and return its exit code.
    return run_ffmpeg(cmd)

def extract_stream(input_path, stream_idx, out_path):
    """
    从源文件中提取单条媒体流并保存到独立文件.
    日本語: 元ファイルから単一のメディアストリームだけを抽出し、独立したファイルとして保存します.
    English: Extract a single media stream from the source file and save it as a standalone file.
    使用 stream copy 模式, 不进行重新编码.
    日本語: stream copy モードを使い、再エンコードなしで処理します.
    English: Use stream copy mode so no re-encoding is performed.
    参数 input_path: 源媒体文件路径.
    日本語: input_path: 元のメディアファイルのパス.
    English: input_path: The path of the source media file.
    参数 stream_idx: 要提取的流索引号.
    日本語: stream_idx: 抽出するストリームの番号.
    English: stream_idx: The index of the stream to extract.
    参数 out_path: 输出文件的完整路径.
    日本語: out_path: 出力ファイルの完全パス.
    English: out_path: The full path of the output file.
    返回值: ffmpeg进程的退出码.
    日本語: 戻り値: ffmpeg プロセスの終了コード.
    English: Return value: The ffmpeg process exit code.
    """
    # 构建ffmpeg命令 : 隐藏版本信息、自动覆盖、指定输入、选择单条流、流复制模式、指定输出
    # 日本語: ffmpeg コマンドを組み立てます.バナーを隠し、出力に上書き、入力ファイルを指定し、単一ストリームをコピーして出力します.
    # English: Build the ffmpeg command to hide the banner, overwrite output, specify the input, select a single stream, copy it, and write the output.
    cmd = ['ffmpeg','-hide_banner','-y','-i',input_path,'-map','0:{}'.format(stream_idx),'-c','copy', out_path]
    # 执行命令并返回退出码
    # 日本語: コマンドを実行し、終了コードを返します.
    # English: Execute the command and return its exit code.
    return run_ffmpeg(cmd)

def build_candidates(input_ext, audio_codec, has_subs):
    """
    根据源文件扩展名、音频编码类型和是否包含字幕, 构建候选输出容器格式的有序列表.
    日本語: 元ファイルの拡張子・音声コーデック・字幕の有無に応じて、試行順を持つ出力コンテナ候補を作ります.
    English: Build an ordered list of candidate output container formats based on the source extension, audio codec, and whether subtitles are present.
    优先级策略 : 原始容器 > 编码推荐容器 > 通用音频容器.
    日本語: 優先順位は、元のコンテナ > コーデック推奨形式 > 汎用音声形式です.
    English: The priority order is original container, codec-recommended container, then general audio container.
    如果包含字幕, 则只保留支持字幕封装的容器格式.
    日本語: 字幕が含まれる場合は、字幕を埋め込めるコンテナ形式だけを候補に残します.
    English: If subtitles are present, only container formats that support subtitle muxing are kept.
    参数 input_ext: 源文件的扩展名(如'.mkv').
    日本語: input_ext: 元ファイルの拡張子(例: '.mkv').
    English: input_ext: The source file extension, such as '.mkv'.
    参数 audio_codec: 音频编解码器名称.
    日本語: audio_codec: 音声コーデック名.
    English: audio_codec: The audio codec name.
    参数 has_subs: 布尔值, 源文件是否包含字幕流.
    日本語: has_subs: 元ファイルに字幕ストリームが含まれるかどうかの真偽値.
    English: has_subs: Boolean indicating whether the source file contains subtitle streams.
    返回值: 去重后的候选扩展名列表(按优先级排序).
    日本語: 戻り値: 重複を除いた候補拡張子の一覧(優先順位順).
    English: Return value: A deduplicated list of candidate extensions in priority order.
    """
    # 将输入扩展名转为小写 ; 如果为None则设为空字符串
    # 日本語: 拡張子を小文字にして、None なら空文字にします.
    # English: Normalize the input extension to lowercase; use an empty string if it is None.
    input_ext = (input_ext or '').lower()
    # 确保扩展名以点号开头
    # 日本語: 拡張子が '.' で始まるように整えます.
    # English: Ensure the extension starts with a dot.
    if input_ext and not input_ext.startswith('.'):
        input_ext = '.' + input_ext
    # 初始化候选列表
    # 日本語: 候補を格納するリストを初期化します.
    # English: Initialize the list of candidates.
    candidates = []
    # 如果源文件扩展名属于已知格式, 将其作为最高优先级候选加入列表
    # 日本語: 元ファイルの拡張子が既知の形式なら、最優先候補として追加します.
    # English: If the source extension is a known format, add it as the highest-priority candidate.
    if input_ext and input_ext.lstrip('.') in KNOWN_FORMATS:
        candidates.append(input_ext)
    # 根据音频编码获取推荐的文件扩展名
    # 日本語: 音声コーデックに応じた推奨拡張子を取得します.
    # English: Get the recommended extension from the audio codec.
    pref = audio_pref_ext_from_codec(audio_codec)
    # 如果推荐扩展名存在且不在候选列表中, 追加到列表(第二优先级)
    # 日本語: 推奨拡張子があり、まだ候補に無ければ第二候補として追加します.
    # English: If a recommended extension exists and is not already in the list, append it as the second priority.
    if pref and pref not in candidates:
        candidates.append(pref)
    # 追加通用音频格式作为后备候选(按常见度排序)
    # 日本語: 汎用的な音声形式を後続候補として追加します.順序は一般的なものから並べます.
    # English: Append general-purpose audio formats as fallback candidates in a common order.
    for add in ['.flac', '.m4a', '.mp3', '.wav', '.ogg', '.mka']:
        if add not in candidates:
            candidates.append(add)
    # 如果源文件包含字幕流, 需要筛选出支持字幕的容器格式
    # 日本語: 元ファイルに字幕が含まれる場合、字幕を含められるコンテナだけを残します.
    # English: If the source contains subtitles, retain only container formats that can carry subtitles.
    if has_subs:
        # 从候选列表中筛选出支持字幕封装的格式
        # 日本語: 候補の中から、字幕対応のコンテナだけを抽出します.
        # English: Filter the candidates down to those that support subtitle muxing.
        filtered = [c for c in candidates if c in SUBTITLE_CAPABLE]
        # 追加所有已知的字幕兼容容器作为额外后备
        # 日本語: 字幕対応のコンテナを追加し、候補が足りない場合の保険としても使います.
        # English: Add well-known subtitle-capable containers as extra fallback options.
        for add in ['.mkv', '.mka', '.mp4', '.mov', '.webm']:
            if add not in filtered:
                filtered.append(add)
        # 使用集合去重并保持顺序
        # 日本語: 重複を除き、順序を保ったまま返します.
        # English: Deduplicate while preserving order.
        seen = set(); out = []
        for e in filtered:
            if e not in seen:
                seen.add(e); out.append(e)
        # 返回去重后的字幕兼容容器候选列表
        # 日本語: その結果を字幕対応の候補リストとして返します.
        # English: Return the deduplicated subtitle-capable candidate list.
        return out
    # 无字幕时的去重处理
    # 日本語: 字幕がない場合は、候補をそのまま重複除去して返します.
    # English: If there are no subtitles, deduplicate the candidate list and return it.
    seen = set(); out = []
    for e in candidates:
        if e not in seen:
            seen.add(e); out.append(e)
    # 返回去重后的候选容器列表
    # 日本語: 重複除去済みの候補一覧を返します.
    # English: Return the deduplicated candidate container list.
    return out

def process_file(path):
    """
    处理单个媒体文件 : 探测流信息, 逐条提取音频轨, 智能处理字幕.
    日本語: 1つのメディアファイルについて、ストリーム情報を調べ、音声トラックを1つずつ抽出し、字幕も適切に処理します.
    English: Process a single media file by probing its streams, extracting each audio track one by one, and handling subtitles intelligently.
    参数 path: 待处理的媒体文件完整路径.
    日本語: path: 処理対象のメディアファイルの完全パス.
    English: path: The full path of the media file to process.
    返回值: 成功创建的所有输出文件路径列表.
    日本語: 戻り値: 正常に作成された出力ファイルパスの一覧.
    English: Return value: A list of all output file paths that were successfully created.
    """
    # 调用ffprobe探测文件, 获取流信息的JSON字典
    # 日本語: ffprobe でファイルを調査し、JSON 形式のストリーム情報を取得します.
    # English: Probe the file with ffprobe and obtain its stream information as a JSON dictionary.
    info = ffprobe_json(path)
    # 如果探测失败(info为None), 返回空列表跳过该文件
    # 日本語: 取得に失敗した場合は空リストを返して、このファイルをスキップします.
    # English: If probing fails and info is None, return an empty list and skip this file.
    if info is None:
        return []
    # 将流信息分类为音频、视频、字幕和全部流
    # 日本語: 取得したストリーム情報を、音声・映像・字幕・全体の4種類に分類します.
    # English: Classify the streams into audio, video, subtitle, and all-stream categories.
    audios, videos, subs, streams = classify_streams(info)
    # 如果文件中没有任何音频流, 打印跳过信息并返回空列表
    # 日本語: 音声ストリームがなければ、スキップメッセージを表示して終了します.
    # English: If the file has no audio streams, print a skip message and return an empty list.
    if not audios:
        print('跳过(无音频):', os.path.basename(path))
        return []
    # 打印当前处理文件的基本信息 : 文件名、音频轨数量、视频轨数量、字幕轨数量
    # 日本語: 現在処理中のファイル名と、音声・映像・字幕の各トラック数を表示します.
    # English: Print the current file name and the number of audio, video, and subtitle tracks.
    print('处理文件:', os.path.basename(path), 'audio_count:', len(audios), 'video:', len(videos), 'subtitle:', len(subs))
    # 获取源文件的扩展名并转为小写
    # 日本語: 元ファイルの拡張子を小文字で取得します.
    # English: Get the source file extension in lowercase.
    input_ext = os.path.splitext(path)[1].lower()
    # 提取所有字幕流的索引号列表
    # 日本語: 字幕ストリームのインデックス番号一覧を作ります.
    # English: Build a list of subtitle stream indices.
    sub_indices = [s.get('index') for s in subs]
    # 初始化已成功创建的文件路径列表
    # 日本語: 正常に作成された出力ファイルのパスを格納するリストを初期化します.
    # English: Initialize the list that will store successfully created output file paths.
    created = []
    # 遍历每一条音频流进行处理
    # 日本語: 各音声トラックについて順に処理を行います.
    # English: Process each audio stream one by one.
    for a in audios:
        # 获取当前音频流的索引号
        # 日本語: 現在の音声ストリームの番号を取得します.
        # English: Get the index of the current audio stream.
        a_idx = a.get('index')
        # 获取当前音频流的编码名称, 不存在则为空字符串
        # 日本語: 音声コーデック名を取得し、ない場合は空文字にします.
        # English: Get the current audio codec name, or use an empty string if missing.
        codec = a.get('codec_name') or ''
        # 根据源文件扩展名、音频编码和是否有字幕, 构建候选输出容器列表
        # 日本語: 元ファイルの拡張子・音声コーデック・字幕の有無から、候補コンテナ一覧を作ります.
        # English: Build the list of candidate output containers from the source extension, audio codec, and subtitle presence.
        candidates = build_candidates(input_ext, codec, bool(subs))
        # 打印当前音轨的处理信息 : 索引号、编码名称、候选容器列表
        # 日本語: 現在処理中の音声トラック番号・コーデック・候補コンテナを表示します.
        # English: Print the current audio track index, codec, and candidate container list.
        print(' 音轨 index={} codec={} 候选容器: {}'.format(a_idx, codec, ','.join(candidates)))
        # 标记变量 : 记录是否已成功将字幕封装进输出文件
        # 日本語: 字幕を出力に同梱できたかどうかを記録するフラグです.
        # English: A flag indicating whether subtitles were successfully muxed into the output.
        muxed = False
        # 如果源文件包含字幕流, 先尝试将音频和字幕一起封装
        # 日本語: 元ファイルに字幕がある場合、まず音声と字幕を同時に封入しようとします.
        # English: If the source contains subtitles, first try to mux the audio and subtitles together.
        if subs:
            # 遍历所有候选容器格式
            # 日本語: 候補の各コンテナ形式について順に試します.
            # English: Try each candidate container format in order.
            for ext in candidates:
                # 跳过不支持字幕封装的容器格式
                # 日本語: 字幕を埋め込めないコンテナはスキップします.
                # English: Skip container formats that do not support embedded subtitles.
                if ext not in SUBTITLE_CAPABLE:
                    continue
                # 为当前音频流和容器格式构建输出文件路径
                # 日本語: 現在の音声トラックとコンテナ形式に合わせて出力パスを作ります.
                # English: Build an output path for the current audio track and container format.
                out_audio = build_audio_name(path, a, ext)
                # 打印尝试封装的信息
                # 日本語: そのコンテナで字幕を同梱して出力しようとしていることを表示します.
                # English: Print the message that the script is attempting to mux subtitles into that container and export the file.
                print('  尝试用 {} 封装字幕并导出 -> {}'.format(ext, os.path.basename(out_audio)))
                # 调用try_mux尝试将音频和所有字幕封装到输出文件中
                # 日本語: try_mux を呼び出して、音声とすべての字幕を同梱します.
                # English: Call try_mux to mux the audio and all subtitles into the output file.
                rc = try_mux(path, a_idx, sub_indices, out_audio)
                # 如果封装成功(退出码为0)
                # 日本語: 成功した場合は、終了コード 0 です.
                # English: If muxing succeeds, the exit code is 0.
                if rc == 0:
                    # 打印成功信息
                    # 日本語: 成功したことを表示します.
                    # English: Print a success message.
                    print('  封装成功:', os.path.basename(out_audio))
                    # 将输出路径添加到已创建文件列表中
                    # 日本語: 作成済みの出力パスを記録します.
                    # English: Append the output path to the list of created files.
                    created.append(out_audio)
                    # 标记为已成功封装
                    # 日本語: 同梱成功フラグを立てます.
                    # English: Mark the operation as successfully muxed.
                    muxed = True
                    # 跳出容器遍历循环, 不再尝试其他容器
                    # 日本語: これ以上別のコンテナを試さず、ループを抜けます.
                    # English: Break out of the container loop and stop trying other formats.
                    break
                else:
                    # 封装失败, 打印失败信息和退出码, 继续尝试下一个容器
                    # 日本語: 封入に失敗したので、終了コードとともにメッセージを表示し次の候補に進みます.
                    # English: If muxing fails, print the failure and exit code and continue to the next candidate container.
                    print('  容器 {} 封装失败, rc={}'.format(ext, rc))
        # 如果未能成功封装(没有字幕或所有字幕兼容容器都失败了)
        # 日本語: 同梱に失敗した場合、字幕がないか、または字幕対応コンテナの試行が全て失敗したことになります.
        # English: If muxing did not succeed, either there were no subtitles or all subtitle-capable container attempts failed.
        if not muxed:
            # 选择候选列表中的第一个格式作为首选, 如果列表为空则默认使用'.mka'
            # 日本語: 最初の候補を優先形式として採用し、候補が空なら '.mka' を使います.
            # English: Use the first candidate as the preferred format, or '.mka' if the list is empty.
            pref = candidates[0] if candidates else '.mka'
            # 构建使用首选容器格式的输出文件路径
            # 日本語: 優先形式で出力ファイルのパスを作ります.
            # English: Build the output path using the preferred container format.
            out_audio = build_audio_name(path, a, pref)
            # 打印导出信息
            # 日本語: 音声トラックだけを出力しようとしていることを表示します.
            # English: Print the message that the audio track is being exported.
            print('  导出音轨到:', os.path.basename(out_audio))
            # 调用extract_stream仅提取音频流(不含字幕)到输出文件
            # 日本語: extract_stream を呼び出して、字幕を含めずに音声だけを抽出します.
            # English: Call extract_stream to extract only the audio stream, without subtitles.
            rc = extract_stream(path, a_idx, out_audio)
            # 如果提取成功
            # 日本語: 抽出に成功した場合です.
            # English: If the extraction succeeds.
            if rc == 0:
                # 打印成功信息并将路径添加到已创建列表
                # 日本語: 成功を表示し、作成済みパスに追加します.
                # English: Print a success message and add the path to the created list.
                print('  导出成功:', os.path.basename(out_audio))
                created.append(out_audio)
            else:
                # 首选容器提取失败, 打印失败信息
                # 日本語: 優先形式での抽出に失敗したので、メッセージを表示します.
                # English: If export with the preferred container fails, print a failure message.
                print('  导出失败, rc={}'.format(rc))
                # 遍历剩余的候选容器格式作为备选方案
                # 日本語: 残りの候補形式を順に試します.
                # English: Try the remaining candidate container formats as fallbacks.
                for ext in candidates[1:]:
                    # 为备选容器构建输出路径
                    # 日本語: 代替コンテナ用の出力パスを作ります.
                    # English: Build an output path for the fallback container.
                    out_audio = build_audio_name(path, a, ext)
                    # 打印尝试备选容器的信息
                    # 日本語: 代替コンテナで再試行する旨を表示します.
                    # English: Print that the script is trying the fallback container.
                    print('   尝试备选容器:', os.path.basename(out_audio))
                    # 使用备选容器再次尝试提取音频流
                    # 日本語: 代替コンテナで再度音声抽出を試します.
                    # English: Try extracting the audio stream again using the fallback container.
                    rc2 = extract_stream(path, a_idx, out_audio)
                    # 如果备选容器提取成功
                    # 日本語: 代替形式でも成功した場合です.
                    # English: If the fallback export succeeds.
                    if rc2 == 0:
                        # 打印成功信息, 添加到已创建列表, 跳出备选循环
                        # 日本語: 成功を表示し、作成済みパスに追加してループを抜けます.
                        # English: Print success, add the path to the created list, and break out of the fallback loop.
                        print('   导出成功:', os.path.basename(out_audio))
                        created.append(out_audio)
                        break
                    else:
                        # 备选容器也失败, 打印失败信息, 继续尝试下一个
                        # 日本語: 代替形式でも失敗したので、次の候補に進みます.
                        # English: If the fallback also fails, print the failure and continue to the next candidate.
                        print('   失败, rc={}'.format(rc2))
        # 如果源文件有字幕且未能成功封装(即字幕没有随音频一起导出), 则单独提取每条字幕
        # 日本語: 元ファイルに字幕があり、同梱に失敗した場合、字幕は個別に抽出します.
        # English: If the source file has subtitles and muxing failed, extract each subtitle track separately.
        if subs and not muxed:
            # 遍历每条字幕流
            # 日本語: 各字幕ストリームについて順に処理します.
            # English: Iterate over each subtitle stream.
            for s in subs:
                # 为当前字幕流构建输出文件路径
                # 日本語: 現在の字幕ストリーム用の出力パスを作ります.
                # English: Build an output path for the current subtitle stream.
                out_sub = build_sub_name(path, s)
                # 打印字幕提取信息
                # 日本語: その字幕を抽出しようとしていることを表示します.
                # English: Print the message that the subtitle stream is being extracted.
                print('  提取字幕 index={} 到 {}'.format(s.get('index'), os.path.basename(out_sub)))
                # 调用extract_stream提取字幕流到独立文件
                # 日本語: extract_stream を呼び出して字幕だけを抽出します.
                # English: Call extract_stream to extract only the subtitle stream into a separate file.
                rc3 = extract_stream(path, s.get('index'), out_sub)
                # 如果字幕提取成功
                # 日本語: 抽出に成功した場合です.
                # English: If subtitle extraction succeeds.
                if rc3 == 0:
                    print('   字幕提取成功:', os.path.basename(out_sub))
                else:
                    # 字幕提取失败, 打印失败信息和退出码
                    # 日本語: 抽出に失敗した場合は、終了コードとともに表示します.
                    # English: If extraction fails, print the failure message and exit code.
                    print('   字幕提取失败, rc={}'.format(rc3))
    # 返回本次处理中所有成功创建的文件路径列表
    # 日本語: このファイル処理で作成された出力ファイルパスの一覧を返します.
    # English: Return the list of output file paths created during this processing run.
    return created

def main():
    """
    主函数 : 脚本的入口点.
    日本語: スクリプトのエントリーポイントで、全体の流れを制御します.
    English: Main function: the script entry point that controls the overall flow.
    检查工具依赖, 扫描目录中的所有文件并逐一处理, 最后汇总输出结果.
    日本語: 実行に必要なツールを確認し、ディレクトリ内のファイルを走査して順に処理し、最後に結果をまとめます.
    English: It checks tool dependencies, scans all files in the directory, processes them one by one, and finally summarizes the results.
    """
    # 首先检查ffmpeg和ffprobe是否可用, 不可用则直接退出
    # 日本語: 最初に ffmpeg と ffprobe が使えるか確認し、使えなければ終了します.
    # English: First check whether ffmpeg and ffprobe are available; if not, exit immediately.
    check_tools()
    # 列出脚本所在目录下的所有文件(不含子目录)
    # 日本語: スクリプトが置かれたディレクトリ内のファイルを、サブディレクトリを除いて取得します.
    # English: List files in the script's directory, excluding subdirectories.
    files = [f for f in os.listdir(SCRIPT_DIR) if os.path.isfile(os.path.join(SCRIPT_DIR,f))]
    # 从文件列表中排除脚本自身, 避免处理自己
    # 日本語: スクリプト自身を対象から外して、自己処理を避けます.
    # English: Exclude the script itself from the file list to avoid processing it.
    files = [f for f in files if f != os.path.basename(__file__)]
    # 如果目录下没有其他文件, 提示用户并按回车等待退出
    # 日本語: 他に処理対象のファイルがない場合、メッセージを表示して Enter を待ちます.
    # English: If there are no other files in the directory, print a message and wait for Enter before exiting.
    if not files:
        print('当前目录无文件.')
        input('按回车退出...')
        return
    # 初始化汇总列表, 用于收集所有成功创建的输出文件路径
    # 日本語: 生成された出力ファイルのパスをまとめて格納するリストを初期化します.
    # English: Initialize the summary list that collects the paths of all successfully created output files.
    all_created = []
    # 遍历目录中的每个文件进行处理
    # 日本語: ディレクトリ内の各ファイルを順に処理します.
    # English: Process each file in the directory one by one.
    for fn in files:
        # 拼接文件的完整路径
        # 日本語: ファイル名から完全なパスを作ります.
        # English: Build the full path from the filename.
        path = os.path.join(SCRIPT_DIR, fn)
        try:
            # 调用process_file处理单个文件, 返回创建的文件列表(可能为空)
            # 日本語: process_file を呼び出して 1 ファイルを処理し、作成されたファイル一覧を取得します.
            # English: Call process_file for the current file and retrieve the list of created files, which may be empty.
            created = process_file(path) or []
            # 将本次创建的文件路径追加到汇总列表
            # 日本語: この処理で作成されたパスをまとめて追加します.
            # English: Append the newly created file paths to the summary list.
            all_created.extend(created)
        except UnicodeDecodeError as e:
            # 捕获文件读取时的Unicode 解码异常(如 GBK 编码不兼容等)记录警告信息后跳过当前文件, 继续处理后续文件.
            # ファイル読み込み時のUnicodeデコード例外(GBK等のエンコーディング非互換含む)を捕捉し、警告を出力した上で当該ファイルをスキップし、後続の処理を継続する.
            # Catch Unicode decode errors(e.g. GBK incompatibility)during file reads; warn and skip, then proceed with remaining files.
            print('\033[33m请忽略这个异常,\033[0m 处理 {} 时出现编码解析异常, 这并不影响FFmpeg的封装.'.format(fn))
        except Exception as e:
            # 如果处理过程中发生未预期的异常, 捕获并打印错误信息, 继续处理下一个文件
            # 日本語: 予期しない例外が起きても、その内容を表示して次のファイルへ進みます.
            # English: If an unexpected exception occurs during processing, print the error and continue with the next file.
            print('处理 {} 时\033[91m异常:\033[0m {}'.format(fn, e))
    # 所有文件处理完毕后, 打印分隔线和汇总标题
    # 日本語: 全ての処理が終わったら、区切り線と結果の要約を表示します.
    # English: After all files are processed, print a separator and the summary heading.
    print('\n全部处理完成.生成文件:')
    # 遍历所有成功创建的文件, 打印其文件名
    # 日本語: 作成されたファイルの名前を 1 つずつ表示します.
    # English: Print the name of each successfully created file.
    for p in all_created:
        print('  ', os.path.basename(p))
    # 如果没有任何文件被成功创建, 打印提示信息
    # 日本語: いずれのファイルも生成されなかった場合は、その旨を表示します.
    # English: If no files were created, print a message indicating that.
    if not all_created:
        print('  (未生成任何文件)')
    # 打印脚本的工作策略说明
    # 日本語: このスクリプトの処理方針を簡潔に表示します.
    # English: Print the script's operational strategy summary.
    print('\n说明: 严格使用 -c copy(无重编码).优先保留原容器 ; 若音轨为 FLAC 则优先 .flac ; 包含字幕时优先使用字幕兼容容器 (.mkv/.mka/.mp4/.mov/.webm), 失败时回退为导出音频并单独提取字幕(最佳努力).')
    # 等待用户按回车键后退出程序
    # 日本語: Enter キーを押すまで待ち、終了します.
    # English: Wait for the user to press Enter before exiting.
    input('\n按回车退出...')

# Python标准入口点判断 : 只有直接运行本脚本时才执行main()
# 日本語: Python の標準的な実行入口判定で、直接実行されたときだけ main() を呼び出します.
# English: Use the standard Python entry-point check so main() runs only when the script is executed directly.
# 被其他模块import时不会自动执行
# 日本語: 他のモジュールから import された場合は自動実行されません.
# English: It will not run automatically when the file is imported as a module by another script.
if __name__ == '__main__':
    main()
