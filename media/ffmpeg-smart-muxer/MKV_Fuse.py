#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
脚本名称: FFmpeg Media Merger v3 (基于流检测的重构版本)
作者署名: 张龙
================================================================================
脚本介绍:
本脚本是一个基于 Python 编写的高级 FFmpeg 媒体合并工具.
其核心创新点在于摒弃了传统仅依赖文件扩展名来判断媒体类型的做法, 转而通过调用 ffprobe 对文件内部的实际流（视频流、音频流、字幕流）进行深度检测与解析.
这使得工具能够精准识别诸如“包含纯音频的 .webm 文件”或“包含字幕流的 .mkv 文件”等复杂情况, 从而实现无损、高效的媒体封装.

主要功能包括 : 
1. 智能流检测 : 利用 ffprobe 获取真实的 codec_type, 确保分类准确无误.
2. 无损合并 : 采用 stream copy 模式, 将视频、多音轨、多字幕无损封装至 MKV 容器.
3. 降级容错机制 : 当字幕流直接 copy 失败时, 自动尝试重编码为 MKV 兼容格式.
4. 灵活的工作模式 : 支持交互式命令行选择、自动同名匹配合并以及命令行参数直接指定.
5. 跨平台兼容 : 自动在系统 PATH 及常见安装目录中查找 ffmpeg/ffprobe 可执行文件.
================================================================================
"""

# 导入操作系统接口模块, 用于环境变量和路径判断
import os
# 导入系统特定参数模块, 用于退出程序
import sys
# 导入子进程模块, 用于调用外部 ffmpeg 和 ffprobe 命令
import subprocess
# 导入 JSON 模块, 用于解析 ffprobe 返回的 JSON 数据
import json
# 导入 shutil 模块, 用于跨平台查找可执行文件
import shutil
# 导入 pathlib 模块, 用于面向对象的路径操作
from pathlib import Path
# 导入 typing 模块, 用于类型提示, 增强代码可读性
from typing import List, Dict, Optional, Tuple, Union

# ─────────────────────────────────────────────
# 扩展名白名单（仅用于初筛, 不作为最终分类依据）
# ─────────────────────────────────────────────
# 定义支持的媒体文件扩展名集合, 用于快速过滤非媒体文件
ALL_MEDIA_EXTENSIONS = {
    # 视频容器 / 纯视频格式
    'mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mpg', 'mpeg',
    'mts', 'm2ts', 'ts', 'vob', 'rm', 'rmvb', 'asf',
    '3gp', '3g2', 'divx', 'f4v', 'ogv', 'dv',
    # 既可能是视频也可能是音频的容器格式
    'webm', 'ogg', 'ogx', 'm4v',
    # 音频格式
    'mp3', 'wav', 'aac', 'm4a', 'flac', 'oga', 'opus',
    'wma', 'ac3', 'dts', 'eac3', 'mka', 'aiff', 'aif',
    'm4b', 'ape', 'tta', 'mp2', 'amr', 'mpc', 'wv',
    'spx', 'ra', 'ram', 'caf',
    # 原始视频流格式
    'h264', 'h265', 'hevc', 'avc', 'vp9', 'ivf',
    # 字幕格式
    'srt', 'ass', 'ssa', 'sub', 'idx', 'vtt',
    'ttml', 'dfxp', 'smi', 'sami', 'mpl', 'pjs',
    'stl', 'sup', 'pgs', 'sbv', 'lrc', 'rt', 'txt',
}

# 定义单个文件的流信息数据类
class StreamInfo:
    """单个文件的流信息"""
    # 使用 __slots__ 限制属性, 优化内存占用
    __slots__ = ('path', 'has_video', 'has_audio', 'has_subtitle',
                 'video_count', 'audio_count', 'subtitle_count', 'streams')
    
    # 初始化方法, 传入文件路径
    def __init__(self, path: Path):
        # 保存文件路径对象
        self.path = path
        # 标记是否包含视频流
        self.has_video = False
        # 标记是否包含音频流
        self.has_audio = False
        # 标记是否包含字幕流
        self.has_subtitle = False
        # 视频流数量
        self.video_count = 0
        # 音频流数量
        self.audio_count = 0
        # 字幕流数量
        self.subtitle_count = 0
        # 存储详细的流信息字典列表
        self.streams: List[dict] = []
        
    # 定义对象的字符串表示形式, 便于调试打印
    def __repr__(self):
        # 初始化标签列表
        tags = []
        # 如果有视频流, 添加视频数量标签
        if self.has_video:
            tags.append(f'V×{self.video_count}')
        # 如果有音频流, 添加音频数量标签
        if self.has_audio:
            tags.append(f'A×{self.audio_count}')
        # 如果有字幕流, 添加字幕数量标签
        if self.has_subtitle:
            tags.append(f'S×{self.subtitle_count}')
        # 返回格式化的字符串, 包含文件名和流标签
        return f"<{self.path.name} [{', '.join(tags)}]>"

# 定义 FFmpeg 媒体合并器主类
class FFmpegMediaMerger:
    """FFmpeg 媒体合并器 — 基于 ffprobe 流检测"""
    
    # 初始化方法, 可选传入工作目录
    def __init__(self, working_dir: Optional[str] = None):
        # 解析并保存工作目录的绝对路径, 默认为当前目录
        self.working_dir = Path(working_dir).resolve() if working_dir else Path.cwd()
        # 设置详细输出模式为 True
        self.verbose = True
        # 查找 ffmpeg 可执行文件路径
        self.ffmpeg_path = self._locate_binary('ffmpeg')
        # 查找 ffprobe 可执行文件路径
        self.ffprobe_path = self._locate_binary('ffprobe')
        # 如果找不到 ffmpeg, 抛出运行时错误并提示安装方法
        if not self.ffmpeg_path:
            raise RuntimeError(
                "未找到 ffmpeg, 请安装或将其加入 PATH.\n"
                "  Windows: https://www.gyan.dev/ffmpeg/builds/\n"
                "  macOS  : brew install ffmpeg\n"
                "  Linux  : sudo apt install ffmpeg"
            )
            
    # ────────────── 工具方法 ──────────────
    
    # 静态方法 : 在 PATH 和常见位置中查找可执行文件
    @staticmethod
    def _locate_binary(name: str) -> Optional[str]:
        """在 PATH 和常见位置中查找可执行文件"""
        # 1. 使用 shutil.which 跨平台查找
        found = shutil.which(name)
        # 如果找到了, 直接返回路径
        if found:
            return found
            
        # 2. 定义常见安装路径列表
        extras = []
        # 如果是 Windows 系统
        if os.name == 'nt':
            extras = [
                # Program Files 目录下的 ffmpeg
                Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'ffmpeg' / 'bin',
                # Program Files (x86) 目录下的 ffmpeg
                Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'ffmpeg' / 'bin',
                # WinGet 安装目录
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Links',
                # Scoop 安装目录
                Path.home() / 'scoop' / 'shims',
            ]
        # 如果是 macOS 或 Linux 系统
        else:
            extras = [
                # 常见的系统级二进制目录
                Path('/usr/local/bin'),
                Path('/usr/bin'),
                # macOS Homebrew (Apple Silicon) 目录
                Path('/opt/homebrew/bin'),
                # 用户级二进制目录
                Path.home() / '.local' / 'bin',
            ]
        # 根据操作系统确定可执行文件后缀名
        suffix = '.exe' if os.name == 'nt' else ''
        # 遍历所有常见路径
        for d in extras:
            # 拼接完整的候选文件路径
            candidate = d / f'{name}{suffix}'
            # 如果文件存在, 返回其字符串路径
            if candidate.exists():
                return str(candidate)
        # 如果都没找到, 返回 None
        return None
        
    # 实例方法 : 用 ffprobe 获取文件流信息
    def _run_ffprobe(self, file_path: Path) -> Optional[dict]:
        """用 ffprobe 获取文件流信息, 返回 JSON dict"""
        # 如果 ffprobe 路径不存在, 直接返回 None
        if not self.ffprobe_path:
            return None
        try:
            # 构建 ffprobe 命令参数列表
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',             # 静默模式, 不输出冗余信息
                '-print_format', 'json',   # 输出格式为 JSON
                '-show_streams',           # 显示流信息
                '-show_format',            # 显示容器格式信息
                str(file_path),            # 目标文件路径
            ]
            # 执行子进程命令
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,    # 捕获标准输出
                stderr=subprocess.PIPE,    # 捕获标准错误
                text=True,                 # 以文本模式返回
                timeout=30,                # 设置 30 秒超时
            )
            # 如果返回码为 0 且标准输出不为空
            if result.returncode == 0 and result.stdout.strip():
                # 解析 JSON 并返回字典
                return json.loads(result.stdout)
        except Exception:
            # 捕获所有异常, 忽略错误
            pass
        # 失败时返回 None
        return None
        
    # 实例方法 : 检测文件实际包含的流类型
    def probe_file(self, file_path: Path) -> StreamInfo:
        """
        检测文件实际包含的流类型.
        优先使用 ffprobe；若不可用则退回到扩展名猜测.
        """
        # 初始化 StreamInfo 对象
        info = StreamInfo(file_path)
        # 调用 ffprobe 获取探测结果
        probe = self._run_ffprobe(file_path)
        # 如果探测成功且包含 streams 字段
        if probe and 'streams' in probe:
            # 保存详细流信息
            info.streams = probe['streams']
            # 遍历每一个流
            for stream in probe['streams']:
                # 获取流的类型并转为小写
                codec_type = stream.get('codec_type', '').lower()
                # 如果是视频流, 视频计数加 1
                if codec_type == 'video':
                    info.video_count += 1
                # 如果是音频流, 音频计数加 1
                elif codec_type == 'audio':
                    info.audio_count += 1
                # 如果是字幕流, 字幕计数加 1
                elif codec_type == 'subtitle':
                    info.subtitle_count += 1
            # 根据计数更新布尔标记
            info.has_video = info.video_count > 0
            info.has_audio = info.audio_count > 0
            info.has_subtitle = info.subtitle_count > 0
            # 返回探测结果
            return info
            
        # ── ffprobe 不可用时的退路 : 按扩展名猜测 ──
        # 获取文件扩展名, 去除点号并转为小写
        ext = file_path.suffix.lstrip('.').lower()
        # 定义常见的视频扩展名集合
        video_exts = {
            'mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'mpg', 'mpeg',
            'mts', 'm2ts', 'ts', 'vob', 'rm', 'rmvb', 'asf',
            '3gp', '3g2', 'divx', 'f4v', 'ogv', 'dv', 'webm', 'm4v',
        }
        # 定义常见的音频扩展名集合
        audio_exts = {
            'mp3', 'wav', 'aac', 'm4a', 'flac', 'ogg', 'oga', 'opus',
            'wma', 'ac3', 'dts', 'eac3', 'mka', 'aiff', 'aif',
            'm4b', 'ape', 'tta', 'mp2', 'amr', 'mpc', 'wv',
            'spx', 'ra', 'ram', 'caf',
        }
        # 定义常见的字幕扩展名集合
        subtitle_exts = {
            'srt', 'ass', 'ssa', 'sub', 'idx', 'vtt',
            'ttml', 'dfxp', 'smi', 'sami', 'mpl', 'pjs',
            'stl', 'sup', 'pgs', 'sbv', 'lrc',
        }
        # 如果扩展名在视频集合中
        if ext in video_exts:
            # 标记包含视频
            info.has_video = True
            info.video_count = 1
            # 容器格式通常也含音频, 默认标记包含音频
            info.has_audio = True
            info.audio_count = 1
        # 如果扩展名在音频集合中
        elif ext in audio_exts:
            # 标记包含音频
            info.has_audio = True
            info.audio_count = 1
        # 如果扩展名在字幕集合中
        elif ext in subtitle_exts:
            # 标记包含字幕
            info.has_subtitle = True
            info.subtitle_count = 1
        # webm/ogg 在退路里两边都算（可能包含音频）
        if ext in ('webm', 'ogg', 'ogx'):
            info.has_audio = True
            info.audio_count = 1
        # 返回猜测结果
        return info
        
    # 实例方法 : 扫描工作目录, 分类文件
    def scan_directory(self) -> Tuple[List[StreamInfo], List[StreamInfo], List[StreamInfo]]:
        """
        扫描工作目录, 返回 (视频文件, 音频文件, 字幕文件) 三个列表.
        分类依据是 ffprobe 检测到的实际流类型, 而非扩展名.
        一个文件可以同时出现在多个列表中（如含视频+音频的 mkv）.
        """
        # 初始化三个空列表
        video_files: List[StreamInfo] = []
        audio_files: List[StreamInfo] = []
        subtitle_files: List[StreamInfo] = []
        # 如果工作目录不是有效目录, 直接返回空列表
        if not self.working_dir.is_dir():
            return video_files, audio_files, subtitle_files
        # 遍历目录下的所有文件, 按文件名小写排序
        for entry in sorted(self.working_dir.iterdir(), key=lambda p: p.name.lower()):
            # 如果不是文件, 跳过
            if not entry.is_file():
                continue
            # 获取扩展名
            ext = entry.suffix.lstrip('.').lower()
            # 如果扩展名不在白名单中, 跳过
            if ext not in ALL_MEDIA_EXTENSIONS:
                continue
            # 跳过隐藏文件、临时文件
            if entry.name.startswith('.') or entry.name.startswith('~'):
                continue
            try:
                # 跳过 0 字节文件
                if entry.stat().st_size == 0:
                    continue
            except OSError:
                # 如果无法获取文件状态, 跳过
                continue
            # 探测文件流信息
            info = self.probe_file(entry)
            # 纯字幕文件（只有字幕流, 没有音视频）
            if info.has_subtitle and not info.has_video and not info.has_audio:
                subtitle_files.append(info)
                continue
            # 含视频流 → 放入视频列表
            if info.has_video:
                video_files.append(info)
            # 含音频流（且无视频流）→ 放入音频列表
            # 注意 : 如果文件同时有视频和音频, 它已经在视频列表了, 不重复放入音频列表
            if info.has_audio and not info.has_video:
                audio_files.append(info)
        # 返回分类后的三个列表
        return video_files, audio_files, subtitle_files
        
    # 实例方法 : 扫描所有含音频流的文件
    def scan_all_for_audio(self) -> List[StreamInfo]:
        """
        扫描所有含音频流的文件（包括同时含视频的文件）, 
        用于音频选择步骤.
        """
        # 初始化结果列表
        result: List[StreamInfo] = []
        # 如果工作目录无效, 返回空列表
        if not self.working_dir.is_dir():
            return result
        # 遍历目录文件
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
            info = self.probe_file(entry)
            # 只要包含音频流, 就加入结果列表
            if info.has_audio:
                result.append(info)
        return result
        
    # 实例方法 : 扫描所有含字幕流或为纯字幕格式的文件
    def scan_all_for_subtitles(self) -> List[StreamInfo]:
        """扫描所有含字幕流或为纯字幕格式的文件"""
        result: List[StreamInfo] = []
        if not self.working_dir.is_dir():
            return result
        # 定义纯字幕扩展名集合
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
            if ext in subtitle_exts:
                info = self.probe_file(entry)
                if info.has_subtitle or ext in subtitle_exts:
                    result.append(info)
                    continue
            # 其他扩展名但含字幕流（且无音视频）
            if ext in ALL_MEDIA_EXTENSIONS:
                info = self.probe_file(entry)
                if info.has_subtitle and not info.has_video and not info.has_audio:
                    result.append(info)
        return result
        
    # ────────────── FFmpeg 命令构建 ──────────────
    
    # 实例方法 : 构建精确的 FFmpeg 命令
    def _build_command(
        self,
        video_file: Path,
        audio_files: List[Path],
        subtitle_files: List[Path],
        output_file: Path,
    ) -> List[str]:
        """
        构建精确的 FFmpeg 命令.
        - 视频文件 : 提取视频流（以及其自带的音频/字幕流）
        - 外部音频文件 : 只提取音频流
        - 外部字幕文件 : 只提取字幕流
        全部使用 copy 模式（无损）.
        """
        # 初始化命令列表, 包含 ffmpeg 路径和全局参数
        cmd: List[str] = [self.ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'warning']
        
        # ── 输入文件 ──
        # 添加主视频文件作为第 0 个输入
        cmd.extend(['-i', str(video_file)])          # input 0: 视频
        # 记录当前输入索引
        input_index = 1
        # 遍历外部音频文件, 依次添加为输入
        for af in audio_files:
            cmd.extend(['-i', str(af)])
            input_index += 1
        # 遍历外部字幕文件, 依次添加为输入
        for sf in subtitle_files:
            cmd.extend(['-i', str(sf)])
            input_index += 1
            
        # ── Map 映射 ──
        # 从视频文件中提取 : 视频流 + 自带音频流 + 自带字幕流
        cmd.extend(['-map', '0:v'])         # 视频流（必须）
        cmd.extend(['-map', '0:a?'])        # 自带音频（可选, ?表示没有也不报错）
        cmd.extend(['-map', '0:s?'])        # 自带字幕（可选）
        
        # 从外部音频文件中只提取音频流
        for i in range(len(audio_files)):
            idx = i + 1
            cmd.extend(['-map', f'{idx}:a'])
            
        # 从外部字幕文件中只提取字幕流
        sub_start = 1 + len(audio_files)
        for i in range(len(subtitle_files)):
            idx = sub_start + i
            cmd.extend(['-map', f'{idx}:s'])
            
        # ── 编码器 : 全部 copy（无损）──
        cmd.extend(['-c:v', 'copy'])
        cmd.extend(['-c:a', 'copy'])
        cmd.extend(['-c:s', 'copy'])
        
        # ── MKV 特定选项 ──
        # 强制输出格式为 matroska (MKV)
        cmd.extend(['-f', 'matroska'])
        
        # ── 输出 ──
        # 添加输出文件路径
        cmd.append(str(output_file))
        return cmd
        
    # 实例方法 : 构建备用命令（字幕降级重编码）
    def _build_command_with_subtitle_fallback(
        self,
        video_file: Path,
        audio_files: List[Path],
        subtitle_files: List[Path],
        output_file: Path,
    ) -> List[str]:
        """
        备用命令 : 当 -c:s copy 失败时, 将字幕重编码为 srt/ass.
        MKV 原生支持 srt 和 ass, 这是有损的字幕转换但几乎不影响使用.
        """
        # 初始化命令列表
        cmd: List[str] = [self.ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'warning']
        # 添加视频输入
        cmd.extend(['-i', str(video_file)])
        # 添加音频输入
        for af in audio_files:
            cmd.extend(['-i', str(af)])
        # 添加字幕输入
        for sf in subtitle_files:
            cmd.extend(['-i', str(sf)])
        # 映射视频、音频、字幕流
        cmd.extend(['-map', '0:v'])
        cmd.extend(['-map', '0:a?'])
        cmd.extend(['-map', '0:s?'])
        for i in range(len(audio_files)):
            cmd.extend(['-map', f'{i + 1}:a'])
        sub_start = 1 + len(audio_files)
        for i in range(len(subtitle_files)):
            cmd.extend(['-map', f'{sub_start + i}:s'])
        # 视频和音频保持 copy
        cmd.extend(['-c:v', 'copy'])
        cmd.extend(['-c:a', 'copy'])
        # 不使用 -c:s copy, 让 ffmpeg 自动选择 MKV 兼容的字幕编码器
        # 强制输出格式为 matroska
        cmd.extend(['-f', 'matroska'])
        # 添加输出文件
        cmd.append(str(output_file))
        return cmd
        
    # ────────────── 合并执行 ──────────────
    
    # 实例方法 : 执行合并操作
    def merge_files(
        self,
        video_file: Union[str, Path],
        audio_files: Optional[List[Union[str, Path]]] = None,
        subtitle_files: Optional[List[Union[str, Path]]] = None,
        output_file: Optional[Union[str, Path]] = None,
    ) -> bool:
        """执行合并, 返回是否成功"""
        try:
            # 解析所有输入输出路径为绝对路径
            video_path = Path(video_file).resolve()
            audio_paths = [Path(f).resolve() for f in (audio_files or [])]
            subtitle_paths = [Path(f).resolve() for f in (subtitle_files or [])]
            
            # 验证视频文件存在性
            if not video_path.is_file():
                print(f"  [错误] 视频文件不存在: {video_path}")
                return False
            # 验证并过滤有效的音频和字幕文件
            audio_paths = [p for p in audio_paths if self._check_file(p, '音频')]
            subtitle_paths = [p for p in subtitle_paths if self._check_file(p, '字幕')]
            
            # 确定输出路径
            if output_file:
                output_path = Path(output_file).resolve()
            else:
                # 默认输出文件名为 视频名_merged.mkv
                output_path = video_path.parent / f"{video_path.stem}_merged.mkv"
            # 确保输出扩展名为 .mkv
            if not output_path.suffix.lower() == '.mkv':
                output_path = output_path.with_suffix('.mkv')
            # 创建输出目录（如果不存在）
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 打印合并任务摘要
            print(f"\n{'─' * 60}")
            print(f"  视频 : {video_path.name}")
            print(f"  音频 : {[p.name for p in audio_paths] or '无（保留原音轨）'}")
            print(f"  字幕 : {[p.name for p in subtitle_paths] or '无（保留原字幕）'}")
            print(f"  输出 : {output_path.name}")
            print(f"{'─' * 60}")
            
            # ── 第一次尝试 : 全部 copy ──
            cmd = self._build_command(video_path, audio_paths, subtitle_paths, output_path)
            if self.verbose:
                print(f"\n  [命令] {' '.join(cmd)}\n")
            # 执行命令
            success = self._execute(cmd)
            
            # ── 第二次尝试 : 字幕不 copy（降级） ──
            # 如果第一次失败且存在字幕文件, 尝试降级重编码字幕
            if not success and subtitle_paths:
                print("  [重试] 字幕 copy 失败, 尝试自动编码字幕...")
                cmd2 = self._build_command_with_subtitle_fallback(
                    video_path, audio_paths, subtitle_paths, output_path
                )
                if self.verbose:
                    print(f"  [命令] {' '.join(cmd2)}\n")
                success = self._execute(cmd2)
                
            # 打印最终结果
            if success:
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"\n  [成功] {output_path}  ({size_mb:.1f} MB)")
            else:
                print(f"\n  [失败] 合并未成功, 请检查输入文件.")
            return success
        except Exception as e:
            # 捕获并打印异常堆栈
            print(f"  [异常] {e}")
            import traceback
            traceback.print_exc()
            return False
            
    # 静态方法 : 检查文件是否有效
    @staticmethod
    def _check_file(path: Path, label: str) -> bool:
        # 如果文件不存在, 打印提示并返回 False
        if not path.is_file():
            print(f"  [跳过] {label}文件不存在: {path}")
            return False
        try:
            # 如果文件为空（0字节）, 打印提示并返回 False
            if path.stat().st_size == 0:
                print(f"  [跳过] {label}文件为空: {path}")
                return False
        except OSError:
            # 如果无法访问文件, 打印提示并返回 False
            print(f"  [跳过] {label}文件不可访问: {path}")
            return False
        return True
        
    # 静态方法 : 执行 FFmpeg 命令
    @staticmethod
    def _execute(cmd: List[str]) -> bool:
        """执行 FFmpeg 命令"""
        try:
            # 使用 Popen 启动子进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # 等待进程结束, 设置 1 小时超时
            _, stderr = process.communicate(timeout=3600)  # 1 小时超时
            # 如果返回码为 0, 表示成功
            if process.returncode == 0:
                return True
            # 打印精简的错误信息
            if stderr:
                lines = stderr.strip().splitlines()
                # 过滤出包含关键错误词汇的行
                error_lines = [
                    l for l in lines
                    if any(kw in l.lower() for kw in ('error', 'fail', 'invalid', 'not'))
                ]
                if error_lines:
                    print("  [FFmpeg 错误]:")
                    # 最多打印前 10 行错误
                    for el in error_lines[:10]:
                        print(f"    {el.strip()}")
                else:
                    # 如果没有匹配的关键错误, 打印最后 5 行输出
                    print(f"  [FFmpeg 退出码] {process.returncode}")
                    for l in lines[-5:]:
                        print(f"    {l.strip()}")
            return False
        except subprocess.TimeoutExpired:
            # 超时处理 : 强制杀死进程
            process.kill()
            print("  [超时] FFmpeg 执行超时")
            return False
        except Exception as e:
            print(f"  [执行异常] {e}")
            return False
            
    # ────────────── 交互模式 ──────────────
    
    # 实例方法 : 交互式文件选择
    def interactive(self) -> bool:
        """
        交互式文件选择.
        核心改进 : 通过 ffprobe 检测实际流类型, 
        .webm（纯音频）会出现在音频列表中, 
        不再依赖扩展名分类.
        """
        try:
            # 打印交互模式欢迎信息
            print(f"\n{'═' * 60}")
            print("  FFmpeg 媒体合并器 — 交互模式")
            print(f"  工作目录: {self.working_dir}")
            print(f"{'═' * 60}")
            
            # ── 扫描 ──
            print("\n  正在扫描目录并检测文件流类型...")
            video_list, _, _ = self.scan_directory()
            audio_list = self.scan_all_for_audio()
            subtitle_list = self.scan_all_for_subtitles()
            
            # ── 步骤 1: 选择视频 ──
            if not video_list:
                print("  [错误] 目录中未找到含视频流的文件")
                return False
            print(f"\n  [步骤 1/3] 选择视频文件（共 {len(video_list)} 个）")
            print(f"  {'─' * 50}")
            # 打印视频列表及流信息
            for i, v in enumerate(video_list, 1):
                size_mb = v.path.stat().st_size / (1024 * 1024)
                tag = f"V×{v.video_count}"
                if v.has_audio:
                    tag += f" A×{v.audio_count}"
                if v.has_subtitle:
                    tag += f" S×{v.subtitle_count}"
                print(f"    {i:3d}. {v.path.name}  [{tag}]  {size_mb:.1f} MB")
            # 获取用户选择的视频
            video_info = self._pick_one(video_list, "视频")
            if not video_info:
                return False
            print(f"  -> 已选: {video_info.path.name}\n")
            
            # ── 步骤 2: 选择音频 ──
            # 排除已选的视频文件本身
            audio_candidates = [a for a in audio_list if a.path != video_info.path]
            print(f"  [步骤 2/3] 选择音频文件（共 {len(audio_candidates)} 个, 可多选）")
            print(f"  {'─' * 50}")
            if audio_candidates:
                for i, a in enumerate(audio_candidates, 1):
                    size_mb = a.path.stat().st_size / (1024 * 1024)
                    tag = f"A×{a.audio_count}"
                    ext = a.path.suffix.lower()
                    print(f"    {i:3d}. {a.path.name}  [{tag}] ({ext})  {size_mb:.1f} MB")
                # 获取用户多选音频
                selected_audio = self._pick_multiple(audio_candidates, "音频")
            else:
                print("    （目录中无可用音频文件）")
                selected_audio = []
            # 打印选择结果
            if selected_audio:
                print(f"  -> 已选 {len(selected_audio)} 个音频:")
                for a in selected_audio:
                    print(f"       {a.path.name}")
            else:
                print("  -> 未选择外部音频（将保留视频原音轨）")
            print()
            
            # ── 步骤 3: 选择字幕 ──
            # 排除已选的视频文件本身
            subtitle_candidates = [s for s in subtitle_list if s.path != video_info.path]
            print(f"  [步骤 3/3] 选择字幕文件（共 {len(subtitle_candidates)} 个, 可多选）")
            print(f"  {'─' * 50}")
            if subtitle_candidates:
                for i, s in enumerate(subtitle_candidates, 1):
                    size_kb = s.path.stat().st_size / 1024
                    ext = s.path.suffix.lower()
                    print(f"    {i:3d}. {s.path.name}  ({ext})  {size_kb:.1f} KB")
                # 获取用户多选字幕
                selected_subs = self._pick_multiple(subtitle_candidates, "字幕")
            else:
                print("    （目录中无可用字幕文件）")
                selected_subs = []
            # 打印选择结果
            if selected_subs:
                print(f"  -> 已选 {len(selected_subs)} 个字幕:")
                for s in selected_subs:
                    print(f"       {s.path.name}")
            else:
                print("  -> 未选择外部字幕")
            print()
            
            # ── 确认 ──
            print(f"{'═' * 60}")
            print(f"  视频: {video_info.path.name}")
            print(f"  音频: {[a.path.name for a in selected_audio] or '保留原音轨'}")
            print(f"  字幕: {[s.path.name for s in selected_subs] or '无'}")
            print(f"{'═' * 60}")
            # 等待用户确认
            confirm = input("\n  确认执行？(Y/n): ").strip().lower()
            if confirm == 'n':
                print("  已取消.")
                return False
                
            # ── 输出文件名 ──
            default_name = f"{video_info.path.stem}_merged.mkv"
            out_input = input(f"  输出文件名 (回车使用 {default_name}): ").strip()
            if not out_input:
                out_input = default_name
            if not out_input.lower().endswith('.mkv'):
                out_input += '.mkv'
            output_path = self.working_dir / out_input
            
            # ── 执行 ──
            # 调用 merge_files 执行实际合并
            return self.merge_files(
                video_info.path,
                [a.path for a in selected_audio],
                [s.path for s in selected_subs],
                output_path,
            )
        except KeyboardInterrupt:
            # 捕获 Ctrl+C 中断
            print("\n\n  操作已取消.")
            return False
        except Exception as e:
            # 捕获其他异常
            print(f"\n  [错误] {e}")
            import traceback
            traceback.print_exc()
            return False
            
    # 静态方法 : 从列表中选择单个文件
    @staticmethod
    def _pick_one(items: List[StreamInfo], label: str) -> Optional[StreamInfo]:
        """从列表中选一个"""
        while True:
            # 获取用户输入
            raw = input(f"  请输入编号 (1-{len(items)}) 或文件名关键字: ").strip()
            if not raw:
                continue
            # 如果输入的是数字
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(items):
                    return items[idx]
                print(f"  编号超出范围, 请重试")
                continue
            # 如果是关键字匹配
            keyword = raw.lower()
            matches = [it for it in items if keyword in it.path.name.lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"  匹配到 {len(matches)} 个文件, 请更精确:")
                for m in matches:
                    print(f"    {m.path.name}")
                continue
            else:
                # 尝试作为完整路径解析
                p = Path(raw)
                if p.is_file():
                    dummy = StreamInfo(p)
                    dummy.has_video = True
                    return dummy
                print(f"  未匹配到任何文件, 请重试")
                
    # 静态方法 : 从列表中多选文件
    @staticmethod
    def _pick_multiple(items: List[StreamInfo], label: str) -> List[StreamInfo]:
        """从列表中多选（逗号/空格分隔）, 支持 all 关键字"""
        while True:
            raw = input(
                f"  请输入编号 (逗号分隔, 'all'=全选, 回车=跳过): "
            ).strip()
            # 回车跳过
            if not raw:
                return []
            # 全选
            if raw.lower() == 'all':
                return list(items)
            # 支持逗号和空格分隔
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
                    keyword = part.lower()
                    matches = [it for it in items if keyword in it.path.name.lower()]
                    for m in matches:
                        if m not in selected:
                            selected.append(m)
            if not selected and valid:
                print("  未匹配到有效文件")
                continue
            return selected
            
    # ────────────── 自动模式 ──────────────
    
    # 实例方法 : 自动匹配同名文件并合并
    def auto_merge(self, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, bool]:
        """自动匹配同名文件并合并"""
        results: Dict[str, bool] = {}
        # 确定输出目录
        out_dir = Path(output_dir).resolve() if output_dir else self.working_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        # 扫描目录
        video_list, _, _ = self.scan_directory()
        all_audio = self.scan_all_for_audio()
        all_subs = self.scan_all_for_subtitles()
        if not video_list:
            print("  [错误] 目录中未找到含视频流的文件")
            return results
        print(f"  找到 {len(video_list)} 个视频文件\n")
        # 遍历每个视频文件
        for v in video_list:
            stem = v.path.stem.lower()
            # 匹配同名的外部音频（排除视频文件自身）
            matched_audio = [
                a for a in all_audio
                if a.path != v.path and stem in a.path.stem.lower()
            ]
            # 匹配同名的外部字幕（排除视频文件自身）
            matched_subs = [
                s for s in all_subs
                if s.path != v.path and stem in s.path.stem.lower()
            ]
            output_path = out_dir / f"{v.path.stem}_merged.mkv"
            print(f"  处理: {v.path.name}")
            print(f"    音频: {[a.path.name for a in matched_audio] or '无'}")
            print(f"    字幕: {[s.path.name for s in matched_subs] or '无'}")
            # 执行合并
            success = self.merge_files(
                v.path,
                [a.path for a in matched_audio],
                [s.path for s in matched_subs],
                output_path,
            )
            results[v.path.stem] = success
            print()
        return results

# ────────────── 入口 ──────────────

# 定义主函数
def main():
    # 导入命令行参数解析模块
    import argparse
    # 创建解析器对象
    parser = argparse.ArgumentParser(
        description='FFmpeg 媒体合并器 v3 — 基于 ffprobe 流类型检测'
    )
    # 添加命令行参数
    parser.add_argument('-d', '--dir', help='工作目录（默认当前目录）')
    parser.add_argument('-a', '--auto', action='store_true', help='自动匹配模式')
    parser.add_argument('-o', '--output-dir', help='输出目录（自动模式）')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
    parser.add_argument('-q', '--quiet', action='store_true', help='安静模式')
    parser.add_argument('-v', '--video', help='手动指定视频文件')
    parser.add_argument('-A', '--audio', nargs='*', help='手动指定音频文件')
    parser.add_argument('-S', '--subtitle', nargs='*', help='手动指定字幕文件')
    parser.add_argument('-O', '--output', help='手动指定输出文件')
    parser.add_argument('-I', '--info', help='显示文件流信息')
    # 解析参数
    args = parser.parse_args()
    try:
        # 初始化合并器实例
        merger = FFmpegMediaMerger(args.dir)
        merger.verbose = not args.quiet
        # 处理 --info 参数 : 仅显示文件流信息
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
        if args.video:
            merger.merge_files(args.video, args.audio, args.subtitle, args.output)
            return
        # 处理自动模式参数
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
        merger.interactive()
    except Exception as e:
        # 捕获致命错误并退出
        print(f"  [致命错误] {e}")
        sys.exit(1)

# 脚本入口点判断
if __name__ == '__main__':
    # 调用主函数
    main()
