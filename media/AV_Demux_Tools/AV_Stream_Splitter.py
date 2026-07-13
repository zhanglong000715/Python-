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

============================================================================

"""


# 导入操作系统相关模块, 用于文件和路径操作
import os
# 导入系统相关模块, 用于退出程序和访问命令行参数
import sys
# 导入JSON模块, 用于解析FFprobe输出的JSON格式数据
import json
# 导入shutil模块, 用于检测系统命令是否可用(which功能)
import shutil
# 导入subprocess模块, 用于调用外部程序(ffmpeg/ffprobe)
import subprocess

# 获取当前脚本文件所在的绝对目录路径, 所有输入输出文件都基于此目录
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

# 定义已知媒体文件格式的集合(包含视频、音频、纯音频、裸流、字幕等格式)
# 用于判断一个文件的扩展名是否属于本脚本可处理的媒体格式

KNOWN_FORMATS = {
    # 常见视频容器格式
    'mp4','mkv','avi','mov','flv','wmv','mpg','mpeg','mts','m2ts','ts','vob','rm','rmvb','asf',
    
    # 移动端及其他视频格式
    '3gp','3g2','divx','f4v','ogv','dv',
    
    # Web媒体格式
    'webm','ogg','ogx','m4v',
    
    # 常见音频格式
    'mp3','wav','aac','m4a','flac','oga','opus','wma','ac3','dts','eac3','mka','aiff','aif',
    
    # 无损/有损压缩音频及有声书等格式
    'm4b','ape','tta','mp2','amr','mpc','wv','spx','ra','ram','caf',
    
    # 裸视频编码流格式
    'h264','h265','hevc','avc','vp9','ivf',
    
    # 常见字幕文件格式
    'srt','ass','ssa','sub','idx','vtt','ttml','dfxp','smi','sami','mpl','pjs','stl','sup','pgs','sbv','lrc','rt','txt'
}

# 音频编解码器名称到推荐输出文件扩展名的映射字典
# 当从容器中提取音轨时, 根据编码类型决定保存为什么格式的文件

AUDIO_CODEC_TO_EXT = {
    'flac': '.flac',                                          # FLAC无损音频 -> .flac文件
    'mp3': '.mp3',                                            # MP3有损音频 -> .mp3文件
    'aac': '.m4a',                                            # AAC音频 -> .m4a文件
    'adts': '.m4a',                                           # ADTS格式的AAC音频 -> .m4a文件
    'aac_latm': '.m4a',                                       # LATM传输格式的AAC音频 -> .m4a文件
    'opus': '.ogg',                                           # Opus音频 -> .ogg文件
    'vorbis': '.ogg',                                          # Vorbis音频 -> .ogg文件
    'pcm_s16le': '.wav', 'pcm_s24le': '.wav',                 # PCM 16位/24位有符号小端 -> .wav文件
    'pcm_u8': '.wav', 'pcm_s16be': '.wav',                    # PCM 8位无符号/16位大端 -> .wav文件
    'alac': '.m4a',                                           # Apple无损音频 -> .m4a文件
    'ac3': '.ac3', 'eac3': '.eac3', 'dts': '.dts',           # AC3/EAC3/DTS环绕声音频 -> 对应扩展名
    'wavpack': '.wv', 'tta': '.tta', 'ape': '.ape',          # WavPack/TTA/APE无损音频 -> 对应扩展名
    'mp2': '.mp2', 'amr': '.amr', 'wma': '.wma'              # MP2/AMR/WMA音频 -> 对应扩展名
}

# 字幕编解码器名称到推荐输出文件扩展名的映射字典
# 当从容器中提取字幕流时, 根据编码类型决定保存为什么格式的文件

SUB_CODEC_TO_EXT = {
    'subrip': '.srt', 'srt': '.srt',                          # SubRip字幕 -> .srt文件
    'ass': '.ass', 'ssa': '.ass',                             # ASS/SSA高级字幕 -> .ass文件
    'webvtt': '.vtt', 'vtt': '.vtt',                          # WebVTT网页字幕 -> .vtt文件
    'hdmv_pgs_subtitle': '.sup', 'pgs': '.sup',               # 蓝光PGS图形字幕 -> .sup文件
    'dvd_subtitle': '.sub',                                    # DVD VobSub字幕 -> .sub文件
    'mov_text': '.txt',                                        # QuickTime/MOV文本字幕 -> .txt文件
    'xsub': '.sub'                                             # XSUB字幕(DivX) -> .sub文件
}

# 定义支持内嵌字幕流的容器格式集合
# 当源文件包含字幕时, 优先尝试将音频和字幕一起封装到这些容器中

SUBTITLE_CAPABLE = {'.mkv', '.mka', '.mp4', '.mov', '.webm', '.ogg'}

# ======================== 工具函数定义 ========================

def check_tools():
    """
    检查系统是否已安装 ffmpeg 和 ffprobe 命令行工具.
    如果任一工具不可用, 则打印提示信息并退出程序.
    """
    # 使用shutil.which检测ffmpeg命令是否在系统PATH中可用
    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        # 如果ffmpeg或ffprobe未找到, 打印错误提示信息
        print('需要系统已安装 ffmpeg 和 ffprobe 并在 PATH 中.')
        # 以退出码1终止程序, 表示异常退出
        sys.exit(1)

def ffprobe_json(path):
    """
    调用 ffprobe 探测指定媒体文件, 获取所有流的详细信息并以字典形式返回.
    参数 path: 待探测的媒体文件的完整路径.
    返回值: 解析后的JSON字典, 包含streams等信息 ; 探测失败时返回None.
    """
    # 构建ffprobe命令行参数列表 : 
    # -v error: 只输出错误级别的日志(减少干扰信息)
    # -print_format json: 以JSON格式输出结果
    # -show_streams: 显示所有媒体流的详细信息
    cmd = ['ffprobe','-v','error','-print_format','json','-show_streams',path]
    try:
        # 执行ffprobe命令, 捕获标准输出和标准错误输出, check=True表示非零退出码时抛出异常
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # 将标准输出从字节流解码为UTF-8字符串(忽略无法解码的字符), 然后解析为JSON字典并返回
        return json.loads(p.stdout.decode('utf-8', errors='ignore'))
    except subprocess.CalledProcessError as e:
        # 如果ffprobe执行失败(返回非零退出码), 捕获异常并打印错误信息
        print('ffprobe 错误 for {}:'.format(os.path.basename(path)), e.stderr.decode('utf-8', errors='ignore'))
        # 返回None表示探测失败
        return None

def classify_streams(info):
    """
    将 ffprobe 返回的流信息按类型分类为音频流、视频流和字幕流.
    参数 info: ffprobe_json() 返回的字典.
    返回值: 四元组 (音频流列表, 视频流列表, 字幕流列表, 全部流列表).
    """
    # 从info字典中获取'streams'列表, 如果info为None或不存在该键则返回空列表
    streams = info.get('streams', []) if info else []
    # 筛选出所有codec_type为'audio'的流, 即音频轨道
    audios = [s for s in streams if s.get('codec_type')=='audio']
    # 筛选出所有codec_type为'video'的流, 即视频轨道
    videos = [s for s in streams if s.get('codec_type')=='video']
    # 筛选出所有codec_type为'subtitle'的流, 即字幕轨道
    subs = [s for s in streams if s.get('codec_type')=='subtitle']
    # 返回分类后的四个列表
    return audios, videos, subs, streams

def sanitize(name):
    """
    清理字符串, 使其适合用作文件名的一部分.
    只保留字母、数字和'-', '_', '.'字符, 并去除首尾的分隔符.
    参数 name: 待清理的原始字符串.
    返回值: 清理后的字符串 ; 如果输入为空或清理后为空则返回None.
    """
    # 如果输入为空值(None或空字符串), 直接返回None
    if not name: return None
    # 遍历每个字符, 只保留字母数字和'-'、'_'、'.'字符
    out = ''.join(c for c in name if c.isalnum() or c in ('-','_','.')).strip('._-')
    # 如果清理后字符串不为空则返回, 否则返回None
    return out or None

def audio_pref_ext_from_codec(codec):
    """
    根据音频编解码器名称获取推荐的文件扩展名.
    参数 codec: 编解码器名称字符串(如'flac'、'aac'等).
    返回值: 对应的文件扩展名(如'.flac'、'.m4a') ; 未知编码返回None.
    """
    # 如果编码名称为空, 返回None
    if not codec: return None
    # 将编码名称转为小写后, 在AUDIO_CODEC_TO_EXT字典中查找对应的扩展名
    return AUDIO_CODEC_TO_EXT.get(codec.lower())

def subtitle_ext_for_codec(codec):
    """
    根据字幕编解码器名称获取对应的文件扩展名.
    参数 codec: 字幕编解码器名称字符串.
    返回值: 对应的文件扩展名(如'.srt') ; 未知编码返回默认值'.subtitle'.
    """
    # 如果编码名称为空, 返回默认扩展名'.subtitle'
    if not codec: return '.subtitle'
    # 在SUB_CODEC_TO_EXT字典中查找, 找不到时返回默认值'.subtitle'
    return SUB_CODEC_TO_EXT.get(codec.lower(), '.subtitle')

def unique_path(path):
    """
    生成唯一的文件路径, 避免覆盖已有文件.
    如果目标路径已存在, 则在文件名末尾追加递增数字后缀直到找到可用路径.
    参数 path: 期望的文件完整路径.
    返回值: 确保不冲突的唯一文件路径.
    """
    # 将路径拆分为不含扩展名的基础部分和扩展名部分
    base, ext = os.path.splitext(path)
    # 初始化数字后缀计数器从1开始
    i = 1
    # 初始尝试使用原始路径
    out = path
    # 循环检测 : 如果当前路径已存在文件, 则追加数字后缀
    while os.path.exists(out):
        # 格式化为"基础路径.数字.扩展名"的形式
        out = "{}.{}{}".format(base, i, ext)
        # 计数器递增
        i += 1
    # 返回找到的第一个不存在的路径
    return out

def build_audio_name(input_path, a_stream, ext):
    """
    为导出的音频文件构建输出文件路径.
    文件名格式: 源文件名.audio.流索引.编码名[.语言][.标题].扩展名
    参数 input_path: 源媒体文件路径.
    参数 a_stream: 音频流的详细信息字典(来自ffprobe).
    参数 ext: 输出文件的扩展名(如'.flac').
    返回值: 唯一的输出文件完整路径.
    """
    # 提取源文件的基本名称(不含扩展名)
    base = os.path.splitext(os.path.basename(input_path))[0]
    # 获取音频编码名称, 如果不存在则默认为'audio'
    codec = a_stream.get('codec_name') or 'audio'
    # 获取该音频流在源文件中的索引号
    idx = a_stream.get('index')
    # 获取流的标签信息字典(包含语言、标题等元数据), 不存在则为空字典
    tags = a_stream.get('tags') or {}
    # 尝试从标签中获取语言代码(兼容大小写两种键名)
    lang = tags.get('language') or tags.get('LANGUAGE') or ''
    # 尝试从标签中获取标题信息
    title = tags.get('title') or ''
    # 构建文件名的各个组成部分列表 : 源文件名、'audio'标识、流索引、编码名称
    parts = [base, 'audio', str(idx), sanitize(codec) or 'audio']
    # 如果有语言标签, 追加经过清理的语言代码到文件名组成部分中
    if lang: parts.append(sanitize(lang))
    # 如果有标题标签, 追加经过清理的标题到文件名组成部分中
    if title: parts.append(sanitize(title))
    # 用点号将所有非空部分连接为完整的文件名(不含扩展名)
    name = '.'.join([p for p in parts if p])
    # 拼接脚本目录、文件名和扩展名, 得到完整的输出路径
    out = os.path.join(SCRIPT_DIR, name + ext)
    # 调用unique_path确保输出路径不与已有文件冲突
    return unique_path(out)

def build_sub_name(input_path, s_stream):
    """
    为导出的字幕文件构建输出文件路径.
    文件名格式: 源文件名.sub.流索引.编码名[.语言][.标题].扩展名
    参数 input_path: 源媒体文件路径.
    参数 s_stream: 字幕流的详细信息字典(来自ffprobe).
    返回值: 唯一的输出文件完整路径.
    """
    # 提取源文件的基本名称(不含扩展名)
    base = os.path.splitext(os.path.basename(input_path))[0]
    # 获取字幕编码名称, 如果不存在则默认为'subtitle'
    codec = s_stream.get('codec_name') or 'subtitle'
    # 获取该字幕流在源文件中的索引号
    idx = s_stream.get('index')
    # 获取流的标签信息字典
    tags = s_stream.get('tags') or {}
    # 尝试从标签中获取语言代码
    lang = tags.get('language') or tags.get('LANGUAGE') or ''
    # 尝试从标签中获取标题信息
    title = tags.get('title') or ''
    # 构建文件名的各个组成部分列表
    parts = [base, 'sub', str(idx), sanitize(codec) or 'sub']
    # 如果有语言标签则追加
    if lang: parts.append(sanitize(lang))
    # 如果有标题标签则追加
    if title: parts.append(sanitize(title))
    # 用点号连接所有非空部分
    name = '.'.join([p for p in parts if p])
    # 根据字幕编码类型确定文件扩展名
    ext = subtitle_ext_for_codec(s_stream.get('codec_name'))
    # 拼接脚本目录、文件名和扩展名
    out = os.path.join(SCRIPT_DIR, name + ext)
    # 确保输出路径唯一
    return unique_path(out)

def run_ffmpeg(cmd):
    """
    执行 ffmpeg 命令并实时输出其运行日志.
    参数 cmd: ffmpeg命令行参数列表.
    返回值: ffmpeg进程的退出码(0表示成功, 非0表示失败).
    """
    # 打印即将执行的完整命令行, 方便调试和追踪
    print('运行:', ' '.join(cmd))
    # 以Popen方式启动ffmpeg进程, 捕获标准输出和标准错误, universal_newlines=True使输出为字符串
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    try:
        # 逐行读取ffmpeg的标准错误输出(ffmpeg将日志信息输出到stderr)
        for line in p.stderr:
            # 去除行尾换行符后打印到控制台
            print(line.rstrip())
        # 等待ffmpeg进程执行完毕
        p.wait()
    except KeyboardInterrupt:
        # 如果用户按下Ctrl+C中断, 强制杀死ffmpeg子进程
        p.kill()
        # 重新抛出KeyboardInterrupt异常, 让上层处理
        raise
    # 返回ffmpeg进程的退出码
    return p.returncode

def try_mux(input_path, audio_idx, sub_indices, out_path):
    """
    尝试将指定的音频轨和所有字幕轨封装(mux)到一个输出容器中.
    使用 stream copy 模式, 不进行重新编码.
    参数 input_path: 源媒体文件路径.
    参数 audio_idx: 要提取的音频流索引号.
    参数 sub_indices: 要封装的字幕流索引号列表.
    参数 out_path: 输出文件的完整路径.
    返回值: ffmpeg进程的退出码.
    """
    # 构建ffmpeg基础命令 : 隐藏版本信息、自动覆盖输出文件、指定输入文件
    cmd = ['ffmpeg','-hide_banner','-y','-i',input_path]
    # 添加-map参数, 选择指定索引的音频流
    cmd += ['-map','0:{}'.format(audio_idx)]
    # 遍历所有字幕流索引, 为每条字幕添加-map参数
    for si in sub_indices:
        cmd += ['-map','0:{}'.format(si)]
    # 添加-c copy参数(流复制模式, 不重编码)和输出文件路径
    cmd += ['-c','copy', out_path]
    # 调用run_ffmpeg执行命令并返回退出码
    return run_ffmpeg(cmd)

def extract_stream(input_path, stream_idx, out_path):
    """
    从源文件中提取单条媒体流并保存到独立文件.
    使用 stream copy 模式, 不进行重新编码.
    参数 input_path: 源媒体文件路径.
    参数 stream_idx: 要提取的流索引号.
    参数 out_path: 输出文件的完整路径.
    返回值: ffmpeg进程的退出码.
    """
    # 构建ffmpeg命令 : 隐藏版本信息、自动覆盖、指定输入、选择单条流、流复制模式、指定输出
    cmd = ['ffmpeg','-hide_banner','-y','-i',input_path,'-map','0:{}'.format(stream_idx),'-c','copy', out_path]
    # 执行命令并返回退出码
    return run_ffmpeg(cmd)

def build_candidates(input_ext, audio_codec, has_subs):
    """
    根据源文件扩展名、音频编码类型和是否包含字幕, 构建候选输出容器格式的有序列表.
    优先级策略 : 原始容器 > 编码推荐容器 > 通用音频容器.
    如果包含字幕, 则只保留支持字幕封装的容器格式.
    参数 input_ext: 源文件的扩展名(如'.mkv').
    参数 audio_codec: 音频编解码器名称.
    参数 has_subs: 布尔值, 源文件是否包含字幕流.
    返回值: 去重后的候选扩展名列表(按优先级排序).
    """
    # 将输入扩展名转为小写 ; 如果为None则设为空字符串
    input_ext = (input_ext or '').lower()
    # 确保扩展名以点号开头
    if input_ext and not input_ext.startswith('.'):
        input_ext = '.' + input_ext
    # 初始化候选列表
    candidates = []
    # 如果源文件扩展名属于已知格式, 将其作为最高优先级候选加入列表
    if input_ext and input_ext.lstrip('.') in KNOWN_FORMATS:
        candidates.append(input_ext)
    # 根据音频编码获取推荐的文件扩展名
    pref = audio_pref_ext_from_codec(audio_codec)
    # 如果推荐扩展名存在且不在候选列表中, 追加到列表(第二优先级)
    if pref and pref not in candidates:
        candidates.append(pref)
    # 追加通用音频格式作为后备候选(按常见度排序)
    for add in ['.flac', '.m4a', '.mp3', '.wav', '.ogg', '.mka']:
        if add not in candidates:
            candidates.append(add)
    # 如果源文件包含字幕流, 需要筛选出支持字幕的容器格式
    if has_subs:
        # 从候选列表中筛选出支持字幕封装的格式
        filtered = [c for c in candidates if c in SUBTITLE_CAPABLE]
        # 追加所有已知的字幕兼容容器作为额外后备
        for add in ['.mkv', '.mka', '.mp4', '.mov', '.webm']:
            if add not in filtered:
                filtered.append(add)
        # 使用集合去重并保持顺序
        seen = set(); out = []
        for e in filtered:
            if e not in seen:
                seen.add(e); out.append(e)
        # 返回去重后的字幕兼容容器候选列表
        return out
    # 无字幕时的去重处理
    seen = set(); out = []
    for e in candidates:
        if e not in seen:
            seen.add(e); out.append(e)
    # 返回去重后的候选容器列表
    return out

def process_file(path):
    """
    处理单个媒体文件 : 探测流信息, 逐条提取音频轨, 智能处理字幕.
    参数 path: 待处理的媒体文件完整路径.
    返回值: 成功创建的所有输出文件路径列表.
    """
    # 调用ffprobe探测文件, 获取流信息的JSON字典
    info = ffprobe_json(path)
    # 如果探测失败(info为None), 返回空列表跳过该文件
    if info is None:
        return []
    # 将流信息分类为音频、视频、字幕和全部流
    audios, videos, subs, streams = classify_streams(info)
    # 如果文件中没有任何音频流, 打印跳过信息并返回空列表
    if not audios:
        print('跳过(无音频):', os.path.basename(path))
        return []
    # 打印当前处理文件的基本信息 : 文件名、音频轨数量、视频轨数量、字幕轨数量
    print('处理文件:', os.path.basename(path), 'audio_count:', len(audios), 'video:', len(videos), 'subtitle:', len(subs))
    # 获取源文件的扩展名并转为小写
    input_ext = os.path.splitext(path)[1].lower()
    # 提取所有字幕流的索引号列表
    sub_indices = [s.get('index') for s in subs]
    # 初始化已成功创建的文件路径列表
    created = []
    # 遍历每一条音频流进行处理
    for a in audios:
        # 获取当前音频流的索引号
        a_idx = a.get('index')
        # 获取当前音频流的编码名称, 不存在则为空字符串
        codec = a.get('codec_name') or ''
        # 根据源文件扩展名、音频编码和是否有字幕, 构建候选输出容器列表
        candidates = build_candidates(input_ext, codec, bool(subs))
        # 打印当前音轨的处理信息 : 索引号、编码名称、候选容器列表
        print(' 音轨 index={} codec={} 候选容器: {}'.format(a_idx, codec, ','.join(candidates)))
        # 标记变量 : 记录是否已成功将字幕封装进输出文件
        muxed = False
        # 如果源文件包含字幕流, 先尝试将音频和字幕一起封装
        if subs:
            # 遍历所有候选容器格式
            for ext in candidates:
                # 跳过不支持字幕封装的容器格式
                if ext not in SUBTITLE_CAPABLE:
                    continue
                # 为当前音频流和容器格式构建输出文件路径
                out_audio = build_audio_name(path, a, ext)
                # 打印尝试封装的信息
                print('  尝试用 {} 封装字幕并导出 -> {}'.format(ext, os.path.basename(out_audio)))
                # 调用try_mux尝试将音频和所有字幕封装到输出文件中
                rc = try_mux(path, a_idx, sub_indices, out_audio)
                # 如果封装成功(退出码为0)
                if rc == 0:
                    # 打印成功信息
                    print('  封装成功:', os.path.basename(out_audio))
                    # 将输出路径添加到已创建文件列表中
                    created.append(out_audio)
                    # 标记为已成功封装
                    muxed = True
                    # 跳出容器遍历循环, 不再尝试其他容器
                    break
                else:
                    # 封装失败, 打印失败信息和退出码, 继续尝试下一个容器
                    print('  容器 {} 封装失败, rc={}'.format(ext, rc))
        # 如果未能成功封装(没有字幕或所有字幕兼容容器都失败了)
        if not muxed:
            # 选择候选列表中的第一个格式作为首选, 如果列表为空则默认使用'.mka'
            pref = candidates[0] if candidates else '.mka'
            # 构建使用首选容器格式的输出文件路径
            out_audio = build_audio_name(path, a, pref)
            # 打印导出信息
            print('  导出音轨到:', os.path.basename(out_audio))
            # 调用extract_stream仅提取音频流(不含字幕)到输出文件
            rc = extract_stream(path, a_idx, out_audio)
            # 如果提取成功
            if rc == 0:
                # 打印成功信息并将路径添加到已创建列表
                print('  导出成功:', os.path.basename(out_audio))
                created.append(out_audio)
            else:
                # 首选容器提取失败, 打印失败信息
                print('  导出失败, rc={}'.format(rc))
                # 遍历剩余的候选容器格式作为备选方案
                for ext in candidates[1:]:
                    # 为备选容器构建输出路径
                    out_audio = build_audio_name(path, a, ext)
                    # 打印尝试备选容器的信息
                    print('   尝试备选容器:', os.path.basename(out_audio))
                    # 使用备选容器再次尝试提取音频流
                    rc2 = extract_stream(path, a_idx, out_audio)
                    # 如果备选容器提取成功
                    if rc2 == 0:
                        # 打印成功信息, 添加到已创建列表, 跳出备选循环
                        print('   导出成功:', os.path.basename(out_audio))
                        created.append(out_audio)
                        break
                    else:
                        # 备选容器也失败, 打印失败信息, 继续尝试下一个
                        print('   失败, rc={}'.format(rc2))
        # 如果源文件有字幕且未能成功封装(即字幕没有随音频一起导出), 则单独提取每条字幕
        if subs and not muxed:
            # 遍历每条字幕流
            for s in subs:
                # 为当前字幕流构建输出文件路径
                out_sub = build_sub_name(path, s)
                # 打印字幕提取信息
                print('  提取字幕 index={} 到 {}'.format(s.get('index'), os.path.basename(out_sub)))
                # 调用extract_stream提取字幕流到独立文件
                rc3 = extract_stream(path, s.get('index'), out_sub)
                # 如果字幕提取成功
                if rc3 == 0:
                    print('   字幕提取成功:', os.path.basename(out_sub))
                else:
                    # 字幕提取失败, 打印失败信息和退出码
                    print('   字幕提取失败, rc={}'.format(rc3))
    # 返回本次处理中所有成功创建的文件路径列表
    return created

def main():
    """
    主函数 : 脚本的入口点.
    检查工具依赖, 扫描目录中的所有文件并逐一处理, 最后汇总输出结果.
    """
    # 首先检查ffmpeg和ffprobe是否可用, 不可用则直接退出
    check_tools()
    # 列出脚本所在目录下的所有文件(不含子目录)
    files = [f for f in os.listdir(SCRIPT_DIR) if os.path.isfile(os.path.join(SCRIPT_DIR,f))]
    # 从文件列表中排除脚本自身, 避免处理自己
    files = [f for f in files if f != os.path.basename(__file__)]
    # 如果目录下没有其他文件, 提示用户并按回车等待退出
    if not files:
        print('当前目录无文件.')
        input('按回车退出...')
        return
    # 初始化汇总列表, 用于收集所有成功创建的输出文件路径
    all_created = []
    # 遍历目录中的每个文件进行处理
    for fn in files:
        # 拼接文件的完整路径
        path = os.path.join(SCRIPT_DIR, fn)
        try:
            # 调用process_file处理单个文件, 返回创建的文件列表(可能为空)
            created = process_file(path) or []
            # 将本次创建的文件路径追加到汇总列表
            all_created.extend(created)
        except UnicodeDecodeError as e:
            # 捕获文件读取时的Unicode 解码异常(如 GBK 编码不兼容等)记录警告信息后跳过当前文件, 继续处理后续文件.
            print('\033[33m请忽略这个异常,\033[0m 处理 {} 时出现编码解析异常, 这并不影响FFmpeg的封装.'.format(fn))
        except Exception as e:
            # 如果处理过程中发生未预期的异常, 捕获并打印错误信息, 继续处理下一个文件
            print('处理 {} 时\033[91m异常:\033[0m {}'.format(fn, e))
    # 所有文件处理完毕后, 打印分隔线和汇总标题
    print('\n全部处理完成.生成文件:')
    # 遍历所有成功创建的文件, 打印其文件名
    for p in all_created:
        print('  ', os.path.basename(p))
    # 如果没有任何文件被成功创建, 打印提示信息
    if not all_created:
        print('  (未生成任何文件)')
    # 打印脚本的工作策略说明
    print('\n说明: 严格使用 -c copy(无重编码).优先保留原容器 ; 若音轨为 FLAC 则优先 .flac ; 包含字幕时优先使用字幕兼容容器 (.mkv/.mka/.mp4/.mov/.webm), 失败时回退为导出音频并单独提取字幕(最佳努力).')
    # 等待用户按回车键后退出程序
    input('\n按回车退出...')

# Python标准入口点判断 : 只有直接运行本脚本时才执行main()
# 被其他模块import时不会自动执行
if __name__ == '__main__':
    main()
